"""Tests for vid_generator.py."""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestVidGeneratorInit:
    def test_default_values(self):
        from vid_generator import VidGenerator
        vg = VidGenerator()
        assert vg.im_w == 1920
        assert vg.im_h == 1080
        assert vg.frame_rate == 10.0
        assert vg.in_progress is False
        assert vg.stop_flag is False

    def test_stop_flag_works(self):
        from vid_generator import VidGenerator
        vg = VidGenerator()
        vg.in_progress = True
        vg.stop_vid_creation()
        assert vg.stop_flag is True


class TestVidGeneratorCsv:
    def test_read_durations(self, tmp_path):
        import vid_generator as vg_mod
        from vid_generator import VidGenerator
        vg = VidGenerator()
        csv_content = "10.5,1.0\n20.3,2.0\n30.1,3.0\n"
        csv_file = tmp_path / "durations.csv"
        csv_file.write_text(csv_content)

        # Patch the module-level constant that was imported
        original = vg_mod.LYRICS_DURATIONS_CSV
        vg_mod.LYRICS_DURATIONS_CSV = str(csv_file)
        try:
            result = vg._read_durations_csv()
            assert result == [10.5, 20.3, 30.1]
        finally:
            vg_mod.LYRICS_DURATIONS_CSV = original
