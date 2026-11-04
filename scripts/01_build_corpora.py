#!/usr/bin/env python3
"""Build text corpora (JSONL) from the raw downloads in data/raw/.

Whitespace is NEVER normalised here: double spaces survive wherever the source preserved them.
Outputs data/corpus/{satoshi,controls,elon}.jsonl
"""
import re, json, glob, gzip, html, subprocess, sys, os, collections
import pandas as pd
from email import message_from_string
from common import *

# ------------------------------------------------------------------ helpers
QUOTE_ATTR = re.compile(r'^(on .{5,120}(wrote|writes)\s*:?|.{3,120}\bwrote\s*:|.{3,120}\bwrites\s*:|-+\s*original message\s*-+.*|from:\s.*|quoting .*)$', re.I)

def strip_quotes(text):
    """Remove quoted lines (>), attribution lines, and everything after a signature marker."""
    out = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('>') or ln.startswith('|'):
            i += 1; continue
        if ln.rstrip() == '--' or ln.startswith('-- ') and len(ln) <= 4:
            break
        if re.match(r'^\s*-{2,}\s*original message', ln, re.I):
            break
        # attribution can wrap over two lines: "On Mon, Jan 5, X wrote:" -- check joined with next line
        joined = (ln + ' ' + (lines[i+1] if i+1 < len(lines) else '')).strip()
        if re.match(r'^on .{5,160}wrote\s*:\s*$', joined, re.I) or re.match(r'^on .{5,160}wrote\s*:\s*$', ln.strip(), re.I):
            i += 2 if not re.match(r'^on .{5,160}wrote\s*:\s*$', ln.strip(), re.I) else 1
            continue
        if re.match(r'^.{3,100}\bwrote:\s*$', ln.strip()):
            i += 1; continue
        out.append(ln)
        i += 1
    return '\n'.join(out)

def dedupe_paragraphs(docs):
    """Drop paragraphs already seen (e.g. the abstract pasted into many emails)."""
    seen = set()
    for d in docs:
        paras = re.split(r'\n\s*\n', d['text'])
        keep = []
        for p in paras:
            k = re.sub(r'\s+', ' ', p).strip().lower()
            if len(k) > 120 and k in seen:
                continue
            seen.add(k); keep.append(p)
        d['text'] = '\n\n'.join(keep)
    return docs

def md_email_to_text(md):
    """lugaxker 'doc/*.md' email -> (from_header, body). <br> -> newline; &nbsp; -> space."""
    md = md.replace('\\>', '>').replace('\\]', ']').replace('\\[', '[')
    body = md.split('\n', 1)[1] if md.startswith('# ') else md
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = body.replace('&nbsp;', ' ')
    body = html.unescape(body)
    m = re.search(r'^From:\s*(.+)$', body, re.M)
    frm = m.group(1) if m else ''
    # split header from body at first blank line AFTER a Subject:/From: header
    parts = re.split(r'\n\s*\n', body.strip('\n'), maxsplit=1)
    txt = parts[1] if len(parts) > 1 else ''
    return frm, txt

def html_post_to_text(h):
    """SNI forum post html -> text. Quote blocks and code blocks removed; <br/> -> \n; &nbsp; -> ' '."""
    h = re.sub(r'<div class="quoteheader">.*?</div>\s*<div class="quote">.*?</div>', '', h, flags=re.S)
    h = re.sub(r'<div class="codeheader">.*?</div>\s*<div class="code">.*?</div>', '', h, flags=re.S)
    h = re.sub(r'<div class="quoteheader">.*?</div>', '', h, flags=re.S)
    h = re.sub(r'<br\s*/?>', '\n', h)
    h = re.sub(r'<img [^>]*alt="([^"]*)"[^>]*>', r' [\1] ', h)  # smileys
    h = re.sub(r'<[^>]+>', '', h)
    h = h.replace('&nbsp;', ' ')
    return html.unescape(h)

# ------------------------------------------------------------------ SATOSHI
sat = []
d = json.load(open(f'{RAW}/nisrepo/server/data/emails.json'))
em = []
for e in d:
    if e.get('satoshi_id'):
        em.append(dict(doc_id=f"sni-email-{e['id']}", author='Satoshi Nakamoto', source='sni_emails_json',
                       genre='email_list', date=e['date'], url=e.get('url'),
                       text=strip_quotes(e['text'])))
em.sort(key=lambda r: r['date'])
sat += dedupe_paragraphs(em)

