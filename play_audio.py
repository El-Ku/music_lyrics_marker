"""Audio playback wrapper around just_playback with speed control."""

import os
import tempfile
from just_playback import Playback
from pydub import AudioSegment


class AudioPlay:
    """Manages playback of a single audio file with speed adjustment."""

    def __init__(self):
        self.playback = Playback()
        self.original_file_path = ""
        self.current_speed = 1.0
        self._temp_speed_file = None

    def update_playback_file(self, file_name):
        """Load a new audio file, resetting speed to 1.0x."""
        self._cleanup_temp_file()
        self.original_file_path = file_name
        self.current_speed = 1.0
        self.playback.load_file(file_name)

    def move_curr_position(self, secs_to_move):
        """Seek forward or backward relative to the current position."""
        self.playback.seek(max(0, self.playback.curr_pos + secs_to_move))

    def seek_absolute(self, position_secs):
        """Seek to an absolute position in seconds."""
        self.playback.seek(max(0, position_secs))

    def set_volume(self, new_volume):
        """Set volume (0.0 to 1.0)."""
        self.playback.set_volume(new_volume)

    def set_speed(self, speed_factor, current_position):
        """Reload audio at a different speed using frame-rate manipulation.

        Changes both speed and pitch. The playback position is adjusted
        proportionally so it stays at the same point in the song.
        """
        self._cleanup_temp_file()
        self.current_speed = speed_factor

        if speed_factor == 1.0:
            self.playback.load_file(self.original_file_path)
        else:
            audio = AudioSegment.from_file(self.original_file_path)
            altered = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed_factor),
            }).set_frame_rate(audio.frame_rate)

            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            altered.export(temp_path, format="wav")
            self._temp_speed_file = temp_path
            self.playback.load_file(temp_path)

        self.playback.play()
        adjusted_pos = current_position / speed_factor
        self.playback.seek(max(0, adjusted_pos))

    def _cleanup_temp_file(self):
        """Remove any temporary speed-adjusted file."""
        if self._temp_speed_file and os.path.exists(self._temp_speed_file):
            try:
                os.unlink(self._temp_speed_file)
            except OSError:
                pass
            self._temp_speed_file = None
