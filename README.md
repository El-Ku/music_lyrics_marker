# Music Lyrics Marker

A desktop GUI app for marking timestamps on audio files, splitting audio by those timestamps, and generating lyric videos with Devanagari + IAST transliteration text overlaid on images.

Built with Python and FreeSimpleGUI (PySimpleGUI fork).

---

## Installation

### Requirements

- Python 3.10+
- Google Chrome (for image generation via html2image)
- FFmpeg (for video/audio processing)

### Install dependencies

```bash
pip install FreeSimpleGUI just-playback pydub numpy matplotlib html2image opencv-python moviepy mutagen
```

### Run the app

```bash
python main.py
```

---

## Overview

The app has three tabs:

1. **Mark Timestamps** — play audio and mark timestamps as lyrics play
2. **Audio Splitter** — split an audio file into segments using a timestamps CSV
3. **Lyric Images & Video** — generate lyric images and stitch them into a video with audio

---

## Tab 1: Mark Timestamps

This is the main workflow tab for syncing lyrics to audio.

### Steps

1. **Browse** for your audio file (MP3, WAV, etc.) using the file browser at the top
2. **Paste lyrics** into the Lyrics panel on the left — one line per timestamp mark
3. Click **PLAY** (or press `P`) to start playback
4. Press **Space** (or click MARK) each time a new lyric line begins
   - The current lyrics line highlights in yellow
   - Previously marked lines turn green
   - The waveform updates centered on the mark position
   - The timestamp table auto-scrolls to show the latest entry
5. Timestamps auto-save every 30 seconds and on pause

### Keyboard shortcuts

| Key | Action |
|---|---|
| `P` | Play / Pause |
| `Space` | Mark timestamp |
| `Ctrl+Z` | Undo last mark |
| `←` | Seek backward 5 seconds |
| `→` | Seek forward 5 seconds |
| `Shift+←` | Seek backward 50ms |
| `Shift+→` | Seek forward 50ms |

### Marking behavior

- **Line 1** in the lyrics box maps to **Mark 0** (row 0 in the table)
- If you seek backward and press Mark, it **inserts at the correct position** and **removes all future timestamps** from that point
- **Undo** removes the last mark, seeks playback to the previous mark, and adjusts the lyrics highlight
- Minimum interval between marks is 1 second (to prevent accidental double-taps)

### Timestamp table

- Click a row to select it — the waveform and seekbar jump to that position
- Use **Up/Down arrow keys** after clicking a row to browse through timestamps
- **+50ms / -50ms** buttons adjust the selected timestamp by 50 milliseconds
- **Delete** removes the selected timestamp row

### Load timestamps

- Check **"Load timestamps from pre_load_timestamps.csv"** to load previously saved timestamps immediately
- This lets you resume a marking session where you left off

### Lyrics panel

- Paste or type lyrics — each line corresponds to one timestamp mark
- Lyrics auto-save to `other_files/lyrics.txt` on every edit
- The highlight always counts from the current text content, so you can freely edit lines

### Output

Timestamps are saved to `other_files/timestamps.csv` with two columns:
- Column 1: Absolute time (seconds from start)
- Column 2: Duration since previous mark (seconds)

---

## Tab 2: Audio Splitter

Split an audio file into individual MP3 segments based on timestamps.

### Steps

1. Select your audio file in the top file browser
2. Switch to the **Audio Splitter** tab
3. Configure options:
   - **Ignore the first segment** — skip the intro before the first timestamp
   - **Ignore the last segment** — skip the outro after the last timestamp
   - **Skip rows** — enter comma-separated row numbers (0-based) to skip specific segments (e.g., `0,3,7`)
4. Click **START SPLITTING**

### Input

Reads timestamps from `other_files/timestamps_for_splitting.csv`.

### Output

Split MP3 files are saved to the `Split_Audios/` folder, numbered sequentially (`001.mp3`, `002.mp3`, etc.).

---

## Tab 3: Lyric Images & Video

Generate images with Devanagari text and IAST transliteration, then stitch them into a video with audio.

### Prerequisites

Prepare these files in `other_files/`:

