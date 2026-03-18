"""GUI rendering, updates, and keyboard bindings."""

import os
try:
    import PySimpleGUI as pg
except ImportError:
    import FreeSimpleGUI as pg

import draw_gui_helper
from gui_layouts import GuiLayout
from config import APP_TITLE, TIMESTAMPS_CSV, LYRICS_FILE


class DrawGui:

    def __init__(self, initial_folder="", default_audio_path=""):
        self.title = APP_TITLE
        self.window = None
        self.gui_layout = GuiLayout(
            initial_folder=initial_folder,
            default_audio_path=default_audio_path,
        )
        self.is_playing = False
        self._last_lyrics_text = ""  # track changes for auto-save

    # ── Window creation ─────────────────────────────────────────

    def draw_gui(self):
        """Create and return the main PySimpleGUI window."""
        layout = self.gui_layout.setup_layout()
        self.window = pg.Window(
            self.title, layout, finalize=True,
            resizable=True, size=(1400, 900),
        )

        # Keyboard shortcuts
        self.window.bind("<p>", "PLAY-KEY")
        self.window.bind("<space>", "MARK-KEY")
        self.window.bind("<Control-z>", "UNDO-KEY")
        self.window.bind("<Left>", "SEEK_LEFT-KEY")
        self.window.bind("<Right>", "SEEK_RIGHT-KEY")
        self.window.bind("<Shift-Left>", "SEEK_LEFT_FINE-KEY")
        self.window.bind("<Shift-Right>", "SEEK_RIGHT_FINE-KEY")

        # Load lyrics from file
        self._load_lyrics()

        return self.window

    def set_controller_object(self, controller):
        self.controller = controller

    def set_audio_player(self, audio_player):
        self.audio_player = audio_player

    # ── Window title (Feature 12) ──────────────────────────────

    def update_window_title(self, file_path):
        """Show the loaded filename in the window title bar."""
        name = os.path.basename(file_path) if file_path else ""
        title = f"{name} \u2014 {self.title}" if name else self.title
        self.window.set_title(title)

    # ── Button state management (Feature 11) ───────────────────

    _SEEK_KEYS = [
        "-BACK_50_MSECS-", "-BACK_5_SECS-", "-BACK_1_MIN-", "-BACK_10_MIN-",
        "-FORW_50_MSECS-", "-FORW_5_SECS-", "-FORW_1_MIN-", "-FORW_10_MIN-",
    ]

    def set_pre_load_state(self):
        """Disable controls that require a loaded audio file."""
        for key in self._SEEK_KEYS:
            self.window[key].update(disabled=True)
        self.window["-MARK-"].update(disabled=True)
        self.window["-UNDO-"].update(disabled=True)
        self.window["-RESTART-"].update(disabled=True)
        self.window["-SEEKBAR-"].update(disabled=True)
        self.window["-SPEED-"].update(disabled=True)
        self.window["-TS_PLUS50-"].update(disabled=True)
        self.window["-TS_MINUS50-"].update(disabled=True)
        self.window["-TS_DELETE-"].update(disabled=True)
        # Tab 2
        self.window["-STOP_SPLIT-"].update(disabled=True)
        # Tab 3
        self.window["-STOP_IMG_GEN-"].update(disabled=True)
        self.window["-STOP_VID_GEN-"].update(disabled=True)

    def set_playing_state(self):
        """Enable all controls while audio is playing."""
        self.is_playing = True
        for key in self._SEEK_KEYS:
            self.window[key].update(disabled=False)
        self.window["-MARK-"].update(disabled=False)
        self.window["-UNDO-"].update(disabled=False)
        self.window["-RESTART-"].update(disabled=False)
        self.window["-SEEKBAR-"].update(disabled=False)
        self.window["-SPEED-"].update(disabled=False)
        self.window["-TS_PLUS50-"].update(disabled=False)
        self.window["-TS_MINUS50-"].update(disabled=False)
        self.window["-TS_DELETE-"].update(disabled=False)
        self.window["-PLAY-"].update("PAUSE [P]")

    def set_paused_state(self):
        """Mark disabled, seek still enabled."""
        self.is_playing = False
        self.window["-MARK-"].update(disabled=True)
        self.window["-PLAY-"].update("PLAY [P]")

    # ── Play / Pause toggle ────────────────────────────────────

    def toggle_play_btn(self):
        """Toggle between play and pause states."""
        if not self.is_playing:
            self.audio_player.playback.resume()
            self.set_playing_state()
            print("Play audio button was pressed")
        else:
            self.audio_player.playback.pause()
            self.set_paused_state()
            draw_gui_helper.write_ts_to_csv(
                self.controller.marked_ts_array, TIMESTAMPS_CSV)
            print("Pause audio button was pressed")

    # ── Seekbar (Feature 1) ────────────────────────────────────

    def set_seekbar_range(self, duration):
        self.window["-SEEKBAR-"].update(range=(0, duration))

    def update_seekbar(self, position):
        self.window["-SEEKBAR-"].update(value=position)

    # ── Time displays ──────────────────────────────────────────

    def update_total_audio_duration(self, duration):
        self.window["-TOTAL_TIME-"].update(
            draw_gui_helper.sec2_timestring(duration))

    def update_time_boxes(self):
        curr_secs = self.audio_player.playback.curr_pos
        total = self.controller.total_audio_duration
        self.window["-CURR_TIME-"].update(
            draw_gui_helper.sec2_timestring(curr_secs))
        self.window["-REM_TIME-"].update(
            draw_gui_helper.sec2_timestring(max(0, total - curr_secs)))
        self.update_seekbar(curr_secs)

    # ── Timestamp table ────────────────────────────────────────

    def update_table(self, marked_ts_array, select_row=None):
        """Update the timestamp table. If select_row is given, scroll to and
        highlight that row; otherwise scroll to the bottom."""
        formatted = draw_gui_helper.format_floats_for_table(marked_ts_array)
        self.window["-TABLE-"].update(values=formatted)
        try:
            tree = self.window["-TABLE-"].Widget
            children = tree.get_children()
            if not children:
                return
            if select_row is not None and 0 <= select_row < len(children):
                tree.selection_set(children[select_row])
                tree.see(children[select_row])
            else:
                tree.see(children[-1])
        except Exception:
            pass

    def update_num_lines_marked(self, marked_ts_array):
        """Remove timestamps after current playback position, update UI."""
        curr_time = self.audio_player.playback.curr_pos
        if marked_ts_array == [[]]:
            self.update_table([[]])
            self.window["-NUM_LINES_MARKED-"].update(0)
            self.clear_lyrics_highlight()
            return 0, [[]]
        marked_ts_array = draw_gui_helper.remove_outdated_timestamps(
            curr_time, marked_ts_array)
        self.update_table(marked_ts_array)
        if marked_ts_array == [[]]:
            self.window["-NUM_LINES_MARKED-"].update(0)
            self.clear_lyrics_highlight()
            return 0, marked_ts_array
        count = len(marked_ts_array)
        self.window["-NUM_LINES_MARKED-"].update(count)
        self.highlight_lyrics_line(count - 1)
        return count, marked_ts_array

    # ── Lyrics panel highlighting ────────────────────────────

    def _get_lyrics_lines(self):
        """Return the lyrics text split into lines."""
        text = self.window["-LYRICS_BOX-"].get()
        if not text or not text.strip():
            return []
        return text.splitlines()

    def highlight_lyrics_line(self, line_number):
        """Highlight the given line (0-based) in the lyrics box.
        Previously marked lines get a subtle 'done' color.
        The current line gets a strong highlight.
        Future lines are unstyled."""
        tk_widget = self.window["-LYRICS_BOX-"].Widget
        lines = self._get_lyrics_lines()
        if not lines:
            return

        # Remove old tags
        tk_widget.tag_remove("done", "1.0", "end")
        tk_widget.tag_remove("current", "1.0", "end")
        tk_widget.tag_remove("upcoming", "1.0", "end")

        # Configure tag styles
        tk_widget.tag_configure("done",
                                background="#388E3C", foreground="white")
        tk_widget.tag_configure("current",
                                background="#FFD600", foreground="black",
                                font=("Arial", 14, "bold"))
        tk_widget.tag_configure("upcoming",
                                background="", foreground="")

        # Apply tags
        for i in range(len(lines)):
            start = f"{i + 1}.0"
            end = f"{i + 1}.end"
            if i < line_number:
                tk_widget.tag_add("done", start, end)
            elif i == line_number:
                tk_widget.tag_add("current", start, end)

        # Scroll to make the current line visible
        if line_number < len(lines):
            tk_widget.see(f"{line_number + 1}.0")

    def clear_lyrics_highlight(self):
        """Remove all highlights from the lyrics box."""
        tk_widget = self.window["-LYRICS_BOX-"].Widget
        tk_widget.tag_remove("done", "1.0", "end")
        tk_widget.tag_remove("current", "1.0", "end")

    # ── Lyrics file persistence ───────────────────────────────

    def _load_lyrics(self):
        """Load lyrics from file into the lyrics box on startup."""
        if os.path.exists(LYRICS_FILE):
            try:
                with open(LYRICS_FILE, "r", encoding="utf-8") as f:
                    text = f.read()
                self.window["-LYRICS_BOX-"].update(text)
                self._last_lyrics_text = text
            except IOError:
                pass

    def _save_lyrics(self):
        """Save lyrics box content to file."""
        text = self.window["-LYRICS_BOX-"].get()
        with open(LYRICS_FILE, "w", encoding="utf-8") as f:
            f.write(text)
        self._last_lyrics_text = text

    def check_lyrics_changed(self):
        """If lyrics text changed since last save, save immediately."""
        text = self.window["-LYRICS_BOX-"].get()
        if text != self._last_lyrics_text:
            self._save_lyrics()

    # ── Waveform ───────────────────────────────────────────────

    def update_waveform_at(self, position):
        """Regenerate and display the waveform centered on *position* (secs).
        Only called when a mark is placed — shows the mark in the center."""
        if self.controller.raw_audio_data is None:
            return
        try:
            img = draw_gui_helper.generate_waveform_image(
                self.controller.raw_audio_data,
                self.controller.frame_rate,
                position,
            )
            self.window["-AUDIO_WAVEFORM-"].update(data=img)
        except Exception:
            pass

    # ── Tab 2: Audio Splitter UI updates ───────────────────────

    def update_table_music_splitter(self, timestamps):
        rows = [[f"{ts:.3f}"] for ts in timestamps]
        self.window["-TABLE2-"].update(values=rows)

    def update_time_boxes_music_splitter(self, max_i, i, elapsed_secs):
        self.window["-TOTAL_NUM_FILES-"].update(max_i)
        self.window["-CURR_FILE_NUM-"].update(i + 1)
        self.window["-REM_FILES-"].update(max_i - i - 1)
        self.window["-ELAPSED_TIME-"].update(
            draw_gui_helper.sec2_timestring(elapsed_secs))

    def update_split_progress(self, current, total):
        self.window["-SPLIT_PROGRESS-"].update(current, max=total)

    # ── Tab 3: Image / Video gen UI updates ────────────────────

    def update_time_boxes_img_vid_gen(self, max_i, i, elapsed_secs):
        self.window["-TOTAL_NUM_IMAGES-"].update(max_i)
        self.window["-CURR_IMAGE_NUM-"].update(i + 1)
        self.window["-REM_IMAGES-"].update(max_i - i - 1)
        self.window["-ELAPSED_TIME_IMG-"].update(
            draw_gui_helper.sec2_timestring(elapsed_secs))

    def update_img_gen_progress(self, current, total):
        self.window["-IMG_GEN_PROGRESS-"].update(current, max=total)

    def update_vid_gen_progress(self, current, total):
        self.window["-VID_GEN_PROGRESS-"].update(current, max=total)

    # ── Window close ───────────────────────────────────────────

    def close_window(self, write_csv=False):
        if write_csv:
            draw_gui_helper.write_ts_to_csv(
                self.controller.marked_ts_array, TIMESTAMPS_CSV)
            print("Timestamps were saved to a csv file")
        print("Saving the contents of the log textbox to a text file")
        from config import LOG_FILE
        log_content = self.window["-LOGGING_BOX-"].get()
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(log_content)
        self.audio_player.playback.stop()
        self.window.close()
