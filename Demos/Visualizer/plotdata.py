#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 15:48:23 2019

@author: keziah
"""

from PyQt5.QtWidgets import QDesktopWidget, QVBoxLayout, QWidget
import pyqtgraph as pg


class PlotData(QWidget):
    
    def __init__(self, numChans, offset):
        super().__init__()
        
        self.numChans = numChans
        self.offset = offset
        
        layout = QVBoxLayout()
        
#        p = pg.PlotWidget()
#        win.showMaximized()
        #win.resize(700,700)
        
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        
        axr = 0.4 #1 #0.015
#        axrx = 1 #0.02
        
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
        
        self.plotWidget = pg.PlotWidget()
        for i in range(self.numChans):
            colour = self.c[(i+self.offset)%12]
            self.plotWidget.plot(pen=colour)
            
        self.plotWidget.setRange(xRange=(-axr, axr), yRange=(-axr, axr))
            
        plotItem = self.plotWidget.getPlotItem()
        self.dataItems = plotItem.listDataItems()
        
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)
        self.show()
        
        

    def centre(self):
        """ Centre window on screen. """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        
    def update(self, z):
        
        for k in range(self.numChans):
#            self.dataItems[k].setData(z[k])
            
            x = z[k].real[::2]
            y = z[k].imag[::2]
            self.dataItems[k].setData(x, y)
            
