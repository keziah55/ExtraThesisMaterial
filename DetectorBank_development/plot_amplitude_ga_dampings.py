#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot the first Lyapunov coefficient found by genetic algorithms for five
damping factors for each of five amplitudes.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from save_plot import SavePlot, SaveLegend
import os


def splitFiles(lst):
    
    n = lst[0].split('_')[0]
    results = []
    group = [lst[0]]
    for i in range(1, len(lst)+1):
        try:
            file = all_files[i]
            m = file.split('_')[0]
            if n == m:
                group.append(file)
            else:
                results.append(group)
                n = m
                group = [file]
        except IndexError:
            results.append(group)
            
    return results
        

def formatLabelDamp(label):
    if label == 0:
        return '{0:.0f}'.format(label)
    else:
        return '{0:.0e}'.format(label)

path = './GA_amplitudes_log/summaries/'

all_files = os.listdir(path)
all_files.sort(key = lambda x:(float(x.split('_')[0]),  
                               float(x.split('_')[1])))

results = splitFiles(all_files)

# minimum bandwidth for each damping factor at sr=48000
min_bws = {0.0001: 0.922, 0.0002: 1.833, 0.0003: 2.743, 0.0004: 3.652, 
           0.0005: 4.574}

# dictionary of damping : colour, zorder
#pltparam = {'1e-04':['blue',5], '2e-04':['lime',4], '3e-04':['orange',3], 
#            '4e-04':['darkmagenta',2], '5e-04':['red',1]}
pltparam = {'1e-04':['red',5], '2e-04':['orange',4], '3e-04':['darkmagenta',3], 
            '4e-04':['lawngreen',2], '5e-04':['blue',1]}
majorLocator = MultipleLocator(1)
minorLocator = MultipleLocator(0.5)

for files in results:
    
    n = 0
    
    amp = files[0].split('_')[0]

    for file in files:
        
        damp = file.split('_')[1]
        c, z = pltparam[damp]
        
        d = float(damp)
        min_bw = min_bws[d]
            
        f = open(path+file, mode='r')
        
        data = f.read()
        
        data = data.split('\n')
        data = list(filter(None, data))
        data = data[1:]

        ga_values = (list((float(datum.split(',')[0]), 
                           float(datum.split(',')[1]), 
                           float(datum.split(',')[2])) for datum in data))
        
        bw = np.array(list(g[0]*2 for g in ga_values))
        b = np.array(list(g[1] for g in ga_values))
        
        # don't include values below minimum bandwidth in the plot
        idx = np.where(bw<min_bw)[0]
        
        for i in idx:
            bw[i] = np.nan
            b[i] = np.nan
        
        line, = plt.plot(np.log(bw), np.log(abs(b)), color=c, zorder=z,
                         label=float(file.split('_')[1]))
        
        n += 1
        
    ax = plt.gca()
    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.grid(True, 'both')
        
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(map(float,labels), handles)))
    labels = map(formatLabelDamp, labels)
#    plt.legend(handles, labels, title='Damping factor', bbox_to_anchor=(0.3, 1.0))
    
#    plt.title('Amplitude: ' + amp)
    plt.xlabel('ln(B)')
    plt.ylabel('ln(|b|)', rotation='horizontal', labelpad=25)
    
    savefile = '../Visualisation/amplitude_ga_out_{0:.0e}_minbw.pdf'.format(
            float(amp))
    sp = SavePlot(False, savefile)
    sp.plot(plt)
    sl = SaveLegend('../Visualisation/damping_factors_legend.pdf',
                    auto_overwrite=True)
    leg_clrs = [c for c, _ in pltparam.values()]
    labels = list(pltparam.keys())
#    sl.plot(labels, colours=leg_clrs, title='Damping factor', ncol=2)
    
    
    
#    plt.show()
#    print('../Visualisation/amplitude_ga_out_{0:.0e}.pdf'.format(float(amp)))
#    plt.savefig('../Visualisation/amplitude_ga_out_{0:.0e}_minbw.pdf'
#                .format(float(amp)), format='pdf', bbox_inches='tight')
#    plt.close()
    
    
#sl = SaveLegend('../Visualisation/amplitude_ga_legend.pdf')
#labels = list(pltparam.keys())
#colours = [i[0] for i in pltparam.values()]
#sl.save(labels, colours, figsize=(1,1.4), title='Damping')
    