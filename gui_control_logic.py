import PySimpleGUI as pg
from play_audio import AudioPlay
import time
from music_splitter_helper import *
from concurrent.futures import ThreadPoolExecutor
from img_generator import ImgGenerator
from vid_generator import VidGenerator

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
        self.file_name = ""
        self.music_splitter_helper = MusicSplitterHelper(draw_gui_object)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None
        self.img_generator = ImgGenerator()
        self.vid_generator = VidGenerator()
        
    # what to do for each event from the gui window. a series of if elif statements.
    def check_for_gui_events(self, event, values):
        active_tab = values['-TAB_GROUP-']
        if(active_tab == "Mark Timestamps"):
            ##############          TAB 1       #####################
            # check if the user has changed the audio file after clicking the play button once
            force_reset_playback = 0
            if(self.window["-AUDIO_FILE_NAME-"].get() != self.file_name or event == "-RESTART-"):
                if(self.play_clicked_once == 1 or event == "-RESTART-"):
                    self.audio_player.playback.stop()
                    self.play_clicked_once = 0
                    force_reset_playback = 1
                    self.num_lines_marked = 0
                    self.marked_ts_array = [[]] 
                    self.last_marked_ts = 0 
                    self.draw_app_gui.update_num_lines_marked(self.marked_ts_array)
                    self.draw_app_gui.update_time_boxes()
                    

            # check for events             
            if event is None or event == "-CLOSE_BTN-":
                self.draw_app_gui.close_window(write_csv=True)
            elif force_reset_playback == 1 or (event == "-PLAY-" or event == "PLAY-KEY"):
                if(self.play_clicked_once == 0):  # the very first time play button is clicked.
                    # check if we need to preload the marked_ts from a file
                    self.play_clicked_once = 1
                    audio_file_fullname = self.window["-AUDIO_FILE_NAME-"].get()
                    self.file_name = audio_file_fullname
                    self.audio_player.update_playback_file(audio_file_fullname) 
                    self.total_audio_duration = self.audio_player.playback.duration
                    self.draw_app_gui.update_total_audio_duration(self.total_audio_duration)
                    self.audio_player.playback.play() # plays loaded audio file from the beginning
                    # load marked_ts from a csv file and update stuff on screen
                    if(self.window["-LOAD_TS_CB-"].get() == True):            
                        self.marked_ts_array = self.draw_app_gui.draw_gui_helper.read_ts_from_csv(file_name="other_files/pre_load_timestamps.csv")
                        self.num_lines_marked = len(self.marked_ts_array)
                        self.audio_player.move_curr_position(self.marked_ts_array[-1][0])    # seek to the latest playtime
                        self.draw_app_gui.update_time_boxes()
                        self.draw_app_gui.update_num_lines_marked(self.marked_ts_array)
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
            
        elif(active_tab == "Audio Splitter"):
            ##############          TAB 2       #####################
            # Split an audio file into multiple audio files based on input csv file which contains timestamps

            # check for events             
            if event is None or event == "-CLOSE_BTN2-":
                self.draw_app_gui.close_window(write_csv=False)
            elif event == "-START_SPLIT-":
                marked_timestamps = self.draw_app_gui.draw_gui_helper.read_ts_from_csv(file_name="other_files/timestamps_for_splitting.csv")
                ignore_first = self.window["-IGNORE_FIRST_CB-"].get()
                ignore_last = self.window["-IGNORE_LAST_CB-"].get()
                print(marked_timestamps)
                file_name = self.window["-AUDIO_FILE_NAME_TO_SPLIT-"].get()
                # start threading for this task
                print("A thread has started to split the audio file")
                self.future = self.executor.submit(self.music_splitter_helper.split_audios,file_name, marked_timestamps, ignore_first, ignore_last)
            elif event == "-STOP_SPLIT-":
                self.music_splitter_helper.stop_audio_splitting() 
                
            # If the window is closed exit out of main loop
            if(event == None or event == "-CLOSE_BTN2-"):
                return False
            else: # If the window is not closed, then continue the main loop
                return True
        
        elif(active_tab == "Create Lyric Images and Videos"):
            ##############          TAB        #####################
            # Split an audio file into multiple audio files based on input csv file which contains timestamps

            # check for events             
            if event is None or event == "-CLOSE_BTN3-":
                pass
                # self.draw_app_gui.close_window(write_csv=False)  
            elif event == "-START_IMG_GEN-":
                if(self.future == None):
                    self.future = self.executor.submit(self.img_generator.generate_images)
            elif event == "-STOP_IMG_GEN-":
                self.img_generator.stop_img_creation()
            elif event == "-START_VID_GEN-":
                if(self.future == None):
                    file_name = self.window["-AUDIO_FILE_NAME_FOR_VID_GEN-"].get()
                    self.future = self.executor.submit(self.vid_generator.generate_video, file_name)
            elif event == "-STOP_VID_GEN-":
                self.vid_generator.stop_vid_creation()
        

            # If the window is closed exit out of main loop
            if(event == None or event == "-CLOSE_BTN3-"):
                return False
            else: # If the window is not closed, then continue the main loop
                return True