#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-blender}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p renders/v3 previews/v3
"$BLENDER_BIN" --background observatory-v3.blend --python scripts/render_v3.py -- final 1 576 > renders/v3/final-render.log 2>&1
"$PYTHON_BIN" scripts/encode_v3.py final > renders/v3/encode.log 2>&1
"$PYTHON_BIN" scripts/proof_v3_from_frames.py > previews/v3/motion-encode.log 2>&1
"$PYTHON_BIN" scripts/validate_movie_v3.py > renders/v3/validation.log 2>&1

"$BLENDER_BIN" --background observatory-v3.blend --python scripts/render_v3.py -- hero 390 > renders/v3/hero-render.log 2>&1
"$BLENDER_BIN" --background observatory-v3.blend --python scripts/audit_scene_v3.py > renders/v3/scene-audit.log 2>&1
