#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
BLENDER="${BLENDER_BIN:-blender}"
PYTHON="${PYTHON_BIN:-python3}"
if [[ ! -x "$PYTHON" ]]; then PYTHON=python3; fi
"$BLENDER" --background observatory-v2.blend --python scripts/render_v2.py -- final 1 576 > renders/v2/final-render.log 2>&1
"$PYTHON" scripts/encode_v2.py final > renders/v2/encode.log 2>&1
"$PYTHON" scripts/validate_movie_v2.py > renders/v2/validation.log 2>&1
