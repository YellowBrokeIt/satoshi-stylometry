#!/usr/bin/env python3
"""Analysis 1: double space after a sentence-ending full stop.

Unit of analysis: an INLINE sentence boundary = [.!?] (+ closing quote/bracket) followed by 1+ spaces and then an
uppercase letter / digit / opening quote, on the SAME line.  Boundaries that fall at a line break (hard-wrapped e-mail,
tweets with newlines) are invisible to us and are not counted.  rate = double / (single + double).
"""
import re, json, collections
import pandas as pd
from common import *

ABBR = {'e.g','i.e','vs','mr','mrs','ms','dr','inc','st','no','fig','eq','cf','al','u.s','ph.d','approx','esp','sec','vol','jr','sr','ca'}
BOUND = re.compile(r'(\S{0,12})([.!?])(["\')\]”’]*)( +)(?=["“(\[]?[A-Z0-9])')

def boundaries(text):
    """yield (kind, context) for every inline sentence boundary; kind in {'single','double'}"""
    for line in text.split('\n'):
        for m in BOUND.finditer(line):
            tok = m.group(1)
            word = re.sub(r'^[\W_]+', '', tok)
            if m.group(2) == '.':
                if word.lower().rstrip('.') in ABBR: continue
                if len(word) == 1 and word.isalpha() and word.isupper(): continue   # initials "A. Back"
                if re.fullmatch(r'\d{1,2}', word) and line[:m.start()+len(tok)].strip() == tok.strip(): continue  # "1. item"
                if '.' in word and len(word) <= 4: continue  # a.m. p.m. etc
            kind = 'double' if len(m.group(4)) >= 2 else 'single'
            ctx = line[max(0, m.start()-25): m.end()+25]
            yield kind, ctx

def count(rows):
    s = d = 0; ex = []
    for r in rows:
        for kind, ctx in boundaries(r['text']):
            if kind == 'double':
                d += 1
                if len(ex) < 4: ex.append(ctx)
            else: s += 1
    return s, d, ex

def row(label, corpus, source, rows, preserved):
    s, d, ex = count(rows)
    n = s + d; lo, hi = wilson(d, n)
    words = sum(len(r['text'].split()) for r in rows)
    docs_with = 0
    return dict(label=label, corpus=corpus, source=source, whitespace_preserved=preserved, docs=len(rows), words=words,
                boundaries=n, single=s, double=d, rate=(d/n if n else float('nan')), ci_lo=lo, ci_hi=hi, examples=ex)

sat = read_jsonl(f'{CORPUS}/satoshi.jsonl')
ctrl = read_jsonl(f'{CORPUS}/controls.jsonl')
elon = read_jsonl(f'{CORPUS}/elon.jsonl')
ct = read_jsonl(f'{CORPUS}/control_tweets.jsonl')
for r in ctrl: r['author'] = norm_author(r['author'])

out = []
G = lambda rows, g: [r for r in rows if r['genre'] == g]
out.append(row('Satoshi - mailing-list emails (SNI/metzdowd/SourceForge)', 'satoshi', 'sni_emails_json', G(sat, 'email_list'), 'yes (raw plain text)'))
out.append(row('Satoshi - private emails (Back/Dai/Finney)', 'satoshi', 'lugaxker_private_emails', G(sat, 'email_private'), 'yes (&nbsp; markers = 2nd space)'))
out.append(row('Satoshi - BitcoinTalk/P2P Foundation forum posts', 'satoshi', 'sni_forum_posts_json', G(sat, 'forum'), 'yes (&nbsp; markers = 2nd space)'))
out.append(row('Satoshi - white paper (PDF text)', 'satoshi', 'bitcoin.pdf', G(sat, 'paper'), 'NO (PDF glyph spacing)'))
allsat = [r for r in sat if r['genre'] != 'paper']
out.append(row('Satoshi - ALL informal writing (emails+forum)', 'satoshi', 'combined', allsat, 'yes'))
out.append(row('Elon - X API sample (raw text)', 'elon', 'x_api_sample', G(elon, 'tweet_raw'), 'yes (verified: API returns raw text)'))
out.append(row('Elon - cmj/elontweets CSV (109k posts)', 'elon', 'cmj_elontweets_csv', G(elon, 'tweet'), 'NO (whitespace collapsed)'))
out.append(row('Elon - Tesla blog posts (HTML copy)', 'elon', 'elonmuskarchive.org', G(elon, 'blog'), 'NO (HTML)'))
for a in ['Hal Finney', 'Adam Back']:
    out.append(row(f'{a} - cryptography list emails', 'control', 'metzdowd', [r for r in ctrl if r['author']==a and r['genre']=='email_list'], 'yes'))
