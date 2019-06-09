#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 15:19:15 2018

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank, NoteDetector, OnsetDict# DetectorCache, Producer  
#from onsetdetector_plot_seg_all import OnsetDetector
import soundfile as sf
import matplotlib.pyplot as plt
import os
import sys
import subprocess
import time
import re


def get_note_num(note):
    
    note = note.lower()
    
    octave = 'abcdefg'
    
    if note[1] is 'b':
        idx = octave.index(note[0]) - 1
        new_note = octave[idx]
        oct_num = note[2]
            
        note = new_note + '#' + oct_num
        
    name = ['a0', 'a#0', 'b0', 'c1', 'c#1', 'd1', 'd#1', 'e1', 'f1', 
            'f#1', 'g1', 'g#1','a1', 'a#1', 'b1', 'c2', 'c#2', 'd2', 
            'd#2', 'e2', 'f2', 'f#2', 'g2', 'g#2', 'a2', 'a#2', 'b2', 
            'c3', 'c#3', 'd3', 'd#3', 'e3', 'f3', 'f#3', 'g3', 'g#3', 
            'a3', 'a#3', 'b3', 'c4', 'c#4', 'd4', 'd#4', 'e4', 'f4', 
            'f#4', 'g4', 'g#4', 'a4', 'a#4', 'b4', 'c5', 'c#5', 'd5', 
            'd#5', 'e5', 'f5', 'f#5', 'g5', 'g#5', 'a5', 'a#5', 'b5', 
            'c6', 'c#6', 'd6', 'd#6', 'e6', 'f6', 'f#6', 'g6', 'g#6', 
            'a6', 'a#6', 'b6', 'c7', 'c#7', 'd7', 'd#7', 'e7', 'f7', 
            'f#7', 'g7', 'g#7', 'a7', 'a#7', 'b7', 'c8']
            
    return name.index(note) - 48


def findOnsets():
    
    user = os.path.expanduser('~')
    project = os.path.join(user, 'onsets', 'hsj')
    result_path = os.path.join(project, 'Sandpit', 'results', 'Iowa')
#    figpath = os.path.join(ondet_path, 'Iowa_figs', 'initial_tests')
#    
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    
    root = os.path.join(user, 'Iowa', 'all')
    
    with open('iowa_files.txt') as fileobj:
        file_list = fileobj.read()
        
    file_list = file_list.split('\n')
    file_list = list(filter(None, file_list))
    
#    file_list = [file_list[0]]
    
    fileobj = open(os.path.join(result_path, 'results.txt'), 'w')
    
    for f in file_list:
        pth = os.path.join(root, *f.split('/'))
        sr, f0, onsets = test(pth)
        
        out = 'File: {}\n'.format(f)
        out += '    Freq: {:.3f}Hz\n'.format(f0)
        samples = _make_string(onsets, 'samples')
        seconds = _make_string([o/sr for o in onsets], 'seconds')
        out += '    Onsets: {}'.format(samples)
        out += '    Onsets: {}\n'.format(seconds)
        fileobj.write(out)
        
    fileobj.close()
        
    
def _make_string(onsets, unit):
    out = ''
    for n in range(len(onsets)-1):
        out += '{}, '.format(onsets[n])
    out += '{} {}\n'.format(onsets[-1], unit)
    return out


def test(file):
    
    print('Testing', file)
    
    audio, sr = sf.read(file)
    
    _, file = os.path.split(file)
    base, ext = os.path.splitext(file)
    baselst = base.split('.')
    i = -1
    while True: 
        if i <= -len(baselst):
            print('Cannot parse file {}'.format(file))
            sys.exit(1)
        try:
            k = get_note_num(baselst[i])
            break
        except ValueError:
            i -= 1
    
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_normalized
    d = 0.0001
    gain = 25

    f0 = np.array([440*2**(k/12)])
    bandwidth = 0
    edo = 12
    
    threshold = 0.001
    
    print('Analysing {} with threshold of {}'.format(file, threshold))
           
    nd = NoteDetector(sr, audio.astype(np.float32), f0, edo, 
                      bandwidth, method|f_norm|a_norm, d, gain)
    
    onsets = OnsetDict()
    weights = (7.375033231580854, -14.59833285997553, -0.3053750760201408)
    
    nd.analyse(onsets, threshold, *weights)
    print('Done!\n')
    
    plot_results(sr, audio, onsets[0])
    
    return sr, f0[0], onsets[0]
    

def plot_results(sr, audio, onsets):
    
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    t = np.linspace(0, len(audio)/sr, len(audio))

    plt.plot(t, audio, color='dodgerblue')
    
    for o in onsets:
        plt.axvline(o/sr, color='red', linestyle='--')
        
    plt.show()
    plt.close()


if __name__ == '__main__':
    
    findOnsets()
    
#    root = '/home/keziah/Iowa/all/'
#    
#    with open('iowa_files.txt') as fileobj:
#        file_list = fileobj.read()
#        
#    file_list = file_list.split('\n')
#    file_list = list(filter(None, file_list))
#    
#    for f in file_list:
#        pth = os.path.join(root, *f.split('/'))
#        test(pth)

