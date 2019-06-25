#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find the minimum detector bandwidth at various sample rates and damping
factors by making a DetectorBank of closely-spaced detectors and finding the
points at which the maximum response in 3dB less than that at the centre
frequency.
"""

from detector_bandwidth import EmpiricalBandwidth
import os
import re


def getEmpiricalBandwidth(path):
    
    # get dir to save everything to
    base = 'Test'
    ndir = getNextDir(path, base)
    savepath = os.path.join(path, ndir)
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    
    # write summary file here, not in object, as I'm creating a new object for
    # each sample rate
    fileobj = open(os.path.join(savepath, 'bandwidth_summary.txt'), 'w')
    
    f0 = 440
    sample_rates = [44100, 48000]
    damping = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005]
    numDetectors = 501
    
    log = ('Calculating empirical bandwidth values by finding peak amplitude '
           'of \n{} detectors over a range of 1.2 to 6Hz, (depending on '
           'damping factor).\n\n'.format(numDetectors))
    log += 'DetectorBank uses amplitude normalisation\n\n'
    fileobj.write(log)
    
    
    for sr in sample_rates:
        emp = EmpiricalBandwidth(f0, sr)
        
        for d in damping:
            print('f0: {:.0f}Hz, sr: {:.0f}Hz, d: {:.0e}'.format(f0, sr, d))
            
            savename = 'freqz_{:.0f}_{:.0f}_{:.0e}.pdf'.format(f0, sr, d)
            
            # get bandwidth
            f3dB = emp.get_bandwidth(d, numDetectors)
            
            # save frequency response plot
            emp.plot_frequency_response(True, os.path.join(savepath, savename))
            
            fd = [f-f0 for f in f3dB]
            abs_fd = [abs(f) for f in fd]
            
            # write details to file
            log = 'f0: {:.0f}Hz, sr: {:.0f}Hz, d: {:.0e}\n'.format(f0, sr, d)
            log += '-3dB points at {:.3f} Hz and {:.3f} Hz\n'.format(*f3dB)
            log += 'Frequency difference: {:.3f} Hz and {:.3f} Hz\n'.format(
                    *fd)
            log += 'Difference between -3dB points: {:.3f}Hz\n'.format(
                    abs(abs_fd[0]-abs_fd[1]))
            log += 'Empirical bandwidth: {:.3f} Hz\n'.format(f3dB[1]-f3dB[0])
            log += ('Minimum bandwidth covering both -3dB points: {:.3f}Hz\n\n'
                    .format(2*max(abs_fd)))
            fileobj.write(log)
    
    fileobj.close()
    
    
def getNextDir(path, base='Test'):
    """ Get next directory in 'path', where the directories are of the
        form baseX, e.g. Test1.
        
        The next suitable numbered directory is returned.
    """
    
    # get all (sub)directories in path
    ls = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]
    
    regex = re.compile(base+'(\d+)')
    
    nums = []
    for d in ls:
        try:
            m = regex.match(d)
            n = m.group(1)
            nums.append(n)
        except:
            pass

    nums = map(int, nums)
    num = max(nums) + 1
    nextdir = base + str(num)
    
    return nextdir
    

def testGAresults(path):
    
    f0 = 440
    
    ## bandwidths found by GA
    params = {44100: [(1e-4,1.12), (2e-4,1.75), (3e-4,2.55), (4e-4,3.38), 
                      (5e-4,4.22)],
              48000: [(1e-4,1.16), (2e-4,1.88), (3e-4,2.76), (4e-4,3.67), 
                      (5e-4,4.58)]}
              
    ## bandwidths found by EmpiricalBandwidth 
#    params = {44100: [(1e-4,0.842), (2e-4,1.68), (3e-4,2.52), (4e-4,3.36), 
#                      (5e-4,4.2)],
#              48000: [(1e-4,0.914), (2e-4,1.824), (3e-4,2.744), (4e-4,3.65), 
#                      (5e-4,4.56)]}
              
    # write summary file here, not in object, as I'm creating a new object for
    # each sample rate
    fileobj = open(os.path.join(path, 'ga_bandwidth_test.txt'), 'w')
    log = ('Calculating peak amplitude (in dB) for bandwidth values found by\n'
           'genetic algorithms. \n\n')
    fileobj.write(log)
    
    for sr in params.keys():
        emp = EmpiricalBandwidth(f0, sr)
        
        d_bw = params[sr]
        
        for d, bw in d_bw:
            amp = emp.get_amplitude(bw, d)
            
            log = ('f0: {:.0f}Hz, sr: {:.0f}Hz, d: {:.0e}, bw: {:.2f}\n'
                   .format(f0, sr, d, bw))
            log += ('Response amplitudes are {:.3f}dB and {:.3f}dB\n\n'
                    .format(*amp))
            
            fileobj.write(log)
    
    fileobj.close()
            
        
if __name__ == '__main__':      
    
    pwd = os.getcwd()
    path = os.path.join(pwd, '..', 'Visualisation', 'freq_response') 
    
    getEmpiricalBandwidth(path)
#    testGAresults(path)
    