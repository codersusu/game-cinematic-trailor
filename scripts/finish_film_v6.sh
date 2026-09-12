#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
BLENDER_BIN="${BLENDER_BIN:-blender}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
mkdir -p renders/v6 previews/v6
"$BLENDER_BIN" --background --disable-autoexec --python-exit-code 1 --python scripts/audit_scene_v6.py > renders/v6/scene-audit.log 2>&1
if [ -f renders/v5/frames/0576.png ]; then
    "$PYTHON_BIN" scripts/seed_frames_v6.py > renders/v6/seed.log 2>&1
fi
"$BLENDER_BIN" --background --disable-autoexec observatory-v6.blend --python-exit-code 1 --python scripts/render_v6.py -- final 1 576 > renders/v6/final-render.log 2>&1
"$PYTHON_BIN" scripts/encode_v6.py final > renders/v6/encode.log 2>&1
"$PYTHON_BIN" scripts/validate_movie_v6.py > renders/v6/movie-validation.log 2>&1
"$PYTHON_BIN" scripts/verify_audio_v6.py > renders/v6/audio-validation.log 2>&1
