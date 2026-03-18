"""Generate 1920x1080 lyric images with Devanagari and IAST text.

Uses html2image (Chrome headless) for proper Indic text shaping.
"""

import os
import time

from html2image import Html2Image

from config import BLANK_IMG, LYRIC_IMAGES_DIR, DEVANAGARI_TXT, IAST_TXT, HEADING_TXT


class ImgGenerator:

    def __init__(self, draw_gui_object):
        self.im_w = 1920
        self.im_h = 1080
        self.font_path_dn = os.path.abspath(
            os.path.join("other_files", "static",
                         "NotoSansDevanagari-Regular.ttf")
        ).replace("\\", "/")
        self.font_path_en = os.path.abspath(
            os.path.join("other_files", "static",
                         "NotoSansDevanagari-Regular.ttf")
        ).replace("\\", "/")
        self.bg_path = os.path.abspath(BLANK_IMG).replace("\\", "/")
        self.font_color = "#271300"
        self.stop_flag = False
        self.in_progress = False
        self.gui = draw_gui_object

        # Chrome path — auto-detect
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        self._chrome = None
        for p in chrome_paths:
            if os.path.exists(p):
                self._chrome = p
                break

    # ── HTML template ─────────────────────────────────────────

    def _build_html(self, dn_text, iast_text, heading_text):
        """Build an HTML string for a single lyric image."""
        # Escape HTML special chars
        dn_text = dn_text.strip().replace("&", "&amp;").replace("<", "&lt;")
        iast_text = iast_text.strip().replace("&", "&amp;").replace("<", "&lt;")
        heading_text = heading_text.strip().replace("&", "&amp;").replace("<", "&lt;")

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@font-face {{
    font-family: 'NotoSansDev';
    src: url('file:///{self.font_path_dn}');
}}
@font-face {{
    font-family: 'NotoSansEn';
    src: url('file:///{self.font_path_en}');
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: {self.im_w}px;
    height: {self.im_h}px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-image: url('file:///{self.bg_path}');
    background-size: cover;
    color: {self.font_color};
    text-align: center;
    position: relative;
}}
.heading {{
    font-family: 'NotoSansDev', sans-serif;
    font-size: 23px;
    position: absolute;
    top: 15px;
    left: 0; right: 0;
    text-align: center;
    opacity: 0.7;
}}
.devanagari {{
    font-family: 'NotoSansDev', 'Noto Sans Devanagari', sans-serif;
    font-size: 94px;
    margin-bottom: 20px;
    padding: 0 30px;
    line-height: 1.5;
}}
.iast {{
    font-family: 'NotoSansEn', 'Noto Sans', sans-serif;
    font-size: 68px;
    padding: 0 30px;
    line-height: 1.5;
}}
</style>
</head>
<body>
<div class="heading">{heading_text}</div>
<div class="devanagari">{dn_text}</div>
<div class="iast">{iast_text}</div>
</body>
</html>"""

    # ── Single image creation ──────────────────────────────────

    def _create_single_img(self, dn_l, iast_l, head_l, file_num, hti):
        html = self._build_html(dn_l, iast_l, head_l)
        hti.screenshot(
            html_str=html,
            save_as=f"{file_num}.png",
        )

    # ── Batch generation ───────────────────────────────────────

    def generate_images(self):
        """Generate all lyric images from text files."""
        self.in_progress = True

        dn_lyrics = open(DEVANAGARI_TXT, "r", encoding="utf-8").readlines()
        en_lyrics = open(IAST_TXT, "r", encoding="utf-8").readlines()
        head_lyrics = open(HEADING_TXT, "r", encoding="utf-8").readlines()

        total = len(dn_lyrics)
        print(f"Number of lines to create images for = {total}")
        assert len(dn_lyrics) == len(en_lyrics), \
            f"devanagari.txt ({len(dn_lyrics)}) and iast.txt ({len(en_lyrics)}) have different line counts"
        assert len(dn_lyrics) == len(head_lyrics), \
            f"devanagari.txt ({len(dn_lyrics)}) and heading.txt ({len(head_lyrics)}) have different line counts"

        os.makedirs(LYRIC_IMAGES_DIR, exist_ok=True)

        hti = Html2Image(
            browser_executable=self._chrome,
            output_path=LYRIC_IMAGES_DIR,
            size=(self.im_w, self.im_h),
        )

        start = time.time()
        for ind in range(total):
            self.gui.update_time_boxes_img_vid_gen(
                total, ind, time.time() - start)
            self.gui.update_img_gen_progress(ind + 1, total)
            if self.stop_flag:
                print("Stopped image creation midway")
                self.stop_flag = False
                break
            self._create_single_img(
                dn_lyrics[ind], en_lyrics[ind], head_lyrics[ind],
                ind + 1, hti)
            print(f"Created image for line #{ind + 1}")

        elapsed = time.time() - start
        print(f"It took {elapsed:.1f}s to process {ind + 1} images")
        self.in_progress = False
        self.gui.update_img_gen_progress(total, total)

    def stop_img_creation(self):
        if self.in_progress:
            self.stop_flag = True
            print("Stop image generation button was pressed")
