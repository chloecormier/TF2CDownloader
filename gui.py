"""
UX-related functions, like showing messages,
asking questions, generally handling any sort
of communication or interactivity with the user.
"""
from os import environ, makedirs, path, rmdir
import sys
from time import sleep
from gettext import gettext as _
import traceback
from rich import print
import vars
import downloads
import versions
import troubleshoot
import gui_tk
from tkinter import filedialog
import os

def message(msg, delay = 0, consoleonly = False):
    """
    Show a message to user.
    Delay stops program for specified amount of seconds.
    """
    if vars.GUI_MODE and not consoleonly:
        gui_tk.message_tk(msg)
        return
    
    print("[bold yellow]" + msg)
    if not vars.SCRIPT_MODE:
        sleep(delay)

def main_menu():
    if vars.GUI_MODE:
        gui_tk.main_menu_tk()
        return
    
    print(_("""Welcome to TF2CDownloader. Enter a number to continue.\n
        1 - Install or reinstall the game
        2 - Check for and apply any available updates
        3 - Verify and repair game files"""))
    user_choice = input()
    if user_choice == '1':
        message(_("Starting the download for TF2 Classic... You may see some errors that are safe to ignore."), 3)
        downloads.install()
        troubleshoot.apply_blacklist()
        message_end(_("The installation has successfully completed. Remember to restart Steam!"), 0)

    elif user_choice == '2':
        if versions.check_for_updates():
            downloads.update()
            message_end(_("The update has successfully completed."), 0)
        else:
            message(_("Starting the download for TF2 Classic... You may see some errors that are safe to ignore."), 3)
            downloads.install()
            troubleshoot.apply_blacklist()
            message_end(_("The installation has successfully completed. Remember to restart Steam!"), 0)

    elif user_choice == '3':
        version_json = versions.get_version_list()["versions"]
        downloads.butler_verify(vars.SOURCE_URL + version_json[versions.get_installed_version()]["signature"], vars.INSTALL_PATH + '/tf2classic', vars.SOURCE_URL + version_json[versions.get_installed_version()]["heal"])
        message_end(_("The verification process has completed, and any corruption has been repaired."), 0)

    else:
        message(_("Invalid choice. Please retry."))
        main_menu()


def message_yes_no(msg: str, default: bool = None, script_mode_default_override:bool = None) -> bool:
    """
    Show a message to user and get yes/no answer.
    """
    if vars.GUI_MODE:
        choice_tk = gui_tk.message_yes_no_tk(msg)
        return choice_tk
    
    if vars.SCRIPT_MODE:
        # Display msg even though we are in script mode, this because it might
        # contain useful information.
        print(msg)
        print(_("The application is in script mode, using default choice."))
        if script_mode_default_override is not None:
            return script_mode_default_override
        return default

    valid = {"yes": True, "no": False, "y": True, "n": False}

    localyes = _("yes")
    localno = _("no")
    valid[localyes] = True
    valid[localyes[0]] = True
    valid[localno] = False
    valid[localno[0]] = False

    prompt = _(" {y/n}")
    if default:
        prompt = _(" {Y/n}")
    elif default is not None:
        prompt = _(" {y/N}")
    msg += prompt

    while True:
        print(msg)
        choice = input().lower()
        if default is not None and choice == "":
            return default
        if choice in valid:
            return valid[choice]
        print(_("[bold blue]Please respond with 'yes' or 'no' (or 'y' or 'n').[/bold blue]"))


def message_input(msg):
    """
    Show a message and get input from user.
    """
    return input(msg + ' >')

def message_dir(msg):
    """
    Show a message and ask for a directory.
    """
    while True:
        if vars.GUI_MODE:
            dir = filedialog.askdirectory()
        else:
            dir = input(msg + ": ")
        if dir.count("~") > 0:
            dir = path.expanduser(dir)
        if dir.count("$") > 0:
            dir = path.expandvars(dir)
        if path.isdir(dir):
            return dir
        try:
            makedirs(dir)
            rmdir(dir)
            return dir
        except Exception:
            pass

def message_end(msg, code, consoleonly = False):
    """
    Show a message and exit.
    """
    if vars.GUI_MODE and not consoleonly:
        gui_tk.message_end_tk(msg, code)
    
    print("[bold green]" + msg)
    if not vars.SCRIPT_MODE:
        input(_("Press Enter to exit."))
    sys.exit(code)

def message_error(msg, code, consoleonly = False):
    """
    Show an error and exit.
    """
    traceback.print_exc()
    print("[bold red]" + msg)
    print(_("[italic magenta]----- Exception details above this line -----"))
    print(_("[bold red]:warning: The program has failed. Post a screenshot in #technical-issues on the Discord. :warning:[/bold red]"))
    if os.environ.get("WT_SESSION"):
        print(_("[bold]You are safe to close this window."))
    else:
        if not vars.SCRIPT_MODE and not vars.GUI_MODE:
            input(_("Press Enter to exit."))

    if vars.GUI_MODE and not consoleonly:
        gui_tk.message_error_tk(msg, code)
    
    sys.exit(code)