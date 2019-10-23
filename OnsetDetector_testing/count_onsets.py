#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Count number of onsets in University of Iowa Musical Instrument Samples
"""

import pandas as pd
import os.path


def count_onsets(file, report=False):
    
    df = pd.read_csv(file)
    
    col = 'Onsets'
    
    count = 0
    
    for i in range(len(df)):
        
        row = df.loc[i]
        onsets = str(row[col])
        onsets = onsets.split(',')
        count += len(onsets)
        
    if report:
        print("{} contains {} onsets, across {} files."
              .format(file, count, len(df)))
    
    return count


def count_roll_onsets(path):
    
    count_roll = 0
    count_files = 0
    mx = 0
    mn = 100
    
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    
    rolls_per_file = {}
    
    for d in dirs:
        
        files = os.listdir(os.path.join(path, d))
        count_files += len(files)
        
        for file in files:
            df = pd.read_csv(os.path.join(path, d, file))
            num = len(df)
            count_roll += num
            
            root, _ = os.path.splitext(file)
            rolls_per_file[root] = num
            
            if num > mx:
                mx = num
            if num < mn:
                mn = num
            
    print("Roll csv files contain a total of {} onsets across {} files."
          .format(count_roll, count_files))
    print("The maximum number of onsets in one file is {}; the minimum is {}."
          .format(mx, mn))
    print("Mean onsets per roll is {:.0f}.".format(count_roll/count_files))
    
    return rolls_per_file
        
    
if __name__ == '__main__':
    
    path = '../Data/'
    file = 'onsets.csv'
    
    count = count_onsets(os.path.join(path, file), True)    
    rolls_per_file = count_roll_onsets(path)
    
    nums = sorted([v for k,v in rolls_per_file.items()])
    files = [k for k,v in rolls_per_file.items() if v==20]
    
    