#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Called by analyse_iowa_samples.py to put all results in single csv file.
"""

import os

sep = '\t'

def join_results(path, outfile):
    
    header = ['Dir1', 'Dir2', 'File', 'Fs', 'Onsets', 'Frequency']
    out = sep.join(header) + '\n'
    
    resultsdir = os.path.join(path, 'results')
    
    files = [f for f in os.listdir(resultsdir) 
             if os.path.splitext(f)[1]=='.csv']
    
    # store csv rows
    rows = []
    
    for file in files:
        with open(os.path.join(resultsdir, file)) as fileobj:
            text = fileobj.read()
        rows.append(text)
        
    # sort rows before writing to file
    rows.sort()
    out += '\n'.join(rows)
        
    with open(os.path.join(path, outfile), 'w') as fileobj:
        fileobj.write(out)
        
    return out


if __name__ == '__main__':

    user = os.path.expanduser('~')
    outdir = '30_Mar_2'
    resultsdir = os.path.join(user, 'onsets', 'hsj', 'Sandpit', 
                              'results', 'Iowa', outdir)
    
    out = join_results(resultsdir, 'found_onsets.csv')
