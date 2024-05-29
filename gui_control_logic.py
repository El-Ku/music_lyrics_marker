import PySimpleGUI as pg
from play_audio import AudioPlay
import time

# this class decides what happens when you click a button on the gui. 
# The functions which act on input are written in a seperate helper file. 
# the gui elements are mostly changed in the draw_gui class.
class ControlGui():
    def __init__(self, draw_gui_object=None):
        self.draw_app_gui = draw_gui_object
        self.window = self.draw_app_gui.window
        self.play_clicked_once = 0
        self.audio_player = AudioPlay()
        self.draw_app_gui.set_audio_player(self.audio_player) 
        self.last_marked_ts = 0 
        self.marked_ts_array = [[]]
        self.num_lines_marked = 0
    # what to do for each event from the gui window. a series of if elif statements.
    def check_for_gui_events(self, event, values):
        if event is None or event == "-CLOSE_BTN-":
            self.draw_app_gui.close_window()
        elif event == "-PLAY-" or event == "PLAY-KEY":
            if(self.play_clicked_once == 0):  # the very first time play button is clicked.
                self.play_clicked_once = 1
                audio_file_fullname = self.window["-AUDIO_FILE_NAME-"].get()
                self.audio_player.update_playback_file(audio_file_fullname) 
                self.total_audio_duration = self.audio_player.playback.duration
                self.draw_app_gui.update_total_audio_duration(self.total_audio_duration)
                self.audio_player.playback.play() # plays loaded audio file from the beginning
            self.draw_app_gui.toggle_play_btn()
        elif event == "-BACK_5_SECS-":   # backward by 5 secs
            self.audio_player.move_curr_position(secs_to_move=-5)
            self.num_lines_marked, self.marked_ts_array = self.draw_app_gui.update_num_lines_marked(self.marked_ts_array)
            # print("marked_ts_array 3: ",self.marked_ts_array)
        elif event == "-BACK_1_MIN-":  # backward by 1 min
            self.audio_player.move_curr_position(secs_to_move=-60)
            self.num_lines_marked, self.marked_ts_array = self.draw_app_gui.update_num_lines_marked(self.marked_ts_array)
            # print("marked_ts_array 3: ",self.marked_ts_array)
        elif event == "-BACK_10_MIN-":   # backward by 10 mins
            self.audio_player.move_curr_position(secs_to_move=-600)
            self.num_lines_marked, self.marked_ts_array = self.draw_app_gui.update_num_lines_marked(self.marked_ts_array)
            # print("marked_ts_array 3: ",self.marked_ts_array)
        elif event == "-FORW_5_SECS-":   # forward by 5 secs
            self.audio_player.move_curr_position(secs_to_move=5)
        elif event == "-FORW_1_MIN-":  # forward by 1 min
            self.audio_player.move_curr_position(secs_to_move=60)
        elif event == "-FORW_10_MIN-":    # forward by 10 mins
            self.audio_player.move_curr_position(secs_to_move=600)
        elif event == "-VOL_CONTROL-":   # change volume.
            self.audio_player.set_volume(values['-VOL_CONTROL-']/100)
        elif event == "-MARK-" or event == "MARK-KEY":  #mark the line
            # the line cannot be < 1 second long
            if(time.time() - self.last_marked_ts > 1):
                curr_time = self.audio_player.playback.curr_pos
                # marked_ts_array contains the list of timestamps and their durations
                # print("num_lines_marked: ",self.num_lines_marked)
                # print("marked_ts_array: ",self.marked_ts_array)
                if(self.num_lines_marked == 0):
                    self.marked_ts_array[self.num_lines_marked] = [curr_time, curr_time]
                else:
                    self.marked_ts_array.append([curr_time, curr_time-self.marked_ts_array[self.num_lines_marked-1][0]]) 
                self.draw_app_gui.update_table(self.marked_ts_array)
                self.last_marked_ts = time.time()
                self.num_lines_marked += 1
                self.window["-NUM_LINES_MARKED-"].update(self.num_lines_marked)
            else:
                print("Dont click ""Mark"" too quickly! The line cannot be < 1 second long")
        # If the audio is playing and window is not closed update the time boxes        
        if(self.audio_player.playback.playing and event != None and event != "-CLOSE_BTN-"):
            self.draw_app_gui.update_time_boxes()
            return True
        # If the window is closed exit out of main loop
        if(event == None or event == "-CLOSE_BTN-"):
            return False
        else: # If the window is not closed, then continue the main loop
            return True