"""Utility functions for GUI rendering and timestamp management."""

import csv
import io

import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment

plt.switch_backend("agg")


def sec2_timestring(secs_in):
    """Convert seconds to a time string: mm:ss or hh:mm:ss."""
    secs_in = max(0, int(secs_in))
    m, s = divmod(secs_in, 60)
    if m < 60:
        return f"{m:02d}:{s:02d}"
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_floats_for_table(marked_ts_array):
    """Format timestamps for table display (chronological, 3 decimal places).
    Row 0 = first mark, row 1 = second mark, etc."""
    if marked_ts_array == [[]]:
        return [["0.0", "0.0"]]
    return [[f"{row[0]:.3f}", f"{row[1]:.3f}"] for row in marked_ts_array]


def remove_outdated_timestamps(curr_time, marked_ts_array):
    """Remove timestamps that are past the current playback position."""
    if marked_ts_array == [[]] or marked_ts_array == []:
        return [[]]
    while marked_ts_array and marked_ts_array[-1][0] >= curr_time:
        marked_ts_array.pop()
    if not marked_ts_array:
        return [[]]
    return marked_ts_array


def write_ts_to_csv(marked_ts_array, file_name):
    """Write timestamp array to a CSV file."""
    with open(file_name, mode="w", newline="") as f:
        writer = csv.writer(f)
        for row in marked_ts_array:
            writer.writerow(row)


def read_ts_from_csv(file_name):
    """Read timestamp array from a CSV file."""
    with open(file_name, mode="r", newline="") as f:
        reader = csv.reader(f)
        return [[float(col) for col in row] for row in reader]


def get_raw_audio_data(audio_file):
    """Load audio file into a numpy array for waveform display."""
    audio_segment = AudioSegment.from_file(audio_file)
    frame_rate = audio_segment.frame_rate
    raw_audio_data = np.array(audio_segment.get_array_of_samples())
    if audio_segment.channels == 2:
        raw_audio_data = raw_audio_data.reshape((-1, 2))
    return raw_audio_data, frame_rate


def generate_waveform_image(raw_audio_data, frame_rate, curr_time):
    """Generate a PNG waveform image centered on the current position."""
    start_time = max(0, curr_time - 1)
    end_time = curr_time + 1

    start_sample = int(start_time * frame_rate)
    end_sample = int(end_time * frame_rate)

    segment = raw_audio_data[start_sample:end_sample]
    times = np.arange(start_sample, end_sample) / float(frame_rate)
    curr_time_aligned = int(curr_time * frame_rate) / float(frame_rate)

    plt.figure(figsize=(9.13, 3.50), dpi=100)
    plt.plot(times, segment)
    plt.axvline(x=curr_time_aligned, color="r", linestyle="--")
    plt.title("Audio Waveform")
    plt.ylabel("Amplitude")
    plt.xlabel("Time (sec)")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf.getvalue()
