"""GUI layout definitions for all tabs and the main window."""

try:
    import PySimpleGUI as pg
except ImportError:
    import FreeSimpleGUI as pg

from config import BIG_FONT, SMALL_FONT, INFO_TEXT_FONT

# Consistent button sizing
BTN_SIZE = (12, 1)
BTN_SMALL = (10, 1)
FRAME_PAD = (10, 8)
SECTION_PAD = (0, 5)


class GuiLayout:

    def __init__(self, initial_folder="", default_audio_path=""):
        self.initial_folder = initial_folder
        self.default_audio_path = default_audio_path

    # ── Tab 1: Mark Timestamps ──────────────────────────────────

    def _ts_marker_layout(self):
        layout_backward = [
            [pg.Text("Jump Backward", text_color="#FFD700", font=SMALL_FONT)],
            [pg.Button("50ms [Shift+\u2190]", key="-BACK_50_MSECS-", size=BTN_SIZE)],
            [pg.Button("5s [\u2190]", key="-BACK_5_SECS-", size=BTN_SIZE)],
            [pg.Button("1 min", key="-BACK_1_MIN-", size=BTN_SIZE)],
            [pg.Button("10 min", key="-BACK_10_MIN-", size=BTN_SIZE)],
        ]
        layout_forward = [
            [pg.Text("Jump Forward", text_color="#FFD700", font=SMALL_FONT)],
            [pg.Button("50ms [Shift+\u2192]", key="-FORW_50_MSECS-", size=BTN_SIZE)],
            [pg.Button("5s [\u2192]", key="-FORW_5_SECS-", size=BTN_SIZE)],
            [pg.Button("1 min", key="-FORW_1_MIN-", size=BTN_SIZE)],
            [pg.Button("10 min", key="-FORW_10_MIN-", size=BTN_SIZE)],
        ]

        playback_controls = pg.Frame("Playback", [
            [
                pg.Button("RESTART", key="-RESTART-", size=BTN_SMALL),
                pg.Button("PLAY [P]", key="-PLAY-", size=BTN_SMALL,
                           button_color=("white", "#2E7D32")),
                pg.Button("MARK [Space]", key="-MARK-", size=BTN_SMALL,
                           button_color=("white", "#C62828")),
                pg.Button("UNDO [Ctrl+Z]", key="-UNDO-", size=BTN_SMALL),
            ],
            [
                pg.Column(layout_backward, element_justification="center"),
                pg.Column(layout_forward, element_justification="center"),
            ],
        ], font=BIG_FONT, pad=FRAME_PAD)

        info_panel = pg.Frame("Info", [
            [pg.Text("Lines marked:", font=SMALL_FONT),
             pg.Text("0", font=INFO_TEXT_FONT, size=(7, 1),
                      border_width=1, relief="solid", key="-NUM_LINES_MARKED-",
                      justification="center")],
            [pg.Text("Elapsed:", font=SMALL_FONT),
             pg.Text("00:00", font=INFO_TEXT_FONT, size=(7, 1),
                      border_width=1, relief="solid", key="-CURR_TIME-",
                      justification="center")],
            [pg.Text("Remaining:", font=SMALL_FONT),
             pg.Text("00:00", font=INFO_TEXT_FONT, size=(7, 1),
                      border_width=1, relief="solid", key="-REM_TIME-",
                      justification="center")],
            [pg.Text("Total:", font=SMALL_FONT),
             pg.Text("00:00", font=INFO_TEXT_FONT, size=(7, 1),
                      border_width=1, relief="solid", key="-TOTAL_TIME-",
                      justification="center")],
        ], font=BIG_FONT, pad=FRAME_PAD)

        speed_volume = pg.Frame("Controls", [
            [pg.Text("Speed", font=SMALL_FONT)],
            [pg.Combo(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x"],
                       default_value="1.0x", key="-SPEED-",
                       enable_events=True, readonly=True, size=(6, 1))],
            [pg.Text("Volume", font=SMALL_FONT)],
            [pg.Slider(range=(0, 100), default_value=100, enable_events=True,
                        orientation="vertical", size=(8, 12), key="-VOL_CONTROL-")],
        ], font=BIG_FONT, pad=FRAME_PAD, element_justification="center")

        timestamp_table = pg.Table(
            values=[[0, 0]],
            headings=["Marked @", "Duration"],
            max_col_width=25,
            background_color="#E3F2FD",
            auto_size_columns=True,
            display_row_numbers=True,
            justification="right",
            text_color="black",
            num_rows=10,
            alternating_row_color="#FFF9C4",
            enable_click_events=True,
            key="-TABLE-",
            tooltip="Click to select, use buttons or arrows to edit",
        )
        table_edit_buttons = [
            pg.Button("+50ms", key="-TS_PLUS50-", size=(7, 1)),
            pg.Button("-50ms", key="-TS_MINUS50-", size=(7, 1)),
            pg.Button("Delete", key="-TS_DELETE-", size=(7, 1),
                       button_color=("white", "#C62828")),
        ]

        checkbox = pg.Checkbox(
            "Load timestamps from pre_load_timestamps.csv",
            key="-LOAD_TS_CB-", font=INFO_TEXT_FONT, enable_events=True,
        )

        seekbar = pg.Slider(
            range=(0, 100),
            default_value=0,
            orientation="horizontal",
            size=(80, 15),
            enable_events=True,
            disable_number_display=True,
            key="-SEEKBAR-",
        )

        # Lyrics panel — paste lyrics here, lines highlight as you mark
        lyrics_panel = pg.Frame("Lyrics (paste here — each line maps to a mark)", [
            [pg.Multiline(
                size=(50, 20),
                key="-LYRICS_BOX-",
                font=("Arial", 13),
                expand_x=True,
                expand_y=True,
                horizontal_scroll=True,
            )],
        ], font=SMALL_FONT, pad=FRAME_PAD, expand_x=True, expand_y=True)

        # Right side: controls + table + info stacked
        right_col = pg.Column([
            [checkbox],
            [pg.Text("Position:", font=SMALL_FONT), seekbar],
            [
                playback_controls,
                speed_volume,
            ],
            [
                pg.Frame("Timestamps", [
                    [timestamp_table],
                    table_edit_buttons,
                ], font=BIG_FONT, pad=FRAME_PAD),
                pg.Push(),
                info_panel,
            ],
        ], vertical_alignment="top")

        return [
            # Lyrics on left, controls on right
            [lyrics_panel, right_col],
            [pg.Frame("Audio Waveform", [
                [pg.Image(key="-AUDIO_WAVEFORM-")],
            ], font=SMALL_FONT, pad=FRAME_PAD, expand_x=True)],
        ]

    # ── Tab 2: Audio Splitter ───────────────────────────────────

    def _audio_splitter_layout(self):
        checkboxes = pg.Frame("Options", [
            [pg.Checkbox("Ignore the first segment", key="-IGNORE_FIRST_CB-")],
            [pg.Checkbox("Ignore the last segment", key="-IGNORE_LAST_CB-")],
            [pg.Text("Skip rows (comma-separated):", font=INFO_TEXT_FONT)],
            [pg.Input("", size=(30, 1), key="-SKIP_ROWS-", font=INFO_TEXT_FONT,
                       tooltip="e.g. 0,3,7 — segments at these row numbers will be skipped")],
        ], font=SMALL_FONT, pad=FRAME_PAD)

        control_buttons = pg.Frame("Actions", [
            [
                pg.Button("START SPLITTING", key="-START_SPLIT-", size=(16, 1),
                           button_color=("white", "#2E7D32")),
                pg.Button("STOP SPLITTING", key="-STOP_SPLIT-", size=(16, 1),
                           button_color=("white", "#C62828")),
            ],
        ], font=SMALL_FONT, pad=FRAME_PAD)

        info_panel = pg.Frame("Progress", [
            [pg.Text("Total files:", font=SMALL_FONT),
             pg.Text("0", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-TOTAL_NUM_FILES-",
                      justification="center")],
            [pg.Text("Current:", font=SMALL_FONT),
             pg.Text("0", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-CURR_FILE_NUM-",
                      justification="center")],
            [pg.Text("Remaining:", font=SMALL_FONT),
             pg.Text("0", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-REM_FILES-",
                      justification="center")],
            [pg.Text("Elapsed:", font=SMALL_FONT),
             pg.Text("00:00", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-ELAPSED_TIME-",
                      justification="center")],
        ], font=SMALL_FONT, pad=FRAME_PAD)

        timestamp_table = pg.Table(
            values=[[0]],
            headings=["Marked @"],
            max_col_width=25,
            background_color="#E3F2FD",
            auto_size_columns=True,
            display_row_numbers=True,
            justification="right",
            text_color="black",
            num_rows=10,
            alternating_row_color="#FFF9C4",
            key="-TABLE2-",
        )

        return [
            [checkboxes],
            [pg.Text("", size=(0, 0))],
            [pg.ProgressBar(100, orientation="h", size=(50, 20),
                             key="-SPLIT_PROGRESS-", bar_color=("#4CAF50", "#E0E0E0"))],
            [
                control_buttons,
                pg.Frame("Timestamps", [[timestamp_table]],
                         font=SMALL_FONT, pad=FRAME_PAD),
                pg.Push(),
                info_panel,
            ],
        ]

    # ── Tab 3: Create Lyric Images and Videos ───────────────────

    def _lyrics_vid_gen_layout(self):
        img_controls = pg.Frame("Image Generation", [
            [
                pg.Button("START", key="-START_IMG_GEN-", size=BTN_SMALL,
                           button_color=("white", "#2E7D32")),
                pg.Button("STOP", key="-STOP_IMG_GEN-", size=BTN_SMALL,
                           button_color=("white", "#C62828")),
            ],
            [pg.ProgressBar(100, orientation="h", size=(30, 18),
                             key="-IMG_GEN_PROGRESS-",
                             bar_color=("#4CAF50", "#E0E0E0"))],
        ], font=SMALL_FONT, pad=FRAME_PAD)

        vid_controls = pg.Frame("Video Generation", [
            [
                pg.Button("START", key="-START_VID_GEN-", size=BTN_SMALL,
                           button_color=("white", "#2E7D32")),
                pg.Button("STOP", key="-STOP_VID_GEN-", size=BTN_SMALL,
                           button_color=("white", "#C62828")),
            ],
            [pg.ProgressBar(100, orientation="h", size=(30, 18),
                             key="-VID_GEN_PROGRESS-",
                             bar_color=("#4CAF50", "#E0E0E0"))],
        ], font=SMALL_FONT, pad=FRAME_PAD)

        info_panel = pg.Frame("Progress", [
            [pg.Text("Total images:", font=SMALL_FONT),
             pg.Text("0", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-TOTAL_NUM_IMAGES-",
                      justification="center")],
            [pg.Text("Current:", font=SMALL_FONT),
             pg.Text("0", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-CURR_IMAGE_NUM-",
                      justification="center")],
            [pg.Text("Remaining:", font=SMALL_FONT),
             pg.Text("0", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-REM_IMAGES-",
                      justification="center")],
            [pg.Text("Elapsed:", font=SMALL_FONT),
             pg.Text("00:00", font=INFO_TEXT_FONT, size=(6, 1),
                      border_width=1, relief="solid", key="-ELAPSED_TIME_IMG-",
                      justification="center")],
        ], font=SMALL_FONT, pad=FRAME_PAD)

        prep = pg.Frame("Prepare", [
            [pg.Button("Generate durations CSV\nfrom timestamps.csv",
                        key="-GEN_DURATIONS_CSV-", size=(22, 2),
                        button_color=("white", "#1565C0"))],
        ], font=SMALL_FONT, pad=FRAME_PAD)

        return [
            [pg.Text("", size=(0, 0))],
            [prep, img_controls, vid_controls, pg.Push(), info_panel],
        ]

    # ── Main Layout Assembly ────────────────────────────────────

    def setup_layout(self):
        pg.theme("DarkAmber")

        layout_ts_marker = self._ts_marker_layout()
        layout_audio_splitter = self._audio_splitter_layout()
        layout_img_vid_gen = self._lyrics_vid_gen_layout()

        # Nicer file browser with Input field
        file_selector = pg.Frame("Audio File", [
            [
                pg.Input(
                    self.default_audio_path,
                    size=(90, 1),
                    key="-AUDIO_FILE_NAME-",
                    font=INFO_TEXT_FONT,
                    readonly=True,
                    text_color="black",
                    background_color="#FFFDE7",
                ),
                pg.FileBrowse(
                    "Browse...",
                    key="-AUDIO_FILE_BROWSE-",
                    enable_events=True,
                    initial_folder=self.initial_folder,
                    target="-AUDIO_FILE_NAME-",
                    size=(10, 1),
                    button_color=("white", "#1565C0"),
                ),
            ],
        ], font=BIG_FONT, pad=FRAME_PAD, expand_x=True)

        layout = [
            # File selector at top
            [file_selector],
            # Tabs
            [pg.TabGroup(
                [[
                    pg.Tab("  Mark Timestamps  ", layout_ts_marker, key="-TAB1-"),
                    pg.Tab("  Audio Splitter  ", layout_audio_splitter, key="-TAB2-"),
                    pg.Tab("  Lyric Images & Video  ", layout_img_vid_gen,
                           key="-TAB3-"),
                ]],
                key="-TAB_GROUP-",
                font=SMALL_FONT,
                tab_background_color="#424242",
                selected_title_color="#FFD700",
                selected_background_color="#5D4037",
            )],
            # Logging area
            [pg.Frame("Log Output", [
                [pg.Multiline(size=(None, 8), key="-LOGGING_BOX-",
                               autoscroll=True, disabled=True, expand_x=True,
                               font=("Consolas", 10))],
            ], font=SMALL_FONT, pad=FRAME_PAD, expand_x=True)],
            # Close button centered
            [pg.Push(),
             pg.Button("CLOSE", key="-CLOSE_BTN-", size=(14, 1),
                        button_color=("white", "#B71C1C")),
             pg.Push()],
        ]
        return layout
