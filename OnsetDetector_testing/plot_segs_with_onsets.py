#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 10:37:11 2019

@author: keziah
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os.path
import glob
from check_onsets import CheckOnsets
from plot_Iowa_note import plot_audio
from save_plot import SavePlot, SaveLegend


def plot_segments(file, threshold=None, save=False, audio_file=None):
    
    sns.set_style('whitegrid')
    
    plot_onsets = True # False # 
    
    plot_ms = False #True # 
    
    savepath = '/home/keziah/onsets/hsj/Visualisation/Iowa/'
#    if plot_onsets:
#        figdir = '{}_octaves_with_onsets'.format('xylophone') #'piano'
#    else:
#        figdir = '{}_octaves_without_onsets'.format('xylophone') #'piano'
    figdir = ''
    figdir = os.path.join(savepath, figdir)
    if not os.path.exists(figdir):
        os.makedirs(figdir)
    
    arr = np.loadtxt(file)
    
#    arr = arr[:-1]
    
    # plot first 500 segments
    i0 = 0
    i1 = len(arr) # 500 # 20 # 
    
    seg_size = 20e-3
    
    title = file.split(os.path.sep)[-2]

    sr, manual_onsets = get_manual_onsets(file)
    sr, found_onsets = get_found_onsets(file)
    found_onsets /= sr
    
    if audio_file is not None:
        sp = SavePlot(True, os.path.join(savepath, title+'_waveform.pdf'),
                      auto_overwrite=True)
        plot_audio(audio_file, sp)#, manual_onsets, found_onsets)
    
    t = np.arange(0, len(arr), dtype=float)
    t *= seg_size
    if plot_ms:
        t *= 1000
    
    plt.plot(t[i0:i1], arr[i0:i1])
    
    correct, diff = CheckOnsets.compare(manual_onsets, found_onsets, 50)

    
    if plot_onsets:
        if correct.size > 0:
            for n, idx in enumerate(correct):
                # correctly found onset
                onset = found_onsets[idx]
                # remove corresponding onset from manual_onsets
                man = manual_onsets + (diff[n]/1000)
                w = np.where(np.isclose(man, onset))[0]
                manual_onsets = np.delete(manual_onsets, w)
                # plot onset
                if onset <= i1*seg_size:
                    if plot_ms:
                        onset *= 1000
                    plt.axvline(onset, color='lime', label='True positive')
            
            # remove correct onsets from found
            found_onsets = np.delete(found_onsets, correct)
#        else:
#            for onset in manual_onsets:
#                plt.axvline(onset, color='red', linestyle='--')
                
        # plot false negatives
        for onset in manual_onsets:
            if onset <= i1*seg_size:
                if plot_ms:
                    onset *= 1000
                plt.axvline(onset, color='indigo', linestyle='--', 
                            label='False negative')
        # plot false positives
        for onset in found_onsets:
            if onset <= i1*seg_size: # t[i1-1]:
                if plot_ms:
                    onset *= 1000
                plt.axvline(onset, color='mediumorchid', linestyle='--',
                            label='False positive')
        
    if threshold is not None:
        threshold = np.log(threshold)
        plt.axhline(threshold, color='green', linestyle='--')
    
#    plt.title(title)
    
    plt.grid(True)
    if plot_ms:
        xlabel = 'Time (ms)'
    else:
        xlabel = 'Time (s)'
    plt.xlabel(xlabel)
    plt.ylabel('Mean log')
    
#    plt.legend()
    
    sp = SavePlot(save, os.path.join(figdir, title+'.pdf'), #+'_w_legend.pdf'),
                  auto_overwrite=True)
    sp.plot(plt)
    
#    sl = SaveLegend(os.path.join(figdir, title+'_legend.pdf'))
#    labels = ['True positive', 'False negative', 'False positive']
#    colours = ['lime', 'indigo', 'mediumorchid']
#    linestyles = ['-', '--', '--'] #  ['--'] * len(colours)
#    labels = ['True positive', 'False positive']
#    colours = ['lime',  'mediumorchid']
#    linestyles = ['-', '--'] #  ['--'] * len(colours)
#    sl.plot(labels, colours=colours, linestyles=linestyles)
    
