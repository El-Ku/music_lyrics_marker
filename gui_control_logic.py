"""Central event handler — decides what happens for every GUI event."""

import time
try:
    import PySimpleGUI as pg
except ImportError:
    import FreeSimpleGUI as pg
from concurrent.futures import ThreadPoolExecutor

from play_audio import AudioPlay
from music_splitter_helper import MusicSplitterHelper
from img_generator import ImgGenerator
from vid_generator import VidGenerator
import logger_setup
import draw_gui_helper
from config import (
    MIN_MARK_INTERVAL_SECS,
    AUTOSAVE_INTERVAL_SECS,
    TIMESTAMPS_CSV,
    PRELOAD_TIMESTAMPS_CSV,
    TIMESTAMPS_FOR_SPLITTING_CSV,
    save_user_config,
)


class ControlGui:

    def __init__(self, draw_gui_object, user_config):
        self.gui = draw_gui_object
        self.window = self.gui.window
        self.user_config = user_config

        # Audio
        self.audio_player = AudioPlay()
        self.gui.set_audio_player(self.audio_player)
        self.audio_loaded = False
        self.total_audio_duration = 0
        self.raw_audio_data = None
        self.frame_rate = 0
        self.current_file = ""

        # Timestamp marking
        self.marked_ts_array = [[]]
        self.num_lines_marked = 0
        self.last_marked_ts = 0

        # Threading
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None

        # Helpers
        self.music_splitter = MusicSplitterHelper(draw_gui_object)
        self.img_generator = ImgGenerator(draw_gui_object)
        self.vid_generator = VidGenerator()

        # Table row browsing
        self._selected_table_row = -1

        # Auto-save (Feature 7)
        self._last_autosave_time = time.time()

        # Logging
        logger_setup.setup_logger(self.window, "-LOGGING_BOX-")

        # Bind Up/Down on the timestamp table widget for row browsing
        tree = self.window["-TABLE-"].Widget
        tree.bind("<Up>", lambda e: self._table_arrow(-1))
        tree.bind("<Down>", lambda e: self._table_arrow(1))

    # ── Helpers ─────────────────────────────────────────────────

    def _recalculate_durations(self):
        """Recompute the duration column for all entries."""
        if self.marked_ts_array == [[]] or not self.marked_ts_array:
            return
        self.marked_ts_array[0][1] = self.marked_ts_array[0][0]
        for i in range(1, len(self.marked_ts_array)):
            self.marked_ts_array[i][1] = (
                self.marked_ts_array[i][0] - self.marked_ts_array[i - 1][0]
            )

    def _get_audio_file(self):
        """Return the currently selected audio file path."""
        return self.window["-AUDIO_FILE_NAME-"].get()

    def _save_user_config(self):
        """Persist user preferences."""
        import os
        audio_path = self._get_audio_file()
        self.user_config["last_audio_path"] = audio_path
        self.user_config["last_browse_folder"] = (
            os.path.dirname(audio_path) if audio_path else "")
        self.user_config["volume"] = int(
            self.window["-VOL_CONTROL-"].TKIntVar.get())
        save_user_config(self.user_config)

    def _do_close(self):
        """Unified close: save, cleanup, close window."""
        tab = self.window["-TAB_GROUP-"].get()
        write_csv = (tab == "-TAB1-" and self.num_lines_marked > 0)
        self._save_user_config()
        self.gui.close_window(write_csv=write_csv)
        if self.future:
            self.future.cancel()

    # ── Load / Reset Audio ──────────────────────────────────────

    def _load_audio(self):
        """Load the audio file for the first time or after file change."""
        audio_file = self._get_audio_file()
        if not audio_file:
            return
        self.raw_audio_data, self.frame_rate = (
            draw_gui_helper.get_raw_audio_data(audio_file))
        self.current_file = audio_file
        self.audio_player.update_playback_file(audio_file)
        self.total_audio_duration = self.audio_player.playback.duration
        self.gui.update_total_audio_duration(self.total_audio_duration)
        self.gui.set_seekbar_range(self.total_audio_duration)
        self.gui.update_window_title(audio_file)
        self.audio_player.playback.play()
        self.audio_loaded = True

        # If timestamps were already loaded via checkbox, seek to last mark
        if self.num_lines_marked > 0:
            self.audio_player.seek_absolute(self.marked_ts_array[-1][0])
            self.gui.update_time_boxes()

    def _reset_playback(self):
        """Reset state when file changes or RESTART is pressed."""
        self.audio_player.playback.stop()
        self.audio_loaded = False
        self.num_lines_marked = 0
        self.marked_ts_array = [[]]
        self.last_marked_ts = 0
        self.gui.update_num_lines_marked(self.marked_ts_array)
        self.gui.update_time_boxes()
        self.gui.clear_lyrics_highlight()

    # ── Main event dispatcher ───────────────────────────────────

    def check_for_gui_events(self, event, values):
        """Process one GUI event. Returns False to exit the main loop."""

        # Logging events (from background threads)
        if event == "-LOGGING_BOX-":
            self.window["-LOGGING_BOX-"].update(
                values[event], append=True)

        # ── Global: Close (Feature 10) ──────────────────────────
        if event is None or event == "-CLOSE_BTN-":
            self._do_close()
            return False

        active_tab = values.get("-TAB_GROUP-")

        # ── Tab 1: Mark Timestamps ──────────────────────────────
        if active_tab == "-TAB1-":
            return self._handle_tab1(event, values)

        # ── Tab 2: Audio Splitter ───────────────────────────────
        if active_tab == "-TAB2-":
            return self._handle_tab2(event, values)

        # ── Tab 3: Create Lyric Images and Videos ───────────────
        if active_tab == "-TAB3-":
            return self._handle_tab3(event, values)

        return True

    # ── Tab 1 handler ───────────────────────────────────────────

    def _handle_tab1(self, event, values):
        # Detect file change
        current_path = self._get_audio_file()
        if current_path != self.current_file and self.audio_loaded:
            self._reset_playback()
        if event == "-RESTART-" and self.audio_loaded:
            self._reset_playback()

        # Play / Pause
        if event in ("-PLAY-", "PLAY-KEY") or (
                not self.audio_loaded and event == "-RESTART-"):
            if not self.audio_loaded:
                self._load_audio()
                self.gui.set_playing_state()
            else:
                self.gui.toggle_play_btn()

        # Seekbar (Feature 1)
        elif event == "-SEEKBAR-":
            slider_val = values["-SEEKBAR-"]
            curr = self.audio_player.playback.curr_pos
            if abs(slider_val - curr) > 0.5:
                self.audio_player.seek_absolute(slider_val)
                self.num_lines_marked, self.marked_ts_array = (
                    self.gui.update_num_lines_marked(self.marked_ts_array))

        # Speed control (Feature 3)
        elif event == "-SPEED-":
            speed_str = values["-SPEED-"]
            speed_factor = float(speed_str.replace("x", ""))
            curr_pos = self.audio_player.playback.curr_pos
            was_paused = not self.gui.is_playing
            self.audio_player.set_speed(speed_factor, curr_pos)
            if was_paused:
                self.audio_player.playback.pause()
            print(f"Playback speed changed to {speed_str}")

        # Undo last mark (Feature 2)
        elif event in ("-UNDO-", "UNDO-KEY"):
            if self.num_lines_marked > 0:
                self.marked_ts_array.pop()
                self.num_lines_marked -= 1
                if self.num_lines_marked == 0:
                    self.marked_ts_array = [[]]
                    self.gui.clear_lyrics_highlight()
                    # Seek back to the start
                    self.audio_player.seek_absolute(0)
                else:
                    self.gui.highlight_lyrics_line(self.num_lines_marked - 1)
                    # Seek to the last remaining mark's position
                    seek_pos = self.marked_ts_array[-1][0]
                    self.audio_player.seek_absolute(seek_pos)
                self.gui.update_table(self.marked_ts_array)
                self.gui.update_time_boxes()
                self.window["-NUM_LINES_MARKED-"].update(
                    self.num_lines_marked)
                print(f"Undid last mark — seeked to "
                      f"{self.audio_player.playback.curr_pos:.2f}s")

        # Mark timestamp
        elif event in ("-MARK-", "MARK-KEY"):
            if time.time() - self.last_marked_ts > MIN_MARK_INTERVAL_SECS:
                curr = self.audio_player.playback.curr_pos

                # Find the correct insertion point (chronological order)
                # and remove all future timestamps from that point onward
                if self.marked_ts_array == [[]]:
                    insert_idx = 0
                    self.marked_ts_array[0] = [curr, curr]
                else:
                    # Find where this timestamp belongs
                    insert_idx = len(self.marked_ts_array)
                    for i, entry in enumerate(self.marked_ts_array):
                        if entry[0] >= curr:
                            insert_idx = i
                            break

                    # Remove all timestamps from insert_idx onward
                    self.marked_ts_array = self.marked_ts_array[:insert_idx]

                    # Calculate duration from previous mark
                    if insert_idx == 0:
                        self.marked_ts_array = [[curr, curr]]
                    else:
                        prev = self.marked_ts_array[insert_idx - 1][0]
                        self.marked_ts_array.append([curr, curr - prev])

                self.num_lines_marked = len(self.marked_ts_array)
                self.gui.update_table(self.marked_ts_array)
                self.last_marked_ts = time.time()
                self.window["-NUM_LINES_MARKED-"].update(
                    self.num_lines_marked)
                # Line 1 = Mark 0, so current highlight = num_lines_marked - 1
                self.gui.highlight_lyrics_line(self.num_lines_marked - 1)
                self.gui.update_waveform_at(curr)
            else:
                print("Don't click Mark too quickly! "
                      "The line cannot be < 1 second long")

        # Seek backward
        elif event == "-BACK_50_MSECS-" or event == "SEEK_LEFT_FINE-KEY":
            self.audio_player.move_curr_position(-0.05)
            self.num_lines_marked, self.marked_ts_array = (
                self.gui.update_num_lines_marked(self.marked_ts_array))
        elif event == "-BACK_5_SECS-" or event == "SEEK_LEFT-KEY":
            self.audio_player.move_curr_position(-5)
            self.num_lines_marked, self.marked_ts_array = (
                self.gui.update_num_lines_marked(self.marked_ts_array))
        elif event == "-BACK_1_MIN-":
            self.audio_player.move_curr_position(-60)
            self.num_lines_marked, self.marked_ts_array = (
                self.gui.update_num_lines_marked(self.marked_ts_array))
        elif event == "-BACK_10_MIN-":
            self.audio_player.move_curr_position(-600)
            self.num_lines_marked, self.marked_ts_array = (
                self.gui.update_num_lines_marked(self.marked_ts_array))

        # Seek forward
        elif event == "-FORW_50_MSECS-" or event == "SEEK_RIGHT_FINE-KEY":
            self.audio_player.move_curr_position(0.05)
        elif event == "-FORW_5_SECS-" or event == "SEEK_RIGHT-KEY":
            self.audio_player.move_curr_position(5)
        elif event == "-FORW_1_MIN-":
            self.audio_player.move_curr_position(60)
        elif event == "-FORW_10_MIN-":
            self.audio_player.move_curr_position(600)

        # Volume
        elif event == "-VOL_CONTROL-":
            self.audio_player.set_volume(values["-VOL_CONTROL-"] / 100)

        # Load timestamps checkbox — load immediately when checked
        elif event == "-LOAD_TS_CB-":
            if values["-LOAD_TS_CB-"]:
                try:
                    self.marked_ts_array = draw_gui_helper.read_ts_from_csv(
                        PRELOAD_TIMESTAMPS_CSV)
                    self.num_lines_marked = len(self.marked_ts_array)
                    self.gui.update_table(self.marked_ts_array)
                    self.window["-NUM_LINES_MARKED-"].update(
                        self.num_lines_marked)
                    self.gui.highlight_lyrics_line(self.num_lines_marked - 1)
                    if self.audio_loaded:
                        self.audio_player.seek_absolute(
                            self.marked_ts_array[-1][0])
                        self.gui.update_time_boxes()
                    print(f"Loaded {self.num_lines_marked} timestamps")
                except Exception as e:
                    print(f"Failed to load timestamps: {e}")

        # Editable table
        elif isinstance(event, tuple) and event[0] == "-TABLE-":
            self._handle_table_click(event)
        elif event == "-TS_PLUS50-":
            self._handle_ts_edit("+50")
        elif event == "-TS_MINUS50-":
            self._handle_ts_edit("-50")
        elif event == "-TS_DELETE-":
            self._handle_ts_edit("delete")

        # Update time displays if playing
        if self.audio_loaded and self.gui.is_playing:
            self.gui.update_time_boxes()

        # Auto-save timestamps (Feature 7)
        self._maybe_autosave()

        # Auto-save lyrics on any change
        self.gui.check_lyrics_changed()

        return True

    # ── Table editing (Feature 5) ───────────────────────────────

    def _table_arrow(self, direction):
        """Move table selection up/down and show waveform at that row."""
        if self.marked_ts_array == [[]] or not self.marked_ts_array:
            return
        new_row = self._selected_table_row + direction
        new_row = max(0, min(new_row, len(self.marked_ts_array) - 1))
        self._selected_table_row = new_row

        ts_val = self.marked_ts_array[new_row][0]
        self.gui.update_waveform_at(ts_val)
        # Seek playback and update position bar
        if self.audio_loaded:
            self.audio_player.seek_absolute(ts_val)
            self.gui.update_time_boxes()

        # Highlight the row in the table
        tree = self.window["-TABLE-"].Widget
        children = tree.get_children()
        if children and new_row < len(children):
            tree.selection_set(children[new_row])
            tree.see(children[new_row])

    def _handle_table_click(self, event):
        """Select a row and show its waveform. No popup."""
        row_clicked = event[2][0]
        if row_clicked is None or row_clicked < 0:
            return
        if self.marked_ts_array == [[]] or not self.marked_ts_array:
            return
        if row_clicked >= len(self.marked_ts_array):
            return

        self._selected_table_row = row_clicked
        ts_val = self.marked_ts_array[row_clicked][0]
        self.gui.update_waveform_at(ts_val)
        # Seek playback and update position bar
        if self.audio_loaded:
            self.audio_player.seek_absolute(ts_val)
            self.gui.update_time_boxes()

    def _handle_ts_edit(self, action):
        """Apply +50ms, -50ms, or delete to the selected table row."""
        row = self._selected_table_row
        if row < 0 or self.marked_ts_array == [[]] or not self.marked_ts_array:
            print("No timestamp row selected")
            return
        if row >= len(self.marked_ts_array):
            return

        if action == "+50":
            self.marked_ts_array[row][0] += 0.050
            self._recalculate_durations()
        elif action == "-50":
            self.marked_ts_array[row][0] -= 0.050
            self._recalculate_durations()
        elif action == "delete":
            self.marked_ts_array.pop(row)
            self.num_lines_marked -= 1
            if not self.marked_ts_array:
                self.marked_ts_array = [[]]
                self.num_lines_marked = 0
            else:
                self._recalculate_durations()
            # Adjust selected row
            if self._selected_table_row >= len(self.marked_ts_array):
                self._selected_table_row = max(0, len(self.marked_ts_array) - 1)

        r = self._selected_table_row
        self.gui.update_table(self.marked_ts_array, select_row=r)
        self.window["-NUM_LINES_MARKED-"].update(self.num_lines_marked)
        if self.num_lines_marked > 0:
            self.gui.highlight_lyrics_line(self.num_lines_marked - 1)
            # Update waveform to show the edited position
            r = min(r, len(self.marked_ts_array) - 1)
            if self.marked_ts_array != [[]]:
                self.gui.update_waveform_at(self.marked_ts_array[r][0])
        else:
            self.gui.clear_lyrics_highlight()

    # ── Auto-save (Feature 7) ──────────────────────────────────

    def _maybe_autosave(self):
        if (self.num_lines_marked > 0 and
                time.time() - self._last_autosave_time >= AUTOSAVE_INTERVAL_SECS):
            draw_gui_helper.write_ts_to_csv(
                self.marked_ts_array, TIMESTAMPS_CSV)
            self._last_autosave_time = time.time()
            print("Auto-saved timestamps")

    # ── Tab 2 handler ───────────────────────────────────────────

    def _handle_tab2(self, event, values):
        self.window["-AUDIO_WAVEFORM-"].set_size((0, 0))

        if event == "-START_SPLIT-":
            timestamps = draw_gui_helper.read_ts_from_csv(
                TIMESTAMPS_FOR_SPLITTING_CSV)
            ignore_first = self.window["-IGNORE_FIRST_CB-"].get()
            ignore_last = self.window["-IGNORE_LAST_CB-"].get()
            file_name = self._get_audio_file()
            # Parse skip rows
            skip_rows = set()
            skip_text = self.window["-SKIP_ROWS-"].get().strip()
            if skip_text:
                try:
                    skip_rows = {int(x.strip()) for x in skip_text.split(",")}
                except ValueError:
                    print("Invalid skip rows — use comma-separated numbers like 0,3,7")
                    return True
            self.window["-START_SPLIT-"].update(disabled=True)
            self.window["-STOP_SPLIT-"].update(disabled=False)
            print("A thread has started to split the audio file")
            self.future = self.executor.submit(
                self.music_splitter.split_audios,
                file_name, timestamps, ignore_first, ignore_last, skip_rows)
        elif event == "-STOP_SPLIT-":
            self.music_splitter.stop_audio_splitting()
            self.window["-START_SPLIT-"].update(disabled=False)
            self.window["-STOP_SPLIT-"].update(disabled=True)

        return True

    # ── Tab 3 handler ───────────────────────────────────────────

    def _handle_tab3(self, event, values):
        self.window["-AUDIO_WAVEFORM-"].set_size((0, 0))

        # Check if previous future had an error
        if self.future and self.future.done():
            try:
                self.future.result()  # raises if the task crashed
            except Exception as e:
                print(f"Previous task error: {e}")
                import traceback
                traceback.print_exc()

        if event == "-START_IMG_GEN-":
            if self.future is None or self.future.done():
                self.window["-START_IMG_GEN-"].update(disabled=True)
                self.window["-STOP_IMG_GEN-"].update(disabled=False)
                self.future = self.executor.submit(
                    self.img_generator.generate_images)
        elif event == "-STOP_IMG_GEN-":
            self.img_generator.stop_img_creation()
            self.window["-START_IMG_GEN-"].update(disabled=False)
            self.window["-STOP_IMG_GEN-"].update(disabled=True)
        elif event == "-START_VID_GEN-":
            if self.future is None or self.future.done():
                file_name = self._get_audio_file()
                self.window["-START_VID_GEN-"].update(disabled=True)
                self.window["-STOP_VID_GEN-"].update(disabled=False)
                self.future = self.executor.submit(
                    self.vid_generator.generate_video, file_name)
        elif event == "-STOP_VID_GEN-":
            self.vid_generator.stop_vid_creation()
            self.window["-START_VID_GEN-"].update(disabled=False)
            self.window["-STOP_VID_GEN-"].update(disabled=True)
        elif event == "-GEN_DURATIONS_CSV-":
            self._generate_durations_csv()

        return True

    def _generate_durations_csv(self):
        """Copy the start-time column from timestamps.csv to
        lyrics_durations_for_vid_gen.csv."""
        import os
        from config import TIMESTAMPS_CSV, LYRICS_DURATIONS_CSV
        if not os.path.exists(TIMESTAMPS_CSV):
            print(f"Cannot find {TIMESTAMPS_CSV} — mark timestamps first")
            return
        try:
            ts_data = draw_gui_helper.read_ts_from_csv(TIMESTAMPS_CSV)
            if ts_data == [[]] or not ts_data:
                print("timestamps.csv is empty")
                return
            # Write only the start times (col 0) and durations (col 1)
            draw_gui_helper.write_ts_to_csv(ts_data, LYRICS_DURATIONS_CSV)
            print(f"Generated {LYRICS_DURATIONS_CSV} with "
                  f"{len(ts_data)} entries from {TIMESTAMPS_CSV}")
        except Exception as e:
            print(f"Error generating durations CSV: {e}")
