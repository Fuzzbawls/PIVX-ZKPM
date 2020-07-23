#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 The PIVX developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE.txt or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import platform

#get system information to setup according platform lock and unlock methods
HOST_OS = platform.system()

def get_default_destination_dir():
    dest_dir = 	os.path.expanduser('~')
    if HOST_OS == 'Windows':
        dest_dir += "\\AppData\\Roaming\\ZcashParams\\"
    elif HOST_OS == 'Linux':
        dest_dir += r"/.zcash-params/"
    elif HOST_OS == 'Darwin':
        dest_dir += r"/Library/Application Support/ZcashParams/"
    else:
        raise Exception(" %s is not currently supported.", HOST_OS)
    return dest_dir

def init_logs(dest_dir):
    filename = os.path.join(dest_dir, "logs.txt")
    filemode = 'w'
    format = '%(asctime)s - %(levelname)s - %(threadName)s | %(message)s'
    level = logging.DEBUG
    logging.basicConfig(filename=filename,
                        filemode=filemode,
                        format=format,
                        level=level
                        )
