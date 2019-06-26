#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check which files have been analysed, with results appearing in the 
found_onsets.csv file.
"""

import pandas as pd
import os.path

def get_analysed_files(file, audio_path):
    
    out = []
    
    # if 'found_onsets.csv' does not exist, return an empty list
    # otherwise, return list of full paths of files in found_onsets.csv
    if os.path.exists(file):
    
        df = pd.read_csv(file, delimiter='\t')
        
        cols = ['Dir1', 'Dir2', 'File']
        
        for i in range(len(df)):
            row = df.loc[i]
            lst = [row[c] for c in cols]
            p = os.path.join(audio_path, *lst)
            out.append(p)
        
    return out


if __name__ == '__main__':
    
    user = os.path.expanduser('~')
    
    audio_path = os.path.join(user, 'Iowa', 'all')
    
    outdir = '28_Mar_4'
    resultsdir = os.path.join(user, 'onsets', 'hsj', 'Sandpit', 
                              'results', 'Iowa', outdir)
    csvfile = 'found_onsets.csv'
    file = os.path.join(resultsdir, csvfile)
    
    out = get_analysed_files(file, audio_path)
    print(len(out))
    