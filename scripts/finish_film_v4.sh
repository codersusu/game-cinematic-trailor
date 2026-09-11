#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-blender}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p renders/v4 previews/v4
"$BLENDER_BIN" --background --disable-autoexec observatory-v4.blend --python scripts/render_v4.py -- final 1 576 > renders/v4/final-render.log 2>&1
"$PYTHON_BIN" scripts/encode_v4.py final > renders/v4/encode.log 2>&1
"$PYTHON_BIN" scripts/validate_movie_v4.py > renders/v4/validation.log 2>&1
"$BLENDER_BIN" --background --disable-autoexec observatory-v4.blend --python scripts/render_v4.py -- hero 317 > renders/v4/hero-render.log 2>&1
"$BLENDER_BIN" --background --disable-autoexec observatory-v4.blend --python scripts/audit_scene_v4.py > renders/v4/scene-audit.log 2>&1
