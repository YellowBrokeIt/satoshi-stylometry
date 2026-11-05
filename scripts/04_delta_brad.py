#!/usr/bin/env python3
"""Brad Mills X-posts insertion rank vs Satoshi (same method as 04_delta.py).
Does not modify 04_delta.py. Writes Brad-specific result CSVs under results/.
"""
import re, json, collections, html, glob, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import importlib.util
spec = importlib.util.spec_from_file_location('build', f'{ROOT}/scripts/01_build_corpora.py')
# avoid executing build; copy helpers inline
def strip_quotes(text):
    lines = text.splitlines(); out=[]
    for ln in lines:
        if re.match(r'^>+', ln): continue
        out.append(ln)
    return '\n'.join(out).strip()
def md_email_to_text(md):
    m = re.search(r'^From:\s*(.+)$', md, re.M)
    frm = m.group(1) if m else ''
    # body after headers / after first blank following frontmatter-ish
    parts = re.split(r'\n\s*\n', md, maxsplit=1)
    body = parts[1] if len(parts)>1 else md
    body = re.sub(r'<br\s*/?>', '\n', body, flags=re.I)
    body = re.sub(r'<[^>]+>', '', body)
    return frm, strip_quotes(body)

sat = read_jsonl(f'{CORPUS}/satoshi.jsonl')
ctrl = read_jsonl(f'{CORPUS}/controls.jsonl')
elon = read_jsonl(f'{CORPUS}/elon.jsonl')
try:
    ct = read_jsonl(f'{CORPUS}/control_tweets.jsonl')
except FileNotFoundError:
    ct = []

# Inject Adam Back private emails authored by Adam (from lug archive)
for f in sorted(glob.glob(f'{RAW}/lug/doc/adam-back/*.md')):
    frm, body = md_email_to_text(open(f).read())
    if 'adam' in frm.lower() and 'back' in frm.lower():
        ctrl.append(dict(doc_id=f"lug-adam-{os.path.basename(f)[:-3]}", author='Adam Back',
                         source='lugaxker_private_emails', genre='email_private', date='', url='', text=body))

def ALIAS(a):
    a = norm_author(a)
    low = a.lower()
    if 'leichter' in low: return 'Jerry Leichter'
    if low.startswith('zooko'): return 'Zooko'
    if low in ('ian g', 'iang'): return 'Ian Grigg'
    if 'geer.org' in low or low == 'dan geer': return 'Dan Geer'
    if 'bellovin' in low: return 'Steven Bellovin'
    if 'heyman' in low or low.startswith('mheyman'): return 'mheyman at gmail.com'
    if low in ('dr adam back', 'adam back'): return 'Adam Back'
    if low.startswith('anne') and 'wheeler' in low: return 'Lynn Wheeler'
    return a
for r in ctrl: r['author'] = ALIAS(r['author'])

TOK = re.compile(r"[a-z]+(?:'[a-z]+)?")
def clean(t, tweet=False):
    t = URL_RE.sub(' ', t)
    if tweet: t = MENTION_RE.sub(' ', t)
    return t.replace('\u2019', "'").replace('\u2018', "'")
def tokens(t): return TOK.findall(t.lower())
def ws_norm(t): return re.sub(r'\s+', ' ', t).strip()

brad_raw = read_jsonl(f'{RAW}/bradmillscan_posts.jsonl')
brad_texts = []
for p in brad_raw:
    t = p.get('note_text') or p.get('text') or ''
    t = html.unescape(t)
    brad_texts.append(clean(t, tweet=True))

G = collections.OrderedDict()
def add(name, rows_or_texts, tweet=False, already_clean=False):
    if already_clean:
        G[name] = list(rows_or_texts)
    else:
        G[name] = [clean(r['text'], tweet) for r in rows_or_texts]

add('Satoshi (emails+forum)', [r for r in sat if r['genre'] != 'paper'])
add('Satoshi - forum posts only', [r for r in sat if r['genre'] == 'forum'])
add('Satoshi - emails only', [r for r in sat if r['genre'] in ('email_list', 'email_private')])
tw = [r for r in elon if r['genre'] == 'tweet']
add('Elon - X posts (all)', tw, True)
yr = lambda r: int(r['date'][-4:])
add('Elon - X posts 2010-2017', [r for r in tw if yr(r) <= 2017], True)
add('Elon - X posts 2023-2026', [r for r in tw if yr(r) >= 2023], True)
add('Elon - Tesla blog prose', [r for r in elon if r['genre'] == 'blog'])

