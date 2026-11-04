#!/usr/bin/env bash
# Download every public source into data/raw/ (git-ignored).  Needs: git, curl, gzip, poppler-utils (pdftotext).
set -euo pipefail
cd "$(dirname "$0")/.."
R=data/raw; mkdir -p $R/ctrl/metzdowd $R/elon/prose

# 1. Satoshi Nakamoto Institute site repo (emails + forum posts + library essays) - pinned commit
[ -d $R/nisrepo ] || git clone https://github.com/NakamotoInstitute/nakamotoinstitute.org.git $R/nisrepo
git -C $R/nisrepo checkout -q 3bb1aa413a325bbf295a1e3424c272a0d549b42b
# 2. Nakamoto Archive (private emails with Back/Dai/Finney, white paper PDF) - pinned commit
[ -d $R/lug ] || git clone https://github.com/lugaxker/nakamoto-archive.git $R/lug
git -C $R/lug checkout -q 8405b13482ae1a1bc55d6fe5bb3a5f2f46a58ffc

# 3. Metzdowd "cryptography" mailing-list archive 2006-2009 (control authors).  Missing months return an HTML 404 -> deleted.
for y in 2006 2007 2008 2009; do for m in January February March April May June July August September October November December; do
  f=$R/ctrl/metzdowd/$y-$m.txt.gz
  [ -s "$f" ] || curl -sfL -o "$f" "https://www.metzdowd.com/pipermail/cryptography/$y-$m.txt.gz" || true
  gzip -t "$f" 2>/dev/null || rm -f "$f"
done; done

# 4. Elon Musk posts, 2010-2026: public scrape by github.com/cmj/elontweets (WHITESPACE IS COLLAPSED in this file)
[ -s $R/elon/elonmusk-all-tweets.csv ] || curl -sfL -o $R/elon/elonmusk-all-tweets.csv \
  https://raw.githubusercontent.com/cmj/elontweets/main/elonmusk-all-tweets.csv

# 5. Elon long-form prose: Tesla blog posts (copies on elonmuskarchive.org; tesla.com blocks scripted downloads)
for s in musk-blog-master-plan-2006 musk-blog-master-plan-part-deux-2016 musk-blog-model-s-fire-2013 \
         musk-blog-patents-2014 musk-blog-peculiar-test-drive-2013; do
  [ -s $R/elon/prose/$s.html ] || curl -sfL -o $R/elon/prose/$s.html https://elonmuskarchive.org/blog/$s
done
# 6. Elon emails / texts released in court & company emails (excerpts as displayed on the archive's /emails page)
[ -s $R/elon/emails_page.html ] || curl -sfL -o $R/elon/emails_page.html https://elonmuskarchive.org/emails
echo "Done. Now run:  X_BEARER_TOKEN=... python scripts/x_fetch_posts.py   (raw-text X posts for the double-space test)"
