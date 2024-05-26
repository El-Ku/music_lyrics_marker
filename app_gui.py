import PySimpleGUI as pg
import datetime
from just_playback import Playback
import time

pg.theme("DarkAmber")

layout_backward = [  
    [pg.Text("Jump Backward", text_color="red", font=("Arial", 16))],
    [pg.Button("5 secs", key="-BACK_5_SECS-")],
    [pg.Button("1 min", key="-BACK_1_MIN-")],
    [pg.Button("10 mins", key="-BACK_10_MIN-")]
]
layout_forward = [  
    [pg.Text("Jump Forward", text_color="red", font=("Arial", 16))],
    [pg.Button("5 secs", key="-FORW_5_SECS-")],
    [pg.Button("1 min", key="-FORW_1_MIN-")],
    [pg.Button("10 mins", key="-FORW_10_MIN-")]
]

control_buttons = [
    [pg.Button("PLAY", key="-PLAY-"), pg.Button("MARK", key="-MARK-")],
    [pg.Column(layout_forward, element_justification="center"), pg.Column(layout_backward, element_justification="center")],   
    [pg.Button("Close", key="-CLOSE_BTN-")]
]

info_panel = [
    [pg.Text("# of lines marked: ", text_color="red", font=("Arial", 12)),
        pg.Text("0", font=("Arial", 11), size=(6,1), border_width=1, relief="solid", key="-NUM_LINES_MARKED-")],
    [pg.Text("Elapsed time: ", text_color="red", font=("Arial", 12)),
        pg.Text("00:00", font=("Arial", 11), size=(6,1), border_width=1, relief="solid", key="-CURR_TIME-")],
    [pg.Text("Remaining time: ", text_color="red", font=("Arial", 12)),
        pg.Text("00:00", font=("Arial", 11), size=(6,1), border_width=1, relief="solid", key="-REM_TIME-")],
    [pg.Text("Total time: ", text_color="red", font=("Arial", 12)),
        pg.Text("00:00", font=("Arial", 11), size=(6,1), border_width=1, relief="solid", key="-TOTAL_TIME-")],
]

layout = [
    [pg.Text("Audio file name", text_color="black", background_color="white", size=(100,2), key="-AUDIO_FILE_NAME-"),
        pg.FileBrowse('Browse', auto_size_button=True, key="-AUDIO_FILE-", \
        initial_folder="C:\\Users\\wipin\\Desktop\\DATA DRIVE\\Vedas")],
    [pg.Column(control_buttons, element_justification="center"), pg.Push(), pg.Column(info_panel, element_justification="right")]
    
]

def sec2_timestring(secs_in):
    secs_in = int(secs_in)
    m, s = divmod(secs_in, 60) 
    if(m < 60):
        time_string = "{:02d}:{:02d}".format(m, s) 
    else:
        (h,m) = divmod(m, 60) 
        time_string = "{:02d}:{:02d}:{:02d}".format(h, m, s) 
    return time_string

def update_time_boxes():
    curr_secs = playback.curr_pos
    curr_time = sec2_timestring(curr_secs)
    rem_time = sec2_timestring(total_audio_duration-curr_secs)
    window["-CURR_TIME-"].update(curr_time)
    window["-REM_TIME-"].update(rem_time)

window = pg.Window("Music Lyrics Marker", layout)
audio_file_fullname = "C:\\Users\\wipin\\Desktop\\DATA DRIVE\\Vedas\\2 Yajur veda\\Krishna Yajur Veda\\KYV001.mp3"
playback = Playback() # creates an object for managing playback of a single audio file
play_clicked_once = 0
total_audio_duration = 0
num_lines_marked = 0
last_marked_ts = 0

while True:
    event, values = window.read(timeout=1000)
    if(playback.playing):
        update_time_boxes()
    if event is None or event == "-CLOSE_BTN-":
        break
    elif event == "-AUDIO_FILE-":
        values["-AUDIO_FILE_NAME-"] = audio_file_fullname
    elif event == "-PLAY-":
        if(play_clicked_once == 0):
            list_ts = []
            play_clicked_once = 1
            print("aaaa")
            audio_file_fullname = values["-AUDIO_FILE-"]
            playback.load_file(audio_file_fullname) 
            total_audio_duration = playback.duration
            window["-TOTAL_TIME-"].update(sec2_timestring(total_audio_duration))
            playback.play() # plays loaded audio file from the beginning
        if(window["-PLAY-"].ButtonText == "PLAY"):
            window["-PLAY-"].update("PAUSE")
            playback.resume()
        else:
            window["-PLAY-"].update("PLAY")
            playback.pause()
    elif event == "-BACK_5_SECS-":
        playback.seek(playback.curr_pos-5)
    elif event == "-BACK_1_MIN-":
        playback.seek(playback.curr_pos-60)
    elif event == "-BACK_10_MIN-":
        playback.seek(playback.curr_pos-600)
    elif event == "-FORW_5_SECS-":
        playback.seek(playback.curr_pos+5)
    elif event == "-FORW_1_MIN-":
        playback.seek(playback.curr_pos+60)
    elif event == "-FORW_10_MIN-":
        playback.seek(playback.curr_pos+600)
    elif event == "-MARK-":
        # the line cannot be < 1 second long
        if(time.time() - last_marked_ts > 1):
            num_lines_marked += 1
            list_ts.append(playback.curr_pos)  # list of timestamps.
            last_marked_ts = time.time()
            window["-NUM_LINES_MARKED-"].update(num_lines_marked)
        else:
            print("Dont click ""Mark"" too quickly! The line cannot be < 1 second long")
    time.sleep(0.01)    
    
print(list_ts)
window.close()
