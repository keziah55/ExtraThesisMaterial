#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 15:27:34 2018

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank, NoteDetector, OnsetDict
import soundfile as sf
import matplotlib.pyplot as plt
import os
import sys


class TestNoteDetector:
    
    def __init__(self, audio_path, results_path):
        """ Test NoteDetector on Iowa samples.
        
            Paramters
            ---------
            audio_path : str
                Path to all audio files. The files should be in two layers of
                subdirectories beyond this, 
                e.g. '<audio_path>/Strings/Violin.arco.ff.sulD/'
            
            results_path : str
                Path to write results file to
        """
        
        self.root = audio_path # path to all audio files
        self.results_path = results_path
        
        # write all results to a tab-separated file
        header = ['Dir1', 'Dir2', 'File', 'Fs', 'Onsets', 'Frequency']
        self.sep = '\t'
        self.out = self.sep.join(header) + '\n'
        
        
    def write_results(self):
        file = 'found_onsets.csv'
        with open(os.path.join(self.results_path, file), 'w') as fileobj:
            fileobj.write(self.out)
            
            
    def _write_csv_line(self, file, sr, onsets, freq):
        # add line to self.out
        # `file` should be the full file path
        
        head, tail = os.path.split(file)
        dir1, dir2 = self._get_dir1_dir2(head)
        
        if len(onsets) == 0:
            onsets_str= 'None'
        elif len(onsets) > 1:
            onsets_str = '"'
            for n in range(len(onsets)-1):
                onsets_str += '{},'.format(onsets[n])
            onsets_str += '{}"'.format(onsets[-1])
        else:
            onsets_str = '{}'.format(onsets[0])
            
        line = [dir1, dir2, tail, str(sr), onsets_str, str(freq)]
        
        self.out += self.sep.join(line) + '\n'
        

    def _get_dir1_dir2(self, path):
        # remove root from path' remainder should be dir1 and dir2
        dir1dir2 = path.replace(self.root, '')
        dir1dir2 = dir1dir2.split(os.path.sep)
        dir1, dir2 = list(filter(None, dir1dir2)) 
        return dir1, dir2
        
            
    @staticmethod
    def listdirs(path):
        """ Return full path of every directory in `path` """
        ls = [os.path.join(path, d) for d in os.listdir(path)
              if os.path.isdir(os.path.join(path, d))]
        return ls
    
    
    @staticmethod
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
            
            
    def analyse(self, plot_onset=False):
        
        dir1s = self.listdirs(self.root)
        
        err_file = 'iowa_files_error.txt'
        
        for dir1 in dir1s:
            dir2s = self.listdirs(dir1)
            
            for dir2 in dir2s:
                print('Analysing {}'.format(dir2))
                files = self.listfiles(dir2, ext='wav')
                
                for file in files:
                    try:
                        self._get_onsets(file, plot_onset)
                    except Exception as err:
                        if not os.path.exists(err_file):
                            err_files = open(err_file, 'w')
                        err_files.write(file+'\n')
                        err_files.write(err+'\n\n')
                        
                    
        self.write_results()
                    
                    
    def _get_onsets(self, file, plot_onset):
        
        audio, sr = sf.read(file)
    
        head, tail = os.path.split(file)
        base, ext = os.path.splitext(tail)
        
        # `base` is file name with data separated by dots
        # go backwards through each item and see if it is a note
        baselst = base.split('.')
        i = -1
        while True: 
            # if we've gone as far back as we can without finding a note, exit
            if i <= -len(baselst):
                print('Cannot parse file {}'.format(tail))
                sys.exit(1)
            # try this item
            try:
                # get note number relative to A4 (for frequency calculation)
                k = self.get_note_num(baselst[i])
                break
            # if this item isn't a note, go backwards and try again
            except ValueError:
                i -= 1
        
        method = DetectorBank.runge_kutta
        f_norm = DetectorBank.freq_unnormalized
        a_norm = DetectorBank.amp_normalized
        d = 0.0001
        gain = 25
    
        # centre frequency and semitones on either side
        edo = 12
        f0 = np.array([440*2**(k/edo)])
        bandwidth = 0
        
        threshold = 0.0005
        
        nd = NoteDetector(sr, audio.astype(np.float32), f0, edo, 
                          bandwidth, method|f_norm|a_norm, d, gain)
        
        onsets = OnsetDict()
        
        nd.analyse(onsets, threshold)
        
        try:
            o = onsets[0]
        except IndexError:
#            print('No onsets found?')
#            print(onsets)
            o = []
        
        self._write_csv_line(file, sr, o, f0[0])
        
        if plot_onset:
            d1, d2 = self._get_dir1_dir2(head)
            path = os.path.join(self.results_path, 'figs', d1, d2)
            if not os.path.exists(path):
                os.makedirs(path)
            plotname = os.path.join(path, base+'.pdf')
            self.plot_results(sr, audio, o, plotname)
            
        
    def plot_results(self, sr, audio, onsets, savefile):
    
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        t = np.linspace(0, len(audio)/sr, len(audio))
    
        plt.plot(t, audio, color='dodgerblue')
        
        if len(onsets) > 0:
            for o in onsets:
                plt.axvline(o/sr, color='red', linestyle='--')
                
        plt.xlabel('Time (s)')
        plt.grid()
            
        plt.savefig(savefile, format='pdf')
        plt.close()
        

    @staticmethod
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
                'f#7', 'g7', 'g#7', 'a7', 'a#7', 'b7', 'c8']
                
        return name.index(note) - 48


    


if __name__ == '__main__':
    
    user = os.path.expanduser('~')
    audio_path = os.path.join(user,'Iowa', 'all')
    results_path = os.path.join(user, 'onsets', 'hsj', 'Sandpit',
                                'results', 'Iowa')
    nd = TestNoteDetector(audio_path, results_path)

#    try:
    nd.analyse(plot_onset=True)
#    except BaseException as err:
#        nd.write_results()
#        print('Error msg: {}'.format(err))
        
        