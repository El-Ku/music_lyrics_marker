import csv
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
import io
plt.switch_backend('agg')

# a set of helper functions. Mainly used the draw_gui module and gui_control_logic.py

# convert to seconds to time format: hh:mm:ss
def sec2_timestring(secs_in):
    secs_in = int(secs_in)
    m, s = divmod(secs_in, 60) 
    if(m < 60):
        time_string = "{:02d}:{:02d}".format(m, s) 
    else:
        (h,m) = divmod(m, 60) 
        time_string = "{:02d}:{:02d}:{:02d}".format(h, m, s) 
    return time_string
        
# the float values are converted to formatted string with only 3 fractionals. For table.
def format_floats_for_table(marked_ts_array):
    marked_ts_string = []
    if(marked_ts_array == [[]]):
        marked_ts_string = [["0.0","0.0"]]
    else:
        for i in range(len(marked_ts_array)):
            marked_ts_string.append([f"{marked_ts_array[i][0]:.3f}", f"{marked_ts_array[i][1]:.3f}"])
    return list(reversed(marked_ts_string))

# when we go backward in the payback, remove some latest values from the marked_ts_array array.
def remove_outdated_timestamps(curr_time, marked_ts_array):
    list_ts = [x[0] for x in marked_ts_array]
    index = len(marked_ts_array)
    # print("list_ts 1: ",list_ts)
    while index >= 1:
        if(curr_time <= list_ts[-1]):
            list_ts.pop()
            marked_ts_array.pop()
            index = len(list_ts)
        else:  
            break
    if(marked_ts_array == []):
        marked_ts_array = [[]]
    return marked_ts_array  # num_lines_marked and marked timestamps

def write_ts_to_csv(marked_ts_array, file_name):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Writing the data rows
        for row in marked_ts_array:
            writer.writerow(row)
            
def read_ts_from_csv(file_name):
    with open(file_name, mode='r', newline='') as file:
        reader = csv.reader(file)
        # Reading the data rows. each element in a row is typecasted into a float from string.
        marked_ts_array = [[float(col) for col in row] for row in reader]
        return marked_ts_array
        
def get_raw_audio_data(audio_file):
    audio_segment = AudioSegment.from_mp3(audio_file)
    frame_rate = audio_segment.frame_rate
    # Convert AudioSegment to raw audio data
    raw_audio_data = np.array(audio_segment.get_array_of_samples())
    # Convert raw_data to 2D NumPy array if stereo
    if audio_segment.channels == 2:
        raw_audio_data = raw_audio_data.reshape((-1, 2))
    return raw_audio_data, frame_rate

        
def generate_waveform_image(raw_audio_data, frame_rate, curr_time):
    start_time = curr_time - 1
    end_time = curr_time + 1
    if(start_time < 0):
        start_time = 0
    # print(start_time, end_time)
    start_time = int(start_time * frame_rate) 
    end_time = int(end_time * frame_rate)
    # print(start_time, end_time)
    segment = raw_audio_data[start_time:end_time]
    times = np.arange(start_time, end_time) / float(frame_rate)
    curr_time = int(curr_time * frame_rate) / float(frame_rate)
    # # Print the shape and type of the array
    # print(f"Shape of segment    : {segment.shape}")
    # print(f"Shape of time x axis: {times.shape}")
    # print(f"Data type: {segment.dtype}")

    plt.figure(figsize=(9.13, 3.50), dpi=100)
    plt.plot(times, segment)
    plt.axvline(x=curr_time, color='r', linestyle='--')  # Add vertical line at x_line
    plt.title("Audio Waveform")
    plt.ylabel("Amplitude")
    plt.xlabel("Time(sec)")
    plt.tight_layout()
    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf.getvalue()
    