#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check onsets returned by NoteDetector against manually found onsets.
"""

import numpy as np
import pandas as pd
import os

def isempty(a):
    """ Check if a numpy array has length of zero. """
    return True if len(a) == 0 else False


def contains(s, sub_s):
    """ Function to do 'in'. Return True if sub_s in s """
    return sub_s in s
    

class CheckOnsets:
    
    def __init__(self, base, foundpath, tolerance=30):
        """ Parameters
            ----------
            base : str
                path to directory with manual onsets.csv
            foundpath : str
                path to automatically found onsets (found_onsets.csv)
                and ondet_params.txt
            tolerance : float
                onset time tolerance (ms). Onsets within tolerance will
                be regarded as correct. Default is 30ms.
        """
            
        self.foundpath = foundpath
        
        foundfile = os.path.join(self.foundpath, 'found_onsets.csv')
        manualfile = os.path.join(base, 'onsets.csv')
        
        self.found = pd.read_csv(foundfile, delimiter='\t')
    
        self.manual = pd.read_csv(manualfile)
        
        # onset time tolerance
        # onsets tolerance ms will be regarded as correct
        self.tolerance = tolerance
        # also use this to see how many of the onsets do not fall within 30ms
        self.tol2 = 15 #tolerance/2
    
        self.outStr = ''
        
        self.writeHeader(self.foundpath)
        
        # initialise stats variables
        self.nm = 0 # count_onsets(manualfile)
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
        self.adv_tol = [0,0]
        self.del_tol = [0,0]
        
        
    def write(self, s, end='\n'):
        # append line to self.outStr
        self.outStr += s + end
        
    def writeFile(self, path, fname):
        # write self.outStr to file
        with open(os.path.join(path, fname), 'w') as fileobj:
            fileobj.write(self.outStr)
            
    def writeHeader(self, path):
        """ Write heading and OnsetDetector parameters """
        
        # print heading, OnsetDetector parameters
        heading = 'Check onsetdetector results'
        self.write(heading+'\n'+'='*len(heading)+'\n')
        
        with open(os.path.join(path, 'ondet_params.txt')) as fileobj:
             header = fileobj.read()
             
        header += 'Onset tolerance: {:.3f}ms\n'.format(self.tolerance)
        
        self.write(header, '\n\n')
         
        
    def check(self, condition=None, return_type=list, write=False, outpath=None, 
              return_str=False, fname_extra=''):
        """ Analyse the detected onsets and write results to file, if requested 
        
            Parameters
            ----------
            condition : list
                Only rows in found_onsets.csv that meet the given condition 
                will analysed. If None, all rows will be analysed.
                Otherwise, condition sould be given as a list of column name,
                operator, condition. E.g. ['Dir1', '==', 'Strings']
            
            return_type : type
                Container type for returning stats, for example list, tuple,
                dict. Default is list.
            
            write : bool
                If True, write stats to a file. Default is False.
                
            outpath : str
                If writing stats to file
                
            return_str : bool
                If True, also return a nicely formatted string of results, 
                as found at end of analysis file
            
            fname_extra : str
                If conditions are supplied, condition[2] will be appended to
                'onset_analysis'. If you want something to go before this,
                supply it here.
        
            Returns
            -------
            Stats in given container type. 
            If 'return_type' is ordered, results will be in the following order:
            Precision, Recall, F-measure, Precision (spill), F-measure (spill)
            
            Also returns nicely formatted string of results as found at end
            of analysis file, if requested
        """
        
        if condition == 'roll':
            fname_append = '_Percussion_roll'
            for idx, row in self.found.iterrows():
                if row['Dir1'] == 'Percussion' and 'roll' in row['File']:
                        self.checkFile(row)
                        
        elif condition == 'no_roll':
            fname_append = '_Percussion_no_roll'
            for idx, row in self.found.iterrows():
                if row['Dir1'] == 'Percussion' and 'roll' not in row['File']:
                        self.checkFile(row)
        
        else:
            # for every file the OnsetDetector analysed
            for idx, row in self.found.iterrows():
                if condition is not None:
                    if fname_extra:
                        fname_extra_info = fname_extra + '_'
                    else:
                        fname_extra_info = ''
                    # make string for onset_analysis file name, removing any
                    # leading or trailing .
                    fname_append = '_{}{}'.format(fname_extra_info, 
                                                  condition[2].strip('.'))
                    label, *rest = condition
                    cond = [row[label]] + rest
                    if self.evaluate_condition(cond):
                        self.checkFile(row)
#                    label, *comp = condition
#                    if eval('"{}"{}"{}"'.format(row[label], *comp)):
#                        self.checkFile(row)
                else:
                    fname_append = ''
                    self.checkFile(row)
        
            
        results = self.getStats()
        stats_str = self.formatStats(results)
        self.write(stats_str)
        
        if write:
            fname = 'onset_analysis{}'.format(fname_append) # 'onset_analysis_Percussion_no_roll'  # 
            ext = '.txt'
#            if condition is not None:
#                fname += '_{}'.format(condition[-1])
            fname += ext
            self.writeFile(outpath, fname)
            
        keys = ['Precision', 'Recall', 'F-measure', 'Precision (spill)', 
                'F-measure (spill)']
            
        try:
            results = return_type(results)
        except TypeError:
            try:
                results = return_type(zip(keys, results))
            except TypeError:
                raise TypeError("Cannot cast 'results' to type '{}'"
                                .format(return_type.__name__))
        
        if return_str:
            return results, stats_str
        else:
            return results
        
        
    @staticmethod
    def evaluate_condition(condition):
        # evaluate whether the items given in the 'condition' list are true
        # 'condition' should be at least 3 items long
        # e.g. condition = ['o', 'in', 'hello']
        # or condition = ['hello', '.startswith(', 'h', ')']
        try:
            lhs, operator, rhs, extra = condition
        except ValueError:
            lhs, operator, rhs = condition
            extra = ''
        return eval('"{}" {} "{}" {}'.format(lhs, operator, rhs, extra))
        
    
    @staticmethod
    def _makeOnsetsArray(s):
        # transform string from DataFrame 'Onsets' item to NumPy array
        if s != 'None':
            return np.array([float(o) for o in s.split(',')])
        else:
            return np.zeros(0)
    
    
    @staticmethod
    def _seriesToValue(s, label):
        # .loc returns a Pandas series, so we have to get the index, then
        # access the value. Fucking really.
        v = s[label]
        idx = v.index
        value = v[idx.item()] # there must be a better way than this
        return value
    
    
    @staticmethod
    def _filterTimes(lst, precision):
        # return sorted list with no duplicates, when printed with the given
        # precision, e.g. 7.3f
        fmt = '{{:{}}}'.format(precision)
        lst = [fmt.format(item) for item in lst]
        lst = set(lst)
        lst = sorted([float(item) for item in lst])
        return lst
        
    
    def checkFile(self, row):
        """ Check results for given frequency 
        
            This method also counts the manual onsets.
        
            Parameters
            ----------
            row : pandas DataFrame row
                Row from found_onsets.csv
        """
        
        precision = '7.3f'
        fmt = '{{:{}}}'.format(precision)
        
        # found onsets
        cols = ['Dir1', 'Dir2', 'File', 'Fs', 'Onsets']
        dir1, dir2, file, sr, results = [row[c] for c in cols]
        results = self._makeOnsetsArray(results) # samples
        results /= sr # seconds
        # when rounded to 3 decimal places, there may be duplicates, so filter
        # them out
        results = self._filterTimes(results, precision=precision)
        
        # manual onsets
        man_row = self.manual.loc[self.manual['File']==file]
        # can't access directly, as .loc returns a series, so need to use index
        times = self._seriesToValue(man_row, 'Onsets') 
        times = self._makeOnsetsArray(times) # seconds
        # when rounded to 3 decimal places, there may be duplicates, so filter
        # them out
        times = self._filterTimes(times, precision=precision)
        
        # increse 'number of onsets' count
        self.nm += len(times)
            
        # only go on if there are correct or found onsets at this frequency
        # i.e. stop if freq is not correct and there were no false detections
        if not isempty(times) or not isempty(results):
            
            header = os.path.join(dir1, dir2, file)
            self.write(header + '\n' + '-'*len(header))
            
            correct, diff = self.compare(times, results, self.tolerance)
            
            # indices of true positives, false negatives and false positives
            tp = np.where(np.isnan(diff) == 0)[0]
            fn = np.where(np.isnan(diff))[0]
            fp = np.setdiff1d(np.arange(len(results)), correct)
            
            # count true and false positives
            self.tp += len(tp)
            self.fp += len(fp)
        
            # write true/false positive/negative info
            for idx in tp:
                s = fmt.format(times[idx])
                self.write('Onset at {} seconds'.format(s), 
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
                        s = fmt.format(times[i])
                        self.write('{}'.format(s))
        
                if not isempty(fp):
                    self.write('\nFalse positives:')
                    for i in fp:
                        s = fmt.format(results[i])
                        self.write('{}'.format(s), end='')
#                        # check if time is in another band
#                        for k in self.onsets_dict.keys():
#                            c, d = self.compare(self.onsets_dict[k], 
#                                                np.array([results[i]]))
#                            if not isempty(c):
#                                self.write('    (spillover from {} band)'
#                                           .format(k), end='')
#                                self.fp_spill += 1
                        self.write('\n', end='')
        
            self.write('\n', end='')
                
            
    @staticmethod
    def compare(times, results, tolerance):
        """ Compare array of manual onset times with found onsets
        
            Parameters
            ----------
            times : np.array
                array of manual times (seconds)
            results : np.array
                array of found times (seconds)
            tolerance : float
                tolerance (ms)
                
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
                if nearest_to_zero <= tolerance:
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
            
        if d < -self.tol2:
            self.adv_tol[0] += d
            self.adv_tol[1] += 1
            
        elif d > self.tol2:
            self.del_tol[0] += d
            self.del_tol[1] += 1


    def getStats(self):
        """ Calculate stats """
        
        # calculate stats
        self.na = self.tp + self.fp
        try:
            precision = self.tp/self.na
        except ZeroDivisionError:
            precision = 0
        try:
            recall = self.tp/self.nm
        except ZeroDivisionError:
            recall = 0
        try:
            fmeasure = 2 * precision * recall / (precision + recall)
        except ZeroDivisionError:
            fmeasure = 0
          
        # precision not including spillover
        try:
            precision_e = self.tp / (self.na-self.fp_spill) 
        except ZeroDivisionError:
            precision_e = 0
        try:
            fmeasure_e = (2 * precision_e * recall) / (precision_e + recall)
        except ZeroDivisionError:
            fmeasure_e = 0
            
        return precision, recall, fmeasure, precision_e, fmeasure_e
    
    
    def formatStats(self, stats):
        """ Put stats in nicely formatted string """
        
        precision, recall, fmeasure, precision_e, fmeasure_e = stats
        
        out = ''
        
        diff_sum = self.mn_adv[0] + self.mn_del[0]
        diff_num = self.mn_adv[1] + self.mn_del[1] + self.zero_diff
        try:
            mn_diff = diff_sum / diff_num
        except ZeroDivisionError:
            mn_diff = 0
        
        out += '\nStats\n=====\n'
        out += 'Total number of onsets:     {}\n'.format(self.nm)
        out += 'Total number of detections: {}\n'.format(self.na)
        out += 'Total true positives:       {}\n'.format(self.tp)
        out += 'Total false positives:      {}\n'.format(self.fp)
        out += 'Total erroneous detections: {}\n'.format(self.fp-self.fp_spill)
        
        out += '\n'
        
        means = []
        
        for mn in [self.mn_adv, self.mn_del]:
            try:
                m = mn[0]/mn[1]
            except ZeroDivisionError:
                m = 0
            means.append(m)
        
        out += 'Largest advance: {:3d}ms\n'.format(self.errors[0])
        out += 'Mean advance:    {:7.3f}ms\n'.format(means[0])
        out += 'Largest delay:   {:3d}ms\n'.format(self.errors[1])
        out += 'Mean delay:      {:7.3f}ms\n'.format(means[1])
        out += 'Mean difference: {:7.3f}ms\n'.format(mn_diff)
        out += 'Number of advances <-{:.2f}ms: {}\n'.format(self.tol2, 
                   self.adv_tol[1])
        out += 'Number of delays   > {:.2f}ms: {}\n'.format(self.tol2, 
                   self.del_tol[1])
        
        out += '\n'
        
        out += 'Precision:             {:.6g}%\n'.format(100*precision)
        out += 'Recall:                {:.6g}%\n'.format(100*recall)
        out += 'F-measure:             {:.6g}%\n'.format(100*fmeasure)
        
        out += 'Precision (tot. err.): {:.6g}%\n'.format(100*precision_e)
        out += 'F-measure (tot. err.): {:.6g}%\n'.format(100*fmeasure_e)
        
        return out

                
