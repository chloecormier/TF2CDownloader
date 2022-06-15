"""
UX-related functions, like showing messages,
asking questions, generally handling any sort
of communication or interactivity with the user.
"""
from os import path as os_path, makedirs, rmdir
from time import sleep
from sys import exit
import os
from rich import print

def message(msg: str, delay = 0):
    """
    Show a message to user.
    Delay stops program for specified amount of seconds.
    """
    print("[bold yellow]" + msg)
    sleep(delay)

def message_yes_no(question, default = None):
    """
    Show a message to user and get yes/no answer.
    "default" sets "yes" as default answer if true, "no" if false.
    """
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("[bold blue]Please respond with 'yes' or 'no' " "(or 'y' or 'n').[/bold blue]")


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
        directory = input(msg + ': ')
        if os_path.isdir(directory):
            return directory
        try:
            # great way to verify that the directory is at least valid
            makedirs(directory)
            rmdir(directory) # lol
            return directory
        except Exception:
            pass

def message_end(msg, code):
    """
    Show a message and exit.
    """
    print("[bold green]" + msg)
    input("Press Enter to exit.")
    if os.environ.get("WT_SESSION"):
        print("[bold]You are safe to close this window.")
    exit(code)