for f in sorted(glob.glob(f'{RAW}/lug/doc/*/*.md')):
    sub = f.split('/')[-2]
    if sub not in ('adam-back', 'wei-dai', 'hal-finney'): continue
    frm, body = md_email_to_text(open(f).read())
    if 'satoshi' in frm.lower():
        sat.append(dict(doc_id=f"lug-{sub}-{os.path.basename(f)[:-3]}", author='Satoshi Nakamoto',
                        source='lugaxker_private_emails', genre='email_private', date='', url='',
                        text=strip_quotes(body)))

d = json.load(open(f'{RAW}/nisrepo/server/data/forum_posts.json'))
for p in d:
    if p.get('satoshi_id'):
        sat.append(dict(doc_id=f"sni-post-{p['id']}", author='Satoshi Nakamoto', source='sni_forum_posts_json',
                        genre='forum', date=p['date'], url=p.get('url'), text=html_post_to_text(p['text'])))

pdf = f'{RAW}/lug/src/bitcoin.pdf'
wp = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
wp = wp.split('References')[0]  # drop reference list
sat.append(dict(doc_id='whitepaper', author='Satoshi Nakamoto', source='bitcoin.pdf (pdftotext)', genre='paper',
                date='2008-10-31', url='https://bitcoin.org/bitcoin.pdf', text=wp))
for r in sat: r['text'] = r['text'].strip('\n')
write_jsonl(f'{CORPUS}/satoshi.jsonl', sat)
print('satoshi docs', len(sat), collections.Counter(r['genre'] for r in sat))

# ------------------------------------------------------------------ CONTROLS
ctrl = []
# (a) Metzdowd cryptography list 2006-2010
NAMEMAP = {}
def parse_from(h):
    m = re.search(r'\(([^)]+)\)', h)
    if m: return m.group(1).strip().strip('"')
    m = re.match(r'"?([^"<]+?)"?\s*<', h)
    return (m.group(1) if m else h).strip()
cnt = collections.Counter()
for f in sorted(glob.glob(f'{RAW}/ctrl/metzdowd/*.txt.gz')):
    raw = gzip.open(f, 'rt', errors='replace').read()
    msgs = re.split(r'\nFrom \S+ at \S+\s{1,3}\w{3} \w{3}\s+\d+ \d\d:\d\d:\d\d \d{4}\n', '\n' + raw)
    for k, m in enumerate(msgs):
        if not m.strip(): continue
        try: msg = message_from_string(m)
        except Exception: continue
        frm = msg.get('From', '')
        name = parse_from(frm)
        body = msg.get_payload(decode=False) if not msg.is_multipart() else ''
        if not isinstance(body, str): continue
        body = strip_quotes(body)
        # skip the Satoshi messages (they are in the Satoshi corpus)
        if 'satoshi' in name.lower() or 'satoshi' in frm.lower(): continue
        ctrl.append(dict(doc_id=f"metz-{os.path.basename(f)[:-7]}-{k}", author=name, source='metzdowd_cryptography_list',
                         genre='email_list', date=msg.get('Date', ''), url='', text=body.strip('\n')))
# (b) SNI forum posts by others (BitcoinTalk, same threads as Satoshi)
d = json.load(open(f'{RAW}/nisrepo/server/data/forum_posts.json'))
for p in d:
    if not p.get('satoshi_id'):
        ctrl.append(dict(doc_id=f"sni-post-{p['id']}", author=p['poster_name'], source='sni_forum_posts_json', genre='forum',
                         date=p['date'], url=p.get('url'), text=html_post_to_text(p['text'])))
# (c) Hal Finney's private emails to Satoshi (lug md files)
for f in sorted(glob.glob(f'{RAW}/lug/doc/hal-finney/*.md')):
    frm, body = md_email_to_text(open(f).read())
    if 'hal' in frm.lower() and 'finney' in frm.lower():
        ctrl.append(dict(doc_id=f"lug-hal-{os.path.basename(f)[:-3]}", author='Hal Finney', source='lugaxker_private_emails',
                         genre='email_private', date='', url='', text=strip_quotes(body)))
