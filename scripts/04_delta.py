#!/usr/bin/env python3
"""Analysis 3: Burrows' Delta / cosine over ~150 function words + character 4-grams.
Also: chunk-based self-attribution validation, and within-author cross-genre baselines (the genre-mismatch yardstick)."""
import re, json, collections, random
import numpy as np, pandas as pd
from common import *

random.seed(7); np.random.seed(7)
sat = read_jsonl(f'{CORPUS}/satoshi.jsonl'); ctrl = read_jsonl(f'{CORPUS}/controls.jsonl')
elon = read_jsonl(f'{CORPUS}/elon.jsonl'); ct = read_jsonl(f'{CORPUS}/control_tweets.jsonl')
ALIAS = lambda a: ('Jerry Leichter' if 'leichter' in a.lower() else 'Zooko' if a.lower().startswith('zooko') else 'Ian Grigg' if a.lower() in ('ian g', 'iang') else 'Dan Geer' if 'geer.org' in a else a)
for r in ctrl: r['author'] = ALIAS(norm_author(r['author']))

TOK = re.compile(r"[a-z]+(?:'[a-z]+)?")
def clean(t, tweet=False):
    t = URL_RE.sub(' ', t)
    if tweet: t = MENTION_RE.sub(' ', t)
    return t.replace('’', "'").replace('‘', "'")
def tokens(t): return TOK.findall(t.lower())
def ws_norm(t): return re.sub(r'\s+', ' ', t).strip()      # char n-grams computed on whitespace-normalised text

# ---------------------------------------------------------------- groups (name -> list of (text) in order)
G = collections.OrderedDict()
def add(name, rows, tweet=False):
    G[name] = [clean(r['text'], tweet) for r in rows]
add('Satoshi (emails+forum)', [r for r in sat if r['genre'] != 'paper'])
add('Satoshi - forum posts only', [r for r in sat if r['genre'] == 'forum'])
add('Satoshi - emails only', [r for r in sat if r['genre'] in ('email_list', 'email_private')])
add('Satoshi - white paper', [r for r in sat if r['genre'] == 'paper'])
tw = [r for r in elon if r['genre'] == 'tweet']
add('Elon - X posts (all)', tw, True)
yr = lambda r: int(r['date'][-4:])
add('Elon - X posts 2010-2017', [r for r in tw if yr(r) <= 2017], True)
add('Elon - X posts 2023-2026', [r for r in tw if yr(r) >= 2023], True)
add('Elon - Tesla blog prose', [r for r in elon if r['genre'] == 'blog'])
# controls: named + everyone with >=5000 words
byauth = collections.defaultdict(list)
for r in ctrl: byauth[r['author']].append(r)
def words(rows): return sum(len(r['text'].split()) for r in rows)
NAMED = ['Hal Finney', 'Nick Szabo', 'Adam Back', 'Wei Dai']
for a in NAMED:
    if a in byauth: add(a + ' (writing)', byauth[a])
for a, rows in sorted(byauth.items(), key=lambda kv: -words(kv[1])):
    if a in NAMED or words(rows) < 5000 or a.lower() in ('', 'unknown'): continue
    add(a, rows)
# tweets of controls (tiny) for genre-matched baselines
ctw = collections.defaultdict(list)
for r in ct: ctw[r['author']].append(r)
for a, rows in ctw.items(): add(f'{a} (X posts)', rows, True)

TOKS = {k: [tokens(t) for t in v] for k, v in G.items()}
NW = {k: sum(len(x) for x in v) for k, v in TOKS.items()}

# ---------------------------------------------------------------- feature selection
CANDS = [k for k in G if NW[k] >= 4500 and not k.startswith('Satoshi') and not k.startswith('Elon - X posts 20')
         and 'X posts' not in k]           # candidate "authors" for ranking
