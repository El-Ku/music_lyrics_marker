"""Mock heavy dependencies that aren't needed for unit tests."""

import sys
from unittest.mock import MagicMock

for mod_name in [
    "pydub", "pydub.AudioSegment",
    "PySimpleGUI",
    "just_playback",
    "mutagen", "mutagen.mp3",
    "moviepy", "moviepy.editor",
    "cv2",
    "tqdm",
    "PIL", "PIL.Image", "PIL.ImageFont", "PIL.ImageDraw",
    "matplotlib", "matplotlib.pyplot",
    "numpy",
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()
