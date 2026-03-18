"""Application constants and user configuration persistence."""

import json
import os

# --- Application ---
APP_TITLE = "Music Lyrics Marker"
THEME = "DarkAmber"
BIG_FONT = ("Arial", 16)
SMALL_FONT = ("Arial", 12)
INFO_TEXT_FONT = ("Arial", 11)

# --- Event Loop ---
EVENT_LOOP_TIMEOUT_MS = 200

# --- Timestamp Marking ---
MIN_MARK_INTERVAL_SECS = 1.0
AUTOSAVE_INTERVAL_SECS = 30.0

# --- File Paths ---
TIMESTAMPS_CSV = os.path.join("other_files", "timestamps.csv")
PRELOAD_TIMESTAMPS_CSV = os.path.join("other_files", "pre_load_timestamps.csv")
TIMESTAMPS_FOR_SPLITTING_CSV = os.path.join("other_files", "timestamps_for_splitting.csv")
LYRICS_DURATIONS_CSV = os.path.join("other_files", "lyrics_durations_for_vid_gen.csv")
DEVANAGARI_TXT = os.path.join("other_files", "devanagari.txt")
IAST_TXT = os.path.join("other_files", "iast.txt")
HEADING_TXT = os.path.join("other_files", "heading.txt")
BLANK_IMG = os.path.join("other_files", "blank.jpg")
NO_LYRICS_OM_IMG = os.path.join("other_files", "no_lyrics_om.png")
ONLY_OM_IMG = os.path.join("other_files", "only_om.png")
LYRIC_IMAGES_DIR = "lyric_images"
SPLIT_AUDIOS_DIR = "Split_Audios"
LOG_FILE = "log.txt"
LYRICS_FILE = os.path.join("other_files", "lyrics.txt")

# --- User Config Persistence ---
CONFIG_FILE = "app_config.json"

DEFAULT_CONFIG = {
    "last_audio_path": "",
    "last_browse_folder": "",
    "volume": 100,
}


def load_user_config():
    """Load user preferences from disk, returning defaults if missing."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
            # Merge with defaults so new keys are always present
            config = DEFAULT_CONFIG.copy()
            config.update(saved)
            return config
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_user_config(config):
    """Persist user preferences to disk."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
