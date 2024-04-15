"""
This module is primarily related to helping
the rest of the application find what it needs.

This includes the path to the user's sourcemods
folder, the binary locations for things like Aria2
depending on their platform, etc.
"""
import sys
from os import environ, getcwd, path
from platform import system
from shutil import which
from rich import print
from gettext import gettext as _
import gui
import vars
if system() == 'Windows':
    import winreg


REGISTRY = 0
REGISTRY_KEY = 0

def sourcemods_path():
    """
    Find path to sourcemod folder.
    """
    if system() == 'Windows':
        try:
            global REGISTRY
            global REGISTRY_KEY
            if REGISTRY == 0:
                REGISTRY = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                REGISTRY_KEY = winreg.OpenKeyEx(REGISTRY, r'SOFTWARE\Valve\Steam', access=winreg.KEY_ALL_ACCESS)

            value = winreg.QueryValueEx(REGISTRY_KEY, 'SourceModInstallPath')
            return value[0]
        except Exception:
            return None
    else:
        try:
            sourcepath = None
            with open(path.expanduser(r'~/.steam/registry.vdf'), encoding="utf-8") as file:
                for _, line in enumerate(file):
                    if 'SourceModInstallPath' in line:
                        sourcepath = line[line.index('/home'):-1].replace(r'\\', '/')
                        break
                file.close()
            return sourcepath
        except Exception:
            return None

def setup_path_script():
    """
    Choose setup path, but without user interference.
    """
    if len(sys.argv) > 2:
        vars.INSTALL_PATH = sys.argv[2].rstrip('"')
    else:
        vars.INSTALL_PATH = sourcemods_path()
        if vars.INSTALL_PATH is not None:
            vars.INSTALL_PATH = vars.INSTALL_PATH.rstrip('"')
        else:
            vars.INSTALL_PATH = getcwd()

        gui.message(_("Installation location not specified, will assume: %s") % vars.INSTALL_PATH)

def setup_path(manual_path):
    """
    Choose setup path.
    """
    confirm = False
    install_path = sourcemods_path()
    if install_path is not None:
        vars.INSTALL_PATH = install_path.rstrip('\"')

    smodsfound = isinstance(vars.INSTALL_PATH, str)
    if smodsfound is True and manual_path is not True:
        if vars.GUI_MODE:
            if gui.message_yes_no(_("Sourcemods folder was automatically found at:\n%s\n\nDoes that look correct?") % vars.INSTALL_PATH):
                confirm = True
            else:
                setup_path(True)
                return
        else:
            gui.message(_("Sourcemods folder was automatically found at:\n%s") % vars.INSTALL_PATH)
            if gui.message_yes_no(_("Does that look correct?")):
                confirm = True
            else:
                setup_path(True)
                return
    else:
        gui.message(_("WARNING: Steam's sourcemods folder has not been found, or you chose not to use it."))
        if gui.message_yes_no(_("Would you like to extract in %s? You must move it to your sourcemods manually.") % getcwd()):
            vars.INSTALL_PATH = getcwd()
            confirm = True
        else:
            vars.INSTALL_PATH = gui.message_dir(_("Please, enter the location in which TF2 Classic will be installed to.\n"))

    if not confirm:
        if not gui.message_yes_no(_("TF2 Classic will be installed in %s\nDo you accept?") % vars.INSTALL_PATH):
            if vars.GUI_MODE:
                gui.message_end(_("We have nothing to do. Goodbye!"), 0)
            else:
                print(_("Reinitialising...\n"))
                setup_path(False)

def setup_binaries():
    """
    Select paths for required binaries.
    """
    if system() == 'Windows':
        # When we can detect that we're compiled using PyInstaller, we use their
        # suggested method of determining the location of the temporary runtime folder
        # to point to Aria2 and Butler.
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            vars.ARIA2C_BINARY = path.abspath(path.join(path.dirname(__file__), 'aria2c.exe'))
            vars.BUTLER_BINARY = path.abspath(path.join(path.dirname(__file__), 'butler.exe'))
            vars.ICO_PATH = path.abspath(path.join(path.dirname(__file__), 'tf2c.ico'))
            vars.BANNER_PATH = path.abspath(path.join(path.dirname(__file__), 'banner.png'))
        else:
            # When running as a script, we just select the Binaries folder directly for Aria2 and Butler.
            vars.ARIA2C_BINARY = 'Binaries/aria2c.exe'
            vars.BUTLER_BINARY = 'Binaries/butler.exe'
            vars.ICO_PATH = 'tf2c.ico'
            vars.BANNER_PATH = 'banner.png'
    else:
        # If we're running on Linux...
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            vars.ARIA2C_BINARY = path.abspath(path.join(path.dirname(__file__), 'aria2c'))
            vars.BUTLER_BINARY = path.abspath(path.join(path.dirname(__file__), 'butler'))
            vars.ICO_PATH = path.abspath(path.join(path.dirname(__file__), 'tf2c.ico'))
            vars.BANNER_PATH = path.abspath(path.join(path.dirname(__file__), 'banner.png'))
        else:
            vars.BUTLER_BINARY = 'Binaries/butler'
            vars.ARIA2C_BINARY = 'Binaries/aria2c'
            vars.ICO_PATH = 'tf2c.ico'
            vars.BANNER_PATH = 'banner.png'
