#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empirically find frequency response across whole spectrum.

See test_system_bandwidth.py for functions which use this object.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt


class EmpiricalBandwidth:
    
    def __init__(self, f0, sr, d, audio_type='sine', snr=None):#, power=4):
        """ Object to find detector response across whole frequency spectrum.
        
            An input tone at 200Hz is generated, then a DetectorBank at
            frequencies from 20Hz-20kHz responds.
        
            Parameters
            ----------
            f0 : float
                Input frequency
            sr : int
                Sample rate
            d : float
                Damping factor
            audio_type : {'sine', 'noise', 'both'}
                Type of input audio to generate
            snr : float
                Signal-to-noise ratio. To be used when audio_type='both'
        """

        bwdth = {0.0001:0.922, 0.0002:1.832, 0.0003:2.752, 0.0004:3.606, 
                 0.0005:4.860}
        
        bw = bwdth[d]

        self.f0 = f0 #200
        # num should be a power of 4 so that 200Hz is in freq array
#        self.f = 2*np.logspace(1, 4, num=4**power)
        # 1Hz-spaced detectors
        nyq = sr//2
        self.f = np.arange(1, nyq, step=bw)
#        self.f = np.array([3169.28])
        
        self.sr = sr
        dur = 3
        self.audio = self._make_input(dur, audio_type, snr)
        
#        self.max_db = None
        
        # DetectorBank parameters
        method = DetectorBank.runge_kutta #central_difference #
        f_norm = DetectorBank.freq_unnormalized #search_normalized #
        a_norm = DetectorBank.amp_normalized
        gain = 25
        features = method|f_norm|a_norm
        
        self.dbp = (features, d, gain)


    @staticmethod
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx, array[idx]
    

    def _make_sine(self, dur):
        t = np.linspace(0, 2*np.pi*self.f0*dur, self.sr*dur)
        return np.sin(t)
    
    def _make_noise(self, dur):
        return 2 * np.random.random(self.sr*dur) - 1
    
    @staticmethod
    def _get_noise_amp(snr):
        a = 10**(snr/10)
        a = np.sqrt(1.5/a)
        return a
    
    @staticmethod
    def signal_to_noise(signal, noise):
        def _power(signal):
            return np.mean(np.square(signal))
    
        p_s = _power(signal)
        p_n = _power(noise)    
        return 10 * np.log10(p_s/p_n)


    def _make_input(self, dur, mode='sine', snr=None):
        
        if mode == 'sine':
            audio = self._make_sine(dur)
        elif mode == 'noise':
            audio = self._make_noise(dur)
        elif mode == 'both':
            tone = self._make_sine(dur)
            noise = self._make_noise(dur)
            noise_amp = self._get_noise_amp(snr)
            noise *= noise_amp
            actual_snr = self.signal_to_noise(tone, noise)
            audio = tone + noise
            audio = audio/np.amax(audio)
            print('SNR of generated audio: {:.3f}dB'.format(actual_snr))
        else:
            raise ValueError("'mode' should be 'sine' or 'noise'")
            
        audio = np.append(audio, np.zeros(100))
            
        return audio

    
    def _get_maxima(self, progress):
        # make DetectorBank, get responses and return max value in response
        
        size = len(self.f)
        
        maxima = np.zeros(size)
        
        # don't need all responses at once - just get max for each frequency
        # run in blocks of numPerRun channels to try and speed it up a bit
        
        numPerRun = 100
        
        numBlocks = int(np.ceil(size/numPerRun))
        count = 0
        
        i0, i1 = 0,0
        
        more = True
        while more:
            i0 = i1
            i1 += numPerRun
            if i1 >= size:
                i1 = size
                more = False
            
            if progress:
                print('Running block {} of {}'.format(count, numBlocks), 
                      end='\r')
#                print('{:.0f}%'.format(100*(i0/size)), end='\r')
            
            freq = self.f[i0:i1]
            bandwidth = np.zeros(len(freq))
            det_char = np.column_stack((freq, bandwidth))
            
            det = DetectorBank(self.sr, self.audio.astype(np.float32), 4, 
                               det_char, *self.dbp)
            
            # get output
            z = np.zeros((len(freq),len(self.audio)), dtype=np.complex128)
            r = np.zeros(z.shape)
            det.getZ(z)
            det.absZ(r, z)
            
            for n in range(len(freq)):
                
                if np.isinf(np.max(r[n])):
                    file = 'debug/{:.0f}Hz.csv'.format(freq[n])
                    np.savetxt(file, r[n], delimiter='\t')
                
                maxima[i0+n] = np.max(r[n])
                
                
            count += 1
            
#            maxima[n] = m
        
        return maxima
    

    def getFreqz(self, progress=False):
        """ Find the max amplitude for detectors at a given damping
        
            Parameters
            ----------
            progress : bool
                If True, progress will be written to stdout
                
            Returns
            -------
            Maxima of detectors
        """
        
        self.maxima = self._get_maxima(progress=progress)
        
        # scale by max amplitude at centre frequency    
#        idx0 = np.where(self.f==self.f0)[0][0]
#        amp0 = maxima[idx0]
#        maxima /= amp0
        
#        # if values in maxima are negative, +/- infinity or just fucking massive, 
#        # set them to NaN
#        neg = np.where(maxima<=0)[0]
#        big = np.where(maxima>1e3)[0]
#        inf = np.where(np.isinf(maxima))[0]
#        where = np.append(neg, inf)
#        
#        if len(where) > 0:
#            for n in range(len(where)):
#                idx = where[n]
#                print('Invalid maxima at {:.3f}Hz: {:.3f}'
#                      .format(self.f[idx], maxima[idx]))
#                maxima[idx] = np.nan
        
#        # turn maxima into decibels
#        self.max_db = 20*np.log10(maxima)
#        self.max_db[where] = -np.inf
        
        return self.maxima   #max_db
    
    
    def max_to_dB(self):
        
        # if values in maxima are negative, +/- infinity or just fucking massive, 
        # set them to NaN
        neg = np.where(self.maxima<=0)[0]
#        big = np.where(self.maxima>1e3)[0]
        inf = np.where(np.isinf(self.maxima))[0]
        where = np.append(neg, inf)
        
        if len(where) > 0:
            for n in range(len(where)):
                idx = where[n]
                print('Invalid maxima at {:.3f}Hz: {:.3f}'
                      .format(self.f[idx], self.maxima[idx]))
                self.maxima[idx] = np.nan
        
        # turn maxima into decibels
        max_db = 20*np.log10(self.maxima)
        max_db[neg] = -np.inf
        max_db[inf] = np.nan
        
        return max_db
    
    
    def save_csv(self, savename):
        csv_arr = np.column_stack((self.f, self.maxima))
        header = 'Frequency (Hz),Max'
        np.savetxt(savename, csv_arr, delimiter='\t', header=header)
    
    
    def plot_frequency_response(self, save=False, savename=None):
        
#        if self.max_db is None:
#            raise RuntimeError("Please first call 'getFreqz()' with your "
#                               "chosen damping factor.")
        
        max_db = self.max_to_dB()
        
        plt.semilogx(self.f, max_db, color='dodgerblue')#, linestyle='', marker='.', )
        xtx = 2*np.logspace(1, 4, num=4)
        xlab = ['{:g}'.format(x) for x in xtx]
        plt.xticks(xtx, xlab)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Peak amplitude (dB)')
        plt.grid(True, which='both')
        
        if save:
            plt.savefig(savename, format='pdf')
        else:
            plt.show()
        plt.close()
        
               
