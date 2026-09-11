#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-blender}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p renders/v2 previews/v2
"$BLENDER_BIN" --background observatory-v2.blend --python scripts/render_v2.py -- final 1 576 > renders/v2/final-render.log 2>&1
"$PYTHON_BIN" scripts/encode_v2.py final > renders/v2/encode.log 2>&1
"$PYTHON_BIN" scripts/proof_v2_from_frames.py > previews/v2/motion-encode.log 2>&1
"$PYTHON_BIN" scripts/validate_movie_v2.py > renders/v2/validation.log 2>&1
