#!/usr/bin/env python3
"""Analysis 2: British vs American spelling.  Exact counts + every British-form hit with source for the small corpora."""
import re, json, collections
import pandas as pd
from common import *
import spelling_lists as SL

CATS = SL.build()
sat = read_jsonl(f'{CORPUS}/satoshi.jsonl')
ctrl = read_jsonl(f'{CORPUS}/controls.jsonl')
elon = read_jsonl(f'{CORPUS}/elon.jsonl')
ct = read_jsonl(f'{CORPUS}/control_tweets.jsonl')
for r in ctrl: r['author'] = norm_author(r['author'])

def clean(t, tweet=False):
    t = URL_RE.sub(' ', t)
    if tweet: t = MENTION_RE.sub(' ', t)
    return t

def proper_noun(t, m):
    """Capitalised mid-sentence hit (e.g. 'Labour Party', 'Department of Defence') = proper noun, skip."""
    w = m.group(0)
    if not w[0].isupper() or w.isupper() and len(w) < 4: return False
    prev = t[:m.start()].rstrip()
    return bool(prev) and prev[-1] not in '.!?:\n"“(' and not t[:m.start()].endswith('\n')

def tally(rows, tweet=False, keep_hits=False):
    res = {c: [0, 0] for c in CATS}
    forms_b, forms_a = collections.Counter(), collections.Counter()
    brit = {k: [0, 0] for k in SL.BRITISHISMS}
    hits = []
    words = 0
    for r in rows:
        t = clean(r['text'], tweet); words += len(t.split())
        for c, (rb, ra, _, _) in CATS.items():
            for m in rb.finditer(t):
                if proper_noun(t, m): continue
                res[c][0] += 1; forms_b[m.group(0).lower()] += 1
                if keep_hits: hits.append((c, 'BR', m.group(0), r['doc_id'], r.get('url', ''), t[max(0, m.start()-60): m.end()+40].replace('\n', ' ')))
            for m in ra.finditer(t):
                if proper_noun(t, m): continue
                res[c][1] += 1; forms_a[m.group(0).lower()] += 1
                if keep_hits: hits.append((c, 'US', m.group(0), r['doc_id'], r.get('url', ''), t[max(0, m.start()-60): m.end()+40].replace('\n', ' ')))
        for k, (rb, ra) in SL.BRITISHISMS.items():
            for m in rb.finditer(t):
                brit[k][0] += 1
                if keep_hits: hits.append(('britishism:'+k, 'BR', m.group(0), r['doc_id'], r.get('url', ''), t[max(0, m.start()-60): m.end()+40].replace('\n', ' ')))
            brit[k][1] += len(ra.findall(t))
    B = sum(v[0] for v in res.values()); A = sum(v[1] for v in res.values())
    return dict(words=words, docs=len(rows), brit_total=B, amer_total=A, by_cat=res, forms_b=forms_b, forms_a=forms_a,
                britishisms=brit, hits=hits)

groups = {
 'Satoshi - informal (emails+forum)': ([r for r in sat if r['genre'] != 'paper'], False),
 'Satoshi - white paper': ([r for r in sat if r['genre'] == 'paper'], False),
 'Satoshi - ALL': (sat, False),
 'Elon - X posts (cmj CSV, non-RT, 2010-2026)': ([r for r in elon if r['genre'] == 'tweet'], True),
 'Elon - X API raw sample': ([r for r in elon if r['genre'] == 'tweet_raw'], True),
 'Elon - Tesla blog prose': ([r for r in elon if r['genre'] == 'blog'], False),
 'Hal Finney (list+emails+essays)': ([r for r in ctrl if r['author'] == 'Hal Finney'], False),
 'Nick Szabo (essays)': ([r for r in ctrl if r['author'] == 'Nick Szabo'], False),
 'Adam Back (list emails)': ([r for r in ctrl if r['author'] == 'Adam Back'], False),
 'Wei Dai (b-money)': ([r for r in ctrl if r['author'] == 'Wei Dai'], False),
 'Cryptography-list others (2006-09)': ([r for r in ctrl if r['genre'] == 'email_list' and r['author'] not in ('Hal Finney', 'Adam Back')], False),
 'BitcoinTalk others (same threads as Satoshi)': ([r for r in ctrl if r['genre'] == 'forum'], False),
 'Control tweets (Back, Szabo, Vitalik)': (ct, True),
}
R = {}
rows = []
for name, (rs, tw) in groups.items():
    keep = name.startswith('Satoshi') or name.startswith('Elon - X API') or name.startswith('Elon - Tesla') or name.startswith('Hal') or name.startswith('Adam') or name.startswith('Wei')
    R[name] = tally(rs, tw, keep_hits=keep or name.startswith('Elon - X posts'))
    t = R[name]
    rows.append(dict(corpus=name, docs=t['docs'], words=t['words'], british=t['brit_total'], american=t['amer_total'],
                     pct_british=100*t['brit_total']/max(1, t['brit_total']+t['amer_total']),
                     british_per_100k=1e5*t['brit_total']/max(1, t['words']), american_per_100k=1e5*t['amer_total']/max(1, t['words'])))
