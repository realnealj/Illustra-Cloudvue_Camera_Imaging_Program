import subprocess
import time


def open_portal_file_manager_and_type_path():
    # File path to type
    file_path = "/home/neal/PycharmProjects/Cloudvue_Camera_Imaging/Firmware/Illustra.Ess4.01.02.10.5982.tar.gz"

    # Use xdg-desktop-portal to open the file manager
    subprocess.run(["xdg-open", "."])  # Open the current directory
ing/Firmware/Illustra.Ess4.01.02.10.5982.tar.gz

    # Allow time for the file manager to open
    time.sleep(2)

    # Use xdotool to type the file path and simulate pressing Enter
    try:
        subprocess.run(["xdotool", "type", file_path], check=True)
        subprocess.run(["xdotool", "key", "Return"], check=True)
        print("Path typed successfully.")
    except Exception as e:
        print(f"An error occurred while typing the path: {e}")


# Execute the function
open_portal_file_manager_and_type_path()
