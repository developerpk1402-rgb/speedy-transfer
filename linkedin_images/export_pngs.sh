#!/usr/bin/env bash
set -euo pipefail

# Convert LinkedIn story SVGs (1200x628) to PNG.
# Prefers rsvg-convert, falls back to Inkscape, then ImageMagick.

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

convert_one() {
	local src="$1"
	local out="${src%.svg}.png"
	if command -v rsvg-convert >/dev/null 2>&1; then
		rsvg-convert -w 1200 -h 628 "$src" > "$out"
	elif command -v inkscape >/dev/null 2>&1; then
		inkscape --export-type=png --export-filename="$out" "$src"
	elif command -v magick >/dev/null 2>&1; then
		magick convert -resize 1200x628 "$src" "$out"
	else
		echo "Error: please install rsvg-convert (librsvg2-bin) or Inkscape or ImageMagick." >&2
		exit 1
	fi
	echo "Generated $out"
}

if [[ $# -gt 0 ]]; then
	for f in "$@"; do
		[[ -f "$f" ]] || { echo "Skipping missing: $f"; continue; }
		convert_one "$f"
	done
else
	shopt -s nullglob
	files=(story-*.svg)
	if [[ ${#files[@]} -eq 0 ]]; then
		echo "No story-*.svg files found in $script_dir" >&2
		exit 1
	fi
	for f in "${files[@]}"; do
		convert_one "$f"
	done
fi