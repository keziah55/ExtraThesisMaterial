#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 19:24:40 2019

@author: keziah
"""

import os.path
import numpy as np
import soundfile as sf
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from save_plot import SavePlot, SaveLegend
import seaborn as sns


def get_f(f0, b=0.922, edo=12):
    """ Get array of frequencies in a critical band
    
        Parameters
        ----------
        f0 : float
            centre frequency
        b : float
            detector bandwidth (default is 1.16Hz)
        edo : int
            number of divisions in octave (default is 12)
            
        Returns
        -------
        array for critical band frequencies around f0
    """
    
    # denominator for half a semitone in given EDO
    # eg for 12EDO, f=f0*2**(1/24)
    half_semitone = 2*edo
    
    # make output array
    freq = np.zeros(0)
    
    # get frequencies from centre +/- half a semitone
    for i in (-1, 1):
        
        f = f0
        f1 = f0 * 2**(i/half_semitone)
        
        # difference between current and stop frequency
        diff = i*(f1-f) # keep diff positive

        # until diff is at minimum or f is within b/4 of stop value
        while i*(f1-f) <= diff and i*(f1-f) > b/4:
            diff = i*(f1-f)
            f += (i*b) # when i == -1, b will be subtracted
            freq = np.append(freq, f)
                        
    freq = np.append(freq, f0)
    
    freq.sort()
        
    return freq


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
            'f#7', 'g7', 'g#7', 'a7', 'a#7', 'b7', 'c8', 'c#8', 'd8', 
            'd#8', 'e8', 'f8', 'f#8', 'g8']
            
    return name.index(note) - 48


def get_responses(file, damping, sp, tp=None, fp=None, fn=None, sl=None, 
                  t0=None, t1=None, spa=None):
    
    sns.set_style('whitegrid')
    
    head, tail = os.path.split(file)
    base, ext = os.path.splitext(tail)
    
    # `base` is file name with data separated by dots
    # go backwards through each item and see if it is a note
    baselst = base.split('.')
    i = -1
    while True: 
        # if we've gone as far back as we can without finding a note, exit
        if i <= -len(baselst):
            msg = 'Cannot parse note in filename {}'.format(tail)
            raise ValueError(msg)
        # check if the file is a (xylophone) glissandi
        if baselst[i].lower() == 'gliss':
            # assuming same xylophone used for all recordings
            if baselst[i+1].lower() == 'up':
                k = get_note_num('F4')
                break
            elif baselst[i+1].lower() == 'down':
                k = get_note_num('C8')
                break
#            note_n = list(range(k0, k1+1))
        # try this item
        try:
            # get note number relative to A4 (for frequency calculation)
            k = get_note_num(baselst[i])
            break
        # if this item isn't a note, go backwards and try again
        except ValueError:
            i -= 1
            
    edo = 12
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    gain = 50
    
    bw = {1e-4:0.922, 2e-4:1.832, 3e-4:2.752, 4e-4:3.606, 5e-4:4.86}
            
    f0 = 440*2**(k/edo)
    f = get_f(f0, b=bw[damping], edo=edo)
    
    print('Band size: {}'.format(len(f)))
            
    audio, sr = sf.read(file)
    
    if spa is not None:
        plot_audio(sr, audio, spa, t0, t1, tp=tp,fp=fp)
    
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
                           method|f_norm|a_norm, damping, gain)
    
    z = np.zeros((len(f), len(audio)), dtype=np.complex128)
    r = np.zeros(z.shape)
    det.getZ(z)
    det.absZ(r, z)
    
    c = ['black', 'blue', 'chocolate', 'cyan', 'darkmagenta', 'khaki', 
     'deeppink', 'aquamarine', 'darkorange', 'firebrick', 'green',
     'lightslategrey', 'dodgerblue', 'magenta', 'mediumvioletred', 
     'orange', 'pink', 'red', 'skyblue', 'lightgrey', 'yellow']
    
    centre_idx = c.index('green')
    centre_f = np.where(f==f0)[0][0]
    color_offset = centre_idx - centre_f
    
    print('Centre freq at index: {}'.format(centre_f))
    print('Colour offset: {}'.format(color_offset))
    
    t = np.linspace(0, r.shape[1]/sr, r.shape[1])
    if t0 is None:
        t0 = 0
    else:
        t0 = int(sr*t0)
    if t1 is None:
        t1 = len(audio)
    else:
        t1 = int(sr*t1)
    
    for k in range(r.shape[0]):
        plt.plot(t[t0:t1], r[k][t0:t1], color=c[(k+color_offset)%len(c)],
                 label='{:.3f}Hz'.format(f[k]))
        
    if tp is not None:
        for onset in tp:
            plt.axvline(onset, color='lime')
    if fp is not None:
        for onset in fp:
            plt.axvline(onset, color='mediumorchid', linestyle='--')
    if fn is not None:
        for onset in fn:
            plt.axvline(onset, color='indigo', linestyle='--')
        
    plt.xlabel('Time (s)')
    plt.ylabel('|z|', rotation='horizontal', labelpad=10)
#    ax = plt.gca()
#    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        
    if sl is not None:
        colours = [c[k+color_offset] for k in range(r.shape[0])]
        labels = ['{:.3f} Hz'.format(f[k]) for k in range(r.shape[0])]
        sl.plot(labels=labels, colours=colours, ncol=1, 
                title='Detector frequencies')
#    else:
#        plt.legend()
        
    plt.grid(True)
    
    sp.plot(plt)


def _get_dir1_dir2(root, path):
    # remove root from path' remainder should be dir1 and dir2
    dir1dir2 = path.replace(root, '')
    dir1dir2 = dir1dir2.split(os.path.sep)
    dir1, dir2 = list(filter(None, dir1dir2)) 
    return dir1, dir2


def plot_audio(sr, audio, sp, t0=None, t1=None, tp=None, fp=None):
    
    sns.set_style('whitegrid')
        
    if t0 is None:
        t0 = 0
    else:
        t0 = int(sr*t0)
    if t1 is None:
        t1 = len(audio)
    else:
        t1 = int(sr*t1)
    
    t = np.linspace(0, len(audio)/sr, len(audio))
    plt.plot(t[t0:t1], audio[t0:t1], color='#e02323')
            
    if tp is not None:
        for onset in tp:
            plt.axvline(onset, color='lime')
    if fp is not None:
        for onset in fp:
            plt.axvline(onset, color='mediumorchid', linestyle='--')
             
    plt.grid(True)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    sp.plot(plt)
    
    

if __name__ == '__main__':
    
    user = os.path.expanduser('~')
    audio_root = os.path.join(user, 'Iowa', 'all')
#    file = 'Cello.arco.ff.sulA.D4.stereo.wav'
#    filepath = os.path.join(audio_root, 'Strings', 'Cello.arco.ff.sulA',
#                            file)
    
    dir1 = 'Percussion' # 'Brass' # 'Woodwind' # 
    dir2 =  'Xylophone.rosewood.roll' #'Trumpet.novib' # 'SopSax.nonvib.ff' # 
    file = dir2 + '.ff.A5.stereo.wav' # '.B5.stereo.wav' # 
    filepath = os.path.join(audio_root, dir1, dir2, file)
    
    damping = 0.0005
    
#    if 'nonvib' in file:
#        truepos = [0.347-37e-3] #[0.269-41e-3]
#        falsepos = None #[2.761]
#        falseneg = None # [0.136]
#    else:
#        truepos = None #[0.240-38e-3] # [0.269-41e-3]
#        falsepos = [0.126] #[2.748] # [2.761]
#        falseneg = [0.182] # [0.136]
        
    truepos, falsepos, falseneg = [None]*3
    
#    truepos = np.array([0.02      , 0.05952083, 0.15772917, 0.25      , 
#                        0.33460417, 0.42735417, 0.50289583, 0.607125  , 
#                        0.69      , 0.78566667, 0.87204167, 0.96258333, 
#                        1.06072917, 1.13885417, 1.22864583, 1.33      , 
#                        1.40279167, 1.49      , 1.5849375 , 1.67133333, 
#                        1.77      , 1.85      , 1.94166667, 2.03      , 
#                        2.11864583, 2.21      , 2.29      , 2.37      ,
#                        2.47])
#        
#    falsepos = np.array([0.59, 1.55, 2.55, 2.61, 2.69, 2.77])
#    
#    falseneg = None
    
    savepath = os.path.join(user, 'onsets', 'hsj', 'Visualisation', 'Iowa')
    saveroot, _ = os.path.splitext(file)
    savefiledmp = '{}_{:.0e}'.format(saveroot, damping)
    ext = '.pdf'
    
    savefile = os.path.join(savepath, savefiledmp+ext)
    savelegfile = os.path.join(savepath, savefiledmp+'_legend'+ext)
    saveaudio = os.path.join(savepath, saveroot+ext)
    spa = SavePlot(save=False, savefile=saveaudio)
    
    
    sp = SavePlot(save=False, savefile=savefile)
    sl = SaveLegend(savelegfile)
    get_responses(filepath, damping=damping, sp=sp, 
                  tp=truepos, fp=falsepos, fn=falseneg,
#                  sl=sl,
#                  spa=spa,
#                  t1=3
                  )
