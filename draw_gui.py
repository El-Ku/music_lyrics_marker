import PySimpleGUI as pg
from draw_gui_helper import DrawGuiHelper

class DrawGui():
    def __init__(self, theme="DarkAmber", title="Music Lyrics Marker", big_font=("Arial", 16), small_font=("Arial", 12), info_text_font=("Arial", 11)):
        self.theme = theme
        self.title = title
        self.big_font = big_font
        self.small_font = small_font
        self.info_text_font = info_text_font
        self.window = []
        self.draw_gui_helper = DrawGuiHelper()
        pg.theme(self.theme)
        
        layout_backward = [  
            [pg.Text("Jump Backward", text_color="red", font=big_font)],
            [pg.Button("5 secs", key="-BACK_5_SECS-")],
            [pg.Button("1 min", key="-BACK_1_MIN-")],
            [pg.Button("10 mins", key="-BACK_10_MIN-")]
        ]
        layout_forward = [  
            [pg.Text("Jump Forward", text_color="red", font=big_font)],
            [pg.Button("5 secs", key="-FORW_5_SECS-")],
            [pg.Button("1 min", key="-FORW_1_MIN-")],
            [pg.Button("10 mins", key="-FORW_10_MIN-")]
        ]
        control_buttons = [
            [pg.Button("PLAY", key="-PLAY-"), pg.Button("MARK", key="-MARK-")],
            [pg.Column(layout_backward, element_justification="center"), pg.Column(layout_forward, element_justification="center")],   
            [pg.Button("CLOSE", key="-CLOSE_BTN-")]
        ]
        info_panel = [
            [pg.Text("# of lines marked: ", text_color="red", font=small_font),
                pg.Text("0", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-NUM_LINES_MARKED-")],
            [pg.Text("Elapsed time: ", text_color="red", font=small_font),
                pg.Text("00:00", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-CURR_TIME-")],
            [pg.Text("Remaining time: ", text_color="red", font=small_font),
                pg.Text("00:00", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-REM_TIME-")],
            [pg.Text("Total time: ", text_color="red", font=small_font),
                pg.Text("00:00", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-TOTAL_TIME-")],
        ]
        slider_element = [
            [pg.Text("Volume", text_color="red", font=small_font)],
            [pg.Slider(range=(0, 100), default_value=100, enable_events=True, \
                orientation='vertical', key='-VOL_CONTROL-')]
        ]
        timestamp_table = [pg.Table(values=[[0,0]], headings=["Marked @", "Duration"], max_col_width=25, 
                            background_color='lightblue',        
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='right',
                            text_color='black',
                            num_rows=10,
                            alternating_row_color='lightyellow',
                            key='-TABLE-',
                            tooltip='Timestamps at which lines are marked in the audio file')],
        self.layout = [
            [pg.Text("", size=(0, 1))],
            [pg.Text("C:/Users/wipin/Desktop/DATA DRIVE/Vedas/2 Yajur veda/Krishna Yajur Veda/KYV001.mp3", text_color="black", \
                    background_color="white", size=(100,2), enable_events=True, key="-AUDIO_FILE_NAME-"),
                pg.FileBrowse('Browse', auto_size_button=True, key="-AUDIO_FILE-", enable_events=True, \
                    initial_folder="C:\\Users\\wipin\\Desktop\\DATA DRIVE\\Vedas")],
            [pg.Text("", size=(0, 1))],
            [pg.Column(control_buttons, element_justification="center"), pg.Column(slider_element), pg.Column(timestamp_table), \
                pg.Push(), pg.Column(info_panel, element_justification="right")]  
        ]
    
    # draw and return the pysimpleGui window 
    def draw_gui(self):
        window = pg.Window(self.title, self.layout, finalize=True)
        # short cut keys
        window.bind("<p>", "PLAY-KEY")  # press "p" to play/pause
        window.bind("<m>", "MARK-KEY")  # press "p" to mark
        self.window = window
        return window
    
    # set the gui_control_logic object
    def set_controller_object(self, controller):
        self.controller = controller
        
    # set the play_audio object
    def set_audio_player(self, audio_player):
        self.audio_player = audio_player

    # what is the total duration of the audio. display on gui
    def update_total_audio_duration(self, duration):
        self.window["-TOTAL_TIME-"].update(self.draw_gui_helper.sec2_timestring(duration))
        
    # toggle the play button to pause and vice versa when its clicked.
    def toggle_play_btn(self):
        if(self.window["-PLAY-"].ButtonText == "PLAY"):
            self.window["-PLAY-"].update("PAUSE")
            self.audio_player.playback.resume()
        else:
            self.window["-PLAY-"].update("PLAY")
            self.audio_player.playback.pause()
            self.draw_gui_helper.write_ts_to_csv(self.controller.marked_ts_array)
            
    # update the table. called to show changes in marked_ts_array
    def update_table(self, marked_ts_array):
        marked_ts_string = self.draw_gui_helper.format_floats_for_table(marked_ts_array)
        self.window['-TABLE-'].update(values=marked_ts_string)
    
    # update the table and the number of marked lines. Called after playback is moved backwards.
    def update_num_lines_marked(self, marked_ts_array):
        curr_time = self.audio_player.playback.curr_pos
        # print("index 1: ",index)
        if(marked_ts_array == [[]]):
            self.update_table([[]])
            return 0, [[]] 
        marked_ts_array = self.draw_gui_helper.remove_outdated_timestamps(curr_time, marked_ts_array)
        self.update_table(marked_ts_array)
        # print(marked_ts_array)
        if(marked_ts_array == [[]]):
            self.window["-NUM_LINES_MARKED-"].update(0)
            return 0, marked_ts_array  # num_lines_marked and marked timestamps
        else:
            self.window["-NUM_LINES_MARKED-"].update(len(marked_ts_array))
            return len(marked_ts_array), marked_ts_array

    # update the current play time and remaining time on gui
    def update_time_boxes(self):
        curr_secs = self.audio_player.playback.curr_pos
        curr_time = self.draw_gui_helper.sec2_timestring(curr_secs)
        rem_time = self.draw_gui_helper.sec2_timestring(self.controller.total_audio_duration-curr_secs)
        self.window["-CURR_TIME-"].update(curr_time)
        self.window["-REM_TIME-"].update(rem_time)
    
    # close the window
    def close_window(self):
        self.draw_gui_helper.write_ts_to_csv(self.controller.marked_ts_array)
        self.window.close()    
