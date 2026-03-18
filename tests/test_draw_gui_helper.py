"""Tests for draw_gui_helper.py — pure utility functions."""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import draw_gui_helper


# ── sec2_timestring ──────────────────────────────────────────────

class TestSec2Timestring:
    def test_zero(self):
        assert draw_gui_helper.sec2_timestring(0) == "00:00"

    def test_seconds_only(self):
        assert draw_gui_helper.sec2_timestring(45) == "00:45"

    def test_minutes_and_seconds(self):
        assert draw_gui_helper.sec2_timestring(125) == "02:05"

    def test_exactly_one_hour(self):
        assert draw_gui_helper.sec2_timestring(3600) == "01:00:00"

    def test_hours_minutes_seconds(self):
        assert draw_gui_helper.sec2_timestring(3661) == "01:01:01"

    def test_float_input_truncates(self):
        assert draw_gui_helper.sec2_timestring(90.9) == "01:30"

    def test_large_value(self):
        assert draw_gui_helper.sec2_timestring(36000) == "10:00:00"

    def test_negative_value_clamped_to_zero(self):
        assert draw_gui_helper.sec2_timestring(-5) == "00:00"


# ── format_floats_for_table ──────────────────────────────────────

class TestFormatFloatsForTable:
    def test_empty_marker(self):
        assert draw_gui_helper.format_floats_for_table([[]]) == [["0.0", "0.0"]]

    def test_single_entry(self):
        result = draw_gui_helper.format_floats_for_table([[1.234, 1.234]])
        assert result == [["1.234", "1.234"]]

    def test_multiple_entries_chronological(self):
        data = [[1.0, 1.0], [3.5, 2.5]]
        result = draw_gui_helper.format_floats_for_table(data)
        assert result == [["1.000", "1.000"], ["3.500", "2.500"]]

    def test_precision(self):
        result = draw_gui_helper.format_floats_for_table([[1.23456789, 0.1]])
        assert result == [["1.235", "0.100"]]


# ── remove_outdated_timestamps ───────────────────────────────────

class TestRemoveOutdatedTimestamps:
    def test_all_timestamps_in_future(self):
        marked = [[5.0, 5.0], [10.0, 5.0]]
        result = draw_gui_helper.remove_outdated_timestamps(1.0, marked)
        assert result == [[]]

    def test_no_timestamps_outdated(self):
        marked = [[1.0, 1.0], [3.0, 2.0]]
        result = draw_gui_helper.remove_outdated_timestamps(5.0, marked)
        assert result == [[1.0, 1.0], [3.0, 2.0]]

    def test_partial_removal(self):
        marked = [[1.0, 1.0], [3.0, 2.0], [7.0, 4.0]]
        result = draw_gui_helper.remove_outdated_timestamps(5.0, marked)
        assert result == [[1.0, 1.0], [3.0, 2.0]]

    def test_empty_input_returns_safely(self):
        assert draw_gui_helper.remove_outdated_timestamps(5.0, [[]]) == [[]]

    def test_truly_empty_returns_safely(self):
        assert draw_gui_helper.remove_outdated_timestamps(5.0, []) == [[]]


# ── CSV round-trip ───────────────────────────────────────────────

class TestCsvReadWrite:
    def test_roundtrip(self, tmp_path):
        data = [[1.234, 1.234], [5.678, 4.444]]
        path = str(tmp_path / "ts.csv")
        draw_gui_helper.write_ts_to_csv(data, path)
        assert draw_gui_helper.read_ts_from_csv(path) == data

    def test_write_empty_marker(self, tmp_path):
        path = str(tmp_path / "empty.csv")
        draw_gui_helper.write_ts_to_csv([[]], path)
        assert draw_gui_helper.read_ts_from_csv(path) == [[]]

    def test_single_column(self, tmp_path):
        data = [[10.5], [20.3]]
        path = str(tmp_path / "single.csv")
        draw_gui_helper.write_ts_to_csv(data, path)
        assert draw_gui_helper.read_ts_from_csv(path) == data
