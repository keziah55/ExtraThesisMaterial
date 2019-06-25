#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empirically find frequency response and approximate -3dB points or find 
amplitudes of given bandwidths.

See test_detector_bandwidth.py for functions which use this object.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns


class EmpiricalBandwidth:
    
    def __init__(self, f0, sr):
        """ Object to find detector bandwidth empirically
        
            Parameters
            ----------
            fo : float
                Frequency around which to find bandwidth
            sr : int
                Sample rate
        """
        
        self.f0 = f0
        self.sr = sr
        dur = 3
        self.audio = self._make_input(dur)
        
        # DetectorBank parameters
        method = DetectorBank.runge_kutta
        f_norm = DetectorBank.freq_unnormalized
        a_norm = DetectorBank.amp_normalized
        self.gain = 25
        self.features = method|f_norm|a_norm

    @staticmethod
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx, array[idx]


    def _make_input(self, dur):
        # mak sine tone
        t = np.linspace(0, 2*np.pi*self.f0*dur, self.sr*dur)
        audio = np.sin(t)
        audio = np.append(audio, np.zeros(self.sr))
        return audio

    
    def _get_max(self, f, dbp):
        # make DetectorBank, get responses and return max value in response
        
        f = np.array([f])
        size = len(f)
        bandwidth = np.zeros(size)
        det_char = np.array(list(zip(f, bandwidth)))
        
        det = DetectorBank(self.sr, self.audio.astype(np.float32), 0, 
                           det_char, *dbp)
        
        # get output
        z = np.zeros((size,len(self.audio)), dtype=np.complex128)
        r = np.zeros(z.shape)
        det.getZ(z,size)
        m = det.absZ(r, z)
        
        return m
    
    
    def _get_abs_z(self, freq, bandwidth, dbp):
        # make a DetectorBank with the given parameters and return |z|
        
        size = len(freq)
        bw = np.zeros(size)
        bw.fill(bandwidth)
        
        det_char = np.array(list(zip(freq, bw)))
        
        det = DetectorBank(self.sr, self.audio.astype(np.float32), 0, 
                           det_char, *dbp)
        
        # get output
        z = np.zeros((size,len(self.audio)), dtype=np.complex128)
        r = np.zeros(z.shape)
        det.getZ(z,size)
        det.absZ(r, z)
        
        return r
    
    
    def _get_maxima(self, dbp):
        
        r = self._get_abs_z(self.f_test, 0, dbp)
        
        size = len(r)
        
        maxima = np.zeros(size)
        
        for k in range(size):
            maxima[k] = np.max(r[k])
            
        return maxima
        


    def get_bandwidth(self, d, numDetectors=101):
        """ Find the bandwidths for a given damping
        
            Parameters
            ----------
            d : float 
                Damping factor
            numDetectors : int
                Number of detectors to use when finding bandwidth. This must 
                be odd, to ensure that the centre frequency is included. 
                Default is 101.
                
            Returns
            -------
            Tuple of frequencies at -3dB points
        """
        
        if numDetectors % 2 == 0:
            raise ValueError('Please provide an odd number for numDetectors.')
            
        dbp = (self.features, d, self.gain)
        
        # hwidhts for 44.1 and 48kHz
        hwidths = {0.0001:0.6, 0.0002:1, 0.0003:2, 0.0004:2.5, 0.0005:3}
        # hwidths for 96kHz
#        hwidths = {0.0001:1.2, 0.0002:2, 0.0003:3, 0.0004:4, 0.0005:5}
        # hwidths for 192kHz
#        hwidths = {0.0001:2, 0.0002:4, 0.0003:6, 0.0004:7.5, 0.0005:9.5}
        
        hwidth = hwidths[d]
        self.f_test = np.linspace(self.f0-hwidth, self.f0+hwidth, 
                                  num=numDetectors)
        
        maxima = self._get_maxima(dbp)
        
        # max amplitude at centre frequency    
        idx0 = np.where(self.f_test==self.f0)[0][0]
        amp0 = maxima[idx0]
        maxima /= amp0
        # turn maxima into decibels
        self.max_db = 20*np.log10(maxima)
        
        # find -3dB points
        i3dB0, _ = self.find_nearest(self.max_db[:idx0], -3)
        i3dB1, _ = self.find_nearest(self.max_db[idx0:], -3)
        i3dB1 += idx0
        
        f3dB0 = self.f_test[i3dB0]
        f3dB1 = self.f_test[i3dB1]
        
        return f3dB0, f3dB1
    
    
    def plot_frequency_response(self, save=False, savename=None):
        
        sns.set_style('whitegrid')
        
        plt.plot(self.f_test, self.max_db, linestyle='', marker='.', 
                 color='dodgerblue')
        plt.axhline(-3, linestyle='--', color='lime', linewidth=3)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Peak amplitude (dB)')
        plt.grid(True)
        
        if save:
            plt.savefig(savename, format='pdf')
        else:
            plt.show()
        plt.close()
        
        
    def get_amplitude(self, bw, d):
        """ Get the response amplitude at f0 +/- bw/2
        
            Parameters
            ----------
            bw : float
                bandwidth to test
            d : float
                damping factor
            
            Returns
            -------
            Tuple of response amplitudes (in dB)
        """
        
        # frequency difference
        fd = bw/2
        
        f = np.array([self.f0-fd, self.f0, self.f0+fd])
        
        dbp = (self.features, d, self.gain)
        
        r = self._get_abs_z(f, 0, dbp)
        
        maxima = np.array([np.max(resp) for resp in r])
        maxima /= maxima[1]
        
        max_db = 20*np.log10(maxima)
        
        return max_db[0], max_db[2]
        
