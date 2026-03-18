"""Tests for config.py — user config persistence."""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import load_user_config, save_user_config, DEFAULT_CONFIG


class TestUserConfig:

    def test_load_returns_defaults_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr("config.CONFIG_FILE", str(tmp_path / "missing.json"))
        result = load_user_config()
        assert result == DEFAULT_CONFIG

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        cfg_path = str(tmp_path / "test_config.json")
        monkeypatch.setattr("config.CONFIG_FILE", cfg_path)

        data = {"last_audio_path": "/some/file.mp3",
                "last_browse_folder": "/some", "volume": 80}
        save_user_config(data)
        loaded = load_user_config()
        assert loaded == data

    def test_load_merges_new_keys(self, tmp_path, monkeypatch):
        cfg_path = str(tmp_path / "partial.json")
        monkeypatch.setattr("config.CONFIG_FILE", cfg_path)

        # Save config missing "volume" key
        with open(cfg_path, "w") as f:
            json.dump({"last_audio_path": "x.mp3"}, f)

        loaded = load_user_config()
        assert loaded["last_audio_path"] == "x.mp3"
        assert "volume" in loaded  # merged from defaults

    def test_load_handles_corrupt_json(self, tmp_path, monkeypatch):
        cfg_path = str(tmp_path / "corrupt.json")
        monkeypatch.setattr("config.CONFIG_FILE", cfg_path)
        with open(cfg_path, "w") as f:
            f.write("{invalid json")

        result = load_user_config()
        assert result == DEFAULT_CONFIG
