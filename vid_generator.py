"""Generate a video from lyric images + audio using OpenCV and moviepy."""

import csv
import os
import queue
import threading
import time

import cv2
import mutagen.mp3
from moviepy import VideoFileClip, AudioFileClip

from config import LYRICS_DURATIONS_CSV, NO_LYRICS_OM_IMG, ONLY_OM_IMG, LYRIC_IMAGES_DIR


class VidGenerator:

    def __init__(self):
        self.im_w = 1920
        self.im_h = 1080
        self.frame_rate = 10.0
        self.video_file_name = "output.avi"
        self.in_progress = False
        self.stop_flag = False
        self.frame_queue = queue.Queue()
        self.stop_event = threading.Event()

    # ── Internals ──────────────────────────────────────────────

    def _read_image(self, ind, curr_duration):
        if ind == 0:
            if curr_duration > 20:
                print("Processing Om Image (no lyrics)")
                return cv2.imread(NO_LYRICS_OM_IMG)
            else:
                print("Processing Om Image")
                return cv2.imread(ONLY_OM_IMG)
        path = os.path.join(LYRIC_IMAGES_DIR, f"{ind}.png")
        frame = cv2.imread(path)
        if ind == self._total_imgs:
            print("Processing the last line")
        else:
            print(f"Processing image #{ind}")
        return frame

    def _read_durations_csv(self):
        with open(LYRICS_DURATIONS_CSV, mode="r", newline="") as f:
            reader = csv.reader(f)
            rows = [[float(c) for c in row] for row in reader]
        return [r[0] for r in rows]

    def _write_frames(self):
        while not self.stop_event.is_set() or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1)
                self._out.write(frame)
                self._frames_written += 1
            except queue.Empty:
                continue

    def _create_writer(self):
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(self.video_file_name, fourcc,
                              self.frame_rate, (self.im_w, self.im_h))
        if out.isOpened():
            return out
        print("Failed to open VideoWriter")
        return None

    # ── Public API ─────────────────────────────────────────────

    def generate_video(self, mp3_file_name):
        """Generate a video from lyric images and an MP3 audio file."""
        print("Generating video with lyric images and selected audio")
        self.in_progress = True
        self.stop_event.clear()

        durations = self._read_durations_csv()
        self._total_imgs = len(durations)
        audio_info = mutagen.mp3.MP3(mp3_file_name)
        total_length = audio_info.info.length
        print(f"Total video length = {total_length:.1f} secs")

        self._out = self._create_writer()
        if self._out is None:
            self.in_progress = False
            return

        self._frames_written = 0
        prev_time = 0
        start = time.time()

        writer_thread = threading.Thread(target=self._write_frames)
        writer_thread.start()

        try:
            for ind in range(self._total_imgs + 1):
                if ind == self._total_imgs:
                    curr_time = total_length
                else:
                    curr_time = durations[ind]

                duration = curr_time - prev_time
                frame = self._read_image(ind, duration)
                prev_time = curr_time
                n_frames = round(duration * self.frame_rate)
                print(n_frames)

                for _ in range(n_frames):
                    self.frame_queue.put(frame)
                    if self.stop_flag:
                        print("Video generation stopped midway")
                        self.in_progress = False
                        self.stop_flag = False
                        return
        finally:
            self.stop_event.set()
            writer_thread.join()
            self._out.release()

        print(f"{self._frames_written} frames written. "
              f"Time: {time.time() - start:.1f}s")

        # Mux audio
        video = VideoFileClip("output.avi")
        audio = AudioFileClip(mp3_file_name)
        print("Video and audio clips were created")

        mux_start = time.time()
        final_clip = video.with_audio(audio)

        if self.stop_flag:
            print("Video generation stopped before final export")
            self.in_progress = False
            self.stop_flag = False
            return

        final_clip.write_videofile("final_video.mp4")
        print(f"Final video exported in {time.time() - mux_start:.1f}s")
        self.in_progress = False

    def stop_vid_creation(self):
        if self.in_progress:
            self.stop_flag = True
            print("Stop video generation button was pressed")
