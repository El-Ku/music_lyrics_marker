"""Entry point — sets up the GUI and runs the main event loop."""

from draw_gui import DrawGui
from gui_control_logic import ControlGui
from config import EVENT_LOOP_TIMEOUT_MS, load_user_config


def main():
    print("Setting up the GUI...")

    # Load persisted user preferences (Feature 9)
    user_config = load_user_config()

    draw_app_gui = DrawGui(
        initial_folder=user_config.get("last_browse_folder", ""),
        default_audio_path=user_config.get("last_audio_path", ""),
    )
    window = draw_app_gui.draw_gui()

    gui_control = ControlGui(draw_app_gui, user_config)
    draw_app_gui.set_controller_object(gui_control)

    # Set initial volume from saved config
    vol = user_config.get("volume", 100)
    window["-VOL_CONTROL-"].update(value=vol)

    # Disable controls until audio is loaded (Feature 11)
    draw_app_gui.set_pre_load_state()

    print("The GUI is ready to use")

    while True:
        event, values = window.read(timeout=EVENT_LOOP_TIMEOUT_MS)
        if not gui_control.check_for_gui_events(event, values):
            break


if __name__ == "__main__":
    main()
