#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 14:05:50 2019

@author: keziah
"""

import glob
import re

path = '/home/keziah/onsets/hsj/Sandpit/results/Iowa/6_Apr_2/log/Percussion/Xylophone.gliss/Xylophone.gliss.down.stereo/'

i = glob.iglob(path+'*_debug.txt')

regex = re.compile(r' +Onset found at 962 samples')

while True:
    
    try:
        file = next(i)
        with open(file) as fileobj:
            text = fileobj.read()
            
        m = regex.search(text)
        if m is not None:
            print(file)
            break
        
    except StopIteration:
        break
