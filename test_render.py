"""Quick test: render the तेजस्वि line to check font rendering."""
from img_generator import ImgGenerator
from unittest.mock import MagicMock

gui = MagicMock()
gen = ImgGenerator(gui)
gen._ensure_fonts_loaded()

# Line 4 from devanagari.txt
dn = "तेजस्वि नावधीतमस्तु मा विद्विषावहै ॥"
en = "tejasvi nāvadhītamastu mā vidviṣāvahai."
hd = "Invocation"

gen._create_single_img(dn, en, hd, 9999)
print("Check lyric_images/9999.png")
