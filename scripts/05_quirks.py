#!/usr/bin/env python3
"""Analysis 4: other quirks (rates per 10,000 words)."""
import re, collections
import pandas as pd
from common import *
sat = read_jsonl(f'{CORPUS}/satoshi.jsonl'); ctrl = read_jsonl(f'{CORPUS}/controls.jsonl')
elon = read_jsonl(f'{CORPUS}/elon.jsonl'); ct = read_jsonl(f'{CORPUS}/control_tweets.jsonl')
for r in ctrl: r['author'] = norm_author(r['author'])
EMOJI = re.compile('[\U0001F300-\U0001FAFF\u2600-\u27BF\U0001F000-\U0001F2FF\U0001F900-\U0001F9FF]')
Q = {
 'lol': re.compile(r'\blol\b', re.I),
 'emoji': EMOJI,
 'ellipsis ("..." or "…")': re.compile(r'\.{3,}|…'),
 'exclamation marks': re.compile(r'!'),
 'spaced hyphen " - " (dash)': re.compile(r'(?<=\w) - (?=\w)'),
 '"e-mail" (hyphenated)': re.compile(r'\be-mail', re.I),
 '"email" (unhyphenated)': re.compile(r'\bemail', re.I),
 '"I think/I believe/I guess"': re.compile(r"\bI (?:think|believe|guess|suppose)\b"),
 '"indeed"': re.compile(r'\bindeed\b', re.I),
 '"order of magnitude"': re.compile(r'order[s]? of magnitude', re.I),
 'parentheses': re.compile(r'\('),
 'semicolons': re.compile(r';'),
}
groups = {
 'Satoshi (emails+forum)': ([r for r in sat if r['genre'] != 'paper'], False),
 'Satoshi forum posts': ([r for r in sat if r['genre'] == 'forum'], False),
 'Satoshi emails': ([r for r in sat if r['genre'].startswith('email')], False),
 'Elon X posts (cmj, own words)': ([r for r in elon if r['genre'] == 'tweet'], True),
 'Elon X API sample': ([r for r in elon if r['genre'] == 'tweet_raw'], True),
 'Elon Tesla blog prose': ([r for r in elon if r['genre'] == 'blog'], False),
 'Hal Finney': ([r for r in ctrl if r['author'] == 'Hal Finney'], False),
 'Nick Szabo': ([r for r in ctrl if r['author'] == 'Nick Szabo'], False),
 'Adam Back (list)': ([r for r in ctrl if r['author'] == 'Adam Back'], False),
 'Crypto-list others': ([r for r in ctrl if r['genre'] == 'email_list' and r['author'] not in ('Hal Finney', 'Adam Back')], False),
 'BitcoinTalk others': ([r for r in ctrl if r['genre'] == 'forum'], False),
 'Control X posts (Back/Szabo/Vitalik)': (ct, True),
}
rows = []
for g, (rs, tw) in groups.items():
    txt = [(MENTION_RE.sub(' ', URL_RE.sub(' ', r['text'])) if tw else URL_RE.sub(' ', r['text'])) for r in rs]
    w = sum(len(t.split()) for t in txt)
    row = dict(group=g, docs=len(rs), words=w)
    for q, rx in Q.items():
        n = sum(len(rx.findall(t)) for t in txt); row[q] = n; row[q + ' /10k'] = round(1e4 * n / w, 2)
    # share of docs starting with lowercase letter
    st = [t.lstrip()[:1] for t in txt if t.strip()]
    row['docs starting lowercase %'] = round(100 * sum(c.islower() for c in st) / max(1, len(st)), 1)
    row['docs ending with period %'] = round(100 * sum(t.rstrip().endswith('.') for t in txt if t.strip()) / max(1, len(st)), 1)
    rows.append(row)
df = pd.DataFrame(rows); df.to_csv(f'{RESULTS}/quirks.csv', index=False)
pd.set_option('display.width', 300)
cols = ['group', 'docs', 'words'] + [c for c in df.columns if c.endswith('/10k')] + ['docs starting lowercase %', 'docs ending with period %']
print(df[cols].to_string(index=False))
print(df[['group'] + [q for q in Q]].to_string(index=False))
