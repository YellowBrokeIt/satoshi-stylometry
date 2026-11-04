#!/usr/bin/env python3
"""Era-shift test.  Claim under test (unverified): Elon grew up with South-African (British) spelling and shifted to American.
We can only test the writing that exists: blog 2006-2016, court/trial-released emails+texts 2010-2026 (elonmuskarchive.org excerpts),
and X posts 2010-2026.  There is NO accessible Elon writing from 1971-2005 (so the 1989 move cannot be tested directly).
Also: how consistent is Satoshi's spelling?  (variant-pair counts)"""
import re, collections, json
import pandas as pd
from bs4 import BeautifulSoup
from common import *
import spelling_lists as SL
CATS = SL.build()

def proper_noun(t, m):
    w = m.group(0)
    if not w[0].isupper() or w.isupper() and len(w) < 4: return False
    prev = t[:m.start()].rstrip()
    return bool(prev) and prev[-1] not in '.!?:\n"“(' and not t[:m.start()].endswith('\n')

def count(texts):
    B = collections.Counter(); A = collections.Counter()
    for t in texts:
        for c, (rb, ra, _, _) in CATS.items():
            for m in rb.finditer(t):
                if not proper_noun(t, m): B[m.group(0).lower()] += 1
            for m in ra.finditer(t):
                if not proper_noun(t, m): A[m.group(0).lower()] += 1
    return B, A

# ---------------------------------------------------------------- Elon writing with dates
elon = read_jsonl(f'{CORPUS}/elon.jsonl')
docs = []   # (year, genre, text)
for r in elon:
    t = MENTION_RE.sub(' ', URL_RE.sub(' ', r['text']))
    if r['genre'] == 'tweet': docs.append((int(r['date'][-4:]), 'X posts', t))
BLOG_YEAR = {'musk-blog-master-plan-2006': 2006, 'musk-blog-master-plan-part-deux-2016': 2016, 'musk-blog-model-s-fire-2013': 2013,
             'musk-blog-patents-2014': 2014, 'musk-blog-peculiar-test-drive-2013': 2013}
for r in elon:
    if r['genre'] == 'blog': docs.append((BLOG_YEAR[r['doc_id'][5:]], 'Tesla blog', r['text']))
# emails/texts released in court + company emails (excerpts as displayed by elonmuskarchive.org/emails); Elon-authored entries only
s = BeautifulSoup(open(f'{RAW}/elon/emails_page.html').read(), 'lxml')
for t in s(['script', 'style']): t.decompose()
lines = [l.strip() for l in s.get_text('\n').split('\n') if l.strip()]
starts = [i for i in range(len(lines) - 3) if lines[i] == 'EM' and lines[i+1] == 'Elon Musk' and re.match(r'^[A-Z][a-z]{2} \d{1,2}, \d{4}$', lines[i+2])]
emails = []
for a, b in zip(starts, starts[1:] + [len(lines)]):
    date, title, body = lines[a+2], lines[a+3], ' \n'.join(lines[a+4:b])
    if not title.startswith('Musk to'): continue            # skip 'X to Musk' and mixed threads (not his words)
    body = re.sub(r'\s*[—-] Elon \(text to [^)]*\)', '', body)
    emails.append(dict(year=int(date[-4:]), title=title, words=len(body.split()), text=body))
    docs.append((int(date[-4:]), 'Emails/texts', body))
pd.DataFrame([{k: v for k, v in e.items() if k != 'text'} for e in emails]).to_csv(f'{RESULTS}/era_elon_email_entries.csv', index=False)
print('email/text entries used:', len(emails), 'words', sum(e['words'] for e in emails))

ERAS = [('2006 (blog)', 2006, 2006), ('2010-2012', 2010, 2012), ('2013-2016', 2013, 2016), ('2017-2020', 2017, 2020), ('2021-2024', 2021, 2024), ('2025-2026', 2025, 2026)]
rows = []; forms = {}
for name, lo, hi in ERAS:
    for genre in ['ALL', 'X posts', 'Tesla blog', 'Emails/texts']:
        tx = [t for y, g, t in docs if lo <= y <= hi and (genre == 'ALL' or g == genre)]
        if not tx: continue
        B, A = count(tx); w = sum(len(t.split()) for t in tx)
        b, a = sum(B.values()), sum(A.values()); lo_, hi_ = wilson(b, b + a) if b + a else (float('nan'),)*2
        rows.append(dict(era=name, genre=genre, docs=len(tx), words=w, british=b, american=a, pct_british=100*b/(a+b) if a+b else float('nan'),
                         ci_lo=100*lo_, ci_hi=100*hi_, british_forms='; '.join(f'{k}:{v}' for k, v in B.most_common(12))))
