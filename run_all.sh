#!/usr/bin/env bash
# Reproduce everything.  Python 3.10+, see requirements.txt.
set -euo pipefail
cd "$(dirname "$0")"
bash scripts/00_fetch_corpora.sh
python scripts/x_fetch_posts.py            # needs X_BEARER_TOKEN
python scripts/01_build_corpora.py
python scripts/02_double_space.py
python scripts/03_spelling.py
python scripts/04_delta.py
python scripts/05_quirks.py
python scripts/07_era_shift.py
python scripts/06_charts.py
