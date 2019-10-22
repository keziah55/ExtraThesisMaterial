#!/usr/bin/env python3

import numpy as np
from detectorbank import DetectorCache, Producer

class OnsetDetector:
    
    def __init__(self, db):
        """ Parameters
            ----------
            db : DetectorBank
                DetectorBank for band           
        """
        
        self.chans = db.getChans()
        self.sr = db.getSR()
        self.p = Producer(db)
        self.seg_len = int(0.03 * self.sr)
        num_segs = 100
        self.cache = DetectorCache(self.p, num_segs, self.seg_len)
        self.n = 0
        self.end = self.cache.end()
        
        if db.tell() > 0:
            db.seek(0)           
            
    def analyse(self, threshold):
        
        threshold = np.log(threshold)
        
        count = 0
        last = 0
        seg_count = 0
        
        onsets = []
        
        stopVal = 0
        startVal = 0
        
        while self.p.more():
            
            current = self.getSegAvg()
            
            if current >= last:
                count += 1
                stopVal = current
                
            else:
                if count >= 3 and last >= threshold and stopVal/startVal<= 0.75:
                    start_seg = seg_count-count-1
                    stop_seg = seg_count-1
                    start = int(start_seg*self.seg_len)
                    stop = int(stop_seg*self.seg_len)
                    
                    verified, onset = self.findExactTime(start, stop)
                    
                    if verified:
                        onsets.append(onset)
                        
                count = 0
                startVal = current
                
            last = current
            seg_count += 1
            
        return onsets
            
            
    def getSegAvg(self):
        
        seg_avg = 0
        
        for m in range(self.seg_len):
            
            if self.n >= self.end:
                raise IndexError
            else:
                for k in range(self.chans):
                    seg_avg += self.cache[k,self.n] #np.log(self.cache[k,self.n])
                    
            self.n += 1
            
        seg_avg /= (self.chans*self.seg_len)
        
        return seg_avg
    
    
    def findExactTime(self, incStart, incStop):
        
        stop_time = int(self.sr * 0.1)
        
        if incStart - stop_time < 0:
            stop = 0
        else:
            stop = incStart - stop_time
            
        idx = incStop
        
        current = 0
        for k in range(self.chans):
            current += np.log(self.cache[k,idx])
        current /= self.chans
        
        N = int(self.sr * 0.075)
        if N > idx:
            N = idx
        
        mean = 0
        for i in range(idx-N, idx):
            for k in range(self.chans):
                mean += np.log(self.cache[k,i])
        mean /= (self.chans*N)
        
        while idx > stop+N:
            
            if mean < current:
                
                idx -= 1
                
                current = 0
                for k in range(self.chans):
                    current += np.log(self.cache[k,idx])
                current /= self.chans
                
                mean -= (current / N)
                
                older = 0
                for k in range(self.chans):
                    older += np.log(self.cache[k,idx-N])
            
                mean += (older / (self.chans*N))
                
            else:
                
                # find local min
                mn = current
                onset = idx
                
                M = int(self.sr*10e-3)
                
                for i in range(idx, idx-M, -1):
                    avg = 0
                    for k in range(self.chans):
                        avg += np.log(self.cache[k,i])
                    avg /= self.chans
                    
                    if avg < mn:
                        mn = avg
                        onset = i
                        
                # if local min and current are v similar, use current time as
                # onset
                if current/mn >= 0.95:
                    onset = idx

                return True, onset
            
        return False, 0
    
