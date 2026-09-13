#!/bin/zsh
set -e
cd "${0:A:h}"
exec ./tools/Blender4.5.app/Contents/MacOS/Blender observatory-v2.blend --python scripts/configure_gpu.py
