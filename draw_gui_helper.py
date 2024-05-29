# a set of helper functions. Used by draw_gui class.

class DrawGuiHelper():
    def __init__(self):
        pass  # nothing to initialize
        
    # convert to seconds to time format: hh:mm:ss
    def sec2_timestring(self, secs_in):
        secs_in = int(secs_in)
        m, s = divmod(secs_in, 60) 
        if(m < 60):
            time_string = "{:02d}:{:02d}".format(m, s) 
        else:
            (h,m) = divmod(m, 60) 
            time_string = "{:02d}:{:02d}:{:02d}".format(h, m, s) 
        return time_string
            
    # the float values are converted to formatted string with only 3 fractionals. For table.
    def format_floats_for_table(self, marked_ts_array):
        marked_ts_string = []
        if(marked_ts_array == [[]]):
            marked_ts_string = [["0.0","0.0"]]
        else:
            for i in range(len(marked_ts_array)):
                marked_ts_string.append([f"{marked_ts_array[i][0]:.3f}", f"{marked_ts_array[i][1]:.3f}"])
        return list(reversed(marked_ts_string))
    
    # when we go backward in the payback, remove some latest values from the marked_ts_array array.
    def remove_outdated_timestamps(self, curr_time, marked_ts_array):
        list_ts = [x[0] for x in marked_ts_array]
        index = len(marked_ts_array)
        # print("list_ts 1: ",list_ts)
        while index >= 1:
            if(curr_time <= list_ts[-1]):
                list_ts.pop()
                marked_ts_array.pop()
                index = len(list_ts)
            else:  
                break
        if(marked_ts_array == []):
            marked_ts_array = [[]]
        return marked_ts_array  # num_lines_marked and marked timestamps