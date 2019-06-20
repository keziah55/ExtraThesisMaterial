#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 14:15:27 2018

@author: keziah
"""

from system_bandwidth import EmpiricalBandwidth
import os
import re


def getEmpiricalBandwidth(path, mode):
    
    # get dir to save everything to
    base = 'Test'
    ndir = getNextDir(path, base)
    savepath = os.path.join(path, ndir)
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    
    # write summary file here, not in object, as I'm creating a new object for
    # each sample rate
    fileobj = open(os.path.join(savepath, 'freqz_summary.txt'), 'w')
    
#    sample_rates = [44100, 48000]
    sr = 48000
    damping = [0.0005]# [0.0001]#, 0.0002, 0.0003, 0.0004, 0.0005]
    
    frequencies = [400] # [1000]#[440*2**(-9/12)] #
    
    snr = -15
    
#    power = 4
    
    log = ('Calculating detector repsonse across whole frequency spectrum '
           '(1Hz-24kHz)\n')
    if mode == 'sine':
        mode_str = '{:g}Hz tone'.format(frequencies[0]) 
    elif mode == 'noise':
        mode_str = 'white noise'
    elif mode == 'both':
        mode_str = 'sine at {:g}Hz with noise; SNR={}'.format(frequencies[0], snr)
    log += ('Testing response of bandwidth-spaced detectors to {}\n'
            .format(mode_str))
    log += 'DetectorBank uses amplitude normalisation and '
    log += 'no frequency normalisation\n'
    log += 'FIR Hilbert transform used, FIRlength=19 (default)\n\n'
    fileobj.write(log)
    fileobj.close()
    
    
#    for sr in sample_rates:
    for f0 in frequencies:
        
        for d in damping:
            print('freq: {:.0f}, sr: {:.0f}Hz, d: {:.0e}'.format(f0, sr, d))
            
            fname = 'freqz_{:.0f}_{:.0f}_{:.0e}'.format(f0, sr, d)
            
            emp = EmpiricalBandwidth(f0, sr, d, mode, snr)#'noise')#, power=power)
            
            # get bandwidth
            emp.getFreqz(progress=True)
            
            emp.save_csv(os.path.join(savepath, fname+'.csv'))
            
            # save frequency response plot
            emp.plot_frequency_response(True, os.path.join(savepath, fname+'.pdf'))
            
#            fileobj.write(log)
    
#    fileobj.close()
    
    
def getNextDir(path, base='Test'):
    """ Get next directory in 'path', where the directories are of the
        form baseX, e.g. Test1.
        
        The next suitable numbered directory is returned.
    """
    
    # get all (sub)directories in path
    ls = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    
    regex = re.compile(base+'(\d+)')
    
    nums = []
    for d in ls:
        try:
            m = regex.match(d)
            n = m.group(1)
            nums.append(n)
        except:
            pass

    if nums:
        nums = map(int, nums)
        num = max(nums) + 1
    else:
        num = 1
    
    nextdir = base + str(num)
    
    return nextdir
    
        
if __name__ == '__main__':      
    
    pwd = os.getcwd()
    path = os.path.join(pwd, '..', 'Visualisation', 'freqz') 
    
    modes = ['sine', 'noise']#'] #, 'sine']
    
#    for mode in modes:
    getEmpiricalBandwidth(path, 'both')
    