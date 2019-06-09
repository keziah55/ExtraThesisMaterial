#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 12:38:57 2019

@author: keziah
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from save_plot import SavePlot, SaveLegend
from read_onset_analysis import read_onset_analysis
import os.path


def make_radar_graph(results, sp, labels=None):
    """ Make a radar chart of F-measure, Precision and Recall
    
        Parameters
        ----------
        results : list of lists
            List of lists, containing F-measure, Precision and Recall for every
            data set to be plotted
        sp : SavePlot
            SavePlot instance to use when saving/showing the plot
        lables : list of lists, optional
            List of lables for plot legend
    """

    sns.set_style('white')
    
    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    colours = get_colours()
    marker = get_marker()
    linestyle = get_linestyle()
    zorders = list(range(len(results), 0, -1))
    
    # if no labels provided, make list of empty strings, so the same plot
    # command can be used
    if labels is None:
        labels = ['' for n in range(len(results))]
    
    for n, data in enumerate(results):
    
        ax_labels= ['F-measure', 'Precision', 'Recall']
        
        # Set the angle
        angles = np.linspace(0, 2*np.pi, len(ax_labels), endpoint=False) 
        # close the plot
        data = np.concatenate((data,[data[0]]))  # Closed
        angles = np.concatenate((angles,[angles[0]]))  # Closed
        angles += np.pi/2
                
        ax.plot(angles, data, color=colours[n], marker=marker, 
                linestyle=linestyle, linewidth=2, zorder=zorders[n], 
                label=labels[n])
        ax.fill(angles, data, alpha=0.25, color=colours[n], zorder=zorders[n]) 
    
    # Set the label for each axis
    ax.set_thetagrids(angles * 180/np.pi, ax_labels)  
    ax.tick_params(pad=10)
    radii = [0, 20, 40, 60, 80, 100]
    r_labels = ['{}%'.format(item) for item in radii]
    r_labels[0] = ''
    ax.set_rgrids(radii, labels=r_labels)
    ax.grid(True)
    
    plt.tight_layout()
    
    # if labels were provided, add a legend
    if labels[0]:
        plt.legend()
    
    sp.plot(plt)
        
    
def plot_file_data(files, savefile=None, plotlabels=None):
    """ Plot radar graph of Fmes, P and R from onset analysis file(s)
    """
    
    data = []
    measures = ['F-measure', 'Precision', 'Recall']
    
    for file in files:
        results = read_onset_analysis(file)
        data.append([results[measure] for measure in measures])
    
    if savefile is not None:
        sp = SavePlot(True, savefile, auto_overwrite=True)
    else:
        sp = SavePlot(False, auto_overwrite=True)
        
    make_radar_graph(data, sp, labels=plotlabels)
    
    
def get_colours():
    return ['#3778bf', 'orange', 'red', 'magenta', 'green', 'deeppink', 
            'yellow', 'navy', 'lime']

def get_marker():
    return 'o'

def get_linestyle():
    return '-'


def make_legend(sl, labels):
    markers = [get_marker()] * len(labels)
    linestyles = [get_linestyle()] * len(labels)
    colours = get_colours()
    colours = colours[:len(labels)]
    sl.plot(labels, colours=colours, markers=markers,
            linestyles=linestyles)


if __name__ == '__main__':
    
    project = '/home/keziah/onsets/hsj/'
    resultspath = os.path.join(project, 'Sandpit', 'results', 'Iowa')
    resultsfile = 'onset_analysis.txt'
    
    resultssubdir = 'result_analysis'
    
    savepath = os.path.join(project, 'Visualisation', 'Iowa')
    
    dir_pairs = [('4_Apr_3', '5_Apr_1'), ('6_Apr_2', '6_Apr_3')]
    dirs = [p[0] for p in dir_pairs]
    savedirs =  ['d_1e-4', 'd_5e-4']
    
    techniques = [('arco', 'pizz'), ('vib', 'novib')]
    octaves = ['octave {}'.format(i) for i in range(9)]
    
#    # plot all with and without last-first for both damping factors
#    for n, pair in enumerate(dir_pairs):
#        savefile = os.path.join(savepath, savedirs[n], 'onset_analysis_all.pdf')
#        files = [os.path.join(resultspath, d, resultssubdir, resultsfile) 
#                 for d in pair]
#        plot_file_data(files, savefile=savefile)
#        
#        # make legend and save in separate file
#        plotlabels = ["With 'last-first'", "W/out 'last-first'"]
#        savefile = os.path.join(savepath, savedirs[n], 
#                            'onset_analysis_all_legend.pdf')
#        sl = SaveLegend(savefile, auto_overwrite=True)
#        make_legend(sl, plotlabels)
        
#
#    # plot arco/pizz and vib/no vib
#    for tcnq in techniques:
#        resultsfiles = ['onset_analysis_{}.txt'.format(t) for t in tcnq]
#        
#        for n, d in enumerate(dirs):
#            details = '{}_{}'.format(*tcnq)
#            savefile = os.path.join(savepath, savedirs[n],
#                                    'onset_analysis_{}.pdf'.format(details))
#            files = [os.path.join(resultspath, d, resultssubdir, resultsfile) 
#                     for resultsfile in resultsfiles]
#            plot_file_data(files, savefile=savefile)
#            
#            # make legend and save in separate file
#            plotlabels = [t.capitalize() for t in tcnq]
#            savefile = os.path.join(savepath, savedirs[n], 
#                                'onset_analysis_{}_legend.pdf'.format(details))
#            sl = SaveLegend(savefile, auto_overwrite=True)
#            make_legend(sl, plotlabels)
#            
      
    instruments = ['Guitar', 'Piano']
    dynamics = ['pp', 'mf', 'ff']
    
    for instrument in instruments:
        file_end = ['{}.{}'.format(instrument, dyn) for dyn in dynamics]
        resultsfiles = ['onset_analysis_{}.txt'.format(s) for s in file_end]
        
        for n, d in enumerate(dirs):
            details = '{}_dynamics'.format(instrument.lower())
            savefile = os.path.join(savepath, savedirs[n],
                                    'onset_analysis_{}.pdf'.format(details))
            files = [os.path.join(resultspath, d, resultssubdir, resultsfile) 
                     for resultsfile in resultsfiles]
            plot_file_data(files, savefile=savefile)
            
            # make legend and save in separate file
            savefile = os.path.join(savepath, savedirs[n], 
                                'onset_analysis_{}_legend.pdf'.format(details))
            sl = SaveLegend(savefile, auto_overwrite=True)
            make_legend(sl, labels=dynamics)
    
        
    
#    # plot octaves
#    for n, d in enumerate(dirs):
#        
#        resultsfiles = ['onset_analysis_{}.txt'.format(o.replace(' ', '_'))
#                        for o in octaves]
#        
#        details = 'octaves'
#        
#        savefile = os.path.join(savepath, savedirs[n],
#                                'onset_analysis_{}.pdf'.format(details))
#        files = [os.path.join(resultspath, d, resultssubdir, resultsfile) 
#                 for resultsfile in resultsfiles]
#        
#        plot_file_data(files, savefile=savefile)
#        
#        # make legend and save in separate file
#        plotlabels = [o.capitalize() for o in octaves]
#        savefile = os.path.join(savepath, savedirs[n], 
#                            'onset_analysis_{}_legend.pdf'.format(details))
#        sl = SaveLegend(savefile, auto_overwrite=True)
#        make_legend(sl, plotlabels)
#    
#    