import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.templatetags.static import static
from PIL import Image, ImageDraw, ImageFont

from speedy_app.core.models import Car


class Command(BaseCommand):
	help = "Generate placeholder images for all vehicles and known filenames used by the app."

	def add_arguments(self, parser):
		parser.add_argument("--size", type=str, default="800x450", help="Image size WxH, default 800x450")
		parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")

	def handle(self, *args, **options):
		width, height = self._parse_size(options["size"]) 
		output_dir = Path(settings.BASE_DIR) / "templates" / "assets" / "images" / "cars"
		output_dir.mkdir(parents=True, exist_ok=True)

		# Filenames referenced in views as defaults
		known_filenames = [
			"Van_Dark.jpg",
			"Small_Sprinter.jpg",
			"Large_Sprinter.jpg",
			"Standard_Van.jpg",
			"Luxury_Van.jpg",
			"Midsize_SUV.jpg",
			"Mini_Bus.jpg",
			"Economy_Sedan.jpg",
		]

		# From the DB sample provided by user (ensure all are present)
		db_sample_filenames = [
			"Van_Dark.jpg",
			"Small_Sprinter.jpg",
			"Large_Sprinter.jpg",
			"Luxury_SUV.jpg",
			"Economy_Sedan.jpg",
			"Premium_Sedan.jpg",
			"Compact_SUV.jpg",
			"Midsize_SUV.jpg",
			"Luxury_SUV.jpg",
			"Standard_Van.jpg",
			"Luxury_Van.jpg",
			"Mini_Sprinter.jpg",
			"Standard_Sprinter.jpg",
			"Luxury_Sprinter.jpg",
			"Large_Sprinter.jpg",
			"Executive_Sprinter.jpg",
			"Mini_Bus.jpg",
			"Luxury_Mini_Bus.jpg",
			"Party_Bus.jpg",
			"Tour_Bus.jpg",
			"Luxury_Limousine.jpg",
			"Stretch_Limousine.jpg",
			"Hummer_Limo.jpg",
			"Charter_Bus.jpg",
			"Hiace_White_001.jpg",
			"Hiace_White_002.jpg",
			"Hiace_White_003.jpg",
			"Suburban_Black_101.jpg",
			"Suburban_Black_102.jpg",
			"Suburban_White_103.jpg",
			"Suburban_White_104.jpg",
			"Mercedes_Sprinter_201.jpg",
			"Mercedes_Sprinter_202.jpg",
			"Mercedes_Sprinter_203.jpg",
			"Mercedes_Sprinter_204.jpg",
			"Mercedes_Sprinter_205.jpg",
			"Honda_Pilot_301.jpg",
			"Honda_Pilot_302.jpg",
			"Honda_Pilot_303.jpg",
			"Ford_Transit_401.jpg",
			"Ford_Transit_402.jpg",
			"Ford_Transit_403.jpg",
		]

		# Gather expected filenames from DB values and model data
		expected_files = set(known_filenames) | set(db_sample_filenames)

		# Add all Car.image basenames from DB, but do not fail if DB is unavailable
		try:
			cars = list(Car.objects.all())
		except Exception as exc:
			self.stdout.write(self.style.WARNING(f"Skipping DB read (Car.objects.all()) due to error: {exc}"))
			cars = []

		for car in cars:
			basename = None
			try:
				if car.image and getattr(car.image, "name", None):
					basename = os.path.basename(car.image.name)
			except Exception:
				basename = None
			if not basename and car.name:
				# Derive using naming rules from views
				upper_name = car.name.upper()
				if upper_name.startswith("HIACE-VAN-"):
					suffix = upper_name.split("HIACE-VAN-")[-1]
					basename = f"Hiace_White_{suffix}.jpg"
				elif "SUBURBAN" in upper_name and any(s in upper_name for s in ["101", "102", "103", "104"]):
					# fallback heuristic; already covered in db sample list above
					pass
				elif "SPRINTER-MB-" in upper_name:
					suffix = upper_name.split("SPRINTER-MB-")[-1]
					basename = f"Mercedes_Sprinter_{suffix}.jpg"
				elif "PILOT-HP-" in upper_name:
					suffix = upper_name.split("PILOT-HP-")[-1]
					basename = f"Honda_Pilot_{suffix}.jpg"
				elif "TRANSIT-FT-" in upper_name:
					suffix = upper_name.split("TRANSIT-FT-")[-1]
					basename = f"Ford_Transit_{suffix}.jpg"
			if basename:
				expected_files.add(basename)

		self.stdout.write(self.style.NOTICE(f"Output directory: {output_dir}"))

		for filename in sorted(expected_files):
			path = output_dir / filename
			if path.exists() and not options["overwrite"]:
				self.stdout.write(f"Skip existing: {filename}")
				continue
			self._create_image(path, width, height, self._label_for(filename))
			self.stdout.write(self.style.SUCCESS(f"Created: {filename}"))

		self.stdout.write(self.style.SUCCESS("Vehicle images generation complete."))

	def _parse_size(self, size_str: str) -> tuple:
		try:
			w_str, h_str = size_str.lower().split("x")
			return int(w_str), int(h_str)
		except Exception:
			return 800, 450

	def _label_for(self, filename: str) -> str:
		name = Path(filename).stem.replace("_", " ")
		return name

	def _create_image(self, path: Path, width: int, height: int, label: str) -> None:
		bg_color = (30, 41, 59)  # slate-800 like
		accent = (234, 179, 8)  # amber-400 like
		img = Image.new("RGB", (width, height), color=bg_color)
		draw = ImageDraw.Draw(img)

		# Draw a simple vehicle-like rectangle
		pad = int(min(width, height) * 0.06)
		shape_top = height // 2 - int(height * 0.15)
		shape_bottom = height // 2 + int(height * 0.18)
		draw.rounded_rectangle([pad, shape_top, width - pad, shape_bottom], radius=20, outline=accent, width=6)

		# Try to load a common font
		font = None
		for font_name in ["DejaVuSans-Bold.ttf", "Arial.ttf", "FreeSansBold.ttf"]:
			try:
				font = ImageFont.truetype(font_name, size=int(height * 0.08))
				break
			except Exception:
				font = None
		if font is None:
			font = ImageFont.load_default()

		text = label
		tw, th = draw.textsize(text, font=font)
		x = (width - tw) // 2
		y = int(height * 0.15)
		draw.text((x, y), text, fill=accent, font=font)

		# Footer line to mimic a card
		draw.line([(pad, height - pad), (width - pad, height - pad)], fill=accent, width=3)

		path.parent.mkdir(parents=True, exist_ok=True)
		img.save(str(path), format="JPEG", quality=90)