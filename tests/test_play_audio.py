"""Tests for play_audio.py — AudioPlay class."""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAudioPlay:

    @patch("play_audio.Playback")
    def test_init_creates_playback(self, mock_cls):
        from play_audio import AudioPlay
        player = AudioPlay()
        mock_cls.assert_called_once()
        assert player.current_speed == 1.0

    @patch("play_audio.Playback")
    def test_update_playback_file(self, mock_cls):
        from play_audio import AudioPlay
        player = AudioPlay()
        player.update_playback_file("test.mp3")
        player.playback.load_file.assert_called_once_with("test.mp3")
        assert player.original_file_path == "test.mp3"
        assert player.current_speed == 1.0

    @patch("play_audio.Playback")
    def test_move_curr_position_forward(self, mock_cls):
        from play_audio import AudioPlay
        player = AudioPlay()
        player.playback.curr_pos = 10.0
        player.move_curr_position(5.0)
        player.playback.seek.assert_called_once_with(15.0)

    @patch("play_audio.Playback")
    def test_move_curr_position_clamped_to_zero(self, mock_cls):
        from play_audio import AudioPlay
        player = AudioPlay()
        player.playback.curr_pos = 2.0
        player.move_curr_position(-5.0)
        player.playback.seek.assert_called_once_with(0)

    @patch("play_audio.Playback")
    def test_seek_absolute(self, mock_cls):
        from play_audio import AudioPlay
        player = AudioPlay()
        player.seek_absolute(42.5)
        player.playback.seek.assert_called_once_with(42.5)

    @patch("play_audio.Playback")
    def test_seek_absolute_clamped(self, mock_cls):
        from play_audio import AudioPlay
        player = AudioPlay()
        player.seek_absolute(-10)
        player.playback.seek.assert_called_once_with(0)

    @patch("play_audio.Playback")
    def test_set_volume(self, mock_cls):
        from play_audio import AudioPlay
        player = AudioPlay()
        player.set_volume(0.75)
        player.playback.set_volume.assert_called_once_with(0.75)
