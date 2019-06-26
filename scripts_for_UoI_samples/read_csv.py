#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python script to add onsets from roll csv files to main onsets csv.

Commented out code at the bottom tracks how much of the onsets.csv file
has onsets filled in.
"""

import pandas as pd
import os.path

def get_times_csv(file):
    
    times = []
    line = ' '
    
    with open(file) as fileobj:
        while line:
            line = fileobj.readline()
            time = line.split(',')[0]
            try: # using try-except rather than filtering empty strings after
                float(time)    
                times.append(time)
            except:
                pass
            
    return times

path = '/home/keziah/Iowa/onsets/'

file = os.path.join(path, 'onsets_original.csv')
dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

df = pd.read_csv(file)

oCol = 'Onsets'
fCol = 'File'

for d in dirs:
    files = os.listdir(os.path.join(path, d))
    
    for file in files:
        
        # get list of onsets
        onsets = get_times_csv(os.path.join(path, d, file))
        
        # remove '.csv' from file name
        name = os.path.splitext(file)[0]
        
        # find row in DataFrame where this file is found
        row = df.loc[df[fCol]==name+'.wav']
        
        if not row.empty:
            # get index of this row for 'at' command
            idx = row.index
            # make string of onsets and put in DataFrame
            df.at[idx, oCol] = ','.join(onsets)
        else:
            print("Could not find '{}' in DataFrame".format(name))

df.to_csv(os.path.join(path, 'onsets.csv'), index=False)



#col = 'Onsets'
#
#files = []
#
#total = len(df)
#
#for i in range(total):
#    row = df.loc[i]
#    if pd.notnull(row[col]):
#        file = os.path.join(row['Dir1'], row['Dir2'], row['File'])
#        files.append(file)
#        
#ready = len(files)
#        
#print('{} files out of {} are ready to be analysed ({}%)'
#      .format(ready, total, int(100*ready/total)))
