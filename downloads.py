from pathlib import Path
from tkinter import filedialog, Tk
from shutil import disk_usage, rmtree
from gettext import gettext as _
from gettext import ngettext as _N
import subprocess
from subprocess import run
from os import path
from platform import system
import tarfile
import os
import pyzstd
from tqdm import tqdm
import vars
import gui
import versions

def download(url, size):
    free_space_check(size, 'temporary')

    run([vars.ARIA2C_BINARY, '--max-connection-per-server=16', '-UTF2CDownloader2023-05-27', '--allow-piece-length-change=true', '--disable-ipv6=true', '--max-concurrent-downloads=16', '--optimize-concurrent-downloads=true', '--check-certificate=false', '--check-integrity=true', '--auto-file-renaming=false', '--continue=true', '--allow-overwrite=true', '--console-log-level=error', '--summary-interval=0', '--bt-hash-check-seed=false', '--seed-time=0',
    '-d' + vars.TEMP_PATH, url], check=True)


def extract(filename, endpath, size):
    free_space_check(size, 'permanent')

    gui.message(_("Extracting the downloaded archive, please wait patiently."), 1, True)
    class ZstdTarFile(tarfile.TarFile):
        def __init__(self, name, mode='r', *, level_or_option=None, zstd_dict=None, **kwargs):
            self.zstd_file = pyzstd.ZstdFile(name, mode,
                                    level_or_option=level_or_option,
                                    zstd_dict=zstd_dict)
            try:
                super().__init__(fileobj=self.zstd_file, mode=mode, **kwargs)
            except:
                self.zstd_file.close()
                raise

        def close(self):
            try:
                super().close()
            finally:
                self.zstd_file.close()

    # read .tar.zst file (decompression)
    with ZstdTarFile(path.join(vars.TEMP_PATH, filename), mode='r') as tar:
        for member in tqdm(iterable=tar.getmembers(), total=len(tar.getmembers())):
            tar.extract(member=member, path=endpath)

def butler_verify(signature, gamedir, remote):
    run([vars.BUTLER_BINARY, 'verify', signature, gamedir, '--heal=archive,' + remote], check=True)

def butler_patch(url, staging_dir, patchfilename, gamedir):
    if Path(staging_dir).exists() and Path(staging_dir).is_dir():
        rmtree(staging_dir)
    run([vars.ARIA2C_BINARY, '--max-connection-per-server=16', '-UTF2CDownloader2023-05-27', '--allow-piece-length-change=true', '--disable-ipv6=true', '--max-concurrent-downloads=16', '--optimize-concurrent-downloads=true', '--check-certificate=false', '--check-integrity=true', '--auto-file-renaming=false', '--continue=true', '--allow-overwrite=true', '--console-log-level=error', '--summary-interval=0', '--bt-hash-check-seed=false', '--seed-time=0',
    '-d' + vars.TEMP_PATH, url], check=True)
    gui.message(_("Patching your game with the new update, please wait patiently."), 1, True)
    run([vars.BUTLER_BINARY, 'apply', '--staging-dir=' + staging_dir, path.join(vars.TEMP_PATH, patchfilename), gamedir], check=True)
    if Path(staging_dir).exists() and Path(staging_dir).is_dir():
        rmtree(staging_dir)


def pretty_size(bytes):
    if bytes < 100:
        return _N("%s byte", "%s bytes", bytes) % bytes
    if bytes < 1000000:
        return _("%.2f kB") % (bytes/1000)
    if bytes < 1000000000:
        return _("%.2f MB") % (bytes/1000000)
    if bytes < 1000000000000:
        return _("%.2f GB") % (bytes/1000000000)
    if bytes < 1000000000000000:
        return _("%.2f TB") % (bytes/1000000000000)
    if bytes < 1000000000000000000:
        return _("%.2f PB") % (bytes/1000000000000000)

def free_space_check(size, cat):
    if cat == 'temporary':
        if disk_usage(vars.TEMP_PATH)[2] < size:
            if gui.message_yes_no(_("You don't have enough free space in your computer's default temporary folder for this. A minimum of %s is required. Select alternate temporary folder?") % pretty_size(size), 1):
                root = Tk()
                root.withdraw()
                try:
                    while disk_usage(vars.TEMP_PATH)[2] < size:
                        vars.TEMP_PATH = filedialog.askdirectory()
                        if disk_usage(vars.TEMP_PATH)[2] < size:
                            gui.message(_("Still not enough space at specified path. Retry, and select a different drive if available."))
                except TypeError:
                    gui.message_error(_("Folder selection prompt closed without choosing any path. Exiting..."), 1)


    if cat == 'permanent':
        if disk_usage(vars.INSTALL_PATH)[2] < size and vars.INSTALLED is False:
            gui.message_error(_("You don't have enough free space for the extraction. A minimum of %s at your chosen extraction site is required.") % pretty_size(size), 1)

def prepare_symlink():
    for s in vars.TO_SYMLINK:
        if path.isfile(vars.INSTALL_PATH + s[1]) and not path.islink(vars.INSTALL_PATH + s[1]):
            os.remove(vars.INSTALL_PATH + s[1])

def do_symlink():
    if system() == "Windows":
        return

    for s in vars.TO_SYMLINK:
        if not path.isfile(vars.INSTALL_PATH + s[1]):
            os.symlink(vars.INSTALL_PATH + s[0], vars.INSTALL_PATH + s[1])

def install():
    version_json = versions.get_version_list()["versions"]
    last_key = list(version_json.keys())[-1]
    lastver = version_json[last_key]

    prepare_symlink()

    gui.message(_("Getting the archive..."), 0, True)

    download(vars.SOURCE_URL + lastver["url"], lastver["presz"])

    if not path.isdir(vars.INSTALL_PATH):
        gui.message_error(_("The specified extraction location does not exist."), 1)

    extract(lastver["file"], vars.INSTALL_PATH, lastver["postsz"])

    do_symlink()

def update():
    """
    The simplest part of all of this.
    We already know the user wants to update, can update, and the local version we get the patch from.
    So at this point, it's just downloading, healing, and applying.
    """

    prepare_symlink()

    # Prepare some variables
    local_version = versions.get_installed_version()

    patch_json = versions.get_version_list()["patches"]
    patch_url = patch_json[local_version]["url"]
    patch_file = patch_json[local_version]["file"]
    patch_tempreq = patch_json[local_version]["tempreq"]

    # Filesize check for butler-staging...
    # patch_tempreq is NOT the size of the patch, this is the size of the staging folder when commiting
    # Even though this is literally temporary, we say this is "permanent" since we want to check and use the same drive as the game
    free_space_check(patch_tempreq, 'permanent')

    version_json = versions.get_version_list()["versions"]
    signature_url = version_json[versions.get_installed_version()]["signature"]
    heal_url = version_json[versions.get_installed_version()]["heal"]

    # Finally, verify and heal with the information we've gathered.
    butler_verify(vars.SOURCE_URL + signature_url, vars.INSTALL_PATH + '/tf2classic', vars.SOURCE_URL + heal_url)
    butler_patch(vars.SOURCE_URL + patch_url, vars.INSTALL_PATH + '/butler-staging', patch_file, vars.INSTALL_PATH + '/tf2classic')

    do_symlink()
