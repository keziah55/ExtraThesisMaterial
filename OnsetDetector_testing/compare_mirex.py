#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 14:10:55 2019

@author: keziah
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib import cm, colors
import seaborn as sns
import os.path
from read_onset_analysis import read_onset_analysis
from save_plot import SavePlot
from make_report import make_table
import sys


def getMirex(mode):
    """ Read MIREX results from file.
    
        'mode' should be 'Precision', 'Recall' or 'F-measure' or the 
        corresponding first letter.
    """
    
    resultspath = '/home/keziah/onsets/MIREX2018_results/'
    
    if mode.lower() in ['p', 'precision']:
        s = 'Precision'
    elif mode.lower() in ['r', 'recall']:
        s = 'Recall'
    elif mode.lower() in ['f', 'f-measure']:
        s = 'FMeasure'
        
    fname = 'PerClass{}.csv'.format(s)
    file = os.path.join(resultspath, fname)
    
    df = pd.read_csv(file)
    
    # get relevant classes
    m2i, _ = getCategories()
    c = m2i.keys()
    
    df = df.loc[df['*Class'].isin(c)]
    df = df.set_index('*Class')
    
    # return relevant lines
    return df
    

def getCategories():
    """ Return dictionaries relating MIREX classes with Iowa categories
    
        Two dictionaries are returned: the first sets the MIREX classes as the
        keys and Iowa as values; the second is the opposite
    """
    
    mirex = ['Solo_Bars_And_Bells', 'Solo_Brass', 'Solo_Plucked_Strings',
             'Solo_Sustained_Strings', 'Solo_Winds']
    iowa = ['Percussion_no_roll', 'Brass', 'pizz', 'arco', 'Woodwind']
    
    mirex2iowa = dict(zip(mirex, iowa))
    iowa2mirex = dict(zip(iowa, mirex))
    
    return mirex2iowa, iowa2mirex


def getIowaResults(mode, dmp):
    """ Read Iowa results from file.
    
        'mode' should be 'Precision', 'Recall' or 'F-measure' or the 
        corresponding first letter.
        
        'dmp' should be 'low' or 'high'
    """
    
    results = {}
    
    if mode.lower() in ['p', 'r', 'f']:
        d = {'p':'Precision', 'r':'Recall', 'f':'F-measure'}
        mode = d[mode.lower()]
    else:
        mode = mode.capitalize()
    
    resultspath = '/home/keziah/onsets/hsj/Sandpit/results/Iowa/'
    if dmp == 'low':
        d = '4_Apr_3'
    elif dmp == 'high':
        d = '6_Apr_2'
    
    resultspath = os.path.join(resultspath, d, 'result_analysis')
    
    _, i2m = getCategories()
    
    for category in i2m.keys():
        fname = 'onset_analysis_{}.txt'.format(category)
        file = os.path.join(resultspath, fname)
        prf = read_onset_analysis(file)
        results[i2m[category]] = prf[mode]
        
    return results
    

def getAllResults(mode):
    """ Return MIREX and Iowa results in single DataFrame.
    
        'mode' should be 'Precision', 'Recall' or 'F-measure' or the 
        corresponding first letter.
    """
    
    df = getMirex(mode)
    
    # put Iowa values into data frames in two new columns
    new_values = {'low':'KM1', 'high':'KM2'}
    
    for dmp, col in new_values.items():
        
        # put empty column at end of dataframe
        df.insert(len(df.columns), col, 0.0)
    
        # get Iowa results for current damping
        results = getIowaResults('f', dmp)
        
        # enter Iowa results into dataframe       
        for k,v in results.items():
            df.at[k, col] = v
            
    return df


def plotResults(row, ylabel, sp):
    
    sns.set_style('darkgrid')
    
    # make colormap, normalise y-values and make list of colours
