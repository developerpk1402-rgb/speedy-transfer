"""
Simple image optimizer:
- Walks `templates/assets/images` and `templates/assets` for images
- Produces WebP variants and resized versions (800px and 400px wide)
- Saves new files alongside originals with suffixes: -800.webp, -400.webp

Usage: .venv\Scripts\python.exe tools\optimize_images.py
"""
import os
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'assets')
IMG_DIRS = ['images']
FORMATS = ('.jpg', '.jpeg', '.png')
TARGET_SIZES = [800, 400]

print('Scanning', ROOT)

for sub in IMG_DIRS:
    d = os.path.join(ROOT, sub)
    if not os.path.isdir(d):
        continue
    for root, dirs, files in os.walk(d):
        for fn in files:
            if not fn.lower().endswith(FORMATS):
                continue
            path = os.path.join(root, fn)
            try:
                img = Image.open(path)
                base, ext = os.path.splitext(path)
                # Save WebP full-size
                webp_path = base + '.webp'
                img.save(webp_path, 'WEBP', quality=85)
                print('Saved', webp_path)
                # Save resized versions
                for w in TARGET_SIZES:
                    if img.width <= w:
                        continue
                    ratio = w / float(img.width)
                    h = int(img.height * ratio)
                    resized = img.resize((w, h), Image.LANCZOS)
                    out_path = f"{base}-{w}.webp"
                    resized.save(out_path, 'WEBP', quality=80)
                    print('Saved', out_path)
            except Exception as e:
                print('Error processing', path, e)

print('Done')
