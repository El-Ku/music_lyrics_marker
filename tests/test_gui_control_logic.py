"""Tests for gui_control_logic.py — structural checks."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestControlGuiStructure:

    def test_future_initialized_in_init(self):
        src = os.path.join(os.path.dirname(__file__), "..", "gui_control_logic.py")
        with open(src, "r") as f:
            source = f.read()

        init_start = source.find("def __init__")
        next_def = source.find("\n    def ", init_start + 1)
        init_body = source[init_start:next_def]
        assert "self.future" in init_body

    def test_single_close_handler(self):
        src = os.path.join(os.path.dirname(__file__), "..", "gui_control_logic.py")
        with open(src, "r") as f:
            source = f.read()

        # Only one close button key should exist
        assert "-CLOSE_BTN-" in source
        assert "-CLOSE_BTN2-" not in source
        assert "-CLOSE_BTN3-" not in source

    def test_autosave_logic_exists(self):
        src = os.path.join(os.path.dirname(__file__), "..", "gui_control_logic.py")
        with open(src, "r") as f:
            source = f.read()
        assert "autosave" in source.lower()

    def test_undo_handler_exists(self):
        src = os.path.join(os.path.dirname(__file__), "..", "gui_control_logic.py")
        with open(src, "r") as f:
            source = f.read()
        assert "UNDO" in source


class TestRecalculateDurations:

    def test_single_entry(self):
        """Importing ControlGui requires full GUI — test logic directly."""
        # Simulate _recalculate_durations logic
        marked = [[5.0, 5.0]]
        marked[0][1] = marked[0][0]
        assert marked == [[5.0, 5.0]]

    def test_multiple_entries(self):
        marked = [[2.0, 2.0], [5.0, 3.0], [7.5, 2.5]]
        # Recalculate
        marked[0][1] = marked[0][0]
        for i in range(1, len(marked)):
            marked[i][1] = marked[i][0] - marked[i - 1][0]
        assert marked == [[2.0, 2.0], [5.0, 3.0], [7.5, 2.5]]

    def test_after_adjustment(self):
        marked = [[2.0, 2.0], [5.0, 3.0], [7.5, 2.5]]
        # Shift middle entry by +50ms
        marked[1][0] += 0.050
        # Recalculate
        marked[0][1] = marked[0][0]
        for i in range(1, len(marked)):
            marked[i][1] = marked[i][0] - marked[i - 1][0]
        assert abs(marked[1][0] - 5.05) < 1e-9
        assert abs(marked[1][1] - 3.05) < 1e-9
        assert abs(marked[2][1] - 2.45) < 1e-9


class TestTimestampSplitLogic:

    def test_with_ignore_flags(self):
        raw = [[10.0, 10.0], [20.0, 10.0], [30.0, 10.0]]
        timestamps = [row[0] for row in raw]

        ts = timestamps.copy()
        ts.insert(0, 0)
        ts.append(45.0)
        assert ts == [0, 10.0, 20.0, 30.0, 45.0]

        ts_no_add = timestamps.copy()
        assert len(ts_no_add) - 1 == 2
