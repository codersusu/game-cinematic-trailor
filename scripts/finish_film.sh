#!/bin/zsh
set -euo pipefail
cd "${0:A:h:h}"
BLENDER="${BLENDER_BIN:-blender}"
PYTHON="${PYTHON_BIN:-python3}"
if [[ ! -x "$PYTHON" ]]; then PYTHON=python3; fi
"$BLENDER" --background observatory.blend --python scripts/render.py -- final 1 576 > renders/final-render.log 2>&1
"$PYTHON" scripts/encode.py final > renders/encode.log 2>&1
"$PYTHON" scripts/motion_from_final.py > previews/motion-encode.log 2>&1
"$PYTHON" scripts/validate_movie.py > renders/validation.log 2>&1
