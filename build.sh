#!/usr/bin/env bash
# Build the distributable single file, and the per-tool exports of D4a.
#
# Stdlib only: zipapp ships with Python, so this needs nothing installed and
# produces something a stranger can run with `python3 hone.pyz`.
#
# The staging step is not decoration. `hone/` carries its own __main__.py so
# that `python3 -m hone` works from the source tree, and zipapp refuses to
# take an entry point when the source already has one. Staging keeps `hone`
# a real package inside the archive, which relative imports need, and puts the
# archive's entry point beside it rather than inside it.
set -euo pipefail
cd "$(dirname "$0")"

OUT="${OUT:-dist}"
mkdir -p "$OUT"

stage_and_build() {
    local dest="$1" keep="${2:-}"
    local stage
    stage="$(mktemp -d)"
    trap 'rm -rf "$stage"' RETURN

    cp -r hone "$stage/hone"
    find "$stage" -name '__pycache__' -type d -prune -exec rm -rf {} +

    if [ -n "$keep" ]; then
        find "$stage/hone/content" -name '*.py' \
             ! -name '__init__.py' ! -name "$keep.py" -delete
    fi

    cat > "$stage/__main__.py" <<'PY'
import sys

from hone.app import main

sys.exit(main())
PY

    python3 -m zipapp "$stage" -p '/usr/bin/env python3' -o "$dest"
    chmod +x "$dest"
    echo "built $dest"
}

stage_and_build "$OUT/hone.pyz"

# D4a: one file per tool from the same source. Discovery is additive, so a
# build that ships fewer content files simply finds fewer modules.
if [ "${1:-}" = "--per-tool" ]; then
    shopt -s nullglob
    for f in hone/content/*.py; do
        name="$(basename "$f" .py)"
        [ "$name" = "__init__" ] && continue
        stage_and_build "$OUT/hone-$name.pyz" "$name"
    done
fi
