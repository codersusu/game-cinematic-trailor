#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec "${PYTHON_BIN:-python3}" scripts/open_arrival.py
