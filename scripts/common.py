"""Shared helpers for the stylometry pipeline."""
import re, json, os, html
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'data', 'raw')
CORPUS = os.path.join(ROOT, 'data', 'corpus')
RESULTS = os.path.join(ROOT, 'results')
CHARTS = os.path.join(ROOT, 'charts')
for d in (CORPUS, RESULTS, CHARTS):
    os.makedirs(d, exist_ok=True)

def write_jsonl(path, rows):
    with open(path, 'w') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

def read_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f]

URL_RE = re.compile(r'https?://\S+|www\.\S+')
MENTION_RE = re.compile(r'(?<!\w)@\w+')

import math
from collections import defaultdict

def norm_author(a):
    a = re.sub(r'\s+', ' ', a).strip()
    m = re.match(r'^([^,]+),\s*(.+)$', a)
    if m: a = f'{m.group(2)} {m.group(1)}'
    a = re.sub(r'^Dr\.? ', '', a)
    a = re.sub(r'^Anne & Lynn Wheeler$', 'Lynn Wheeler', a)
    return a

def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'), float('nan'))
    p = k / n
    den = 1 + z*z/n
    c = (p + z*z/(2*n)) / den
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return (max(0, c-h), min(1, c+h))
