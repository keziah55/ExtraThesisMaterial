#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive visualisation of DetectorBank responses in complex plane
"""

## pulseaudio --kill  
## jack_control  start

## jack_control exit  
## pulseaudio --start

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from detectorbank import DetectorBank
import pyaudio

def getDeviceID(name='TASCAM'):
    """ Return index of audio device which contains the string `name`
    """
    pya = pyaudio.PyAudio()
    info = pya.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devices = [pya.get_device_info_by_host_api_device_index(0,i) 
               for i in range(numdevices)]
    devices = [device for device in devices if device['maxInputChannels'] > 0]
    
    selected_devices = [device for device in devices if name in device['name']]
    
    if len(selected_devices) == 1:
        idx = selected_devices[0]['index']
        return idx
    elif len(selected_devices) > 1:
        print("Multiple devices match name '{}':\n{}".format(name, 
              [dev['name'] for dev in selected_devices]))
    else:
        print("No devices match name '{}'. Please choose from:\n{}".format(name, 
              [dev['name'] for dev in selected_devices]))


def makeDetectorBank():
    # detector parameters
    edo = 12
    f = np.array(list(440 * 2**(n/edo) for n in range(-48, 40)))
    method = DetectorBank.runge_kutta 
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_normalized
    dmp = 0.0001
    gain = 5
    
    bandwidth = np.zeros(len(f))
    bandwidth.fill(0)
    det_char = np.array(list(zip(f, bandwidth)))
    
    det = DetectorBank(sr, np.zeros(buflen, dtype=np.dtype('float32')), 4, 
                       det_char, method|f_norm|a_norm, dmp, gain)
    return det


# initialise pyaudio
fmt = pyaudio.paInt16
channels = 1
sr = 48000
buflen = int(sr*30e-3)


det = DetectorBank("48k_12edo_amp_norm_min_bw", 
                   np.zeros(buflen, dtype=np.dtype('float32')))

#det = makeDetectorBank()
num_chans = det.getChans()

print(num_chans)

QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])

win = pg.GraphicsWindow()
win.showMaximized()
#win.resize(700,700)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

axr = 0.015
axrx = 0.02

p = win.addPlot()

c = [pg.hsvColor(0/360), 
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

curves = [p.plot(pen=c[i%12]) for i in range(num_chans)]

p.setRange(xRange=(-axrx, axrx), yRange=(-axr, axr))


audio = pyaudio.PyAudio()

#dev_id = getDeviceID('TASCAM')

stream = audio.open(format=fmt, channels=channels, rate=sr, input=True,
                    frames_per_buffer=buflen)#, input_device_index=dev_id)
                    
    
all_z = np.zeros((num_chans, buflen), dtype=np.complex128)  
#all_dz = np.zeros((len(f), buflen), dtype=np.complex128)
#dz = np.zeros(buflen, dtype=np.complex128)

zp = np.zeros(num_chans)


def update():
    global curve, data, p, zp
    
    data = stream.read(buflen)
    audio = np.frombuffer(data, dtype=np.int16)
    audio = np.array(audio/2**15, dtype=np.dtype('float32'))
    
    det.setInputBuffer(audio)

    det.getZ(all_z)
    
    for p in range(num_chans):
        z = all_z[p]
        curve = curves[p]
        curve.setData(z.real, z.imag)
        
    
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(30)





## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
