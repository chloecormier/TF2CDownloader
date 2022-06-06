from sys import stdin, exit, argv
from platform import system
from shutil import which
from subprocess import run
import os
import vars
import gui
import setup
import install

# PyInstaller offers no native way to select which application you use for the console.
# Instead, it uses the system default, which is cmd.exe at time of writing.
# This hack checks if Windows Terminal is installed. If it is, and if the application
# is launched with cmd.exe instead, it relaunches the application in WT instead.
#
# We should find a more reliable way to detect this so it doesn't break if you're
# running it from a relative path (like Downloads\TF2CDownloaderWindows.exe),
# or if the executable is named something different. Surely there's a variable
# that just corresponds to the absolute path of the executable.
if system() == 'Windows':
	if which('wt') is not None and os.environ.get("WT_SESSION") is None:
		run(['wt', argv[0]], check=True)
		exit()

# This is mainly for Linux, because it's easy to launch it by double-clicking it, which would
# run it in the background and not show any output. PyInstaller has no way to force a terminal
# open for this on Linux. We could implement something similar to what we do to force using WT,
# but it's not a priority right now since Linux users can figure out how to use the terminal.
def sanity_check():
	if not stdin or not stdin.isatty():
		print("Looks like we're running in the background. We don't want that, so we're exiting.")
		exit(1)

sanity_check()
setup.setup_path()
setup.setup_binaries()
install.tf2c_download()
install.tf2c_extract()

gui.message_end("The installation has successfully completed. Remember to restart Steam!", 0)