#    plt.show()
#    plt.close()
    
    
def get_found_onsets(path):
    """ Return sample rate and onsets """
    
    dirs = path.split(os.path.sep)
    i0 = dirs.index('log')
    
    resultspath = os.path.sep.join(dirs[:i0])
    found_file = os.path.join(resultspath, 'found_onsets.csv')
    df = pd.read_csv(found_file, delimiter='\t')
    
    file = dirs[i0+3] + '.wav'
    row = df.loc[df['File']==file]
    
    onsets = _get_item_from_series(row, 'Onsets', try_scalar=False)
    sr = _get_item_from_series(row, 'Fs')
    
    return sr, onsets   
    
    
def get_manual_onsets(path):
    """ Return sample rate and onsets """
    
    df = pd.read_csv('/home/keziah/Iowa/onsets/onsets.csv')
    
    # split path into parts
    dirs = path.split(os.path.sep)
    i0 = dirs.index('log') + 1
    file = dirs[i0+2] + '.wav'
    
    # this returns everything in the cell as a string
    row = df.loc[df['File']==file]
    onsets = _get_item_from_series(row, 'Onsets', try_scalar=False)
    sr = _get_item_from_series(row, 'Fs')
    
    return sr, onsets
    

def _get_item_from_series(series, column, try_scalar=True):
    
    values = series[column].values[0]
    
    if isinstance(values, str):
        try:
            values = [float(item) for item in values.split(',')]
        except ValueError:
            values = []
        
    if try_scalar:
        try:
            len(values)
            return values[0]
        except TypeError:
            pass
    
    return values
    
    

if __name__ == '__main__':
    
    audiopath = '/home/keziah/Iowa/all/'
    resultspath = 'results'
    
    resultsdirs = ['low_damping/with_last-first', 
                   'low_damping/without_last-first', 
                   'high_damping/with_last-first', 
                   'high_damping/without_last-first']
    
    whichdir = resultsdirs[2]
#    dir1 = 'Piano_Guitar' # 'Strings' # 'Percussion' # 
#    dir2 = 'Piano' #'Bass.arco.ff.sulA' # 'Xylophone.rosewood' # 'Marimba.rubber' #
#    
    files = []
    audio_files = []
##    
    octaves = np.arange(8) # [1,2,3] #[4,5,6,7] # [2,3,4,5,6] # [3,4,5] # np.arange(8)
###    
#    for o in octaves:
#        dir3 = '{}.ff.A{}'.format(dir2, o) #'Piano.ff.A{}'.format(o)
##        dir3 = '{}.A{}.stereo'.format(dir2, o)
#        dir3 = '{}.pp.Bb{}'.format(dir2, o)
#    
##    dir3 = 'Piano.ff.A4'
#        logpath = os.path.join(resultspath, whichdir, 'log', dir1, dir2, dir3)
#        csvpath = os.path.join(logpath, '*.csv')
#        csvfiles = glob.glob(csvpath)
#        try:
#            files.append(csvfiles[0])
#        except IndexError:
#            pass
#        
#        afile = os.path.join(audiopath, dir1, dir2, dir3+'.wav')
#        audio_files.append(afile)
#        
    dir1 = 'Piano_Guitar' # 'Percussion' # 'Strings' # 
    dir2 = 'Guitar' # 'Crotale' # 'Vibraphone.bow' # 'Cello.arco.ff.sulA' # 'Xylophone.rosewood' # 'Piano' # 
    dir3 = dir2 + '.ff.sulA.C3' # '.ff.B7.stereo' # '.A4.stereo' # '.pp.B0' # 
##    
#    dir1 = 'Woodwind'
#    dir2 = 'SopSax.nonvib.ff'
#    dir3 = dir2 + '.A5.stereo'
    
    logpath = os.path.join(resultspath, whichdir, 'log', dir1, dir2, dir3)
    csvpath = os.path.join(logpath, '*.csv')
    csvfiles = glob.glob(csvpath)
    try:
        files.append(csvfiles[0])
    except IndexError:
        pass
    
    afile = os.path.join(audiopath, dir1, dir2, dir3+'.wav')
    audio_files.append(afile)
    
    
    for i, file in enumerate(files):
        plot_segments(file, save=True, threshold=0.0003, 
#                      audio_file=audio_files[i]
                      )
        