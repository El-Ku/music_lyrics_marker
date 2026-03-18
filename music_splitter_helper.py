"""Split an audio file into segments based on timestamp CSV data."""

import os
import time
from pydub import AudioSegment

from config import SPLIT_AUDIOS_DIR


class MusicSplitterHelper:

    def __init__(self, draw_gui_object):
        self.stop_flag = False
        self.gui = draw_gui_object

    def split_audios(self, file_name, marked_timestamps,
                     ignore_first, ignore_last, skip_rows=None):
        """Split *file_name* into MP3 segments defined by *marked_timestamps*.
        *skip_rows* is a set of segment indices (0-based) to skip."""
        start = time.time()
        self.stop_flag = False
        if skip_rows is None:
            skip_rows = set()

        audio = AudioSegment.from_file(file_name)
        timestamps = [row[0] for row in marked_timestamps]

        if not ignore_first:
            timestamps.insert(0, 0)
        if not ignore_last:
            timestamps.append(len(audio) / 1000)

        total = len(timestamps) - 1
        self.gui.update_table_music_splitter(timestamps)

        os.makedirs(SPLIT_AUDIOS_DIR, exist_ok=True)

        saved_count = 0
        for i in range(total):
            self.gui.update_time_boxes_music_splitter(
                total, i, time.time() - start)
            self.gui.update_split_progress(i + 1, total)

            if self.stop_flag:
                self.stop_flag = False
                print("Audio splitting was stopped successfully")
                return

            if i in skip_rows:
                print(f"Segment {i} skipped (row {i} in skip list)")
                continue

            start_ms = timestamps[i] * 1000
            end_ms = timestamps[i + 1] * 1000
            segment = audio[start_ms:end_ms]
            saved_count += 1
            out_path = os.path.join(SPLIT_AUDIOS_DIR, f"{saved_count:03}.mp3")
            segment.export(out_path, format="mp3")
            print(f"Segment {i} saved as {saved_count:03}.mp3 "
                  f"({timestamps[i]:.1f}s to {timestamps[i + 1]:.1f}s)")

        self.gui.update_split_progress(total, total)
        skipped = len(skip_rows & set(range(total)))
        print(f"Done — {saved_count} files saved, {skipped} skipped")

    def stop_audio_splitting(self):
        self.stop_flag = True
        print("Stop splitting button was pressed")
