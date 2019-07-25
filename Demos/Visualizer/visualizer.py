#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live visualisation of DetectorBank
"""

import sys
import os

from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtWidgets import (QAction, 
                             QApplication, QComboBox, QDesktopWidget, 
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)
from PyQt5.QtMultimedia import (QAudio, QAudioDeviceInfo, QAudioInput)

from detectorbank import DetectorBank
import numpy as np

class Visualizer(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        self.initUI()


    def initUI(self):
        
        window = QWidget()
        
        layout = QVBoxLayout()
        deviceLayout = QHBoxLayout()
        
        deviceBox = QComboBox()
        defaultDeviceInfo = QAudioDeviceInfo.defaultInputDevice()
        deviceBox.addItem(defaultDeviceInfo.deviceName())
        availableDevices = QAudioDeviceInfo.availableDevices(QAudio.AudioInput)
        for device in availableDevices:
            deviceBox.addItem(device.deviceName())
            
        sRateLabel = QLabel("Sample rate:")
        sRateLabel.setAlignment(Qt.AlignRight)
        
        sRateBox = QComboBox()
        sRateBox.addItem("44100")
        sRateBox.addItem("48000")
        sRateBox.setCurrentIndex(1)
        
        deviceLayout.addWidget(deviceBox)
        deviceLayout.addWidget(sRateLabel)
        deviceLayout.addWidget(sRateBox)
        
        layout.addLayout(deviceLayout)
        
        detBankParamLayout = QGridLayout()
        
        bandwidthLabel = QLabel("Bandwidth (cents):")
        dampingLabel = QLabel("Damping:")
        gainLabel = QLabel("Gain:")
        edoLabel = QLabel("EDO:")
        lwrLabel = QLabel("Lower note:")
        uprLabel = QLabel("Upper note:")
        
        bandwidthEdit = QLineEdit("0")
        dampingEdit = QLineEdit("0.0001")
        gainEdit = QLineEdit("25")
        edoEdit = QLineEdit("12")
        lwrEdit = QLineEdit("A3")
        uprEdit = QLineEdit("A5")
        
        detBankParamLabels = [bandwidthLabel, dampingLabel, gainLabel, 
                              edoLabel, lwrLabel, uprLabel]
        
        detBankParamEdits = [bandwidthEdit, dampingEdit, gainEdit, edoEdit, 
                             lwrEdit, uprEdit]
        
        row = 0

        for row in range(2):
            widgetNum = 0
        
            for i in range((row*3), (row*3)+3):
                detBankParamLayout.addWidget(detBankParamLabels[i], row, 
                                             widgetNum)
                widgetNum += 1
                detBankParamLayout.addWidget(detBankParamEdits[i], row, 
                                             widgetNum)
                widgetNum += 1
            
            
        for i in range(len(detBankParamLabels)):
            detBankParamLabels[i].setAlignment(Qt.AlignRight)
                
        row += 1
        startButton = QPushButton("&Start!")
        detBankParamLayout.addWidget(startButton, row, 5)
        
        layout.addLayout(detBankParamLayout)
        
        window.setLayout(layout)
        self.setCentralWidget(window)
        
        self.show()
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = Visualizer()
    sys.exit(app.exec_())
