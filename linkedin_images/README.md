# LinkedIn Success Story Images

- Format: SVG, 1200x628 (LinkedIn-friendly)
- Style: Dark navy gradient, cyan/teal accents
- Footer: "Cristian Meléndez • linkedin.com/in/cmelendezgp"

## Files
- story-01.svg .. story-08.svg
- story-0X-alt.txt (ALT text for accessibility)

## Export to PNG (optional)

Using Inkscape:
```bash
# Single
inkscape --export-type=png --export-filename=story-01.png story-01.svg
# All
for f in story-*.svg; do inkscape --export-type=png "$f" --export-filename="${f%.svg}.png"; done
```

Using rsvg-convert:
```bash
# Single
rsvg-convert -w 1200 -h 628 story-01.svg > story-01.png
# All
for f in story-*.svg; do rsvg-convert -w 1200 -h 628 "$f" > "${f%.svg}.png"; done
```

Using ImageMagick (requires proper SVG support):
```bash
magick convert -resize 1200x628 story-01.svg story-01.png
```

## Branding
- Background: #0B132B → #1F2A44
- Accent: #00D1B2 → #66E4FF

Feel free to tweak titles/bullets directly in the SVG text nodes.