out.append(row('Hal Finney - emails to Satoshi', 'control', 'lugaxker', [r for r in ctrl if r['author']=='Hal Finney' and r['genre']=='email_private'], 'yes'))
for u in ['adam3us', 'NickSzabo4', 'VitalikButerin']:
    out.append(row(f'{u} - X API sample', 'control', 'x_api_sample', [r for r in ct if r['author'].startswith(u)], 'yes'))
out.append(row('Nick Szabo - essays (SNI markdown)', 'control', 'sni_library', [r for r in ctrl if r['author']=='Nick Szabo' and r['genre']=='essay'], 'unknown (markdown)'))
df = pd.DataFrame(out)
df.to_csv(f'{RESULTS}/double_space_summary.csv', index=False)
json.dump(out, open(f'{RESULTS}/double_space_summary.json', 'w'), indent=1)

# per-author rates among the metzdowd mailing-list authors (same genre/era as Satoshi's emails)
by = collections.defaultdict(list)
for r in ctrl:
    if r['genre'] == 'email_list': by[r['author']].append(r)
au = []
for a, rows in by.items():
    s, d, _ = count(rows)
    if s + d >= 50: au.append(dict(author=a, docs=len(rows), boundaries=s+d, double=d, rate=d/(s+d), ci_lo=wilson(d, s+d)[0], ci_hi=wilson(d, s+d)[1]))
au = pd.DataFrame(au).sort_values('rate', ascending=False)
au.to_csv(f'{RESULTS}/double_space_by_list_author.csv', index=False)
# per-author in BitcoinTalk forum (same threads as Satoshi)
by = collections.defaultdict(list)
for r in ctrl:
    if r['genre'] == 'forum': by[r['author']].append(r)
fa = []
for a, rows in by.items():
    s, d, _ = count(rows)
    if s + d >= 50: fa.append(dict(author=a, docs=len(rows), boundaries=s+d, double=d, rate=d/(s+d)))
fa = pd.DataFrame(fa).sort_values('rate', ascending=False)
fa.to_csv(f'{RESULTS}/double_space_by_forum_author.csv', index=False)

pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print(df[['label','docs','words','boundaries','single','double','rate','ci_lo','ci_hi']].to_string())
print('\nlist authors (>=50 boundaries):', len(au), ' median rate', au.rate.median(), ' share with rate>=0.5:', (au.rate>=0.5).mean(), ' share with 0 doubles', (au.double==0).mean())
print(au.head(12).to_string())
print('\nforum authors (>=50 boundaries):', len(fa), 'median', fa.rate.median(), 'share>=0.5', (fa.rate>=.5).mean())
print(fa.head(8).to_string())
for r in out[:3]: print(r['label'], r['examples'])

# ---- Elon raw-API sample split by era (does a phone-era change explain the zero?)
import json as _json
_er = [r for r in elon_rows if r['genre'] == 'tweet_raw'] if 'elon_rows' in globals() else [r for r in read_jsonl(f'{CORPUS}/elon.jsonl') if r['genre'] == 'tweet_raw']
_out = []
for _lab, _f in [('2012-2017', lambda y: y <= 2017), ('2018-2022', lambda y: 2018 <= y <= 2022), ('2023-2026', lambda y: y >= 2023)]:
    _rs = [r for r in _er if _f(int(r['date'][:4]))]
    _s, _d, _ = count(_rs); _out.append(dict(era=_lab, posts=len(_rs), boundaries=_s + _d, double=_d))
import pandas as _pd
_pd.DataFrame(_out).to_csv(f'{RESULTS}/double_space_elon_api_by_era.csv', index=False); print(_pd.DataFrame(_out))
