#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse all Iowa samples, using SCOOP. If you don't want to use SCOOP, simply
comment out the import statement
"""

import numpy as np
from detectorbank import DetectorBank, NoteDetector, OnsetDict
import soundfile as sf
import matplotlib.pyplot as plt
from save_plot import SavePlot
from do_all_onset_checking import check_onsets_all_breakdown
from join_results import join_results
from analysed_files import get_analysed_files
import os
import time
from datetime import datetime
import calendar
import re
import subprocess
import scoop

sep = '\t'

def listdirs(path):
    """ Return full path of every directory in `path` """
    ls = [os.path.join(path, d) for d in os.listdir(path)
          if os.path.isdir(os.path.join(path, d))]
    return ls


def listfiles(path, ext=None):
    """ Return full path of every file in `path`
    
        If extenstion `ext` is supplied, the list will be filtered 
        accordingly.
    """
    ls = [os.path.join(path, f) for f in os.listdir(path)
          if os.path.isfile(os.path.join(path, f))]
    # if `ext` has been supplied, filter the list
    if ext is not None:
        # add leading dot to ext, if required, so can be compared with
        # result of os.path.splitext
        if ext[0] != '.':
            ext = '.' + ext
        ls = [f for f in ls if os.path.splitext(f)[1]==ext]
    return ls

    
def write_results(path, file, data):
    with open(os.path.join(path, file), 'w') as fileobj:
        fileobj.write(data)
        
        
def make_csv_line(file, sr, onsets, freq, audio_path):
    # add line to self.out
    # `file` should be the full file path
    
    head, tail = os.path.split(file)
    dir1, dir2 = _get_dir1_dir2(audio_path, head)
    
    if len(onsets) == 0:
        onsets_str = 'None'
    elif len(onsets) > 1:
        onsets_str = '"'
        for n in range(len(onsets)-1):
            onsets_str += '{},'.format(onsets[n])
        onsets_str += '{}"'.format(onsets[-1])
    else:
        onsets_str = '{}'.format(onsets[0])
        
    try:
        len(freq)
        freq_str = ','.join([str(f) for f in freq])
        freq_str = '"' + freq_str + '"'
    except:
        freq_str = '"' + str(freq) + '"'
        
    line = [dir1, dir2, tail, str(sr), onsets_str, freq_str]
    
    out = sep.join(line)
    
    return out
    

def _get_dir1_dir2(root, path):
    # remove root from path' remainder should be dir1 and dir2
    dir1dir2 = path.replace(root, '')
    dir1dir2 = dir1dir2.split(os.path.sep)
    dir1, dir2 = list(filter(None, dir1dir2)) 
    return dir1, dir2
    
        
def analyse(file, outdir='.', audio_path='.'):
    if 'scoop' in sys.modules:
        print_func = scoop.logger.info
    else:
        print_func = print
        
    out = []
    try:
        out = _get_onsets(file, plot_onset=False, outdir=outdir, 
                          audio_path=audio_path)
        msg = '{} completed'.format(file)
        print_func(msg)
    except Exception as err:
        msg = '{}: {}'.format(file, err)
        print_func(msg)
    return out


def _get_onsets(file, plot_onset=True, outdir='.', audio_path='.'):
    
    head, tail = os.path.split(file)
    base, ext = os.path.splitext(tail)
    d1, d2 = _get_dir1_dir2(audio_path, head)
    
    # store integers to give frequencies (relative to A4)
    note_n = []
    
    # `base` is file name with data separated by dots
    # go backwards through each item and see if it is a note
    baselst = base.split('.')
    i = -1
    while True: 
        # if we've gone as far back as we can without finding a note, exit
        if i <= -len(baselst):
            msg = 'Cannot parse note in filename {}'.format(tail)
            raise ValueError(msg)
        # check if the file is a (xylophone) glissandi
        if baselst[i].lower() == 'gliss':
            # assuming same xylophone used for all recordings
            if baselst[i+1].lower() == 'up':
                k = get_note_num('F4')
                break
            elif baselst[i+1].lower() == 'down':
                k = get_note_num('C8')
                break
#            note_n = list(range(k0, k1+1))
        # try this item
        try:
            # get note number relative to A4 (for frequency calculation)
            k = get_note_num(baselst[i])
            break
        # if this item isn't a note, go backwards and try again
        except ValueError:
            i -= 1
            
    audio, sr = sf.read(file)
    
    args = getNDargs()
    threshold, f_size, edo, bandwidth, method, f_norm, a_norm, d, gain = args
    
    # if note_n not yet full (i.e. file is not a glissando)
    if not note_n:
        # make indices for frequency list comprehension
        # if given f_size is odd, it will be rounded up to the next odd number
        # frequencies will be symmetrical around centre
        note_n = [k]
        for i in range(1, f_size//2+1):
            note_n.append(k-i)
            note_n.append(k+i)
        note_n.sort()
    
    f0 = np.array([440*2**(i/edo) for i in note_n])
    
    path = os.path.join(outdir, 'log', d1, d2, base)
    if not os.path.exists(path):
        os.makedirs(path)
    
    nd = NoteDetector(sr, audio.astype(np.float32), f0, edo, 
                      bandwidth, method|f_norm|a_norm, d, gain,
                      path)
    
    onsets = OnsetDict()
    
    nd.analyse(onsets, threshold)
    
    try:
        # collect all onsets together, remove duplicates and sort
        o = set([v for k in onsets.keys() for v in onsets[k]])
        o = sorted(list(o))
    except IndexError:
#            print('No onsets found?')
#            print(onsets)
        o = []
    
    out = make_csv_line(file, sr, o, f0, audio_path=audio_path)
    
    path = os.path.join(outdir, 'results')
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, base+'.csv'), 'w') as fileobj:
        fileobj.write(out)
    
    if plot_onset:
        path = os.path.join(outdir, 'figs', d1, d2)
        if not os.path.exists(path):
            os.makedirs(path)
        plotname = os.path.join(path, base+'.pdf')
        plot_results(sr, audio, o, plotname)
        
    return out
            
        
def plot_results(sr, audio, onsets, savefile):

    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    t = np.linspace(0, len(audio)/sr, len(audio))

    plt.plot(t, audio, color='dodgerblue')
    
    if len(onsets) > 0:
        for o in onsets:
            plt.axvline(o/sr, color='red', linestyle='--')
            
    plt.xlabel('Time (s)')
    plt.grid()
    
    sp = SavePlot(True, savefile=savefile, auto_overwrite=True)
    sp.plot(plt)
    

def get_note_num(note):
    
    note = note.lower()
    
    octave = 'abcdefg'
    
    if note[1] is 'b':
        idx = octave.index(note[0]) - 1
        new_note = octave[idx]
        oct_num = note[2]
            
        note = new_note + '#' + oct_num
        
    name = ['a0', 'a#0', 'b0', 'c1', 'c#1', 'd1', 'd#1', 'e1', 'f1', 
            'f#1', 'g1', 'g#1','a1', 'a#1', 'b1', 'c2', 'c#2', 'd2', 
            'd#2', 'e2', 'f2', 'f#2', 'g2', 'g#2', 'a2', 'a#2', 'b2', 
            'c3', 'c#3', 'd3', 'd#3', 'e3', 'f3', 'f#3', 'g3', 'g#3', 
            'a3', 'a#3', 'b3', 'c4', 'c#4', 'd4', 'd#4', 'e4', 'f4', 
            'f#4', 'g4', 'g#4', 'a4', 'a#4', 'b4', 'c5', 'c#5', 'd5', 
            'd#5', 'e5', 'f5', 'f#5', 'g5', 'g#5', 'a5', 'a#5', 'b5', 
            'c6', 'c#6', 'd6', 'd#6', 'e6', 'f6', 'f#6', 'g6', 'g#6', 
            'a6', 'a#6', 'b6', 'c7', 'c#7', 'd7', 'd#7', 'e7', 'f7', 
            'f#7', 'g7', 'g#7', 'a7', 'a#7', 'b7', 'c8', 'c#8', 'd8', 
            'd#8', 'e8', 'f8', 'f#8', 'g8']
            
    return name.index(note) - 48


def get_ondet_params_str(threshold, freq_size, seg_size, ifstmt, ndargs):
    
    ndargs = list(ndargs)
    
    if freq_size == 1:
        fs_str = 'frequency'
    else:
        fs_str = 'frequencies'

    features = [['Central difference', 'Runge-Kutta'],
                ['Freq unnormalized', 'Search normalized'],
                ['Amp unnormalized', 'Amp normalized']]
    
    ndstr = ['    EDO: {}\n', '    Bandwidth: {}\n',
    '    Method: {}\n', '    Freq norm: {}\n', '    Amp norm: {}\n',
    '    Damping: {}\n', '    Gain: {}\n']
    
    for idx in range(len(ndstr)):
        try:
            arg = ndargs[idx]
            if 2 <= idx <= 4:
                i = idx-2
                lst = features[i]
                shift = 8*i
                arg = lst[(arg >> shift)-1]
        except IndexError:
            arg = 'Default'
        ndstr[idx] = ndstr[idx].format(arg)
        
    s = time.ctime(time.time()) + '\n\n'
    s += 'OnsetDetector if statement: {}\n'.format(ifstmt)
    s += 'findExactTime() local min decision: if (std::isnan(current/mn) || current/mn >= 0.95) \n'
    s += 'OnsetDetector segment size: {}ms\n'.format(seg_size)
    s += 'Threshold: {}\n'.format(threshold)
    s += 'Searching for {} {}\n'.format(freq_size, fs_str)
    s += 'NoteDetector args:\n'
    s += ''.join(ndstr)
#    s += '\n'
    
    return s


def _get_next_dir(resultsdir):
    ## Get next outdir by getting current date and checking whether any
    ## dirs already exist for that date
    ## Returns day_mnth_X where X is the next results number for that date
    ## e.g. 13_Oct_2
    
    pwd = os.getcwd()
    
    # get current date as base of outdir
    now = datetime.now()
    day = now.day
    month = calendar.month_abbr[now.month]
    
    outdir = '{}_{}_'.format(day, month)
    
    # look in resultsdir for any other dirs beginning with that date
    path = os.path.join(pwd, resultsdir)
    
    # make regex for dirname
    pattern = re.compile(outdir+'(\d+)')
    
    # max number anywhere in dirnames
    # i.e. if only 'dream' has a dir for this date, all outdirs will be
    # the next number
    mx = 0
    
    # get all dirs in subdir
    ls = os.listdir(path)
    # get numbers of any matching dirs
    nums = [int(pattern.findall(dr)[0]) for dr in ls 
            if pattern.findall(dr)]
    # if there are dirs for this day, get the maximum number 
    if nums and max(nums) > mx:
        mx = max(nums)
        
    # next dir num is current max + 1
    num = mx + 1
    
    outdir += str(num)
    
    return outdir
    

def getNDargs():
    """ Return NoteDetector args in the following order:
        threshold, edo, bandwidth, method, f_norm, a_norm, damping, gain
    """
    
    # dictionary of damping:threshold pairs
    thresholds = {0.0005:0.0005, 0.0001:0.0003}
    
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_normalized
    damping = 0.0005 # 0.0001 #  
    gain = 25
    
    freqSize = 1

    edo = 12
    bandwidth = 0
    
    threshold = thresholds[damping]#  0.0015 #0.0005  # 0.0003 # 0.0001   
    
    return (threshold, freqSize, edo, bandwidth, method, f_norm, a_norm, 
            damping, gain)
    

if __name__ == '__main__':
    
    import sys
    
    if 'scoop' in sys.modules:
        map_func = scoop.futures.map
    else:
        map_func = map
    
    user = os.path.expanduser('~')
    audio_path = os.path.join(user, 'Iowa', 'all')
    onsets_path = os.path.join('..', 'Data')
    
    resultsdir = os.path.join('results')
    
    # get directory to write to
    # outdir will be of form 26_Mar_X
    outdir = _get_next_dir(resultsdir)
#    outdir = '6_Apr_3' # '5_Apr_1' # '4_Apr_3' #'6_Apr_2' # 
    outdir = os.path.join(resultsdir, outdir)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    outfile = 'found_onsets.csv'
    
    ifstmt = ('if (count >= 3 && last >= threshold)'
                  ', if (last-first >= std::log(2))')
    seg_size = 20
    
    tolerance = 50
    
    thr, freq_size, *args = getNDargs()
    ondet_params_str = get_ondet_params_str(thr, freq_size, seg_size, ifstmt, 
                                            args)
    with open(os.path.join(outdir, 'ondet_params.txt'), 'w') as fileobj:
            fileobj.write(ondet_params_str)
    
    header = ['Dir1', 'Dir2', 'File', 'Fs', 'Onsets', 'Frequency']
    out = sep.join(header) + '\n'
    
    done = get_analysed_files(os.path.join(outdir, outfile), audio_path)
    
    all_files = []
    
    dir1s = listdirs(audio_path)
    
    for dir1 in dir1s:
        dir2s = listdirs(dir1)
        
        for dir2 in dir2s:
            all_files += (listfiles(dir2, ext='wav'))
            
    all_files = [f for f in all_files if f not in done]
            
    all_files.sort()
    
    print('Analysing {} audio files...'.format(len(all_files)))
    
    # 'analyse' returns a string of csv-formatted data
    func = lambda f: analyse(f, outdir=outdir, audio_path=audio_path)
    csvdata = list(map_func(func, all_files))
        
#### if running on multiple machines, you may want to include these lines to
#### copy results over
#    for d in ['results', 'log']:
#        path = os.path.join(outdir, d)
#
#        subprocess.run(["scp", "-r", 
#                        "keziah@192.168.0.15:"+path+"/*",
#                        path])
        
    join_results(outdir, outfile)
  
    # check onsets and write analysis files
    check_onsets_all_breakdown(outdir)
