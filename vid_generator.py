import cv2
import time
import csv
import mutagen.mp3
import moviepy.editor as mpe
import numpy as np
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

class VidGenerator():
    def __init__(self):
        self.im_w = 1920
        self.im_h = 1080
        self.frame_rate = 10.0
        self.video_file_name = 'output.avi'
        self.Fs = 44100
        self.vid_generation_under_progress = False
        self.frame_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.stop_vid_creation_flag = False
  
    def read_image_into_frame(self, ind, curr_duration):
        if(ind == 0):  # for the first frame , display "no_lyrics" image with Om
            if(curr_duration > 20): # if there is no lyrics for 20 secs display no_lyrics_om image
                print(f"Processing Om Image(no lyrics)")
                frame = cv2.imread(f".\\other_files\\no_lyrics_om.png")
            else:  # if there is no lyrics for < 20 secs display Om image
                print(f"Processing Om Image")
                frame = cv2.imread(f".\\other_files\\only_om.png")
        else:
            frame = cv2.imread(f".\\lyric_images\\{ind}.png")
            if(ind == self.total_num_imgs):
                print(f"Processing the last line")
            else:
                print(f"Processing image #{ind}")          
        return frame

    def get_durations_from_csv_file(self):
        durations = []
        file_name = './other_files/lyrics_durations_for_vid_gen.csv'
        # print(file_name)
        with open(file_name, mode='r', newline='') as file:
            reader = csv.reader(file)
            # Reading the data rows. each element in a row is typecasted into a float from string.
            durations = [[float(col) for col in row] for row in reader]
        durations = [x[0] for x in durations]
        return durations
    
    def write_frames(self):
        while not self.stop_event.is_set() or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1)
                self.out.write(frame)
                self.num_frames_written = self.num_frames_written + 1
            except queue.Empty:
                continue
            
    def create_video_writer_object(self):
        # Create a VideoWriter object.
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(self.video_file_name, fourcc, self.frame_rate, (self.im_w, self.im_h))
        if out.isOpened():
            return out
        else:
            print("Failed to open VideoWriter")
            return None
        
    def get_curr_duration_frames_and_frame(self, ind):
        if(ind == self.total_num_imgs):
            curr_start_time_secs = self.total_video_length
        else:
            curr_start_time_secs = self.duration_lyrics[ind]  # in seconds
        curr_duration = curr_start_time_secs - self.prev_curr_start_time_secs
        frame = self.read_image_into_frame(ind, curr_duration)
        # print(type(frame), frame.shape[1], frame.shape[0])
        self.prev_curr_start_time_secs = curr_start_time_secs
        curr_duration_frames = round(curr_duration*self.frame_rate)  # in number of frames for a single line
        return curr_duration_frames, frame
    
    def check_if_stop_button_is_pressed(self):
        if(self.stop_vid_creation_flag == True):
            print("Video generation stopped midway")
            self.vid_generation_under_progress = False
            self.stop_vid_creation_flag = False
            return True
        else:
            return False

    # First line starts at curr_duration_lyrics[0] seconds.
    # 2nd line starts at curr_duration_lyrics[1] seconds and so on...
    def generate_video(self, mp3_file_name):
        print("Generating video with the images of lyrics and selected audio")
        self.vid_generation_under_progress = True
        self.duration_lyrics = self.get_durations_from_csv_file()
        # print(self.duration_lyrics)
        self.total_num_imgs = len(self.duration_lyrics)
        audio = mutagen.mp3.MP3(mp3_file_name)
        self.total_video_length = audio.info.length
        print("total_video_curr_start_time_secs = ",self.total_video_length," secs")

        # Initializing video writer object
        self.out = self.create_video_writer_object()
        if self.out is None:
            return
        
        # Write some frames to the video.
        self.prev_curr_start_time_secs = 0
        self.num_frames_written = 0
        start_time = time.time()
        
        writer_thread = threading.Thread(target=self.write_frames)
        writer_thread.start()
        # self.progress_bar = tqdm(total=int(self.total_video_length*self.frame_rate), mininterval=100)
        # print(int(self.total_video_length*self.frame_rate))
        
        for ind in range(self.total_num_imgs+1):
            curr_duration_frames, frame = self.get_curr_duration_frames_and_frame(ind)
            print(curr_duration_frames)
            for j in range(curr_duration_frames):
                self.frame_queue.put(frame)
                if(self.check_if_stop_button_is_pressed()):
                    return
                
        self.stop_event.set()   # stop the threading as user hasnt interrupted it manually during writing of video frames.
        writer_thread.join()
        self.out.release()  # Release the VideoWriter object.
        self.progress_bar.close()
        print(f"A total of {self.num_frames_written} frames were written to create the Video file. Time taken={time.time()-start_time} secs")

        video = mpe.VideoFileClip("output.avi")     # Create a VideoFileClip object for the AVI file
        audio = mpe.AudioFileClip(mp3_file_name)    # Create an AudioFileClip object for the MP3 file
        
        start_time = time.time()
        final_clip = video.set_audio(audio)   # Combine the video and audio clips
        if(self.check_if_stop_button_is_pressed()):
            return
        
        final_clip.write_videofile("final_video.mp4")   # Export the final clip as an MP4 file
        print(f"Time taken for generating the video file={time.time()-start_time} secs")
        self.vid_generation_under_progress = False
        
    def stop_vid_creation(self):
        if(self.vid_generation_under_progress == True):
            self.stop_vid_creation_flag = True