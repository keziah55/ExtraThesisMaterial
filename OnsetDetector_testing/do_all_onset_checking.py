#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 12:44:57 2019

@author: keziah
"""

import pandas as pd
import os.path
from check_onsets import CheckOnsets
from report_results import read_results

def check_onsets_all_breakdown(outdir):
    
    check_onsets(outdir)
    make_all_reports(outdir)
    
    
def check_onsets(outdir):

    user = os.path.expanduser('~')
    onsets_path = os.path.join(user, 'Iowa', 'onsets')
    
    tolerance = 50
    
    # get directory to read from
    print('Checking results from {}'.format(outdir))
    
    # subdir for in-depth analysis
    outpath = os.path.join(outdir, 'result_analysis')
    
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    # get all onset analysis
    c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
    c.check(write=True, outpath=outpath)
    
    # get onset analysis by instrument type
    dirs = ['Brass', 'Percussion', 'Strings', 'Woodwind', 'Piano_Guitar']
    for dr in dirs:
        print('  Checking {} files...'.format(dr))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['Dir1', '==', dr], write=True, outpath=outpath)
        
    # get piano and guitar onset analysis
    dirs = ['Piano', 'Guitar']
    for dr in dirs:
        print('  Checking {} files...'.format(dr))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['Dir2', '==', dr], write=True, outpath=outpath)
        
    dynamics = ['Piano.ff', 'Piano.mf', 'Piano.pp', 'Guitar.ff', 'Guitar.mf',
                'Guitar.pp']
    for dyn in dynamics:
        print('  Checking {} files...'.format(dyn))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['File', '.__contains__(', dyn, ')'], write=True, 
                           outpath=outpath)
        
    # analyse percursion onsets with and without rolls
    conditions = ['roll', 'no_roll']
    for condition in conditions:
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=condition, write=True, outpath=outpath)
        
    # anlayse by dir2, but remove strings, as they are split by sulA etc.
    # because xylophone samples are xylo.rosewood and xylo.rosewood.roll etc,
    # need to test for equality, rather than str contains
    # therefore all string analysis is done after this
    file = os.path.join(outdir, 'found_onsets.csv')
    
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    # get Dir2 column
    df = pd.read_csv(file, sep='\t')
    # get set of dirs
    dirs = list(set(df['Dir2']))
    # group strings by these categories
    strings = ['Violin.pizz.ff', 'Violin.arco.ff', 'Viola.pizz.ff', 
               'Viola.arco.ff', 'Cello.pizz.ff', 'Cello.arco.ff', 
               'Bass.pizz.ff', 'Bass.arco.ff']
    # remove items that contain each string from dirs
    dirs = [item for item in dirs if not item.startswith(tuple(strings))]
    dirs.sort()
    
    for dr in dirs:
        print('  Checking {} files...'.format(dr))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['Dir2', '==', dr], write=True, 
                           outpath=outpath)
        
    # group all string samples that differ only by string
    # also group by vib, novib, arco and pizz      
    other_categories = ['.vib.', '.novib', '.arco.', '.pizz.']
    dirs = strings + other_categories
    dirs.sort()
    
    for dr in dirs:
        print('  Checking {} files...'.format(dr))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['Dir2', '.__contains__(', dr, ')'], write=True, 
                           outpath=outpath)    
    
    # analyse by octave number
    octaves = ['{:.0f}'.format(item) for item in range(9)]
    for octave in octaves:
        print('  Checking files in ocatve {}...'.format(octave))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['File', '.__contains__(', octave, ')'], write=True, 
                           outpath=outpath, fname_extra='octave')
        
        
    
    
def make_all_reports(resultsdir, resultssubdir='result_analysis'):
    
    print('Making tables...')
    
    # report instrument categories 
    categories = ['All', 'Brass', 'Guitar', 'Piano', 'Percussion (all)', 
                  'Percussion (rolls)', 'Percussion (no rolls)', 'Strings', 
                  'Woodwind']
    
    # filenames that are not 'onset_analysis_Category.txt'
    cat_name = {'All':'', 'Percussion (all)':'_Percussion',
                'Percussion (rolls)':'_Percussion_roll', 
                'Percussion (no rolls)':'_Percussion_no_roll'}
    
    read_results(resultsdir, categories, cat_name)
    
    # report octaves
    categories = [str(i) for i in range(9)]
    cat_name = {c:'_octave_{}'.format(c) for c in categories}
    
    read_results(os.path.join(resultsdir, resultssubdir), categories, cat_name, 
                 os.path.join(resultsdir, 'results_table_octave.tex'))
    
    
    # report arco/pizz
    categories = ['Arco', 'Pizzicato']
    cat_name = {'Arco':'_arco', 'Pizzicato':'_pizz'}
    
    read_results(os.path.join(resultsdir, resultssubdir), categories, cat_name, 
                 os.path.join(resultsdir, 'results_table_arcopizz.tex'))
    
    # report with/without vibrato
    categories = ['Vibrato', 'No vibrato']
    cat_name = {'Vibrato':'_vib', 'No vibrato':'_novib'}
    
    read_results(os.path.join(resultsdir, resultssubdir), categories, cat_name, 
                 os.path.join(resultsdir, 'results_table_vibrato.tex'))
    
    
if __name__ == '__main__':
    
    dirs = ['4_Apr_3', '5_Apr_1', '6_Apr_2' , '6_Apr_3']
    resultspath = '/home/keziah/onsets/hsj/Sandpit/results/Iowa/'
    
    for dr in dirs:
        path = os.path.join(resultspath, dr)
        check_onsets(path)
        
#    check_onsets_all_breakdown(path)
    
    
    

        