if __name__ == '__main__':
    
    user = os.path.expanduser('~')
    audio_path = os.path.join(user, 'Iowa', 'all')
    onsets_path = os.path.join('..', 'Data')
    
    resultsdir = os.path.join('results')
    
    tolerance = 50
    
    # get directory to read from
    outdir = '5_Apr_1' 
    print('Checking results from {}'.format(outdir))
    outdir = os.path.join(resultsdir, outdir)
    
    # subdir for in-depth analysis
    outpath = os.path.join(outdir, 'result_analysis')
    
    # get all onset analysis
    c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
    c.check(write=True, outpath=outdir)
    
    # get onset analysis by instrument type
    dirs = ['Brass', 'Percussion', 'Strings', 'Woodwind', 'Piano_Guitar']
    for dr in dirs:
        print('  Checking {} files...'.format(dr))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['Dir1', '==', dr], write=True, outpath=outdir)
        
#    # get piano and guitar onset analysis
#    dirs = ['Piano', 'Guitar']
#    for dr in dirs:
#        print('  Checking {} files...'.format(dr))
#        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
#        c.check(condition=['Dir2', '==', dr], write=True, outpath=outdir)
#        
    # analyse percursion onsets with and without rolls
    conditions = ['roll', 'no_roll']
    for condition in conditions:
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=condition, write=True, outpath=outdir)
        
    # anlayse by dir2, but group all string samples that differ only by string
    # (this will do piano and guitar)
    # also group by vib, novib, arco and pizz
    file = os.path.join(outdir, 'found_onsets.csv')
    
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    # get Dir2 column
    df = pd.read_csv(file, sep='\t')
    # get set of dirs
    dirs = list(set(df['Dir2']))
    # group strings by these categories
    strings = ['Violin.pizz.ff', 'Violin.arco.ff', 'Viola.pizz.ff', 
               'Viola.arco.ff', 'Cello.pizz.ff', 'Cello.arco.ff', 
               'Bass.pizz.ff', 'Bass.arco.ff']
    # remove items that contain each string from dirs
    dirs = [item for item in dirs if not item.startswith(tuple(strings))]
    # put strings in list       
    dirs += strings
    # other categories to break down analysis by
    other_categories = ['.vib.', '.novib', '.arco.', '.pizz.']
    dirs += other_categories
    dirs.sort()
    
    for dr in dirs:
        print('  Checking {} files...'.format(dr))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['Dir2', '.__contains__(', dr, ')'], write=True, 
                           outpath=outpath)
        
    # analyse by octave number
    octaves = ['{:.0f}'.format(item) for item in np.arange(9)]
    for octave in octaves:
        print('  Checking files in ocatve {}...'.format(octave))
        c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
        c.check(condition=['File', '.__contains__(', octave, ')'], write=True, 
                           outpath=outpath, fname_extra='octave')
        
        
#    c = CheckOnsets(onsets_path, outdir, tolerance=tolerance)
#    c.check(condition=None, write=True, outpath=outdir)
    