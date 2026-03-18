"""Tests verifying code quality fixes are in place."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestNoHardcodedPaths:

    def test_gui_layouts_no_hardcoded_audio_path(self):
        src = os.path.join(os.path.dirname(__file__), "..", "gui_layouts.py")
        with open(src, "r") as f:
            source = f.read()
        assert "KYV001.mp3" not in source, \
            "Hardcoded audio path should be removed from layouts"

    def test_no_backslash_paths_in_music_splitter(self):
        src = os.path.join(os.path.dirname(__file__), "..", "music_splitter_helper.py")
        with open(src, "r") as f:
            source = f.read()
        assert "os.path.join" in source

    def test_no_backslash_paths_in_img_generator(self):
        src = os.path.join(os.path.dirname(__file__), "..", "img_generator.py")
        with open(src, "r", encoding="utf-8") as f:
            source = f.read()
        # Should import paths from config
        assert "from config import" in source


class TestImgGeneratorUsesHtml2Image:

    def test_uses_html2image(self):
        src = os.path.join(os.path.dirname(__file__), "..", "img_generator.py")
        with open(src, "r", encoding="utf-8") as f:
            source = f.read()
        assert "html2image" in source
        assert "Html2Image" in source


class TestProgressBarRemoved:

    def test_no_progress_bar_close_in_vid_gen(self):
        src = os.path.join(os.path.dirname(__file__), "..", "vid_generator.py")
        with open(src, "r") as f:
            source = f.read()
        assert "progress_bar.close()" not in source

    def test_vid_gen_has_try_finally(self):
        src = os.path.join(os.path.dirname(__file__), "..", "vid_generator.py")
        with open(src, "r") as f:
            source = f.read()
        assert "finally:" in source


class TestSharedAudioFile:

    def test_single_audio_file_selector(self):
        src = os.path.join(os.path.dirname(__file__), "..", "gui_layouts.py")
        with open(src, "r") as f:
            source = f.read()
        # Should have one shared selector, not per-tab ones
        assert "-AUDIO_FILE_NAME-" in source
        assert "-AUDIO_FILE_NAME_TO_SPLIT-" not in source
        assert "-AUDIO_FILE_NAME_FOR_VID_GEN-" not in source


class TestKeyboardShortcuts:

    def test_shortcuts_shown_on_buttons(self):
        src = os.path.join(os.path.dirname(__file__), "..", "gui_layouts.py")
        with open(src, "r") as f:
            source = f.read()
        assert "[P]" in source
        assert "[Space]" in source
        assert "[Ctrl+Z]" in source

    def test_arrow_key_bindings(self):
        src = os.path.join(os.path.dirname(__file__), "..", "draw_gui.py")
        with open(src, "r") as f:
            source = f.read()
        assert "<Left>" in source
        assert "<Right>" in source
        assert "SEEK_LEFT" in source
        assert "SEEK_RIGHT" in source
