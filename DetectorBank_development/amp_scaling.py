#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New version on amplitude_decay.py
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt

from save_plot import SavePlot
import os


def make_audio(f0, amp, dur, sr):
    t = np.linspace(0, 2*np.pi*f0*dur, sr*dur)
    audio = np.sin(t)*amp
    audio = np.append(audio, np.zeros(sr))
    return audio


def getMax(f0, sr, method, f_norm):
    """ Get maximum abs value in response. Also returns internal detector
        frequency (which will be different from f0 if search normalisation is
        used)
        
        Parameters
        ----------
        fo : float
            Centre frequency
        sr : int
            Sample rate
        method : DetectorBank Feature
            Numerical method
        f_norm : DetectorBank Feature
            Frequency normalisation
    
        Returns
        -------
        z value at point which is max value in |z|, max value in |z|,
        frequency used by detector 
    """
    
    f = np.array([f0])
    b = np.zeros(len(f))
    det_char = np.array(list(zip(f, b)))
    d = 0.0001
    amp = 5
    a_norm = DetectorBank.amp_unnormalized
    
    audio = make_audio(f0, 1, 4, sr)
    
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                          method|f_norm|a_norm, d, amp)
    
    z = np.zeros((len(f), len(audio)), dtype=np.complex128)
    r = np.zeros(z.shape)
    
    det.getZ(z)
    m = det.absZ(r, z)
    
    i = np.where(r[0]==m)[0][0]
    mz = z[0][i]
    
    f_adjusted = det.getW(0) / (2*np.pi)
    
    return mz, m, f_adjusted


def getMaxResp(sp, f, sr, method, f_norm):
    
    max_abs = np.zeros(len(f))
    max_z = np.zeros(len(f), dtype=np.complex128)
    f_adjusted = np.zeros(len(f))
    
    for n, f0 in enumerate(f):
        
        mz, m, f_det = getMax(f0, sr, method, f_norm)
        max_abs[n] = m
        max_z[n] = mz
        f_adjusted[n] = f_det

#    plt.plot(f, max_abs, color='dodgerblue') 
#    
#    ax = plt.gca()
#    ax.grid(True)
#    
#    plt.xlabel('Frequency (Hz)')
#    plt.ylabel('Max(|z|)')#, rotation='horizontal')
#    
#    #plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
#    
##    ax.yaxis.labelpad = 10
#    
#    sp.plot(plt)
    
    return max_z, f_adjusted


def writeIncFile(s, path, filename):
    name = os.path.join(path, filename)
    with open(name, 'w') as fileobj:
        fileobj.write(s)
    print('Written file {} to {}'.format(filename, path))


def makeVectorStr(data_type, arr):
    out = '    std::vector<{}> {{\n'.format(data_type)
    for item in arr[:-1]:
        out += '        {},\n'.format(item)
    out += '        {}}}'.format(arr[-1])
    return out 



if __name__ == '__main__':
    
    savepath = '../Visualisation/'
    
#    f = np.array([10, 20, 50, 100, 200, 400, 600, 800, 1000, 1250, 1500, 1750, 
#                  2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000])#, 4500, 
#    #              5000, 5500, 6000, 6500, 7000])
    f = np.linspace(5, 4200, num=150)
    
    s_rates = [44100, 48000]
    methods = {'rk4' : DetectorBank.runge_kutta, 
               'cd' : DetectorBank.central_difference}
    f_norms = {'un' : DetectorBank.freq_unnormalized,
               'sn' : DetectorBank.search_normalized}
    
    freqsStr = ('// Frequencies for rk4_un_freqs, rk4_sn_freqs, cd_un_freqs, '
                'cd_sn_freqs at 44.1kHz and 48kHz\n\n')
    scaleStr = ('// Scale factors for rk4_un_freqs, rk4_sn_freqs, cd_un_freqs, '
                'cd_sn_freqs at 44.1kHz and 48kHz\n\n')
    
    #freqsStr += '#include <complex>\n\n'
    
    freqsStr += 'const std::array<std::vector<parameter_t>, 8> AbstractDetector::scaleFreqs = {\n'
    scaleStr += 'const std::array<std::vector<discriminator_t>, 8> AbstractDetector::scaleFactors = {\n'
    
    str_end = '\n};\n\n'
    
    fVec = []
    sVec = []
    
    for sr in s_rates:
        for mKey in methods:
            for fKey in f_norms:
                
                file = 'amp_decay_{:g}_{}_{}.pdf'.format(sr/1000, mKey, fKey)
                savefile = os.path.join(savepath, file)
                sp = SavePlot(False)#, savefile, auto_overwrite=True)
                
                method = methods[mKey]
                f_norm = f_norms[fKey]
    
                m, f = getMaxResp(sp, f, sr, method, f_norm)
                
                fVec.append(makeVectorStr('parameter_t', f))
                sVec.append(makeVectorStr('discriminator_t', m))
                
    freqsStr += ',\n\n'.join(fVec)
    scaleStr += ',\n\n'.join(sVec)
                
    freqsStr += str_end
    scaleStr += str_end
    
    file = 'scale_values.inc'
    incPath = '../DetectorBank/src/' #'.' #
    
    writeIncFile(freqsStr+scaleStr, incPath, file)
