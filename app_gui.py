import PySimpleGUI as pg

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
        pg.Text("0", font=("Arial", 11), size=(6,1), border_width=1, relief="solid")],
    [pg.Text("Elapsed time: ", text_color="red", font=("Arial", 12)),
        pg.Text("00:00", font=("Arial", 11), size=(6,1), border_width=1, relief="solid")],
    [pg.Text("Remaining time: ", text_color="red", font=("Arial", 12)),
        pg.Text("00:00", font=("Arial", 11), size=(6,1), border_width=1, relief="solid")],
    [pg.Text("Total time: ", text_color="red", font=("Arial", 12)),
        pg.Text("00:00", font=("Arial", 11), size=(6,1), border_width=1, relief="solid")],
]

layout = [
    [pg.Text("Audio file name", text_color="black", background_color="white", size=(100,2), key="-AUDIO_FILE_NAME-"),
        pg.FileBrowse('Browse', auto_size_button=True, key="-AUDIO_FILE-", \
        initial_folder="C:\\Users\\wipin\\Desktop\\DATA DRIVE\\Vedas", enable_events=True)],
    [pg.Column(control_buttons, element_justification="center"), pg.Push(), pg.Column(info_panel, element_justification="right")]
    
]

window = pg.Window("Music Lyrics Marker", layout)

while True:
    event, values = window.read()
    if event is None or event == "-CLOSE_BTN-":
        break
    elif event == "-AUDIO_FILE-":
        audio_file_fullname = values["-AUDIO_FILE-"]
        print("The audio file was selected : ",audio_file_fullname)
        values["-AUDIO_FILE_NAME-"] = audio_file_fullname
    elif event == "-PLAY-":
        if(window["-PLAY-"].ButtonText == "PLAY"):
            window["-PLAY-"].update("PAUSE")
        else:
            window["-PLAY-"].update("PLAY")

window.close()
