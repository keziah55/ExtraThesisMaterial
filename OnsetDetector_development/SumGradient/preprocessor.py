#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" NoteDetector Preprocessor """

import abc
import numpy as np

class Preprocessor:
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, cache, seg_len, channels):
        """ Make a Preprocessor
        
            Parameters
            ----------
            cache
                DetectorCache
            seg_len : int
                DetectorCache segment length
            channels : array-like
                list of channel indices for this band in cache
        """
        self.r = cache
        self.seg_len = seg_len
        self.channels = channels
        
        self.current = 0
    
    @abc.abstractmethod
    def getNext(self, *args):
        pass


class PreprocessorOD(Preprocessor):
    
    def __init__(self, cache, seg_len, channels, grad_N):
        """ Make a Preprocessor
        
            Parameters
            ----------
            cache
                DetectorCache
            seg_len : int
                DetectorCache segment length
            channels : array-like
                list of channel indices for this band in cache
            grad_N : int
                number of samples over which to calculate gradient
        """
        
        super().__init__(cache, seg_len, channels)

        self.grad_N = grad_N
        
    
    def getNext(self):
        
#        result = np.zeros((self.seg_len, 2))
        result = np.zeros(self.seg_len)
        
        for n in range(self.seg_len):
            self.current += n
            result[n] = self.getGradient(self.current)
            
        return result
        
        
    def getGradient(self, n):
        """ Return sum of gradients of all detectors in cache at sample `n`. 
        """
        
#        gradient = np.array([0, 0])
        gradient = 0
        
        for k in self.channels:
            
            r0 = self.r[k,n]
            
            # if we don't have N samples yet, r1 is zero
            if n-self.grad_N < 0:
                r1 = 0
            else:
                r1 = self.r[k,n-self.grad_N]
                
            g = (r0 - r1) / self.grad_N
            
#            if g >= 0:
#                gradient[0] += g
#            else:
#                gradient[1] += g
            
            gradient += g
            
        return gradient * 10e4
    
    
class PreprocessorPT(Preprocessor):
    
    def getNext(self):
        
        result = np.zeros((len(self.channels), self.seg_len))
        
        for n in range(self.seg_len):
            
            self.current += 1
            
            for idx, k in enumerate(self.channels):
                
                d = self.differentiate(k, self.current) * 10e8
                z = self.r[k, self.current] * 100
                
                print('channel: {:2d}, sample: {:5d}, |z|: {:.6f}, '
                      'dz/dt: {:9.6f}, weight: {:9.6f}'
                      .format(k, self.current, z, d, z*d))
                
                result[idx,n] = d * z
                
        return result
        
    
    def differentiate(self, k, n):
        """ Return the derivative at sample n in channel k.
        
            Parameters
            ----------
            k : int
                channel
            n : int
                current sample
                
            Notes
            -----
            The central difference approximation is used to calculate the 
            derivative, so the oldest value that will be used is n-2. 
            If this value is not available, it will be assumed to be zero.
            
            The value could be unavailable either because it is before the 
            beginning of the audio (n-2 < 0) or because it is in an 
            expired segment. In both cases, the value will be taken to be 0.
        """
        
        current = self.r[k,n]
        
        try:
            previous = self.r[k,n-2]
        except IndexError:
            # NB will also get IndexError if k is negative
            # should probably check this somewhere, just to be thorough
            previous = 0
        
        result = 2 * (current - previous) / self.r.getSR()
            
        return result
        
    