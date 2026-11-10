#!/usr/bin/env bash
# Configure THIS clone of the repo. Run once after cloning (idempotent —
# safe to re-run):
#
#     bash scripts/setup-git.sh
#
# It sets up two things that .gitattributes alone cannot install, because git
# filter programs and hooks live in the local .git/config and .git/hooks, which
# never travel with a repo:
#
#   1. The gzip clean/smudge filter that keeps the large, regenerable
#      graphify-out/graph.json small in git.
#   2. The pre-commit size guard that blocks accidental giant blobs.
#   3. The safe knowledge-graph refresh hooks (kg:rebuild, M-80).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# --- gzip clean/smudge filter for graphify-out/graph.json -------------------
# clean  (staged at commit): flat JSON  -> gzipped blob stored in git (~15x smaller)
# smudge (checkout):         gzipped blob -> flat JSON in the working tree
# -n drops the name/mtime header bytes so the output is deterministic and git
#    never reports a phantom modification.
# required=true makes git fail loudly rather than silently pass the file through
#    unfiltered if gzip/gunzip is missing.
git config filter.gzip_graph.clean  "gzip -n -c -6"
git config filter.gzip_graph.smudge "gunzip -c"
git config filter.gzip_graph.required true
echo "configured: filter.gzip_graph (clean / smudge / required)"

# --- pre-commit size guard --------------------------------------------------
src="$ROOT/scripts/git-hooks/pre-commit"
dst="$ROOT/.git/hooks/pre-commit"
if [ -e "$dst" ] && ! grep -q "gtai-size-guard" "$dst" 2>/dev/null; then
	echo "warning: $dst exists and is not ours — leaving it in place." >&2
	echo "         Merge scripts/git-hooks/pre-commit into it by hand." >&2
else
	cp "$src" "$dst"
	chmod +x "$dst"
	echo "installed: .git/hooks/pre-commit (size guard + staged-file ruff)"
fi

echo
echo "Done. If graphify-out/graph.json is still stored flat in git, normalise it:"
echo "    git add --renormalize graphify-out/graph.json"
echo "    git commit -m 'chore(graphify): store graph.json gzipped'"
echo
echo "On a FRESH clone the filter does not exist yet, so graph.json on disk is"
echo "the raw gzipped bytes. After running this script, re-inflate it with:"
echo "    git checkout -- graphify-out/graph.json"

# >>> kg-rebuild-hooks (M-80) >>>
# Safe knowledge-graph refresh hooks (kg:rebuild). They replace graphify's own post-commit and
# post-checkout hooks, whose rebuild deleted document knowledge: never run `graphify hook install`.
KG_HOOKS_DIR="$(git rev-parse --git-common-dir)/hooks"
for kg_hook in post-commit post-checkout post-merge; do
  kg_dst="$KG_HOOKS_DIR/$kg_hook"
  if [ -e "$kg_dst" ] && ! grep -qE "graphify-hook-start|graphify-checkout-hook-start|kg-refresh.sh" "$kg_dst"; then
    echo "warning: $kg_dst is a custom hook - left in place; add the kg refresh by hand." >&2
    continue
  fi
  install -m 0755 "$(git rev-parse --show-toplevel)/scripts/git-hooks/$kg_hook" "$kg_dst"
done
echo "installed: safe knowledge-graph refresh hooks (post-commit, post-checkout, post-merge)"
# <<< kg-rebuild-hooks <<<