era = pd.DataFrame(rows); era.to_csv(f'{RESULTS}/era_shift_elon.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 90)
print(era.drop(columns=['ci_lo', 'ci_hi']).round(2).to_string(index=False))

# Elon by single year (all genres) for the chart's fine print
yr = []
for y in range(2006, 2027):
    tx = [t for yy, g, t in docs if yy == y]
    if not tx: continue
    B, A = count(tx); yr.append(dict(year=y, words=sum(len(t.split()) for t in tx), british=sum(B.values()), american=sum(A.values())))
pd.DataFrame(yr).to_csv(f'{RESULTS}/era_shift_elon_by_year.csv', index=False)

# ---------------------------------------------------------------- Satoshi: is the spelling consistent?
sat = [r for r in read_jsonl(f'{CORPUS}/satoshi.jsonl')]
def pairmap():
    pm = {}
    for c, (rb, ra, b, a) in CATS.items():
        for x, y in zip(b, a): pm[x] = (y, c)
    return pm
PM = pairmap()
def pair_table(texts):
    B, A = count(texts); tab = collections.defaultdict(lambda: [0, 0, ''])
    # group inflections by the American stem, using explicit partner map
    for x, n in B.items():
        y, c = PM[x]; k = re.sub(r'(e|es|ed|ing|ation|ations|er|ers|s|ings)$', '', y); tab[k][0] += n; tab[k][2] = c
    for y, n in A.items():
        k = re.sub(r'(e|es|ed|ing|ation|ations|er|ers|s|ings)$', '', y); tab[k][1] += n
    t = pd.DataFrame([dict(stem=k, british=v[0], american=v[1], category=v[2]) for k, v in tab.items()])
    return t
st = pair_table([r['text'] for r in sat if r['genre'] != 'paper' or True])
st['total'] = st.british + st.american; st = st.sort_values('total', ascending=False)
st.to_csv(f'{RESULTS}/satoshi_spelling_pairs.csv', index=False)
print('\nSATOSHI variant pairs (stem: british / american)'); print(st.head(25).to_string(index=False))
mixed = st[(st.british > 0) & (st.american > 0)]
print('stems used in BOTH variants by Satoshi:', len(mixed), 'of', len(st), '| British-only stems:', int(((st.british > 0) & (st.american == 0)).sum()), '| American-only stems:', int(((st.british == 0) & (st.american > 0)).sum()))
# Satoshi by year, dated docs only
sy = collections.defaultdict(list)
for r in sat:
    if r['genre'] == 'paper': sy['2008'].append(r['text']); continue
    m = re.search(r'(200\d|2010)', r.get('date', '') or '')
    if m: sy[m.group(1)].append(r['text'])
    else: sy['undated (private emails)'].append(r['text'])
sr = []
for k, tx in sorted(sy.items()):
    B, A = count(tx); sr.append(dict(period=k, docs=len(tx), words=sum(len(t.split()) for t in tx), british=sum(B.values()), american=sum(A.values())))
sr = pd.DataFrame(sr); sr.to_csv(f'{RESULTS}/era_satoshi_by_year.csv', index=False); print(sr.to_string(index=False))

# ---------------------------------------------------------------- the four words in the Grok claim
W = {'colour/color': (r'colou?r(?:s|ed|ing)?', r'colou?r'), 'realise/realize': r'realis|realiz', 'organise/organize': r'organis|organiz', 'centre/center': r'centre|center'}
def wc(texts, uk, us):
    u = sum(len(re.findall(rf'\b{uk}\w*', t, re.I)) for t in texts); a = sum(len(re.findall(rf'\b{us}\w*', t, re.I)) for t in texts); return u, a
SUF = r'(?:e|es|ed|ing|ation|ations|er|ers)\b'
words = {'colour/color': ('colour', 'color'), 'realise/realize': ('realis', 'realiz'), 'organise/organize': ('organis', 'organiz'), 'centre/center': ('centre', 'center'),
         'optimise/optimize': ('optimis', 'optimiz'), 'whilst/while': ('whilst', 'while')}
SUFS = {'colour/color': r'(?:s|ed|ing|ful)?\b', 'centre/center': r'(?:s|d|ed|ing)?\b'}
sets = {'Satoshi (all)': [r['text'] for r in sat], 'Elon X posts 2010-2024': [t for y, g, t in docs if g == 'X posts' and y <= 2024],
        'Elon X posts 2025-26': [t for y, g, t in docs if g == 'X posts' and y >= 2025], 'Elon blog+emails 2006-2026': [t for y, g, t in docs if g != 'X posts']}
wr = []
for sname, tx in sets.items():
    for w, (uk, us) in words.items():
        if w == 'whilst/while':
            u = sum(len(re.findall(r'\bwhilst\b', t, re.I)) for t in tx); a = sum(len(re.findall(r'\bwhile\b', t, re.I)) for t in tx)
        else:
            tx2 = []
            u = a = 0
            for t in tx:
                for m in re.finditer(rf'\b({uk}|{us})' + SUFS.get(w, SUF), t, re.I):
                    if proper_noun(t, m): continue
                    if m.group(1).lower() == uk: u += 1
                    else: a += 1
        wr.append(dict(corpus=sname, word=w, british=u, american=a))
wr = pd.DataFrame(wr); wr.to_csv(f'{RESULTS}/era_claim_words.csv', index=False)
docs_b = sum(1 for r in sat if any(not proper_noun(r['text'], m) for rb, *_ in CATS.values() for m in rb.finditer(r['text'])))
print('Satoshi docs containing >=1 British -ise/-our/etc form:', docs_b, 'of', len(sat))
json.dump(dict(docs_with_british=docs_b, docs=len(sat)), open(f'{RESULTS}/satoshi_british_doc_count.json', 'w'))
print(wr.pivot(index='corpus', columns='word', values=['british', 'american']).to_string())
