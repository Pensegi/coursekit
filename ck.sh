#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Dennis Rudin - see LICENSE and NOTICE
# ck.sh - run coursekit with its own Python environment (made on first use).
#   bash ck.sh setup [en] [sv] [piper:VOICE]   first run: download voice models (default: English)
#   bash ck.sh skill [--code]             package the Claude skill (dist/slide-video-course.zip)
#   bash ck.sh init  ~/Desktop/deck.pptx [--lang sv]
#   bash ck.sh check | voicetest | audio | video | subs | all  <course folder>
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
command -v ffmpeg >/dev/null   || { echo "ffmpeg missing:   brew install ffmpeg";  exit 1; }
command -v pdftoppm >/dev/null || { echo "pdftoppm missing: brew install poppler"; exit 1; }
if [ ! -x "$KIT/.venv/bin/python" ]; then
  echo "First run: setting up the Python environment (a few minutes) ..."
  python3 -m venv "$KIT/.venv"
  "$KIT/.venv/bin/pip" install -q --upgrade pip
  "$KIT/.venv/bin/pip" install -q -r "$KIT/requirements.txt"
fi
exec "$KIT/.venv/bin/python" "$KIT/coursekit.py" "$@"
