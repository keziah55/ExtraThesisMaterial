#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live visualisation of DetectorBank
"""

import sys
import os

from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QAudioDeviceInfo, QAudioInput, 
                             QApplication, QComboBox, QDesktopWidget, 
                             QHBoxLayout,
                             QFileDialog, QMainWindow, QMessageBox, 
                             QVariant, QVBoxLayout)

from detectorbank import DetectorBank
import numpy as np

class Visualizer(QMainWindow):
    
    def __init__(self):
        
        super().__init()
        self.initUI()


    def initUI(self):
        
        layout = QVBoxLayout()
        deviceLayout = QHBoxLayout()
        
        deviceBox = QComboBox()
        defaultDeviceInfo = QAudioDeviceInfo.defaultInputDevice()
        deviceBox.addItem(defaultDeviceInfo.deviceName(), 
                          QVariant.fromValue(defaultDeviceInfo))
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = Visualizer()
    sys.exit(app.exec_())
