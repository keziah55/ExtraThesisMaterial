#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 15:48:23 2019

@author: keziah
"""

from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QComboBox, QDesktopWidget, 
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QPushButton,
                             QVBoxLayout, QWidget)

import pyqtgraph as pg
#from pyqtgraph.Qt import QtGui, QtCore

import numpy as np


class PlotData(QWidget):
    
    def __init__(self, numChans, offset):
        super().__init__()
        
        global plotWidget

        self.numChans = numChans
        self.offset = offset
        
        layout = QVBoxLayout()
        
#        p = pg.PlotWidget()
#        win.showMaximized()
        #win.resize(700,700)
        
        # Enable antialiasing for prettier plots
#        pg.setConfigOptions(antialias=True)
        
        axr = 0.015
        axrx = 0.02
        
        self.c = [pg.hsvColor(0/360), 
                  pg.hsvColor(300/360),
                  pg.hsvColor(32/360), 
                  pg.hsvColor(60/360), 
                  pg.hsvColor(100/360), 
                  pg.hsvColor(270/360), 
                  pg.hsvColor(120/360, val=0.6), 
                  pg.hsvColor(160/360, sat=0.0), 
                  pg.hsvColor(180/360, val=0.7), 
                  pg.hsvColor(60/360, sat=0.8, val=0.7),
                  pg.hsvColor(200/360), 
                  pg.hsvColor(230/360)]
        
#        self.plotItem.setRange(xRange=(-axrx, axrx), yRange=(-axr, axr))
        
        plotWidget = pg.PlotWidget()
        for i in range(self.numChans):
            colour = self.c[(i+self.offset)%12]
            plotWidget.plot(pen=colour)
            
        layout.addWidget(plotWidget)
        self.setLayout(layout)
        self.show()
        
        

    def centre(self):
        """ Centre window on screen. """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
    def update(self, z):
        
        plotItem = plotWidget.getPlotItem()
        
        for k in range(self.numChans):
            data = z[k]
            x = np.random.rand(len(data))
            y = np.random.rand(len(data))
            # could take slice of x and y arrays, a[::2] for half the data points
            plotItem.listDataItems()[k].setData(x[::2],y[::2])
            
