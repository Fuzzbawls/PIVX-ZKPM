#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 The PIVX developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE.txt or http://www.opensource.org/licenses/mit-license.php.

import os
import signal
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

try:
    from .downloader import Downloader, PARAMS
    from .util import get_default_destination_dir, init_logs
except ImportError:
    from downloader import Downloader, PARAMS
    from util import get_default_destination_dir, init_logs

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

class ParamLine(QWidget):
    def __init__(self, parent, label):
        super(QWidget, self).__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(35, 0, 35, 0)
        self.lbl = QLabel(label[:-7])     # remove ending '.params' from filename
        self.lbl.setFont(QFont('Consolas', 10))
        self.lbl.setMinimumWidth(200)
        layout.addWidget(self.lbl)
        layout.addStretch()
        self.bar = QProgressBar()
        self.bar.setMinimumWidth(250)
        self.bar.setMaximumWidth(250)
        self.bar.setMaximumHeight(15)
        self.bar.setRange(0, 100)
        layout.addWidget(self.bar)
        self.setLayout(layout)

    def updateProgressPercent(self, percent):
        self.bar.setValue(percent)
        #QApplication.processEvents()

    def updateFileVerified(self):
        self.lbl.setStyleSheet("color: green")
        #QApplication.processEvents()




def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit

class MainWidget(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super(QWidget, self).__init__(parent)
        self.destination = get_default_destination_dir()
        self.paramline = {}
        self.initUI()
        # connect buttons
        self.btn_download.clicked.connect(self.onDownload)
        self.btn_destination.clicked.connect(self.onChangeDestination)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 20, 40, 20)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignTop)
        rowtop = QHBoxLayout()

        rowtop.setAlignment(Qt.AlignCenter)
        intro_txt = "This Wizard will download PIVX Zk-SNARK parameters\n"\
                    "and verify their integrity with sha256sum.\n\n"\
                    "If they already exist locally,\n"\
                    "it will only verify their integrity."
        self.lbl_intro = QLabel(intro_txt)
        self.lbl_intro.setAlignment(Qt.AlignCenter)
        rowtop.addWidget(self.lbl_intro)
        self.layout.addLayout(rowtop)
        start_layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Save to: "))
        self.led_destination = QLineEdit()
        self.led_destination.setDisabled(True)
        self.led_destination.setText(self.destination)
        self.led_destination.setMinimumWidth(300)
        #self.led_destination.setAlignment(Qt.AlignHCenter)
        self.led_destination.setFont(QFont('Consolas', 9))
        row1.addWidget(self.led_destination)
        self.btn_destination = QPushButton("Change...")
        self.btn_destination.setMaximumWidth(120)
        row1.addWidget(self.btn_destination)
        start_layout.addLayout(row1)
        self.btn_download = QPushButton("Download")
        self.btn_download.setMinimumWidth(200)
        row2 = QHBoxLayout()
        row2.setAlignment(Qt.AlignCenter)
        row2.addWidget(self.btn_download)
        start_layout.addLayout(row2)
        self.start_layout = QWidget()
        self.start_layout.setLayout(start_layout)
        self.layout.addWidget(self.start_layout)
        self.pbar_layout = QVBoxLayout()
        self.pbar_wdg = QWidget()
        self.pbar_wdg.setLayout(self.pbar_layout)
        self.layout.addWidget(self.pbar_wdg)
        self.setLayout(self.layout)

    def onChangeDestination(self):
        selected_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.destination))
        if selected_dir != "":
            self.destination = selected_dir
            self.led_destination.setText(self.destination)

    def onDownload(self):
        self.start_layout.hide()
        check = True
        if not os.path.exists(self.destination):
            check = False
            os.makedirs(self.destination)
        init_logs(self.destination)
        self.downloader_thread = QThread()
        self.downloader = Downloader(self.destination)
        self.downloader.moveToThread(self.downloader_thread)
        self.downloader.download_progress.connect(self.updateProgressPercent)
        self.downloader.file_verified.connect(self.updateFileVerified)
        if check:
            self.downloader_thread.started.connect(self.downloader.check_params)
        else:
            self.downloader_thread.started.connect(self.downloader.get_params)
        self.downloader_thread.start()

    # Activated by signal download_progress from downloader
    def updateProgressPercent(self, key, percent):
        if key not in self.paramline:
            self.paramline[key] = ParamLine(self, key)
            self.pbar_layout.addWidget(self.paramline[key])
        self.paramline[key].updateProgressPercent(percent)

    # Activated by signal file_verified from downloader
    def updateFileVerified(self, key):
        if key in self.paramline:
            self.paramline[key].updateFileVerified()
        if len(self.paramline) == len(PARAMS):
            self.showCompleted()

    def showCompleted(self):
        self.lbl_intro.hide()
        self.pbar_wdg.hide()
        lbl_finished_txt = "zkSNARK parameters fetched and integrity verified.\n"\
                       "You can now close and delete this application."
        lbl_finished = QLabel(lbl_finished_txt)
        lbl_finished.setAlignment(Qt.AlignCenter)
        lbl_finished.setStyleSheet("color: green")
        self.layout.addWidget(lbl_finished)
        self.btn_close = QPushButton("Close")
        self.btn_close.setMaximumWidth(120)
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.addWidget(self.btn_close)
        self.layout.addLayout(row)
        self.btn_close.clicked.connect(lambda: self.parent.close())



class MainWindow(QMainWindow):
    def __init__(self, app, version, imgDir):
        super().__init__()
        self.app = app
        self.version = version
        self.title = 'ZK-Params Wizard - v.%s' % str(self.version)

        # Register the signal handlers
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)

        # Initialize user interface
        self.initUI(imgDir)
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)
        self.show()
        self.activateWindow()

    def initUI(self, imgDir):
        # Set title and geometry
        self.setWindowTitle(self.title)
        self.resize(500, 180)
        # Set window icon
        self.setWindowIcon(QIcon(os.path.join(imgDir, 'zkpw.png')))
