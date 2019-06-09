#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 14:24:07 2019

@author: keziah
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors
import seaborn as sns


def plot_bar_diff(d, sp):
    
    measure = 'F-measure'
    categories = list(d.keys())
     
    for cat in ['Percussion (rolls)', 'Percussion (no rolls)']:
        if cat in categories:
            categories.remove(cat)
     
    fmes = np.array([d[cat][measure] for cat in categories])
    fmes -= 1
#     fmes *= 100
     
    sns.set_style('darkgrid')
    fig, ax = plt.subplots()
     
    y_pos = np.arange(len(fmes))
     
    extent = max(abs(fmes))
    cmap = cm.get_cmap('Blues')
    norm = colors.Normalize(-extent/2, extent)
    c = [cmap(norm(w)) for w in abs(fmes)]
     
    bars = ax.barh(y_pos, fmes, color=c)
     
    for i, rect in enumerate(bars):
        # get values for x,y location of text
        r_width = rect.get_width()
        r_height = rect.get_height()
        r_x = rect.get_x()
        r_y = rect.get_y()
        # text aligned left or right
        horiz_align = 'right' if fmes[i] < 0 else 'left'
        # add the % above the bar
        plt.text(r_x + r_width, r_y+r_height/2, '{:4.2f}%'.format(fmes[i]), 
                 ha=horiz_align, va='center')
     
    if 'Percussion (all)' in categories:
        idx = categories.index('Percussion (all)')
        ylab = categories[:idx] + ['Percussion'] + categories[idx+1:]
    else:
        ylab = categories
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ylab)
    ax.invert_yaxis() 
    
    ax.set_xlabel('%-point difference')
    
    # have to set left xlim, as otherwise test may clash with y-axis labels
    # pick either 1.15*min(fmes) or pad based on width of whole plot
    # (depending on which is lower)
    _, rightlim = ax.get_xlim()
    leftlims = [(1+(rightlim-min(fmes))/100), 1.15]
    leftlims = [min(fmes)*lim for lim in leftlims]
    ax.set_xlim(left=min(leftlims))
    
    sp.plot(plt)
    

