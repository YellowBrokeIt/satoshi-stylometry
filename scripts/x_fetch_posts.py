#!/usr/bin/env python3
"""Hydrate post IDs from data/ids/*.txt through the X API v2 (GET /2/tweets?ids=...), keeping the RAW text
(whitespace intact - this matters for the double-space test).

Needs a bearer token with read access in the environment:  export X_BEARER_TOKEN=...
(never put the token in a file in this repo).  Output: data/raw/x_posts/<name>.jsonl
    id, created_at, text, note_text   (note_text = long-form text for posts over 280 chars)

Usage:  python scripts/x_fetch_posts.py            # sample files only (~1,200 posts, ~13 API calls)
        python scripts/x_fetch_posts.py --all      # also hydrates the 89k-ID scrape (~900 calls; not needed for the results)
"""
import os, sys, json, time, urllib.request, urllib.parse
from common import ROOT, RAW

TOKEN = os.environ.get('X_BEARER_TOKEN')
if not TOKEN:
    sys.exit('Set X_BEARER_TOKEN in your environment first.')
IDS = os.path.join(ROOT, 'data', 'ids')
OUT = os.path.join(RAW, 'x_posts'); os.makedirs(OUT, exist_ok=True)
JOBS = {'elonmusk': 'elon_x_api_sample_ids.txt', 'adam3us': 'control_adam3us_ids.txt',
        'NickSzabo4': 'control_NickSzabo4_ids.txt', 'VitalikButerin': 'control_VitalikButerin_ids.txt'}
if '--all' in sys.argv: JOBS['elonmusk_all'] = 'elon_cmj_scrape_ids.txt'

def lookup(ids):
    q = urllib.parse.urlencode({'ids': ','.join(ids), 'tweet.fields': 'created_at,note_tweet'})
    req = urllib.request.Request(f'https://api.x.com/2/tweets?{q}', headers={'Authorization': f'Bearer {TOKEN}'})
    return json.load(urllib.request.urlopen(req))

for name, fn in JOBS.items():
    ids = [l.strip() for l in open(os.path.join(IDS, fn)) if l.strip()]
    with open(os.path.join(OUT, f'{name}.jsonl'), 'w') as f:
        for i in range(0, len(ids), 100):
            d = lookup(ids[i:i+100])
            for p in d.get('data', []):
                f.write(json.dumps(dict(id=p['id'], created_at=p['created_at'], text=p['text'],
                                        note_text=(p.get('note_tweet') or {}).get('text')), ensure_ascii=False) + '\n')
            time.sleep(1)
    print('fetched', name, len(ids), 'ids')