byauth = collections.defaultdict(list)
for r in ctrl: byauth[r['author']].append(r)
def words(rows): return sum(len(r['text'].split()) for r in rows)
NAMED = ['Hal Finney', 'Nick Szabo', 'Adam Back', 'Wei Dai']
for a in NAMED:
    if a in byauth: add(a + ' (writing)', byauth[a])
# Use 4500 threshold to add (align with CANDS word floor; recovers Thierry Moreau etc.)
for a, rows in sorted(byauth.items(), key=lambda kv: -words(kv[1])):
    if a in NAMED or words(rows) < 4500 or a.lower() in ('', 'unknown'): continue
    add(a, rows)
ctw = collections.defaultdict(list)
for r in ct: ctw[r['author']].append(r)
for a, rows in ctw.items(): add(f'{a} (X posts)', rows, True)

add('Brad Mills - X posts', brad_texts, already_clean=True)
add('Brad Mills (tweets corpus)', brad_texts, already_clean=True)

TOKS = {k: [tokens(t) for t in v] for k, v in G.items()}
NW = {k: sum(len(x) for x in v) for k, v in TOKS.items()}

CANDS = [k for k in G if NW[k] >= 4500 and not k.startswith('Satoshi') and not k.startswith('Elon - X posts 20')
         and 'X posts' not in k]
CANDS = [k for k in CANDS if k != 'Elon - Tesla blog prose'] + ['Elon - Tesla blog prose']
CANDS_PRIMARY = [k for k in CANDS if k != 'Brad Mills (tweets corpus)']

