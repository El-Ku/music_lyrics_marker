from just_playback import Playback

# this class just deals with basic audio manipulations.
class AudioPlay():
    # creates an object for managing playback of a single audio file
    def __init__(self):
        self.playback = Playback() 
    
    # in case a different file is selected after the initial run
    def update_playback_file(self, file_name):
        self.playback.load_file(file_name)
        
    # go backward or forward during the playback
    def move_curr_position(self, secs_to_move):
        self.playback.seek(self.playback.curr_pos + secs_to_move)
    
    # adjust the volume.
    def set_volume(self, new_volume):
        self.playback.set_volume(new_volume)
        
        