df = pd.DataFrame(rows)
df.to_csv(f'{RESULTS}/spelling_summary.csv', index=False)
cat_rows = []
for name, t in R.items():
    for c, (b, a) in t['by_cat'].items():
        cat_rows.append(dict(corpus=name, category=c, british=b, american=a))
pd.DataFrame(cat_rows).to_csv(f'{RESULTS}/spelling_by_category.csv', index=False)
br_rows = []
for name, t in R.items():
    for k, (b, a) in t['britishisms'].items():
        br_rows.append(dict(corpus=name, marker=k, british_count=b, american_partner_count=a))
pd.DataFrame(br_rows).to_csv(f'{RESULTS}/britishisms.csv', index=False)

# Hit logs (every hit for the small corpora; Elon CSV British hits only)
with open(f'{RESULTS}/spelling_hits.tsv', 'w') as f:
    f.write('corpus\tcategory\tside\tform\tdoc_id\turl\tcontext\n')
    for name, t in R.items():
        for h in t['hits']:
            if name.startswith('Elon - X posts') and h[1] == 'US': continue
            f.write(name + '\t' + '\t'.join(map(str, h)) + '\n')

# Elon by year: British vs American counts
by_year = collections.defaultdict(lambda: [0, 0, 0])
for r in elon:
    if r['genre'] != 'tweet': continue
    y = r['date'][-4:]
    t = clean(r['text'], True)
    b = sum(len(rb.findall(t)) for rb, ra, _, _ in CATS.values()); a = sum(len(ra.findall(t)) for rb, ra, _, _ in CATS.values())
    by_year[y][0] += b; by_year[y][1] += a; by_year[y][2] += len(t.split())
yr = pd.DataFrame([dict(year=y, british=v[0], american=v[1], words=v[2]) for y, v in sorted(by_year.items())])
yr.to_csv(f'{RESULTS}/spelling_elon_by_year.csv', index=False)

# Satoshi by period / source
ps = []
for name, f in [('2008 (cryptography list + private)', lambda r: r['date'].startswith('2008') or (r['genre']=='email_private')),
                ('2009-2010 emails (bitcoin-list, p2p)', lambda r: r['genre']=='email_list' and r['date'][:4] in ('2009','2010')),
                ('forum 2009-2010', lambda r: r['genre']=='forum')]:
    rs = [r for r in sat if r['genre'] != 'paper' and f(r)]
    t = tally(rs); ps.append(dict(period=name, docs=t['docs'], words=t['words'], british=t['brit_total'], american=t['amer_total']))
pd.DataFrame(ps).to_csv(f'{RESULTS}/spelling_satoshi_by_period.csv', index=False)

pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70)
print(df.round(2).to_string())
print()
for name in ['Satoshi - ALL', 'Elon - X posts (cmj CSV, non-RT, 2010-2026)', 'Elon - Tesla blog prose', 'Elon - X API raw sample']:
    t = R[name]
    print('==', name, 'words', t['words'])
    print('  British forms:', dict(t['forms_b'].most_common(30)))
    print('  American forms:', dict(t['forms_a'].most_common(30)))
    print('  britishisms:', {k: v for k, v in t['britishisms'].items() if v[0] or v[1]})
print(pd.DataFrame(ps))
print(yr.to_string())
