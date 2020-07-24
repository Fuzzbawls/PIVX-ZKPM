#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 The PIVX developers
# Distributed under the MIT software license, see the accompanying
# file LICENSE.txt or http://www.opensource.org/licenses/mit-license.php.

import os
import signal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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

from downloader import Downloader
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
        layout.setContentsMargins(15, 0, 15, 0)
        lbl = QLabel(label[:-7])     # remove ending '.params' from filename
        lbl.setFont(QFont('Consolas', 10))
        layout.addWidget(lbl)
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
        QApplication.processEvents()




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
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignTop)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Save in: "))
        self.led_destination = QLineEdit()
        self.led_destination.setDisabled(True)
        self.led_destination.setText(self.destination)
        self.led_destination.setMinimumWidth(300)
        self.led_destination.setAlignment(Qt.AlignHCenter)
        self.led_destination.setFont(QFont('Consolas', 9))
        row1.addWidget(self.led_destination)
        self.btn_destination = QPushButton("Change...")
        row1.addWidget(self.btn_destination)
        self.layout.addLayout(row1)
        self.btn_download = QPushButton("Download")
        self.btn_download.setMaximumWidth(120)
        row2 = QHBoxLayout()
        row2.setAlignment(Qt.AlignCenter)
        row2.addWidget(self.btn_download)
        self.layout.addLayout(row2)
        self.setLayout(self.layout)

    def onChangeDestination(self):
        selected_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.destination))
        if selected_dir != "":
            self.destination = selected_dir
            self.led_destination.setText(self.destination)

    def onDownload(self):
        check = True
        if not os.path.exists(self.destination):
            check = False
            os.makedirs(self.destination)
        init_logs(self.destination)
        downloader = Downloader(self.destination)
        downloader.download_progress.connect(self.updateProgressPercent)
        if check:
            downloader.check_params()
        else:
            downloader.get_params()
        self.showCompleted()

    # Activated by signal download_progress from downloader
    def updateProgressPercent(self, key, percent):
        if key not in self.paramline:
            self.paramline[key] = ParamLine(self, key)
            self.layout.addWidget(self.paramline[key])
        self.paramline[key].updateProgressPercent(percent)

    def showCompleted(self):
        for key in self.paramline:
            self.paramline[key].hide()
        self.btn_download.setDisabled(True)
        self.btn_destination.setDisabled(True)
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
    def __init__(self, app, version):
        super().__init__()
        self.app = app
        self.version = version
        self.title = 'ZK-Params Wizard - v.%s' % str(self.version)

        # Register the signal handlers
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)

        # Initialize user interface
        self.initUI()
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)
        self.show()
        self.activateWindow()

    def initUI(self):
        # Set title and geometry
        self.setWindowTitle(self.title)
        self.resize(500, 180)