profile = lambda toks: collections.Counter(w for d in toks for w in d)
PROF = {k: profile(TOKS[k]) for k in G}
FW_OK = set(['a', 'about', 'above', 'after', 'again', 'against', 'all', 'already', 'also', 'although', 'always', 'am', 'among', 'an', 'and', 'any', 'anyone', 'anything', 'are', "aren't", 'around', 'as', 'at', 'away', 'back', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'either', 'else', 'even', 'ever', 'every', 'everyone', 'everything', 'few', 'for', 'from', 'further', 'get', 'got', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'however', 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', 'just', "let's", 'like', 'many', 'may', 'maybe', 'me', 'might', 'more', 'most', 'much', 'must', "mustn't", 'my', 'myself', 'neither', 'never', 'no', 'nor', 'not', 'nothing', 'now', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'per', 'perhaps', 'rather', 'really', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'since', 'so', 'some', 'someone', 'something', 'still', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'therefore', 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'though', 'through', 'thus', 'to', 'too', 'two', 'under', 'until', 'up', 'upon', 'very', 'via', 'was', "wasn't", 'way', 'we', "we'd", "we'll", "we're", "we've", 'well', 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'whether', 'which', 'while', 'whilst', 'who', "who's", 'whom', 'why', "why's", 'will', 'with', 'within', 'without', "won't", 'would', "wouldn't", 'yes', 'yet', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'])

pool = collections.Counter()
for k in CANDS_PRIMARY + ['Satoshi (emails+forum)']:
    n = sum(PROF[k].values())
    for w, c in PROF[k].items(): pool[w] += c / n
MFW = [w for w, _ in pool.most_common() if w in FW_OK][:150]
def fvec(counter, n=None):
    n = n or sum(counter.values())
    return np.array([counter.get(w, 0) / n for w in MFW])

REF = np.array([fvec(PROF[k]) for k in CANDS_PRIMARY])
MU, SD = REF.mean(0), REF.std(0) + 1e-9
Z = lambda v: (v - MU) / SD
delta = lambda a, b: float(np.mean(np.abs(Z(a) - Z(b))))
def cosz(a, b):
    za, zb = Z(a), Z(b); return float(za @ zb / (np.linalg.norm(za) * np.linalg.norm(zb)))
V = {k: fvec(PROF[k]) for k in G}

def cgrams(texts, n=4):
    c = collections.Counter()
    for t in texts:
        t = ws_norm(t)
        for i in range(len(t) - n + 1): c[t[i:i+n]] += 1
    return c
CG = {k: cgrams(G[k]) for k in set(['Satoshi (emails+forum)'] + CANDS_PRIMARY +
      [x for x in G if 'X posts' in x or x.startswith('Brad')])}
cpool = collections.Counter()
for k in CANDS_PRIMARY + ['Satoshi (emails+forum)']:
    n = sum(CG[k].values())
    for g, c in CG[k].items(): cpool[g] += c / n
CGF = [g for g, _ in cpool.most_common(1500)]
def cvec(k):
    n = sum(CG[k].values()); return np.array([CG[k].get(g, 0) / n for g in CGF])
CV = {k: cvec(k) for k in CG}
CMU = np.array([CV[k] for k in CANDS_PRIMARY]).mean(0); CSD = np.array([CV[k] for k in CANDS_PRIMARY]).std(0) + 1e-9
def ccos(a, b):
    za, zb = (a - CMU) / CSD, (b - CMU) / CSD; return float(za @ zb / (np.linalg.norm(za) * np.linalg.norm(zb)))

S = 'Satoshi (emails+forum)'
rows = []
for k in CANDS_PRIMARY:
    rows.append(dict(candidate=k, words=NW[k], delta=delta(V[S], V[k]), cos_fw=cosz(V[S], V[k]),
                     cos_char4=ccos(CV[S], CV[k]) if k in CV else np.nan))
rk = pd.DataFrame(rows)
rk['rank_delta'] = rk.delta.rank().astype(int)
rk['rank_cos_fw'] = rk.cos_fw.rank(ascending=False).astype(int)
rk = rk.sort_values('delta').reset_index(drop=True)
N = len(rk)
print(f'{N} primary candidates; Satoshi words={NW[S]}')
print(f'Brad Mills - X posts words={NW["Brad Mills - X posts"]} posts={len(brad_raw)}')

extras = []
for k in ['Brad Mills - X posts', 'Elon - X posts (all)', 'Elon - X posts 2010-2017', 'Elon - X posts 2023-2026', 'Elon - Tesla blog prose']:
    dk = delta(V[S], V[k]); ck = cosz(V[S], V[k])
    ir = 1 + int((rk.delta < dk).sum())
    cr = 1 + int((rk.cos_fw > ck).sum())
    extras.append(dict(slice=k, words=NW[k], delta=dk, cos_fw=ck,
                       cos_char4=ccos(CV[S], CV[k]) if k in CV else np.nan,
                       insertion_rank_delta=ir, insertion_rank_cos_fw=cr, among=N+1))
    print(f'INSERTION RANK of {k}: Delta {ir}/{N+1} (delta={dk:.3f}, cos_fw={ck:.3f}); words={NW[k]}')

ex = pd.DataFrame(extras)
ex.to_csv(f'{RESULTS}/delta_brad_insertion_vs_satoshi.csv', index=False)

brad_d = float(ex.loc[ex['slice']=='Brad Mills - X posts', 'delta'].iloc[0])
brad_c = float(ex.loc[ex['slice']=='Brad Mills - X posts', 'cos_fw'].iloc[0])
brad_ir = int(ex.loc[ex['slice']=='Brad Mills - X posts', 'insertion_rank_delta'].iloc[0])
merged = rk[['candidate','words','delta','cos_fw','rank_delta']].copy()
brad_row = pd.DataFrame([dict(candidate='Brad Mills - X posts', words=NW['Brad Mills - X posts'],
                              delta=brad_d, cos_fw=brad_c, rank_delta=brad_ir)])
merged = pd.concat([merged, brad_row], ignore_index=True).sort_values('delta').reset_index(drop=True)
merged['rank_with_brad'] = range(1, len(merged)+1)
pos = int(merged.index[merged.candidate=='Brad Mills - X posts'][0])
lo = max(0, pos-3); hi = min(len(merged), pos+4)
neigh = merged.iloc[lo:hi].copy()
neigh.to_csv(f'{RESULTS}/delta_brad_neighbors.csv', index=False)
print('\nNEIGHBORS (3 above / Brad / 3 below):')
print(neigh.round(3).to_string(index=False))

elon_d = float(ex.loc[ex['slice']=='Elon - X posts (all)', 'delta'].iloc[0])
elon_ir = int(ex.loc[ex['slice']=='Elon - X posts (all)', 'insertion_rank_delta'].iloc[0])
print(f'\nElon X posts insertion rank sanity: {elon_ir}/{N+1} delta={elon_d:.3f} (article ~30/66)')

# Placement on the ARTICLE's published 65-candidate list (committed CSV): insert by delta value
# using Brad's delta computed above (same method; MU/SD from this rebuild's CANDS).
pub = pd.read_csv(f'{RESULTS}/delta_rank_vs_satoshi.csv').sort_values('delta').reset_index(drop=True)
# Prefer not overwriting the published main rank; keep a copy-aware insertion file
pub_ins = pub[['candidate','words','delta','cos_fw']].copy()
pub_ins = pd.concat([pub_ins, pd.DataFrame([dict(candidate='Brad Mills - X posts',
    words=NW['Brad Mills - X posts'], delta=brad_d, cos_fw=brad_c)])], ignore_index=True)
pub_ins = pub_ins.sort_values('delta').reset_index(drop=True)
pub_ins['rank'] = range(1, len(pub_ins)+1)
pub_ir = int(pub_ins.loc[pub_ins.candidate=='Brad Mills - X posts','rank'].iloc[0])
print(f'\nINSERTION onto published 65-list by delta value: Brad rank {pub_ir}/{len(pub)+1} (N_published={len(pub)})')
pos2 = int(pub_ins.index[pub_ins.candidate=='Brad Mills - X posts'][0])
lo2 = max(0, pos2-3); hi2 = min(len(pub_ins), pos2+4)
neigh_pub = pub_ins.iloc[lo2:hi2].copy()
neigh_pub.to_csv(f'{RESULTS}/delta_brad_neighbors_on_published65.csv', index=False)
print(neigh_pub.round(3).to_string(index=False))
# Elon on published list
elon_pub_ir = 1 + int((pub.delta < elon_d).sum())
print(f'Elon delta={elon_d:.3f} insertion on published 65-list: {elon_pub_ir}/{len(pub)+1} (article reported 30/66)')

# Second check: full re-rank with Brad as candidate (no "X posts" in name)
CANDS2 = CANDS_PRIMARY + ['Brad Mills (tweets corpus)']
REF2 = np.array([fvec(PROF[k]) for k in CANDS2])
MU2, SD2 = REF2.mean(0), REF2.std(0) + 1e-9
Z2 = lambda v: (v - MU2) / SD2
delta2 = lambda a, b: float(np.mean(np.abs(Z2(a) - Z2(b))))
rows2 = []
for k in CANDS2:
    rows2.append(dict(candidate=k, words=NW[k], delta=delta2(V[S], V[k])))
rk2 = pd.DataFrame(rows2).sort_values('delta').reset_index(drop=True)
rk2['rank_delta'] = range(1, len(rk2)+1)
rk2.to_csv(f'{RESULTS}/delta_rank_vs_satoshi_with_brad_candidate.csv', index=False)
brad2 = rk2[rk2.candidate=='Brad Mills (tweets corpus)'].iloc[0]
print(f"\nSECOND CHECK (Brad as candidate, MU/SD rebuilt): rank {int(brad2.rank_delta)}/{len(rk2)} delta={brad2.delta:.3f}")

# Update extra-slices file to include Brad + Elon slices with insertion ranks
extra_out = []
for _, r in ex.iterrows():
    extra_out.append(dict(slice=r['slice'], words=int(r['words']), delta=float(r['delta']),
                          cos_fw=float(r['cos_fw']), cos_char4=float(r['cos_char4']) if pd.notna(r['cos_char4']) else '',
                          insertion_rank_delta=int(r['insertion_rank_delta']), among=int(r['among'])))
pd.DataFrame(extra_out).to_csv(f'{RESULTS}/delta_extra_slices_vs_satoshi.csv', index=False)

# Summary JSON for README / report
summary = dict(
    brad_handle='bradmillscan',
    brad_user_id='246911146',
    brad_profile='https://x.com/bradmillscan',
    posts=len(brad_raw),
    words_cleaned=int(NW['Brad Mills - X posts']),
    delta=brad_d,
    cos_fw=brad_c,
    insertion_rank=brad_ir,
    among=N+1,
    n_cands=N,
    published65_insertion_rank=pub_ir,
    published65_among=len(pub)+1,
    elon_insertion_rank=elon_ir,
    elon_delta=elon_d,
    elon_published65_insertion_rank=elon_pub_ir,
    second_check_rank=int(brad2.rank_delta),
    second_check_among=len(rk2),
    second_check_delta=float(brad2.delta),
    caveat='Genre mismatch: tweets vs emails/forum (same caveat as Elon X posts).',
)
json.dump(summary, open(f'{RESULTS}/delta_brad_summary.json','w'), indent=2)
print('\nWrote Brad result CSVs + summary JSON')
print(f'median candidate delta={rk.delta.median():.3f}')
