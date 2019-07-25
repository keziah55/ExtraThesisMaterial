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
from PyQt5.QtMultimedia import (QAudio, QAudioDeviceInfo, QAudioFormat, 
                                QAudioInput)

from detectorbank import DetectorBank
import numpy as np
from musicfuncs import getNoteNum, centsToHz

class Visualizer(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        self.initUI()
        self._buflen = 4096


    def initUI(self):
        
        # main window/layout
        window = QWidget()
        layout = QVBoxLayout()
        
        # layout for audio device and sample rate selection
        deviceLayout = QHBoxLayout()
        
        # make audio device selection box and list of available devices
        self.deviceBox = QComboBox()
        defaultDeviceInfo = QAudioDeviceInfo.defaultInputDevice()
        self.availableDevices = [defaultDeviceInfo]
        self.availableDevices += QAudioDeviceInfo.availableDevices(
                                                             QAudio.AudioInput)
        for device in self.availableDevices:
            self.deviceBox.addItem(device.deviceName())
            
        # make sample rate label and combobox
        sRateLabel = QLabel("Sample rate:")
        sRateLabel.setAlignment(Qt.AlignRight)
        
        # user can choose between 44.1 and 48kHz (valid DetectorBank rates)
        self.sRateBox = QComboBox()
        self.sRateBox.addItem("44100")
        self.sRateBox.addItem("48000")
        self.sRateBox.setCurrentIndex(1)
        
        # add device and sr widgets to device layout
        deviceLayout.addWidget(self.deviceBox)
        deviceLayout.addWidget(sRateLabel)
        deviceLayout.addWidget(self.sRateBox)
        
        # add device layout to main layout
        layout.addLayout(deviceLayout)
        
        # DetectorBank parameters layout
        # two rows of three parameters
        # each param needs label and edit, 
        # and a 'Start' button will be added at the bottom
        # so grid should be 3x6
        detBankParamLayout = QGridLayout()
        
        # label and lineedit for each
        bandwidthLabel = QLabel("Bandwidth (cents):")
        dampingLabel = QLabel("Damping:")
        gainLabel = QLabel("Gain:")
        edoLabel = QLabel("EDO:")
        lwrLabel = QLabel("Lower note:")
        uprLabel = QLabel("Upper note:")
        
        self.bandwidthEdit = QLineEdit("0")
        self.dampingEdit = QLineEdit("0.0001")
        self.gainEdit = QLineEdit("25")
        self.edoEdit = QLineEdit("12")
        self.lwrEdit = QLineEdit("A3")
        self.uprEdit = QLineEdit("A5")
        
        # store all in lists
        detBankParamLabels = [bandwidthLabel, dampingLabel, gainLabel, 
                              edoLabel, lwrLabel, uprLabel]
        
        detBankParamEdits = [self.bandwidthEdit, self.dampingEdit, 
                             self.gainEdit, self.edoEdit, self.lwrEdit, 
                             self.uprEdit]
         
        # fill first two rows of grid with labels and edits
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
            
        # align labels to the right (next to the edit)
        for i in range(len(detBankParamLabels)):
            detBankParamLabels[i].setAlignment(Qt.AlignRight)
                
        # button to make DetectorBank and start visualisation
        row += 1
        startButton = QPushButton("&Start!")
        detBankParamLayout.addWidget(startButton, row, 5)
        startButton.clicked.connect(self.start)
        
        # add grid of detbank params (and start button) to main layout
        layout.addLayout(detBankParamLayout)
        
        window.setLayout(layout)
        self.setCentralWidget(window)
        self.show()
        
        
    def initializeAudio(self, deviceInfo):
        """ Make a QAudioInput from the given device """
        
        # make buffers of 40ms of samples
        sr = self.getSampleRate()
        self.buflen = int(sr*0.04)
        
        # mono, 32-bit float audio
        fmt = QAudioFormat()
        fmt.setSampleRate(sr)
        fmt.setChannelCount(1)
        fmt.setSampleSize(32)
        fmt.setSampleType(QAudioFormat.Float)
        fmt.setByteOrder(QAudioFormat.LittleEndian)
        fmt.setCodec("audio/pcm")
        
        if not deviceInfo.isFormatSupported(fmt):
            fmt = deviceInfo.nearestFormat(fmt)
            
        self.audioInput = QAudioInput(deviceInfo, fmt)

        
    def startAudio(self):
        self.audioDevice = self.audioInput.start()
        ## connect(audioDevice.get(), SIGNAL(update()), this, SLOT(getDetBankData()));
        
        
    def start(self):
        """ Initialise audio, make DetectorBank, open PlotData window and 
            start audio 
        """
        
        print('Initalising audio...')
        deviceIdx = self.deviceBox.currentIndex()
        device = self.availableDevices[deviceIdx]
        self.initializeAudio(device)
        
        print('Making DetectorBank...')
        self.makeDetectorBank()
        
#        print('Making PlotData object...')
        
        print('Starting audio...')
        self.startAudio()
        
        
    def makeDetectorBank(self):
        """ Make DetectorBank from given parameters """
        
        sr = self.getSampleRate()
        bandwidth_cents = float(self.bandwidthEdit.text())
        dmp = float(self.dampingEdit.text())
        gain = float(self.gainEdit.text())
        edo = float(self.edoEdit.text())
        lwr = self.lwrEdit.text()
        upr = self.uprEdit.text()
        
        lwr, picthOffset = getNoteNum(lwr, edo)
        upr, _ = getNoteNum(upr, edo)
        upr += 1 # include upr note in DetectorBank
        
        # make and fill frequency and bandwidth arrays
        freq = np.zeros(upr-lwr)
        bw = np.zeros(len(freq))
        for i in range(len(freq)):
            k = lwr+i
            freq[i] = 440*2**(k/edo)
            # if non-minimum bandwidth detectors requested, find B in Hz
            if bandwidth_cents != 0:
                bw[i] = centsToHz(freq[i], bandwidth_cents, edo)
                
        # combine into stacked array
        det_char = np.stack((freq,bw), axis=1)
        
        # (almost) empty input buffer
        buffer = np.zeros(1, dtype=np.float32)
        
        # DetectorBank features
        method = DetectorBank.runge_kutta
        f_norm = DetectorBank.freq_unnormalized
        a_norm = DetectorBank.amp_unnormalized
        
        self.det = DetectorBank(sr, buffer, 4, det_char, method|f_norm|a_norm, 
                                dmp, gain)
        
        print("Made DetectorBank with {} channels, with a sample rate of {}Hz"
              .format(self.det.getChans(), self.det.getSR()))
        
    ## get and/or set various values
    def getSampleRate(self, returnType=int):
        return returnType(self.sRateBox.currentText())
    
    @property
    def buflen(self):
        return self._buflen
        
    @buflen.setter
    def buflen(self, value):
        self._buflen = value


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = Visualizer()
    sys.exit(app.exec_())
