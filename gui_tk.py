
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import sys
import versions
import gui
import downloads
import troubleshoot
import vars
from gettext import gettext as _

# Define a global variable to hold the Tkinter window instance
global_root_tk = None

# Function to create or get the global Tkinter window
def get_global_root():
    global global_root_tk
    if global_root_tk is None:
        global_root_tk = tk.Tk()
    return global_root_tk

def toggle_global_root_buttons():
    rootTKWindow = get_global_root()
    frame = rootTKWindow.configure()

def message_tk(msg: str):
    # Create the main window
    messagebox.showinfo("TF2CDownloader", msg)

def main_menu_tk():
    def set_button_state(buttonstate: str):
        for frame in get_global_root().winfo_children():
            if frame.winfo_name() == "globalbuttonframe":
                for button in frame.winfo_children():
                    button.configure(state=buttonstate)

    def threaded_install_tk():
        set_button_state('disabled')
        downloads.install()
        troubleshoot.apply_blacklist()
        gui.message_end(_("The installation has successfully completed. Remember to restart Steam!"), 0)
        set_button_state('enabled')

    def threaded_update_tk():
        set_button_state('disabled')
        if versions.check_for_updates():
            downloads.update()
            message_error_tk("Error!", 1)
            gui.message_end(_("The update has successfully completed."), 0)
        else:
            downloads.install()
            troubleshoot.apply_blacklist()
            gui.message_end(_("The installation has successfully completed. Remember to restart Steam!"), 0)
        set_button_state('enabled')
  
    def threaded_validate_tk():
        set_button_state('disabled')
        downloads.install()
        troubleshoot.apply_blacklist()
        version_json = versions.get_version_list()["versions"]
        downloads.butler_verify(vars.SOURCE_URL + version_json[versions.get_installed_version()]["signature"], vars.INSTALL_PATH + '/tf2classic', vars.SOURCE_URL + version_json[versions.get_installed_version()]["heal"])
        gui.message_end(_("The verification process has completed, and any corruption has been repaired."), 0)
        set_button_state('enabled')

    def install_click():
        thread = threading.Thread(target=threaded_install_tk)
        thread.start()

    def update_click():
        thread = threading.Thread(target=threaded_update_tk)
        thread.start()

    def validate_click():
        thread = threading.Thread(target=threaded_validate_tk)
        thread.start()

    # Create the main window
    rootTKWindow = get_global_root()
    rootTKWindow.title("TF2CDownloader")
    rootTKWindow.iconbitmap(vars.ICO_PATH)
    rootTKWindow.resizable(False, False)

    # Load the banner image
    image = Image.open(vars.BANNER_PATH)
    # Resize the image to desired dimensions
    image = image.resize((677, 163))
    photo = ImageTk.PhotoImage(image)

    # Create a banner label with the image
    banner = tk.Label(rootTKWindow, image=photo)
    banner.image = photo
    banner.pack(fill=tk.X)

    # Apply a modern Windows-style theme
    style = ttk.Style()
    style.theme_use("vista")

    # Create a frame for the buttons
    button_frame = ttk.Frame(rootTKWindow, name="globalbuttonframe")
    button_frame.pack(pady=20)

    # Create buttons
    install_button = ttk.Button(button_frame, text="Install", width=15, command=install_click)
    install_button.grid(row=0, column=0, padx=10)

    update_button = ttk.Button(button_frame, text="Update", width=15, command=update_click)
    update_button.grid(row=0, column=1, padx=10)

    validate_button = ttk.Button(button_frame, text="Validate", width=15, command=validate_click)
    validate_button.grid(row=0, column=2, padx=10)

    rootTKWindow.mainloop()
    sys.exit(0)

def message_yes_no_tk(msg: str) -> bool:
    return messagebox.askyesno("TF2CDownloader", msg)

def message_end_tk(msg, code):
    messagebox.showinfo("TF2CDownloader", msg)
    rootTKWindow = get_global_root()
    if rootTKWindow is not None:
        rootTKWindow.quit()

    sys.exit(code)

def message_error_tk(msg, code):
    messagebox.showerror("TF2CDownloader Error!", msg)
    rootTKWindow = get_global_root()
    if rootTKWindow is not None:
        rootTKWindow.quit()
