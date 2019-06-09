#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 15:23:30 2016

@author: keziah
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

def sortKey(listItem):
    return float(listItem.split(',')[0])

def get_b(bandwidth):
    
#    y0, y1 = 0.160401176805, 532.883701808
    y0, y1 = 0.159239248927307, 533.247977056948
    x0, x1 = 2, 30
    
#    y0, y1 = 0.15, 20
#    x0, x1 = 2, 10
    
    m = (np.log(y1) - np.log(y0)) / (np.log(x1) - np.log(x0))
    
    logb = m * np.log(abs(bandwidth)) - m * np.log(x0) + np.log(y0)
    
    return -np.exp(logb)

#ga_file = open('./GA Lyapunov 1Hz/lyapunov.out')
ga_file = open('./GA_Lyapunov_bandwidth_log/lyapunov.csv')

ga_values = ga_file.read()

ga_values = ga_values.split('\n')

ga_values = list(filter(None, ga_values))

# if running on old lyapunov.out file, remove this line
ga_values = ga_values[1:]
#ga_values = ga_values[:-1]

ga_values.sort(key=sortKey)

ga_values = (list((float(ga.split(',')[0]), float(ga.split(',')[1]), 
                   float(ga.split(',')[2])) for ga in ga_values))

bw = np.array(list(g[0]*2 for g in ga_values))
b = np.array(list(g[1] for g in ga_values))

#line, = plt.plot(np.log(bw), np.log(abs(get_b(bw))), 'red')
line, = plt.plot(np.log(bw), np.log(abs(b)), 'blue', linestyle='', marker='o',
                 markersize=3)

plt.xlabel('ln(B)')
plt.ylabel('ln(|b|)', rotation='horizontal', labelpad=15)

ax = plt.gca()
#ax.xaxis.set_major_locator(MultipleLocator(1))
#ax.xaxis.set_minor_locator(MultipleLocator(0.5))
#ax.yaxis.set_major_locator(MultipleLocator(2.5))
#ax.yaxis.set_minor_locator(MultipleLocator(1.25))
#ax.yaxis.set_label_coords(-0.075, 0.535)
ax.grid(True, 'both')
plt.show()
#plt.savefig('../Visualisation/logbw_logb_ga_logf.pdf', format='pdf')
plt.close()