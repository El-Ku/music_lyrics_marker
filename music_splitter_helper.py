from pydub import AudioSegment
import time

class MusicSplitterHelper():
    def __init__(self, draw_gui_object):
        self.stop_audio_splitting_flag = False
        self.draw_gui_class = draw_gui_object
    
    def split_audios(self, file_name, marked_timestamps, ignore_first, ignore_last):
        start_time_secs = time.time()
        self.stop_audio_splitting_flag = False
        audio = AudioSegment.from_mp3(file_name)
        timestamps = [row[0] for row in marked_timestamps]
        if(ignore_first == False):
            timestamps.insert(0,0)  #starting timestamp
        if(ignore_last == False):
            timestamps.append(len(audio)/1000)  # total playtime
        self.draw_gui_class.update_table_music_splitter(timestamps)
        for i in range(len(timestamps) - 1):
            self.draw_gui_class.update_time_boxes_music_splitter(len(timestamps)-1, i, time.time()-start_time_secs)
            if(self.stop_audio_splitting_flag == False):
                start_time = timestamps[i] * 1000  # Convert to milliseconds
                end_time = timestamps[i + 1] * 1000  # Convert to milliseconds
                segment = audio[start_time:end_time]
                segment.export(f"Split_Audios\segment_{i+1}.mp3", format="mp3")
                print(f"Segment {i+1} saved from {timestamps[i]}s to {timestamps[i+1]}s")
            else:
                self.stop_audio_splitting_flag = False
                print("The thread to split audio file was stopped successfully")
                self.draw_gui_class.update_time_boxes_music_splitter(len(timestamps)-1, i-1, time.time()-start_time_secs)
                return
        print("The bigger audio file was successfully splitted into smaller audio files")
        self.draw_gui_class.update_time_boxes_music_splitter(len(timestamps)-1, i, time.time()-start_time_secs)
        
    def stop_audio_splitting(self):
        self.stop_audio_splitting_flag = True    