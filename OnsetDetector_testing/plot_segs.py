#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 14:39:30 2019

@author: keziah
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from save_plot import SavePlot
import os

def plot_segs(file, savepath='.'):
    
    df = pd.read_csv(file, sep='\t')
    
    cols = ['Dir1', 'Dir2', 'File', 'Fs', 'Onsets']
    
    seg_c = ['cyan', 'blue', 'steelblue']
    onsets_c = 'red'
    
    seg_size = 0.02 # segments represent 20ms
    
    offset = 0 # 1/4 # offset (seconds)
    
    for i in range(len(df)):
        
        row = df.loc[i]
        
        dir1, dir2, file, sr, onsets = [row[c] for c in cols]
        
        base, _ = os.path.splitext(file)
        
        if onsets != 'None':
            onsets = onsets.split(',')
            onsets = [int(o)/int(sr) for o in onsets]
            
        else:
            onsets = []
            
        csvdir = os.path.join(savepath, 'log', dir1, dir2, base)
        csvfiles = [f for f in os.listdir(csvdir) 
                    if os.path.splitext(os.path.split(f)[1])[1]=='.csv']
        csvfiles.sort()
        
        c = iter(seg_c)
        
        for csvfile in csvfiles:
            arr = np.loadtxt(os.path.join(csvdir, csvfile), delimiter=',')
            t = np.linspace(0, int(len(arr)*seg_size), len(arr))
            plt.plot(t, arr, color=next(c), marker='.', linestyle='',
                     label=os.path.splitext(csvfile)[0])
            
        for onset in onsets:
            plt.axvline(onset+offset, color=onsets_c, linestyle='--')
            
        plt.xlabel('Time (s)')
        plt.ylabel('Mean log')
        
        plt.grid()
            
        plt.legend()
        
        figpath = os.path.join(savepath, 'figs', dir1, dir2)
        if not os.path.exists(figpath):
            os.makedirs(figpath)
        
        savefile = os.path.join(figpath, '{}_segs.pdf'.format(base))
        
        sp = SavePlot(save=False, savefile=savefile, auto_overwrite=True)
        sp.plot(plt)    
        
        
if __name__ == '__main__':
    file = 'found_onsets.csv'
    plot_segs(file)
