import PySimpleGUI as pg
from draw_gui_helper import DrawGuiHelper
from gui_layouts import GuiLayout

class DrawGui():
    def __init__(self, theme="DarkAmber", title="Music Lyrics Marker", big_font=("Arial", 16), small_font=("Arial", 12), info_text_font=("Arial", 11)):
        self.theme = theme
        self.title = title
        self.big_font = big_font
        self.small_font = small_font
        self.info_text_font = info_text_font
        self.window = []
        self.draw_gui_helper = DrawGuiHelper()
        self.gui_layout = GuiLayout()
        
    # draw and return the pysimpleGui window 
    def draw_gui(self):
        self.layout = self.gui_layout.setup_layout(theme=self.theme, big_font=self.big_font, 
                                                   small_font=self.small_font, info_text_font=self.info_text_font)
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
            self.draw_gui_helper.write_ts_to_csv(self.controller.marked_ts_array, 'csv_files/timestamps.csv')
            
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
            self.window["-NUM_LINES_MARKED-"].update(0)
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
        
    def update_table_music_splitter(self, timestamps):
        marked_ts_string = []
        for i in range(len(timestamps)):
            marked_ts_string.append([f"{timestamps[i]:.3f}"])
        self.window['-TABLE2-'].update(values=marked_ts_string)
    
    def update_time_boxes_music_splitter(self, max_i, i, elapsed_secs):
        self.window["-TOTAL_NUM_FILES-"].update(max_i)
        self.window["-CURR_FILE_NUM-"].update(i+1)
        self.window["-REM_FILES-"].update(max_i-i-1)
        elapsed_secs_str = self.draw_gui_helper.sec2_timestring(elapsed_secs)
        self.window["-ELAPSED_TIME-"].update(elapsed_secs_str)          
        
    # close the window
    def close_window(self, write_csv=False):
        if(write_csv == True):
            self.draw_gui_helper.write_ts_to_csv(self.controller.marked_ts_array, 'other_files/timestamps.csv')
        self.window.close()    