#    cmap = cm.get_cmap('Blues')
#    norm = colors.Normalize(-50, 100)
#    c = [cmap(norm(w)) for w in row.values]
#    
#    colour = ['#3778bf', 'orange']
    c = ['#3778bf']*(len(row)-2) + ['orange']*2
#    c = ['orange']*(len(row)-2) + ['#3778bf']*2
    
    bars = plt.bar(np.arange(len(row)), row.values, color=c,
                   tick_label=row.index)
    
    for n, rect in enumerate(bars):
        # get values for x,y location of text
        r_height = rect.get_height()
        r_width = rect.get_width()
        r_x = rect.get_x()
        # add the percentage above the bar
        plt.text(r_x + r_width/2.0, r_height, '{:.0f}%'.format(row.values[n]), 
                 ha='center', va='bottom')
        
#    plt.title(row.name)
    
    plt.xlabel('Algorithm')
    plt.ylabel(ylabel + ' (%)')
    
    if row.name == 'Solo_Bars_And_Bells':
        top = 102
    else:
        top = 100
        
    plt.ylim(0,top)
    
    sp.plot(plt)
    
    
def getName(c):
    """ For a given MIREX class, return a string describing the category """
    
    mirex = ['Solo_Bars_And_Bells', 'Solo_Brass', 'Solo_Plucked_Strings',
             'Solo_Sustained_Strings', 'Solo_Winds']
    names = ['percussion_single_note', 'brass', 'pizz', 'arco', 'woodwind']
    mirex2name = dict(zip(mirex, names))
    return mirex2name[c]


def getStats(row):
    
    mrx = row[:-2]
    iowa = row[-2:]
    
    mrx_mn = np.mean(mrx)
    mrx_sd = np.std(mrx)
    
    d = {'Mean':mrx_mn, 'SD':mrx_sd, 'KM1':iowa['KM1'], 
         'KM2':iowa['KM2']}
    
    print("Mean of MIREX results: {:.3f}%".format(mrx_mn))
    print("SD of MIREX results:   {:.3f}%".format(mrx_sd))
    
    for idx in iowa.index:
        result = iowa[idx]
        diff = result - mrx_mn
        
        if np.sign(diff) >= 0:
            abv_bel = 'above'
        else:
            abv_bel = 'below'
            
        num_dev = diff // mrx_sd
        if num_dev >= 0:
            num_dev += 1
        num_dev = np.abs(num_dev)
        
        print("{} result: {:.3f}%".format(idx, result))
        print("This is {} the mean, and within {:.0f} deviation(s)"
              .format(abv_bel, num_dev))
        
    return d
        
if __name__ == '__main__':
    
    savepath = '/home/keziah/onsets/hsj/Visualisation/Iowa/compare_mirex/'
    outpath = '/home/keziah/onsets/hsj/Sandpit/results/Iowa/'
    
#    sys.stdout = open(os.path.join(outpath, 'compare_mirex_summary.txt'), 'w')
    
    modes = ['Precision', 'Recall', 'F-measure']
    which = modes[2]
    
    tab_d = {}
    
    df = getAllResults(which)
       
    for idx in df.index:
        name = getName(idx)
        savefile = '{}_{}.pdf'.format(name, which)
        savefile = os.path.join(savepath, savefile)
        sp = SavePlot(False, savefile, auto_overwrite=True, mode='quiet')
        row = df.loc[idx]
        plotResults(row, ylabel=which, sp=sp)
        
        if name == 'percussion_single_note':
            name = 'Percussion'
        elif name == 'pizz':
            name = 'Pizzicato strings'
        elif name == 'arco':
            name = 'Arco strings'
        
        print(name.capitalize())
        d = getStats(row)
        print()
        
        tab_d[name.capitalize()] = d
        
    comment = 'Sandpit/Iowa/compare_mirex.py'
    
    tex_file = os.path.join(outpath, 'compare_mirex.tex')
    make_table(tab_d, tex_file, fmt=':.6g', mode='tabular')
    