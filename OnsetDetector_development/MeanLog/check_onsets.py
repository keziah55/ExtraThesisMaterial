#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check onsets found by OnsetDetector prototypes
"""

import numpy as np
import re
import os
import sys
from collections import OrderedDict


def isempty(a):
    """ Check if a numpy array has length of zero. """
    if len(a) == 0:
        return True
    else:
        return False


class CheckOnsets:
    
    def __init__(self, base, foundpath):
        """ Parameters
            ----------
            base : str
                path to directory with relevant onsets.txt
            foundpath : str
                path to directory with automatically found onsets (xxxHz.txt)
                and ondet_params.txt
        """
            
        self.foundpath = foundpath
        
        self.outStr = ''
        
        # get list of all frequencies searched for
        self.all_freqs = self.getAllFreqs(self.foundpath)
        
        # get number of manual onsets and dict of onsets
        self.nm, self.onsets_dict = self.readManual(base)
        
        self.writeHeader(self.foundpath)
        
        # initialise stats variables
        self.tp = 0
        self.fp = 0
        self.fp_spill = 0 # no. of fp that are actually notes in another band
        
        # find largest -/+ delay
        self.errors = [0,0]
        
        # get average advance and delay
        # each list here will store total and count
        # so mean = mn[0]/mn[1]
        self.mn_adv = [0,0]
        self.mn_del = [0,0]
        self.zero_diff = 0
        self.adv_15 = [0,0]
        self.del_15 = [0,0]
        
        
    def write(self, s, end='\n'):
        self.outStr += s + end
        
    def writeFile(self, path):
        with open(os.path.join(path, 'onset_analysis.txt'), 'w') as fileobj:
            fileobj.write(self.outStr)
            
    def writeHeader(self, path):
        """ Write heading and OnsetDetector parameters """
        
        # print heading, OnsetDetector parameters
        heading = 'Check onsetdetector results'
        self.write(heading+'\n'+'='*len(heading)+'\n')
        
        with open(os.path.join(path, 'ondet_params.txt')) as fileobj:
             header = fileobj.read()
        
        self.write(header, '\n')
            
    def check(self, write, outpath=None):
        """ Analyse the detected onsets and write results to file, if requested 
        """
        
        # for every frequency the OnsetDetector looked for
        for freq in self.all_freqs:
            self.checkFreq(self.foundpath, freq)
            
        p, r, f, pe, fe = self.getStats()
        
        if write:
            self.writeFile(outpath)
        
        return p, r, f, pe, fe
        
    @staticmethod
    def getAllFreqs(path):
        """ Get list of all frequencies the OnsetDetector analysed
        
            Parameters
            ----------
            path
                location of xxxHz.txt files
                
            Returns
            -------
            all_freqs
                sorted list of frequencies
        """
        
        # get list of files of found onsets
        txt_files = [f for f in os.listdir(path) 
                     if re.search(r'\d\d\d?Hz.txt', f)]
        
        # get list of all frequencies searched for
        all_freqs = []
        for file in txt_files:
            _, tail = os.path.split(file)
            all_freqs.append(os.path.splitext(tail)[0])

        all_freqs.sort()
        
        return all_freqs
    
    @staticmethod
    def readManual(path):
        """ Read file of manual onsets. 
        
            Parameters
            ----------
            path
                location of xxxHz.txt files
                
            Returns
            -------
            nm : int
                number of manual onsets
            onsets_dict : OrderedDict
                dictionary of frequency:onset times
        """
        
        # initialise number of correct onsets
        nm = 0
        
        # read all correct onsets into a dictionary and count them
        with open(os.path.join(path, 'onsets.txt')) as fileobj:
            onsets = fileobj.read()
        onsets = re.split('\n\n', onsets)
        onsets = list(filter(None, onsets))
        
        onsets_dict = OrderedDict()
        
        for idx, s in enumerate(onsets):
        
            freq, times = re.split(r'-+', s)
        
            freq = freq.strip()
            times = times.strip().split('\n')
            times = np.array(list(float(time) for time in times))
            nm += len(times)
            
            onsets_dict[freq] = times
            
        return nm, onsets_dict
    
    
    def checkFreq(self, path, freq):
        """ Check results for given frequency """
        
        self.report = [False, False]
        
        # if freq was in onsets.txt, get its times (from dict)
        # otherwise, empty array
        try:
            times = self.onsets_dict[freq]
        except KeyError:
            times = np.zeros(0)
            
        # initialise list of found times
        results = []
                
        # read file, get times
        with open(os.path.join(path, freq+'.txt')) as fileobj:
    
            while True:
                line = fileobj.readline()
                if re.match('Offsets', line):
                    break
                elif re.match('sample', line):
                    s = re.search('\d+\.\d+ seconds', line)
                    time, _ = s.group().split(' ')
                    results.append(float(time))
    
        results = np.array(results)
        
        # only go on if there are correct or found onsets at this frequency
        # i.e. stop if freq is not correct and there were no false detections
        if not isempty(times) or not isempty(results):
            
            self.write(freq + '\n' + '-'*len(freq))
            
            correct, diff = self.compare(times, results)
            
            # indices of true positives, false negatives and false positives
            tp = np.where(np.isnan(diff) == 0)[0]
            fn = np.where(np.isnan(diff))[0]
            fp = np.setdiff1d(np.arange(len(results)), correct)
            
            # count true and false positives
            self.tp += len(tp)
            self.fp += len(fp)
        
            # write true/false positive/negative info
            for idx in tp:
                self.write('Onset at {:6.3f} seconds'.format(times[idx]), 
                           end='')
                # get delay/advance for this time and add to stats
                d = int(diff[idx])
                self.analyseDiff(d)
                
                if d != 0:
                    self.write(', delay: {:3d}ms.'.format(d))
                else:
                    self.write('\n', end='')
        
            if isempty(fn) and isempty(fp):
                self.write('All onsets found!')
            else:
                if not isempty(fn):
                    self.write('\nFalse negatives:')
                    for i in fn:
                        self.write('{:6.3f}'.format(times[i]))
                        # write debug info
                        s = self.get_debug_data(path, freq, times[i], 'fn')
                        self.write(s)
                        self.report_append('fn', freq, times[i], s)
        
                if not isempty(fp):
                    self.write('\nFalse positives:')
                    for i in fp:
                        thereWasSpillover = False
                        self.write('{:6.3f}'.format(results[i]), end='')
                        # check if time is in another band
                        for k in self.onsets_dict.keys():
                            c, d = self.compare(self.onsets_dict[k], 
                                                np.array([results[i]]))
                            if not isempty(c):
#                                t = self.onsets_dict[k][c[0]]
                                self.write('    (spillover from {} band)'
                                           .format(k), end='')
                                self.fp_spill += 1
                                thereWasSpillover = True
                        if not thereWasSpillover:
                            # write debug info
                            s = self.get_debug_data(path, freq, results[i], 
                                                    'fp')
                            self.write(s)
                            self.report_append('fp', freq, results[i], s)
                            
                        self.write('\n', end='')
        
            self.write('\n', end='')
            
            
    def report_append(self, mode, freq, time, data):

        indices = {'fp':0, 'fn':1}
        fname_insert = ['positives', 'negatives']
        idx = indices[mode]
        
        fname = os.path.join(self.foundpath, 'false_{}.txt'
                             .format(fname_insert[idx]))
        header = ''

        if not self.report[idx]:
            # write num detectors and freq
            pth = self.foundpath
            d = ''
            while not d:
                pth, d = os.path.split(pth)
            det_freq = ' '.join(d.split('_')[2:]) + ' --- ' + freq
            det_freq += '\n' + '='*len(det_freq) + '\n'
            header += det_freq
            self.report[idx] = True
        
        with open(fname, 'a') as fileobj:
            fileobj.write(header)
            fileobj.write('* Detection at {:6.3f} seconds\n'.format(time))
            fileobj.write(data+'\n')
        
            
    @staticmethod
    def get_debug_data(path, freq, time, mode, sr=48000):
        """ Get debug data for a detection
    
            Parameters
            ---------
            path : str
                path to xxxHz_debug.txt file
            freq : str
                current frequency with Hz (i.e. xxxHz)
            time : float
                detection time to find
            mode : {'fp', 'fn'}
                are we looking for a false positive or a false negative
            sr : int
                sample rate of input. Default is 48000.
        """
    
        modes = {'fp':['accepted', 
                       re.compile(r'(?:Onset found at )(\d+)(?: samples)'),
                       int(0.001*sr)], 
                 'fn':['rejected',
                       re.compile(r'(?:Sample: )(\d+)'),
                       int(10*0.02*sr)]}
                 
        keyword, regex, margin = modes[mode]
    
        s_time = int(time*sr)
    
        with open(os.path.join(path, freq+'_debug.txt')) as fileobj:
            text = fileobj.read()
    
        data = text.split('\n\n')
        data = list(filter(None, data))
    
        results = [d for d in data if keyword in d]
        
        if mode == 'fp':
            results = [r for r in results if 'not verified' not in r]
        
        samples = np.array([int(regex.findall(r)[0]) for r in results])
        
        diff = samples-s_time
        idx = np.where(abs(diff) <= margin)[0]
        
        data = ''
        
        for i in idx:
            data += '\n>>> ' + results[i] + '\n'
    
        return data
                
    @staticmethod
    def compare(times, results):
        """ Compare array of manual onset times with found onsets
        
            Parameters
            ----------
            times : np.array
                array of manual times
            results : np.array
                array of found times
                
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
            
                
    def analyseDiff(self, d):
        """ Analyse difference, add to stats """
        
        # check if d is largest +/- error
        if d < 0 and d < self.errors[0]:
            self.errors[0] = d
            self.mn_adv[0] += d
            self.mn_adv[1] += 1
            
        elif d > 0 and d > self.errors[1]:
            self.errors[1] = d
            self.mn_del[0] += d
            self.mn_del[1] += 1
            
        elif d == 0:
            self.zero_diff += 1
            
        if d < -15:
            self.adv_15[0] += d
            self.adv_15[1] += 1
            
        elif d > 15:
            self.del_15[0] += d
            self.del_15[1] += 1


    def getStats(self):
        """ Calculate and write stats """
        
        # calculate stats
        na = self.tp + self.fp
        precision = self.tp/na
        recall = self.tp/self.nm
        try:
            fmeasure = 2 * precision * recall / (precision + recall)
        except ZeroDivisionError:
            fmeasure = 0
          
        # precision not including spillover
        precision_e = self.tp / (na-self.fp_spill) 
        try:
            fmeasure_e = (2 * precision_e * recall) / (precision_e + recall)
        except ZeroDivisionError:
            fmeasure_e = 0
        
        diff_sum = self.mn_adv[0] + self.mn_del[0]
        diff_num = self.mn_adv[1] + self.mn_del[1] + self.zero_diff
        mn_diff = diff_sum / diff_num
        
        self.write('\nStats\n=====')
        self.write('Total number of onsets:     {}'.format(self.nm))
        self.write('Total number of detections: {}'.format(na))
        self.write('Total true positives:       {}'.format(self.tp))
        self.write('Total false positives:      {}'.format(self.fp))
        self.write('Total erroneous detections: {}'.format(self.fp-self.fp_spill))
        
        self.write('\n', end='')
        
        means = []
        
        for mn in [self.mn_adv, self.mn_del]:
            try:
                m = mn[0]/mn[1]
            except ZeroDivisionError:
                m = 0
            means.append(m)
        
        self.write('Largest advance: {:3d}ms'.format(self.errors[0]))
        self.write('Mean advance:    {:7.3f}ms'.format(means[0]))
        self.write('Largest delay:   {:3d}ms'.format(self.errors[1]))
        self.write('Mean delay:      {:7.3f}ms'.format(means[1]))
        self.write('Mean difference: {:7.3f}ms'.format(mn_diff))
        self.write('Number of advances <-15ms: {}'.format(self.adv_15[1]))
        self.write('Number of delays   > 15ms: {}'.format(self.del_15[1]))
        
        self.write('\n', end='')
        
        self.write('Precision:             {:d}%'.format(int(100*precision)))
        self.write('Recall:                {:d}%'.format(int(100*recall)))
        self.write('F-measure:             {:d}%'.format(int(100*fmeasure)))
        
        self.write('Precision (tot. err.): {:d}%'.format(int(100*precision_e)))
        self.write('F-measure (tot. err.): {:d}%'.format(int(100*fmeasure_e)))
        
        return precision, recall, fmeasure, precision_e, fmeasure_e

                
if __name__ == '__main__':
    
    """ py3 check_onsets.py indir outdir
    """
    
    args = sys.argv
    
    if args[1] == '.':
        in_d = os.getcwd()
    else:
        in_d = os.path.abspath(args[1])
        
    if args[2] == '.':
        out_d = os.getcwd()
    else:
        out_d = os.path.abspath(args[2])
        
    user = os.path.expanduser('~')
    project = os.path.join(user, 'onsets', 'hsj')
#    
#    in_d = os.path.join(project, 'Visualisation', 'onset_detection','alice')
#    out_d = os.path.join(in_d, 'test_check_onsets')
        
    c = CheckOnsets(in_d, out_d)
    c.check(True, out_d)
