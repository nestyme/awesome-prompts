#!/bin/bash
# Export picked shots as JPEGs, at most 1080 px wide (Gemini returns 896x1200; it is kept as is, never upscaled). No grain, no vignette: the prompt already asks for the phone look.
#   finish.sh <out_dir> <image.png>...
set -euo pipefail; out=$1; shift; mkdir -p "$out"
for src in "$@"; do n=$(basename "${src%.*}"); ffmpeg -loglevel error -y -i "$src" -vf "scale='min(1080,iw)':-2" -frames:v 1 -q:v 3 "$out/$n.jpg"; echo "$out/$n.jpg"; done
