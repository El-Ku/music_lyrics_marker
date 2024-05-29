from draw_gui import DrawGui
from gui_control_logic import ControlGui
import PySimpleGUI as pg
import time

def main():
    draw_app_gui = DrawGui()
    window = draw_app_gui.draw_gui()
    gui_control = ControlGui(draw_app_gui)
    draw_app_gui.set_controller_object(gui_control)
    
    while True:
        # even if the window doesnt have an event, because of the 1000 msec timeout, it will be called once every second.
        event, values = window.read(timeout=1000)
        # we need to exit from the "while true" loop when the window is closed.
        stop = gui_control.check_for_gui_events(event, values)
        if(stop):
            time.sleep(0.01)  # loop again after waiting for 10 msec
        else:
            break
    
if __name__ == "__main__":
    main()
    