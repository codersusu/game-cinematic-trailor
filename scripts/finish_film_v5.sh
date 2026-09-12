#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-blender}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p renders/v5 previews/v5
"$BLENDER_BIN" --background --disable-autoexec observatory-v5.blend --python-exit-code 1 --python scripts/render_v5.py -- final 1 576 > renders/v5/final-render.log 2>&1
"$PYTHON_BIN" scripts/encode_v5.py final > renders/v5/encode.log 2>&1
"$PYTHON_BIN" scripts/validate_movie_v5.py > renders/v5/validation.log 2>&1
"$BLENDER_BIN" --background --disable-autoexec observatory-v5.blend --python-exit-code 1 --python scripts/render_v5.py -- hero 420 > renders/v5/hero-render.log 2>&1
"$BLENDER_BIN" --background --disable-autoexec observatory-v5.blend --python-exit-code 1 --python scripts/audit_scene_v5.py > renders/v5/scene-audit.log 2>&1
