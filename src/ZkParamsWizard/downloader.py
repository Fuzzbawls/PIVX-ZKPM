#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 The PIVX developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE.txt or http://www.opensource.org/licenses/mit-license.php.

import hashlib
import logging
import os
import requests
from tqdm import tqdm

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

try:
    from .util import HOST_OS
except ImportError:
    from util import HOST_OS

PARAMS = {
    "sapling-spend.params" : {
        "sha256" : "8e48ffd23abb3a5fd9c5589204f32d9c31285a04b78096ba40a79b75677efc13",
        "ipfs_bhash" : "QmaaA4e7C4QkxrooomzmrjdFgv6WXPGpizj6gcKxdRUnkW"
    },
    "sapling-output.params" : {
        "sha256" : "2f0ebbcbb9bb0bcffe95a397e7eba89c29eb4dde6191c339db88570e3f3fb0e4",
        "ipfs_bhash" : "QmQ8E53Fpp1q1zXvsqscskaQXrgyqfac9b3AqLxFxCubAz"
    },
    "sprout-groth16.params" : {
        "sha256" : "b685d700c60328498fbde589c8c7c484c722b788b265b72af448a5bf0ee55b50",
        "ipfs_bhash" : "QmWFuKQ1JgwJBrqYgGHDEmGSXR9pbkv51NYC1yNUaWwpMU"
    }
}

PARAMS_URL = "https://z.cash/downloads/"

DOWNLOADING = 1
DOWNLOADED = 0

if HOST_OS == 'Windows':
    import win32con, win32file, pywintypes

    LOCK_SH = 0  # default flag
    LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
    LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
    __overlapped = pywintypes.OVERLAPPED()

    def lock(file, flags):
        try:
            hfile = win32file._get_osfhandle(file.fileno())
            win32file.LockFileEx(hfile, flags, 0, 0xffff0000, __overlapped)
        except:
            logging.exception("Unable to lock : %s", file)

    def unlock(file):
        try:
            hfile = win32file._get_osfhandle(file.fileno())
            win32file.UnlockFileEx(hfile, 0, 0xffff0000, __overlapped)
        except:
            logging.exception("Unable to unlock : %s", file)

elif HOST_OS == 'Linux' or HOST_OS == 'Darwin':
    import fcntl
    LOCK_SH = fcntl.LOCK_SH
    LOCK_NB = fcntl.LOCK_NB
    LOCK_EX = fcntl.LOCK_EX

    def lock(file, flags):
        try:
            fcntl.flock(file.fileno(), flags)
        except:
            logging.exception("Unable to lock : %s", file)

    def unlock(file):
        try:
            fcntl.flock(file.fileno(), fcntl.LOCK_UN)
        except:
            logging.exception("Unable to unlock : %s", file)

else:
    raise Exception(" %s is not currently supported.", HOST_OS)

class Downloader(QObject):
    # filename progress percent
    download_progress = pyqtSignal(str, int)
    file_verified = pyqtSignal(str)

    def __init__(self, dest_dir, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.dest_dir = dest_dir

    def use_https(self, filename):
        path = os.path.join(self.dest_dir, filename + ".dl")
        response = requests.get(PARAMS_URL + filename, stream=True)
        size = 0
        total_size = int(response.headers['Content-Length'])
        block_size = 1024

        logging.info("Retrieving : %s", PARAMS_URL + filename)
        logging.info("Length : ~ %s KB [ %s ]", str(total_size / block_size), response.headers['Content-Type'])
        logging.info("Saving to : %s", path)
        logging.debug(response.headers)

        with open(path, "wb") as handle:
            lock(handle, LOCK_EX)
            for chunk in tqdm(response.iter_content(block_size), total=int(total_size // block_size), unit="KB",
                              desc=filename + ".dl"):
                if chunk:
                    handle.write(chunk)
                    size += len(chunk)
                    self.download_progress.emit(filename, int((size * 100) // total_size))
                else:
                    logging.warning("Received response that was not content data.")
            unlock(handle)

        logging.info(" '%s' saved [%d/%d]", filename, size, total_size)

        if size == total_size:
            self.verify_param_file(filename, DOWNLOADING)

    def download_param_file(self, filename):
        # only HTTPS for now
        self.use_https(filename)

    def verify_param_file(self, filename, download_state):
        path = os.path.join(self.dest_dir, filename)
        if download_state == DOWNLOADING:
            path += ".dl"

        logging.info("Checking SHA256 for: %s", path)
        with open(path, 'rb') as f:
            try:
                contents = f.read()
            except:
                logging.exception("Unable to read in data blocks to verify SHA256 for: %s", path)

            if hashlib.sha256(contents).hexdigest() != PARAMS[filename]["sha256"]:
                logging.error("Download failed: SHA256 on %s does NOT match.", path)
                return

            if download_state == DOWNLOADING:
                logging.info("Download successful!")
                try:
                    os.rename(path, path[:-3])
                except:
                    logging.exception("Unable to rename file:", path)
                logging.debug("Renamed '%s' -> '%s' \n", path, path[:-3])

            if download_state == DOWNLOADED:
                logging.info("%s: OK", path)

            self.file_verified.emit(filename)

    @pyqtSlot()
    def get_params(self):
        print("In get params")
        for key in PARAMS:
            self.download_param_file(key)

    @pyqtSlot()
    def check_params(self):
        print("In check params")
        for key in PARAMS:
            if os.path.exists(os.path.join(self.dest_dir, key)):
                self.download_progress.emit(key, 100)
                self.verify_param_file(key, DOWNLOADED)
            else:
                logging.warning("%s does not exist and will now be downloaded...", str(os.path.join(self.dest_dir, key)))
                self.download_param_file(key)
