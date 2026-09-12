#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-blender}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p renders/v7 previews/v7
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/audit_scene_v7.py > renders/v7/scene-audit.log 2>&1
if [ -f renders/v6/frames/0576.png ]; then
    "$PYTHON_BIN" scripts/seed_frames_v7.py > renders/v7/seed.log 2>&1
fi
"$BLENDER_BIN" --background --disable-autoexec observatory-v7.blend --python-exit-code 1 --python scripts/render_v7.py -- final 1 576 > renders/v7/final-render.log 2>&1
"$PYTHON_BIN" scripts/encode_v7.py final > renders/v7/encode.log 2>&1
"$PYTHON_BIN" scripts/validate_movie_v7.py > renders/v7/movie-validation.log 2>&1
"$PYTHON_BIN" scripts/verify_audio_v7.py > renders/v7/audio-validation.log 2>&1
