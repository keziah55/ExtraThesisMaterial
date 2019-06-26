#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Write csv file of all onset times.
"""

import os
import soundfile as sf

def lsdir(path):
    """ Return sorted list of directories in path """
    dirs = os.listdir(path)
    dirs = [d for d in dirs if os.path.isdir(os.path.join(path,d))]
    dirs.sort()
    return dirs

# directory layers:
# category/instrument/file.wav
root = '/home/keziah/Iowa/all/'

header = ['Dir1', 'Dir2', 'File', 'Fs', 'Onsets']
rows = []
rows.append(header)
sep = '\t'

dirs = lsdir(root)

for d in dirs:
    
    subdirs = lsdir(os.path.join(root,d))
    
    for subdir in subdirs:
        
        files = os.listdir(os.path.join(root, d, subdir))
        files = [f for f in files if os.path.splitext(f)[1] == '.wav']
        files.sort()
        
        for file in files:
            audio, sr = sf.read(os.path.join(root,d,subdir,file))
            
            row = [d, subdir, file, str(sr), '']
            rows.append(row)
            
            
s = '\n'.join([sep.join(row) for row in rows]) + '\n'

with open('onsets.csv', 'w') as fileobj:
    fileobj.write(s)

            