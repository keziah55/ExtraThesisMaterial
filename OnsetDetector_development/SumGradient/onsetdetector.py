#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OnsetDetector implemented with sum gradient method 
"""

import numpy as np
import os
import time

class OnsetDetector:
    
    def __init__(self, preprocessor, channels, sr, path=None):
        """ Create a NoteDetector for a critical band.
        
            Parameters
            ----------
            preprocessor
                Preprcoessor to provide data
            channels : array-like
                list of indices to channels in cache corresponding to current 
                band
            sr : int
                sample rate
                
            path : 
                for debugging
        """
        
        self.channels = channels
        
        self.sr = sr
        
        # preprocessor get gradient over 30ms
        self.preproc = preprocessor
        
        self.num100ms = int(0.1 * sr)
        self.num30ms = int(30e-3 * sr)
        
        # keep cache of 100ms worth of values
        self.prev_pos = Buffer(self.num100ms)
        self.prev_neg = Buffer(self.num100ms)
        self.prev_sum = Buffer(self.num100ms)
        
        self.state = 'indeterminate'
        
        self.onsets = []
        self.offsets = []
        
        ## LOG PARAMETERS
        # these are only selfed here so they can be logged and used later
        self.func = np.greater_equal
        self.num = 1
        self.size = self.num30ms
        self.prop = 0.5
        self.threshold_mult = 7.5
        
        if path:
            # write separate file of parameters
            with open(os.path.join(path, 'ondet_params.txt'), 'w') as fileobj:
                
                fileobj.write(time.ctime(time.time()) + '\n\n')
                
                fileobj.write('Comparison function: np.{}\n'
                              .format(self.func.__name__))
                fileobj.write('Comparison size: {} samples\n'.format(self.size))
                fileobj.write('Comparison proportion: {}%\n\n'
                              .format(int(100*self.num)))
                fileobj.write('Threshold: len(self.channels) * {}\n'
                              .format(self.threshold_mult))
                fileobj.write('Proportion which must exceed threshold: {}%\n'
                              .format(int(self.prop * 100)))
        
    
    def do_stuff(self, n):
        
        g = self.preproc.getGradient(n)
#        self.prev_pos.insert(g[0])
#        self.prev_neg.insert(g[1])
        self.prev_sum.insert(g)#[0]+g[1])
        
        if n > self.num30ms:
            self._lazy(n)
        
        return g
    
    def get_onsets(self):
        return self.onsets
    
    def get_offsets(self):
        return self.offsets
    
    def log(self, event, time):
        
        message = 'sample {:5d}, {:.3f} seconds'.format(time, time/self.sr)
        
        if event == 'on':
            print('Onset:  ' + message)
        elif event == 'off':
            print('Offset: ' + message)
        else:
            raise ValueError('log() event arg takes "on" or "off"')
        
        
    def _lazy(self, n):
        
        func = self.func #np.greater_equal
        num = self.num #1
        
        size = self.size #self.num30ms
        
        #### instead of self.prev.pos, need to check whether prev_pos > prev_neg
        #### for > num proportion of values
        #### write function which takes sum buffer, comparison function and 
        #### function args and returns function(sum_buf, *args)
        
        # rough analysis of the contents of self.prev to find potential onsets
        if func(self.prev_sum.pos(size), num):
            # if this is a switch from 'off' (or 'indeterminate') to 'on'
            if self.state != 'on':
                s = n-size
                if self._industrious(size, n):
                    self.onsets.append(s)
                    self.state = 'on'
       
        elif func(self.prev_sum.neg(size), num):
            # if this is a switch from 'on' (or 'indeterminate') to 'off'
            if self.state != 'off':
                s = n-size
#                self.log('off', s)    # print message
                self.offsets.append(s)
                self.state = 'off'
                
        else:
            self.state = 'indeterminate'
    
    
    def _industrious(self, size, n):
        # size : number of previous samples to look at
        
        print('Checking from sample {} ({:.2f} seconds)...'
              .format(n, n/self.sr))
        
        threshold = len(self.channels) * self.threshold_mult #* 10
        
        prop_thr = self.prev_sum.proportion(int(size/4), np.greater_equal, 
                                            threshold)
        
#        prop_dec = self.prev_neg.proportion(int(size/4), np.less_equal, 0)
        
#        print('{:.2f}% of previous values are decreasing'.format(100*prop_dec))
        print('{:.2f}% of previous values exceed the threshold of {}'
              .format(100*prop_thr, threshold))
        print('Current gradient: {:.2f}'.format(self.prev_sum[0]))
        
        if prop_thr >= self.prop:# and prop_dec >= 1-self.prop: #0.5:
            print('>>> Onset verified\n')
            return True
        
        else:
            print('>>> Onset rejected\n')
            return False
        
        
class Buffer:
    
    def __init__(self, size):
        """ Make a FIFO buffer """
        
        self.buf = np.zeros(size)
        self.size = size
        
    def __getitem__(self, idx):
        return self.buf[idx]
    
    def __len__(self):
        return self.buf.shape[0]
    
    def __repr__(self):
        return 'Buffer(' + str(self.buf[:]) + ')'
    
    @property
    def shape(self):
        try:
            len(self.size)
            return self.size
        except TypeError:
            return (self.size,)
        
    def insert(self, value):
        
        self.buf = np.roll(self.buf, 1)
        self.buf[0] = value
        
        
    def proportion(self, n, func, *args, **kwargs):
        """ Return proportion of values in Buffer for which `func` is True.
        
            Parameters
            ----------
            n : int or None
                Number of previous values to check
                If None, whole Buffer will be used
            func : function
                Comparison function
            args, kwargs
                Any additional argumnets to be passed to the function
        """
        
        if n is None:
            n = self.size
            
        result = func(self.buf[:n], *args, **kwargs)
        
        values, counts = np.unique(result, return_counts=True)
        
        try:
            prop = counts[np.where(values==True)[0][0]] / n
            return prop
        except IndexError:
            return 0
        
        
    def pos(self, n=None):
        """ Return True if last `n` samples were all positive """
        
        if n is None:
            n = self.size
            
        return self.proportion(n, np.greater_equal, 1)

        
    def neg(self, n=None):
        """ Return True if last `n` samples were all positive """
        
        if n is None:
            n = self.size
            
        return self.proportion(n, np.less_equal, -1)
    
    