CANDS = [k for k in CANDS if k != 'Elon - Tesla blog prose'] + ['Elon - Tesla blog prose']
profile = lambda toks: collections.Counter(w for d in toks for w in d)
PROF = {k: profile(TOKS[k]) for k in G}
FW_OK = set(['a', 'about', 'above', 'after', 'again', 'against', 'all', 'already', 'also', 'although', 'always', 'am', 'among', 'an', 'and', 'any', 'anyone', 'anything', 'are', "aren't", 'around', 'as', 'at', 'away', 'back', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'either', 'else', 'even', 'ever', 'every', 'everyone', 'everything', 'few', 'for', 'from', 'further', 'get', 'got', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'however', 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', 'just', "let's", 'like', 'many', 'may', 'maybe', 'me', 'might', 'more', 'most', 'much', 'must', "mustn't", 'my', 'myself', 'neither', 'never', 'no', 'nor', 'not', 'nothing', 'now', 'of', 'off', 'often', 'on', 'once', 'one', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'per', 'perhaps', 'rather', 'really', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'since', 'so', 'some', 'someone', 'something', 'still', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'therefore', 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'though', 'through', 'thus', 'to', 'too', 'two', 'under', 'until', 'up', 'upon', 'very', 'via', 'was', "wasn't", 'way', 'we', "we'd", "we'll", "we're", "we've", 'well', 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'whether', 'which', 'while', 'whilst', 'who', "who's", 'whom', 'why', "why's", 'will', 'with', 'within', 'without', "won't", 'would', "wouldn't", 'yes', 'yet', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'])
pool = collections.Counter()
for k in CANDS + ['Satoshi (emails+forum)']:      # author-equal-weighted mean relative frequency
    n = sum(PROF[k].values())
    for w, c in PROF[k].items(): pool[w] += c / n
MFW = [w for w, _ in pool.most_common() if w in FW_OK][:150]
print('150 function words, first 40:', MFW[:40])
json.dump(MFW, open(f'{RESULTS}/function_words_150.json', 'w'))
def fvec(counter, n=None):
    n = n or sum(counter.values())
    return np.array([counter.get(w, 0) / n for w in MFW])

# ---------------------------------------------------------------- Delta machinery
REF = np.array([fvec(PROF[k]) for k in CANDS])
MU, SD = REF.mean(0), REF.std(0) + 1e-9
Z = lambda v: (v - MU) / SD
delta = lambda a, b: float(np.mean(np.abs(Z(a) - Z(b))))
def cosz(a, b):
    za, zb = Z(a), Z(b); return float(za @ zb / (np.linalg.norm(za) * np.linalg.norm(zb)))
V = {k: fvec(PROF[k]) for k in G}

# character 4-grams (whitespace-normalised), top 1500 most frequent in pooled candidate text
def cgrams(texts, n=4):
    c = collections.Counter()
    for t in texts:
        t = ws_norm(t)
        for i in range(len(t) - n + 1): c[t[i:i+n]] += 1
    return c
CG = {k: cgrams(G[k]) for k in ['Satoshi (emails+forum)'] + CANDS + [x for x in G if 'X posts' in x or x.startswith('Satoshi')]}
cpool = collections.Counter()
for k in CANDS + ['Satoshi (emails+forum)']:
    n = sum(CG[k].values())
    for g, c in CG[k].items(): cpool[g] += c / n
CGF = [g for g, _ in cpool.most_common(1500)]
def cvec(k):
    n = sum(CG[k].values()); return np.array([CG[k].get(g, 0) / n for g in CGF])
CV = {k: cvec(k) for k in CG}
CMU = np.array([CV[k] for k in CANDS]).mean(0); CSD = np.array([CV[k] for k in CANDS]).std(0) + 1e-9
def ccos(a, b):
    za, zb = (a - CMU) / CSD, (b - CMU) / CSD; return float(za @ zb / (np.linalg.norm(za) * np.linalg.norm(zb)))

# ---------------------------------------------------------------- ranking vs Satoshi
S = 'Satoshi (emails+forum)'
rows = []
for k in CANDS:
    rows.append(dict(candidate=k, words=NW[k], delta=delta(V[S], V[k]), cos_fw=cosz(V[S], V[k]), cos_char4=ccos(CV[S], CV[k])))
rk = pd.DataFrame(rows)
rk['rank_delta'] = rk.delta.rank().astype(int); rk['rank_cos_fw'] = rk.cos_fw.rank(ascending=False).astype(int)
rk['rank_cos_char4'] = rk.cos_char4.rank(ascending=False).astype(int)
rk = rk.sort_values('delta'); rk.to_csv(f'{RESULTS}/delta_rank_vs_satoshi.csv', index=False)
N = len(rk)
print(f'\n{N} candidates; Satoshi (emails+forum) {NW[S]} words')
print(rk.head(12).round(3).to_string(index=False))
print(rk[rk.candidate.isin(['Elon - X posts (all)', 'Elon - Tesla blog prose'] + [a + ' (writing)' for a in NAMED])].round(3).to_string(index=False))
# extra Elon slices (not in ranking pool; compared to the same Satoshi vector with the same MU/SD)
extra = []
for k in ['Elon - X posts (all)', 'Elon - X posts 2010-2017', 'Elon - X posts 2023-2026', 'Elon - Tesla blog prose'] + [x for x in G if 'X posts' in x and not x.startswith('Elon')]:
    extra.append(dict(slice=k, words=NW[k], delta=delta(V[S], V[k]), cos_fw=cosz(V[S], V[k]),
                      cos_char4=ccos(CV[S], CV[k]) if k in CV else np.nan))
ex = pd.DataFrame(extra); ex.to_csv(f'{RESULTS}/delta_extra_slices_vs_satoshi.csv', index=False); print(ex.round(3).to_string(index=False))
for k in ['Elon - X posts (all)', 'Elon - X posts 2010-2017', 'Elon - X posts 2023-2026', 'Elon - Tesla blog prose']:
    dk = delta(V[S], V[k]); ck = cosz(V[S], V[k])
    print(f"INSERTION RANK of {k}: Delta rank {1+int((rk.delta<dk).sum())}/{N+1}; cosine rank {1+int((rk.cos_fw>ck).sum())}/{N+1}")
# Delta distribution of the 'wrong' candidates (for context on where Elon falls)
print('delta distribution among candidates: min %.3f median %.3f max %.3f' % (rk.delta.min(), rk.delta.median(), rk.delta.max()))

# ---------------------------------------------------------------- genre-mismatch baselines
base = []
def pair(a, b, label):
    base.append(dict(pair=label, words_a=NW[a], words_b=NW[b], delta=delta(V[a], V[b]), cos_fw=cosz(V[a], V[b]),
                     cos_char4=ccos(CV[a], CV[b]) if a in CV and b in CV else np.nan))
a, b = 'Satoshi - forum posts only', 'Satoshi - emails only'
pair(a, b, 'Satoshi forum vs Satoshi emails (same author, 2 channels)')
pair('Elon - X posts (all)', 'Elon - Tesla blog prose', 'Elon X posts vs Elon blog prose (same author, 2 genres)')
pair('Elon - X posts 2010-2017', 'Elon - X posts 2023-2026', 'Elon early X posts vs recent X posts')
for au in ['Adam Back', 'Nick Szabo']:
    ta = f'{[x for x in ctw if au.split()[0].lower() in x.lower() or (au=="Adam Back" and "adam3us" in x.lower())][0]} (X posts)'
    pair(f'{au} (writing)', ta, f'{au}: emails/essays vs own X posts (same author, 2 genres)')
pair('Hal Finney (writing)', 'Nick Szabo (writing)', 'Hal Finney vs Nick Szabo (different authors, same era/topic)')
pair(S, 'Hal Finney (writing)', 'Satoshi vs Hal Finney (different authors, same topic)')
pair(S, 'Nick Szabo (writing)', 'Satoshi vs Nick Szabo')
pair(S, 'Adam Back (writing)', 'Satoshi vs Adam Back')
pair(S, 'Elon - X posts (all)', 'Satoshi vs Elon X posts')
pair(S, 'Elon - Tesla blog prose', 'Satoshi vs Elon blog prose')
bl = pd.DataFrame(base); bl.to_csv(f'{RESULTS}/delta_genre_baselines.csv', index=False)
print(); print(bl.round(3).to_string(index=False))

# ---------------------------------------------------------------- chunk validation (closed-set attribution)
CH = 2000
def chunks(k):
    ws = [w for d in TOKS[k] for w in d]
    return [ws[i:i+CH] for i in range(0, len(ws) - CH + 1, CH)]
VAL = [k for k in CANDS if NW[k] >= 10000 and k != 'Elon - Tesla blog prose'] + [S, 'Elon - X posts (all)']
VAL = list(dict.fromkeys(VAL))
CHK = {k: chunks(k) for k in VAL}
# cap chunks per author at 40 (Elon, Szabo have hundreds)
for k in VAL:
    if len(CHK[k]) > 40: CHK[k] = random.sample(CHK[k], 40)
res = collections.defaultdict(collections.Counter); correct = collections.Counter(); total = collections.Counter()
for k in VAL:
    for ci, ch in enumerate(CHK[k]):
        cnt = collections.Counter(ch); q = fvec(cnt, len(ch))
        # leave-chunk-out: own profile minus this chunk
        best, bd = None, 1e9
        for a2 in VAL:
            p = PROF[a2].copy()
            if a2 == k:
                p = p.copy(); p.subtract(cnt)
            d = delta(q, fvec(p))
            if d < bd: best, bd = a2, d
        res[k][best] += 1; total[k] += 1; correct[k] += (best == k)
acc = pd.DataFrame([dict(author=k, chunks=total[k], correct=correct[k], accuracy=correct[k]/total[k],
                         most_common_wrong=(res[k].most_common(2)[1][0] if len(res[k]) > 1 and res[k].most_common(1)[0][0] == k else res[k].most_common(1)[0][0]) if total[k] else '')
                    for k in VAL])
acc.to_csv(f'{RESULTS}/delta_chunk_validation.csv', index=False)
print(f'\nChunk validation: {len(VAL)} candidate authors, {sum(total.values())} chunks of {CH} words; overall accuracy {sum(correct.values())/sum(total.values()):.3f} (chance ~{1/len(VAL):.3f})')
print(acc[acc.author.isin([S, 'Elon - X posts (all)', 'Nick Szabo (writing)', 'Hal Finney (writing)'])].to_string(index=False))
print('Satoshi chunks attributed to:', dict(res[S])); print('Elon chunks attributed to:', dict(res['Elon - X posts (all)']))
json.dump({k: dict(v) for k, v in res.items() if k in (S, 'Elon - X posts (all)')}, open(f'{RESULTS}/delta_chunk_confusion.json', 'w'), indent=1)
