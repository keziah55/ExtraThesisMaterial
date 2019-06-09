#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:07:35 2019

@author: keziah
"""

import os.path
import glob
import re
import numpy as np
import pandas as pd

def _checkDuplicate(lst, value, precision):
    # check if lst already contains value, when rounded to precision
    # returns True if value is duplicated, otherwise False
    fmt = '{{:{}}}'.format(precision)
    lst = [fmt.format(item) for item in lst]
    value = fmt.format(value)
    if value in lst:
        return True
    else:
        return False
    

def analyse(path):
    
    # get iterator path to all debug files
    i = get_dirs(path)
    
    all_tp_last = np.zeros(0)
    all_fp_last = np.zeros(0)
    
    all_tp_count = np.zeros(0)
    all_fp_count = np.zeros(0)
    
    all_tp_diff = np.zeros(0)
    all_fp_diff = np.zeros(0)
    
    while True:
        try:
            dr = next(i)
            files = glob.glob(dr+'/*_debug.txt')
#            files.sort()
#            # ugly, but want to do centre freq first
#            files = [files[1], files[0], files[2]]
            audio_file = os.path.split(dr)[1] + '.wav'
            times = []
            lasts = []
            counts = []
            diffs = []
            # for each file, get times and values
            for file in files:
                tms, lst, cnt, dff = getTPFP(file)
                # check if we already have a result at the given times
                for idx, t in enumerate(tms):
                    # if not, put time and corresponding value in list
                    if not _checkDuplicate(times, t, '7.3f'):
                        times.append(t)
                        lasts.append(lst[idx])
                        counts.append(cnt[idx])
                        diffs.append(dff[idx])
                
            # check all the times found
            # return arrays of 'last' values at true and false positives
            tpl, fpl = check_onsets(audio_file, times, lasts)
            tpc, fpc = check_onsets(audio_file, times, counts)
            tpd, fpd = check_onsets(audio_file, times, diffs)
                    
            # put results in arrays collecting all
            all_tp_last = np.append(all_tp_last, tpl)
            all_fp_last = np.append(all_fp_last, fpl)
            
            all_tp_count = np.append(all_tp_count, tpc)
            all_fp_count = np.append(all_fp_count, fpc)
            
            all_tp_diff = np.append(all_tp_diff, tpd)
            all_fp_diff = np.append(all_fp_diff, fpd)
            
        except StopIteration:
            break
        
    # print stats
    print('Found {} true positives and {} false positives\n'
          .format(len(all_tp_last), len(all_fp_last)))
    
    funcs = {'Mean':np.mean, 'STD':np.std, 'Min':np.min, 'Max':np.max}
    data = {'true positives':{'Last segment value':all_tp_last, 
                              'Count':all_tp_count,
                              'Difference':all_tp_diff}, 
            'false positives':{'Last segment value':all_fp_last, 
                               'Count':all_fp_count,
                               'Difference':all_tp_diff}}
    
    for s, arrs in data.items():
        print(s.upper() + '\n' + '-'*len(s))
        
        for label, arr in arrs.items():
            print('** ' + label + ' **')
        
            for name, func in funcs.items():
                value = func(arr)
                
                if label != 'Last segment value':
                    s = '{: >4}: {:6.3f}'.format(name, value)
                else:
                    exp = np.exp(value)
                    s = '{: >4}: {:7.3f} = log({:.4f})'.format(name, value, exp)

                print(s)
            print()

    return all_tp_last, all_fp_last


def get_files(path):
    # return iterator of full path to files ending _debug.txt
    i = glob.iglob(path+'/**/*_debug.txt', recursive=True)
    return i

def get_dirs(path):
    # return iterator of full path to dirs containing _debug.txt files
    i = glob.iglob(path+'/*/*/*')
    return i


def getTPFP(file):
    # return array of 'last' values for successful detections
    
    with open(file) as fileobj:
        text = fileobj.read()
        
    detections = [item for item in text.split('\n\n') if item]
    
    r_onset = re.compile(r'Onset found at \d+ samples, (\d+.?\d*) seconds')
    r_thr = re.compile(r'Last: (-?\d+.?\d*), threshold: (-?\d+.?\d*)')
    r_count = re.compile(r'Count: (\d+)')
    r_diff = re.compile(r'Last: -?\d+.?\d*, first: -?\d+.?\d*, last-first: log\((-?\d+.?\d*)\)')
    
    times = []
    lasts = []
    counts = []
    diffs = []

    for detection in detections:
        # get if detection returned an onset
        lines = [item.strip() for item in detection.split('\n') if item]
        m_onset = r_onset.match(lines[-1])
        # if so, find the time and the 'last' value and add to lists
        if m_onset:
            m_count = r_count.match(lines[1])
            count = m_count.group(1)
            
            m_thr = r_thr.match(lines[2])
            last = m_thr.group(1)
            
            m_diff = r_diff.match(lines[3])
            diff = m_diff.group(1)
            
            time = m_onset.group(1)
            times.append(float(time))
            lasts.append(float(last))
            counts.append(float(count))
            diffs.append(float(diff))
            
    times = np.array(times)
    lasts = np.array(lasts)
    counts = np.array(counts)
    diffs = np.array(diffs)
    
    return times, lasts, counts, diffs
            
            
def check_onsets(file, times, values):
    """ Check if the given onset times are correct and return the corresponding
        values
        
        Parameters
        ----------
        file : str
            audio file name, without full path
        times : np.array or list
            times found by NoteDetector
        values : np.array or list
            values to filter by result correctness
            
        Returns
        -------
        Two numpy arrays: the values that correspond to true positive detections
        and those that correspond to false positives
    """
    
    # get manual onsets
    df = pd.read_csv('/home/keziah/Iowa/onsets/onsets.csv')
    row = df.loc[df['File']==file]
    # this returns a Series
    onsets = row['Onsets']
    # Series.values returns the Series as an np.array BUT the values are
    # one big string, so we have to take the first (and only) value from the
    # array and split by commas, then cast as float, then put in array
    # Fuck sake
    onsets = np.array([float(o) for o in onsets.values[0].split(',') if o])
    
    # compare manual onsets with automatic
    # 'correct' is array of indices where times were correct
    correct, _ = compare(onsets, times)
    
    # get values where times were correct (true positives)
    tp = np.array([values[i] for i in correct])
    # get values where times were incorrect (false positives)
    fp = np.array([values[i] for i in range(len(times)) if i not in correct])
    
    return tp, fp

            
# copied from check_onsets.py
def compare(times, results):
    """ Compare array of manual onset times with found onsets
    
        Parameters
        ----------
        times : np.array
            array of manual times (seconds)
        results : np.array
            array of found times (seconds)
            
        Returns
        -------
        correct : np.array
            array of indices where `results` values were correct
        diff : np.array
            array of time differences (ms) between maunal and found times.  
            If onset was not found, value will be NaN
    """
    
    # difference between found and correct
    diff = np.zeros(len(times))
    diff.fill(np.nan)
    
    correct = np.zeros(0, dtype=int)

    if not isempty(results):

        # for every correct time, get the difference between all the
        # found times...
        for idx, time in enumerate(times):
            all_diffs = np.zeros(len(results))

            for n, result in enumerate(results):
                dms = 1000*(result-time)
                all_diffs[n] = dms

            # ...find the smallest difference between current time
            # and all results...
            nearest_to_zero = np.min(np.abs(all_diffs))
            n = np.where(np.abs(all_diffs)==nearest_to_zero)[0][0]
            
            # ...if this difference is less than 50ms, it counts
            if nearest_to_zero <= 50:
                diff[idx] = all_diffs[n]
                correct = np.append(correct, n)
                
    return correct, diff


def isempty(a):
    """ Check if a numpy array has length of zero. """
    return True if len(a) == 0 else False
            

if __name__ == '__main__':
    
    root = '/home/keziah/onsets/hsj/Sandpit/results/Iowa'
    which = '4_Apr_2'
    path = os.path.join(root, which, 'log')
    
#    file = '/home/keziah/onsets/hsj/Sandpit/results/Iowa/1_Apr_1/log/Brass/Trumpet.vib/Trumpet.vib.ff.C4.stereo/261Hz_debug.txt'
#    tp, fp = getTPFP(file)
    
    tp, fp = analyse(path)

    
    
