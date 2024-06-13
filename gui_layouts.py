import PySimpleGUI as pg

class GuiLayout():
    def __init__(self, ):
        pass

    def setup_ts_marker_layout(self, big_font, small_font, info_text_font):
        ######## layout for marking the timestamps of an audio
        # pg.theme("DarkAmber")
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
            [pg.Button("RESTART", key="-RESTART-"), pg.Button("PLAY", key="-PLAY-"), pg.Button("MARK", key="-MARK-")],
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
            [pg.Slider(range=(0, 100), default_value=100, enable_events=True, orientation='vertical', key='-VOL_CONTROL-')]
        ]
        timestamp_table = pg.Table(
            values=[[0,0]], 
            headings=["Marked @", "Duration"], 
            max_col_width=25, 
            background_color='lightblue',        
            auto_size_columns=True,
            display_row_numbers=True,
            justification='right',
            text_color='black',
            num_rows=10,
            alternating_row_color='lightyellow',
            key='-TABLE-',
            tooltip='Timestamps at which lines are marked in the audio file'
        )
        checkbox_element = pg.Checkbox(
            text="Load marked timestamps from marked_ts_input.csv file", 
            key="-LOAD_TS_CB-"
        )
        layout_ts_marker = [
            [pg.Text("", size=(0, 1))],
            [pg.Text("C:/Users/wipin/Desktop/DATA DRIVE/Vedas/2 Yajur veda/Krishna Yajur Veda/KYV001.mp3", text_color="black", \
                    background_color="white", size=(100,2), enable_events=True, key="-AUDIO_FILE_NAME-"),
                pg.FileBrowse('Browse', auto_size_button=True, key="-AUDIO_FILE-", enable_events=True, \
                    initial_folder="C:\\Users\\wipin\\Desktop\\DATA DRIVE\\Vedas")],
            [checkbox_element],
            [pg.Text("", size=(0, 1))],
            [pg.Column(control_buttons, element_justification="center"), pg.Column(slider_element), timestamp_table, \
                pg.Push(), pg.Column(info_panel, element_justification="right")], 
        ]
        return layout_ts_marker
    
    def audio_splitter_layout(self, big_font, small_font, info_text_font):
        ######## layout for marking the timestamps of an audio
        checkbox_element = [
            [pg.Checkbox(text="Ignore the first segment", key="-IGNORE_FIRST_CB-")],
            [pg.Checkbox(text="Ignore the last segment", key="-IGNORE_LAST_CB-")],
        ]
        control_buttons = [
            [pg.Button("START SPLITTING", key="-START_SPLIT-"), pg.Button("STOP SPLITTING", key="-STOP_SPLIT-")],
            [pg.Button("CLOSE", key="-CLOSE_BTN2-")],
        ]
        info_panel = [
            [pg.Text("Total # of audio files: ", text_color="red", font=small_font),
                pg.Text("0", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-TOTAL_NUM_FILES-")],
            [pg.Text("Currently saving: ", text_color="red", font=small_font),
                pg.Text("0", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-CURR_FILE_NUM-")],
            [pg.Text("Remaining # of files: ", text_color="red", font=small_font),
                pg.Text("00:00", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-REM_FILES-")],
            [pg.Text("Elapsed time: ", text_color="red", font=small_font),
                pg.Text("00:00", font=info_text_font, size=(6,1), border_width=1, relief="solid", key="-ELAPSED_TIME-")],
        ]
        timestamp_table = pg.Table(
            values=[[0]], 
            headings=["Marked @"], 
            max_col_width=25, 
            background_color='lightblue',        
            auto_size_columns=True,
            display_row_numbers=True,
            justification='right',
            text_color='black',
            num_rows=10,
            alternating_row_color='lightyellow',
            key='-TABLE2-',
            tooltip='Timestamps at which lines are marked in the audio file'
        )
        layout_audio_splitter = [
            [pg.Text("", size=(0, 1))],
            [pg.Text("C:/Users/wipin/Desktop/DATA DRIVE/Vedas/2 Yajur veda/Krishna Yajur Veda/KYV001.mp3", text_color="black", \
                    background_color="white", size=(100,2), enable_events=True, key="-AUDIO_FILE_NAME_TO_SPLIT-"),
                pg.FileBrowse('Browse', auto_size_button=True, key="-AUDIO_FILE-", enable_events=True, \
                    initial_folder="C:\\Users\\wipin\\Desktop\\DATA DRIVE\\Vedas")],
            [pg.Column(checkbox_element)],
            [pg.Text("", size=(0, 1))],
            [pg.Column(control_buttons, element_justification="center"), timestamp_table, \
                pg.Push(), pg.Column(info_panel, element_justification="right")]  
        ]
        return layout_audio_splitter
        
    def setup_layout(self, theme, big_font, small_font, info_text_font):
        pg.theme(theme)
        layout_ts_marker = self.setup_ts_marker_layout(big_font, small_font, info_text_font)
        layout_audio_splitter = self.audio_splitter_layout(big_font, small_font, info_text_font)
        
        # Finally putting all tabs together
        layout = [
            [pg.TabGroup([
                [pg.Tab("Mark Timestamps", layout_ts_marker),
                pg.Tab("Audio Splitter", layout_audio_splitter)]
            ], key='-TAB_GROUP-')]
        ]
        return layout