| File | Description |
|---|---|
| `devanagari.txt` | One line of Devanagari text per verse/image |
| `iast.txt` | One line of IAST transliteration per verse (same line count) |
| `heading.txt` | One line heading per verse — e.g., "Verse 1.1.1" (same line count) |
| `blank.jpg` | Background image (1920x1080 recommended) |
| `lyrics_durations_for_vid_gen.csv` | Start times for each image (auto-generated — see below) |

All three text files **must have the same number of lines**.

### Step 1: Generate durations CSV

Click **"Generate durations CSV from timestamps.csv"** — this copies the start times from your marked timestamps into `lyrics_durations_for_vid_gen.csv`.

### Step 2: Generate images

Click **START** under Image Generation:
- Creates one 1920x1080 PNG per line in the `lyric_images/` folder
- Uses Chrome headless (html2image) for proper Devanagari rendering with the Noto Sans Devanagari font
- Images are numbered `1.png`, `2.png`, etc.

### Step 3: Generate video

1. Make sure your MP3 is selected in the file browser
2. Click **START** under Video Generation
3. The app:
   - Reads `lyrics_durations_for_vid_gen.csv` for timing
   - Stitches images from `lyric_images/` into an AVI video
   - Muxes the audio to produce `final_video.mp4`

---

## Project structure

```
music_lyrics_marker/
├── main.py                  # Entry point
├── config.py                # Constants, file paths, user config
├── draw_gui.py              # GUI rendering, updates, keyboard bindings
├── draw_gui_helper.py       # Utilities: time formatting, CSV I/O, waveform
├── gui_control_logic.py     # Event handler for all GUI events
├── gui_layouts.py           # GUI layout definitions (all tabs)
├── play_audio.py            # Audio playback wrapper (just_playback + speed)
├── music_splitter_helper.py # Audio splitting logic
├── img_generator.py         # Lyric image generation (html2image)
├── vid_generator.py         # Video generation (OpenCV + moviepy)
├── logger_setup.py          # Logging to GUI log panel
├── other_files/
│   ├── blank.jpg            # Background image for lyric images
│   ├── no_lyrics_om.png     # Om image (long intro, no lyrics)
│   ├── only_om.png          # Om image (short intro)
│   ├── devanagari.txt       # Devanagari verse text
│   ├── iast.txt             # IAST transliteration text
│   ├── heading.txt          # Verse headings
│   ├── lyrics.txt           # Pasted lyrics (auto-saved from GUI)
│   ├── timestamps.csv       # Marked timestamps (auto-saved)
│   ├── pre_load_timestamps.csv        # Timestamps to pre-load
│   ├── timestamps_for_splitting.csv   # Timestamps for audio splitting
│   ├── lyrics_durations_for_vid_gen.csv # Durations for video generation
│   └── static/              # Fonts (Noto Sans Devanagari)
├── lyric_images/            # Generated lyric PNGs (created at runtime)
├── Split_Audios/            # Split MP3 segments (created at runtime)
└── app_config.json          # Persisted user preferences (auto-created)
```

---

## Typical end-to-end workflow

1. **Mark timestamps** — Tab 1: load audio, paste lyrics, press Play, tap Space for each line
2. **Copy timestamps** — the CSV is auto-saved; copy to `timestamps_for_splitting.csv` if splitting
3. **Prepare text files** — ensure `devanagari.txt`, `iast.txt`, `heading.txt` have equal line counts
4. **Generate durations CSV** — Tab 3: click the blue button
5. **Generate images** — Tab 3: click START under Image Generation
6. **Generate video** — Tab 3: click START under Video Generation
7. **Split audio** (optional) — Tab 2: configure options, click START SPLITTING

---

## Configuration

The app remembers:
- Last opened audio file and folder
- Volume level

These are saved to `app_config.json` automatically.

---

## Notes

- The app uses `just_playback` for audio — speed changes alter both speed and pitch (frame-rate manipulation)
- Image generation requires Google Chrome installed (used headlessly via html2image)
- Video generation uses OpenCV (XVID codec) for frames and moviepy for final audio muxing
- The waveform only updates when you mark a timestamp or click a table row (not during continuous playback)