#!/bin/bash
# 使い方: tools/render.sh deck.pptx outdir   → outdir/deck.pdf と outdir/p-XX.png（100dpi）
set -e
F="$1"; O="${2:-render}"; mkdir -p "$O"
SOFFICE=~/.local/opt/libreoffice-root/opt/libreoffice26.2/program/soffice
export LD_LIBRARY_PATH=~/.local/opt/libreoffice-root/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
$SOFFICE --headless --convert-to pdf --outdir "$O" "$F" >/dev/null 2>&1
B=$(basename "${F%.pptx}")
pdftoppm -r 100 -png "$O/$B.pdf" "$O/p"
echo "$O/$B.pdf: $(pdfinfo "$O/$B.pdf" | grep Pages)"
