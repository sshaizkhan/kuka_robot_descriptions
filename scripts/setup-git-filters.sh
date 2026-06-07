#!/usr/bin/env bash
# One-time setup so *.dae meshes (stored gzip-compressed in git) are
# transparently decompressed on checkout. Run once after cloning.
#
#   ./scripts/setup-git-filters.sh
#
# Git intentionally does NOT run clean/smudge filters defined only in
# .gitattributes (security): the filter command must be registered in the
# local repo config, which is what this script does.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

git config filter.daegz.clean  "gzip -n -9"
git config filter.daegz.smudge "gzip -d"
git config filter.daegz.required true

echo "daegz filter registered. Re-materializing *.dae from compressed blobs..."

# A fresh clone checks out BEFORE the filter is registered, so existing .dae
# hold raw gzip bytes. Delete them and re-checkout to run the smudge filter.
git ls-files -z -- '*.dae' | xargs -0 -r rm -f
git checkout -- .

echo "Done. Sample:"
ls -lh "$(git ls-files -- '*.dae' | head -1)" 2>/dev/null || true