# (d) SNI library essays (markdown) by Szabo, Finney, Dai, Back etc.
lib = f'{RAW}/nisrepo/server/content/library'
for f in sorted(glob.glob(f'{lib}/*.en.md')):
    t = open(f).read()
    m = re.match(r'---\n(.*?)\n---\n(.*)', t, re.S)
    if not m: continue
    fm, body = m.groups()
    auth = re.findall(r'^\s+-\s+(\S+)\s*$', fm.split('authors:')[1].split('\n', 1)[1] if 'authors:' in fm else '', re.M)
    # authors block ends at next key
    blk = re.search(r'authors:\n((?:\s+- .*\n?)+)', fm)
    auth = re.findall(r'-\s+(\S+)', blk.group(1)) if blk else []
    title = re.search(r'^title:\s*(.*)$', fm, re.M)
    if len(auth) != 1: continue
    nm = {'nick-szabo': 'Nick Szabo', 'hal-finney': 'Hal Finney', 'wei-dai': 'Wei Dai', 'adam-back': 'Adam Back',
          'timothy-c-may': 'Tim May', 'ian-grigg': 'Ian Grigg', 'david-chaum': 'David Chaum'}.get(auth[0])
    if not nm: continue
    ctrl.append(dict(doc_id=f"sni-lib-{os.path.basename(f)[:-6]}", author=nm, source='sni_library_essay', genre='essay',
                     date='', url='', text=body.strip('\n')))
for r in ctrl: r['text'] = r['text'].strip('\n')
write_jsonl(f'{CORPUS}/controls.jsonl', ctrl)
print('control docs', len(ctrl), collections.Counter(r['genre'] for r in ctrl))

# ------------------------------------------------------------------ ELON
elon = []
# (a) big scraped CSV (cmj/elontweets) -- whitespace is normalised in this source
df = pd.read_csv(f'{RAW}/elon/elonmusk-all-tweets.csv', dtype=str)
df['Text'] = df['Text'].fillna('')
n_all = len(df)
for _, r in df.iterrows():
    t = r['Text']
    if t.startswith('RT @'): continue
    # The scrape appends a quoted post (someone else's words) after a '[@quoted_handle]' marker -> keep only Elon's own text
    t = re.split(r'\[@\w+\]', t)[0].strip()
    if not t: continue
    elon.append(dict(doc_id=f"cmj-{r['Id']}", author='Elon Musk', source='cmj_elontweets_csv', genre='tweet',
                     date=r['Date'], url=r['Url'], text=t))
print('cmj rows', n_all, 'non-RT', len(elon))
# (b) raw X API samples (whitespace preserved)
# (b) raw X API samples (whitespace preserved); produced by scripts/x_fetch_posts.py from data/ids/*.txt
def x_posts(user):
    for p in read_jsonl(f'{RAW}/x_posts/{user}.jsonl'):
        yield p, (p.get('note_text') or p['text'])
for p, t in x_posts('elonmusk'):
    elon.append(dict(doc_id=f"xapi-{p['id']}", author='Elon Musk', source='x_api_sample', genre='tweet_raw',
                     date=p['created_at'], url=f"https://x.com/elonmusk/status/{p['id']}", text=t))
# (c) Elon blog prose (elonmuskarchive.org copies of Tesla blog posts)
from bs4 import BeautifulSoup
for slug in ['musk-blog-master-plan-2006', 'musk-blog-master-plan-part-deux-2016', 'musk-blog-model-s-fire-2013',
             'musk-blog-patents-2014', 'musk-blog-peculiar-test-drive-2013']:
    s = BeautifulSoup(open(f'{RAW}/elon/prose/{slug}.html').read(), 'lxml')
    for t in s(['script', 'style', 'nav', 'header', 'footer']): t.decompose()
    m = s.find('article') or s.find('main') or s.body
    txt = m.get_text('\n').strip()
    txt = re.sub(r'^←\s*\n\s*Back\s*\n', '', txt)
    txt = txt.split('Source:')[0] if 'Source:' in txt[-600:] else txt
    elon.append(dict(doc_id=f"blog-{slug}", author='Elon Musk', source='elonmuskarchive.org (Tesla blog copy)', genre='blog',
                     date='', url=f'https://elonmuskarchive.org/blog/{slug}', text=txt))
write_jsonl(f'{CORPUS}/elon.jsonl', elon)
print('elon docs', len(elon), collections.Counter(r['genre'] for r in elon))

# (d) control tweets (X API, whitespace preserved)
ct = []
for user in ['adam3us', 'NickSzabo4', 'VitalikButerin']:
    for p, t in x_posts(user):
        ct.append(dict(doc_id=f"xapi-{user}-{p['id']}", author=f'{user} (tweets)', source='x_api_sample', genre='tweet_raw',
                       date=p['created_at'], url=f"https://x.com/{user}/status/{p['id']}", text=t))
write_jsonl(f'{CORPUS}/control_tweets.jsonl', ct)
print('control tweets', len(ct))
