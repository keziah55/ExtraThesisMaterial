#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test OnsetDetector prototypes using piano test audio. These test used old 
versions of the OnsetDetector (before the NoteDetector was implemented as the 
object with which the user will interact), so may require some tweaking in 
order to be used.

For example, the critical bands are contructed in Python here; in the current
version of the NoteDetector, this happens internally
"""

import numpy as np
from detectorbank import DetectorBank, NoteDetector
from check_onsets import CheckOnsets
import soundfile as sf
import os
import sys
import time


def get_dict():
    """ Return a dictionary of dictionaries of parameters for the various 
        test audio extracts
    """

    dream_dict = {'name':'Dream a Little Dream of Me', 'fname':'dre48', 
                  'datapath':os.path.join('..', 'data'), 'sr':48000,
                  'threshold':0.015, 'range':range(-9,4), 'edo':12}
    
    before_dict = {'name':'Before All Things', 'fname':'bfr48', 
                   'datapath':os.path.join('..', 'data'), 'sr':48000,
                   'threshold':0.008, 'range':range(-5,13), 'edo':12}
    
    alice_dict = {'name':'Alice', 'fname':'ali48', 
                  'datapath':os.path.join('..', 'data'), 'sr':48000,
                  'threshold':0.015, 'range':range(-17,1), 'edo':12}
    
    swan1_dict = {'name':'Swan Lake excerpt 1', 'fname':'sw1_48', 
                  'datapath':os.path.join('..', 'data'), 'sr':48000,
                  'threshold':0.015, 'range':range(-39,-25), 'edo':12}
    
    swan2_dict = {'name':'Swan Lake excerpt 2', 'fname':'sw2_48', 
                  'datapath':os.path.join('..', 'data'), 'sr':48000,
                  'threshold':0.015, 'range':range(-23,-7), 'edo':12}
    
    parameters = {'dream':dream_dict, 'before':before_dict, 'alice':alice_dict,
                  'swan1':swan1_dict, 'swan2':swan2_dict}
    
    return parameters


def make_band(f0, band_type, num):
    
    if band_type == '1Hz-spaced':
        hwidth = num//2
        step = 1
        f = np.arange(f0-hwidth, f0+hwidth+step, step)
        
    else:
        lwr = -(num-1)//2  # lower range bound for frequency calculation
        upr =  (num+1)//2  # upper range bound for frequency calculation
        f = np.array(list(f0*2**(k/(12*num)) for k in range(lwr,upr)))
        
    return f


def get_note_num(note):
    
    note = note.lower()
    
    name = ['a0', 'a#0', 'b0', 'c1', 'c#1', 'd1', 'd#1', 'e1', 'f1', 
            'f#1', 'g1', 'g#1','a1', 'a#1', 'b1', 'c2', 'c#2', 'd2', 
            'd#2', 'e2', 'f2', 'f#2', 'g2', 'g#3', 'a2', 'a#2', 'b2', 
            'c3', 'c#3', 'd3', 'd#3', 'e3', 'f3', 'f#3', 'g3', 'g#3', 
            'a3', 'a#3', 'b3', 'c4', 'c#4', 'd4', 'd#4', 'e4', 'f4', 
            'f#4', 'g4', 'g#4', 'a4', 'a#4', 'b4', 'c5', 'c#5', 'd5', 
            'd#5', 'e5', 'f5', 'f#5', 'g5', 'g#5', 'a5', 'a#5', 'b5', 
            'c6', 'c#6', 'd6', 'd#6', 'e6', 'f6', 'f#6', 'g6', 'g#6', 
            'a6', 'a#6', 'b6', 'c7', 'c#7', 'd7', 'd#7', 'e7', 'f7', 
            'f#7', 'g7', 'g#7', 'a7', 'a#7', 'b7', 'c8']
    
    return name.index(note) - 48


def run(which, outdir):
    
    # get parameters
    parameters = get_dict()
    fname = parameters[which]['fname']
    file = os.path.join(parameters[which]['datapath'], fname + '.wav')
    
    # get paths to onsets.txt and to location to write results
    whichpath = os.path.join('results', which)
    savepath = os.path.join(whichpath, outdir)
       
    if os.path.exists(savepath):
        print('{} exists. Overwrite? [Y/n]'.format(savepath))
        answer = input()
        if answer not in ['', 'y', 'Y']:
            sys.exit(0)
    else:
        os.makedirs(savepath)
    
    # DetectorBank parameters
    audio, sr = sf.read(file)
    
    bandwidth = 0
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    d = 0.0001
    gain = 50
    
    r = parameters[which]['range']
    frequencies = np.array(list(440*2**(k/12) for k in r))
    
    band_types = ['1Hz-spaced', 'EDO']
    band_type = band_types[1]
    
    num = 21
    
    threshold = parameters[which]['threshold']
    
    print('Analysing {} with threshold of {}'.format(fname, threshold))
           
    # new way of making a NoteDetector
    nd = NoteDetector(sr, audio.astype(np.float32), frequencies, num, 
                      bandwidth, method|f_norm|a_norm, d, gain)
    
    # write file of OnsetDetector parameters that will be used here
    with open(os.path.join(savepath, 'ondet_params.txt'), 'w') as fileobj:
        
        fileobj.write(time.ctime(time.time()) + '\n\n')
        
        fileobj.write('Input: '+fname+'\n')
        fileobj.write('seg_len: 20ms, 100 segments\n')
        fileobj.write('With stop-start >= log(2) criterion\n')
        fileobj.write('Backtracking with local min\n')
        fileobj.write('Log threshold/seg avg.\n')
        fileobj.write('Critical band: {} detectors, {}\n'.format(num, band_type))
        fileobj.write('Threshold: {}\n'.format(threshold))
        fileobj.write('C++\n')
    
    # for each frequency the user asks for...
    for f0 in frequencies:
    
        fname = '{}Hz.txt'.format(int(f0))
        
        print('{:.0f}Hz'.format(f0))
    
        # make critical band freqs
        f = make_band(f0, band_type, num)
        
        # make a DetectorBank
        bandwidth = np.zeros(len(f))
        det_char = np.array(list(zip(f, bandwidth)))
        det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
                           method|f_norm|a_norm, d, gain)
        
        # use (now defunct) OnsetDetector
        od = OnsetDetector(det)
        # get onsets
        onsets = od.analyse(threshold)
        onsets = np.array(onsets)
        
        # write results to file
        with open(os.path.join(savepath, fname), 'w') as fileobj:
            fileobj.write('Onsets\n------\n')
            
            for onset in onsets:
                line = 'sample {:6d}, {:6.3f} seconds\n'.format(onset, onset/sr)
                fileobj.write(line)
            
            # no longer finding offset times
            fileobj.write('\nOffsets\n-------\n')
            
    # check returned onsets
    c = CheckOnsets(whichpath, savepath)
    precision, recall, fmeasure, precision_e, fmeasure_e = c.check(True, savepath)
    
              
        
if __name__ == '__main__':
    
    for which in ['dream', 'alice', 'swan1', 'swan2']:
        run(which, '23_Oct')
    
