#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot the initial response of the DetectorBank under a range of circumstances.
"""

import numpy as np
import itertools as it
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns


def where(lst, condition):
    """ Return indices where items in 'lst' meet 'condition'
    
        Parameters
        ----------
        lst : lst
            List to be analysed
        condition : function
            Function that returns either True or False when called with an
            item from the list
            
        Returns
        -------
        List of indices where condition(lst[i])==True
    """
    ind = []
    for i, item in enumerate(lst):
        if condition(item):
            ind.append(i)
    return ind


def make_audio(f0, sr=48000, duration=1):
    
    for n in range(len(f0)):
    
        t = np.linspace(0, 2*np.pi*f0[n]*duration, int(sr*duration))
        audio = np.sin(t)
        
    audio = np.append(audio, np.zeros(2*sr))
    
    return audio


def get_response(sr, audio, f, bw=0, damping=0.0001):
    """ Get DetectorBank output
    
        Parameters
        ----------
        sr : int
            Sample rate
        audio : array
            Input samples
        f : one-element array
            Frequency to test, in an array
        bw : float
            Bandwidth. Default is minimum bandwidth
        damping : float
            Damping factor. Default is 0.0001
    """
    
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    gain = 1
    
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
     
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)    
    r = np.zeros(z.shape) 
    
    det = DetectorBank(sr, audio, 4, det_char, method|f_norm|a_norm, damping, 
                       gain)
    
    det.getZ(z) 
    det.absZ(r, z)
    
    return r[0]
    

def plot(t, responses, labels):
    
    sns.set_style('whitegrid')
    
    t = t*1000
    l = iter(labels)
    
    c = ['red', 'orange',  'darkmagenta', 'lawngreen', 'blue']
    damping = np.linspace(1e-4, 5e-4, num=5)
    d_str = ['{:.0e}'.format(d) for d in damping]
    colours = dict(zip(d_str, c))
    
    t0 = 0
    t1 = int(48000 * 0.4)
    
    for r in responses:
        label = next(l)
        k = label.split(',')[-1]
        k = k.strip()
        colour = colours[k]
        plt.plot(t[t0:t1], r[t0:t1], color=colour, label=label) #color=next(c), 
        
    plt.grid(True)
    plt.xlabel('Time (ms)')
    plt.ylabel('|z|', rotation='horizontal')
    
    plt.show()
    plt.close()
    
    
def getDiff(responses, labels):
    """ Split responses by input frequency and damping factor. 
        Print mean difference in input when bandwidth is the only difference.
    """
    
    # format damping factors as strings
    damping = np.linspace(1e-4, 5e-4, num=5)
    d_str = ['{:.0e}'.format(d) for d in damping]
    
    out = ''
    
    # check that responses are exactly the same when the only difference is bw
    for key in ['100Hz', '1000Hz']:
    
        out += '\n' + key + '\n'
        
        # for each damping factor, get the difference between responses
        for dmp in d_str:
            
            out += '  ' + dmp + '\n'
            
            # get indices from 'labels' list by input frequency
            # 'labels' indices are the same for 'responses'
            f = (lambda s: s.split(',')[0].strip() == key and 
                           s.split(',')[-1].strip() == dmp)
            ind = where(labels, f)
            
            r = [responses[i] for i in ind]
            
            for n in range(1, len(r)):
                diff = r[n] - r[n-1]
                mean = np.mean(diff)
                out += '    Mean difference is: {}\n'.format(mean)
                
    return out


def testFreqBwDamping(f, sr):

    responses = []
    labels = []
    
    for freq in f:
        
        f0 = np.array([freq])
    
        # make input
        # 'dur' is tone duration
        # 2 seconds of silence will automatically be appended
        dur = 3
        audio = make_audio(f0, sr, dur)
        
        def_d = 0.0001
        
        # test these values
        bandwidths = np.array([5,10,50])
        damping = np.linspace(1e-4, 5e-4, num=5) 
        
        # get response with default values
        r = get_response(sr, audio, f0)
        responses.append(r)
        labels.append('{}Hz, min., {:.0e}'.format(f0[0], def_d))
        
        for bw in bandwidths:
            for d in damping:
                r = get_response(sr, audio, f0, bw=bw, damping=d)
                responses.append(r)
                labels.append('{}Hz, {}Hz, {:.0e}'.format(f0[0], bw, d))
        
    t = np.linspace(0, len(audio)/sr, len(audio))
    
    plot(t, responses, labels)
    
    out = getDiff(responses, labels)
    print(out)
#    with open('results/response_differences.txt', 'w') as fileobj:
#        funcname = sys._getframe().f_code.co_name
#        fileobj.write('Generated by {}, {}()\n\n'.format(__file__, funcname))
#        fileobj.write('Mean differences between responses for detectors '
#                      'with different bandwidths.\n')
#        fileobj.write('See also: Visualisation/compare_initial_responses.pdf\n')
#        fileobj.write('Basically, this shows that the bandwidth (i.e. first '
#                      'Lyapunov coefficient)\nhas no effect on response shape.\n')
##        fileobj.write('\n\n')
#        fileobj.write(out)


def testFreqDiff(f, sr):
    ### Note used prop_freq.py to generate this instead

    responses = []
    labels = []
    
    # make input
    # 'dur' is tone duration
    # 2 seconds of silence will automatically be appended
    dur = 3
    audio = make_audio([f[0]], sr, dur)
    
    damping = np.linspace(1e-4, 5e-4, num=5) 
    
    for f0 in f:
    
        for d in damping:
            r = get_response(sr, audio, [f0], damping=d)
            responses.append(r)
            labels.append('{}Hz, {:.0e}'.format(f0-f[0], d))
        
    t = np.linspace(0, len(audio)/sr, len(audio))
    
    plot(t, responses, labels)
    
    out = getDiff(responses, labels)
    print(out)
#    with open('results/response_differences.txt', 'w') as fileobj:
#        funcname = sys._getframe().f_code.co_name
#        fileobj.write('Generated by {}, {}()\n\n'.format(__file__, funcname))
#        fileobj.write('Mean differences between responses for detectors '
#                      'with different bandwidths.\n')
#        fileobj.write('See also: Visualisation/compare_initial_responses.pdf\n')
#        fileobj.write('Basically, this shows that the bandwidth (i.e. first '
#                      'Lyapunov coefficient)\nhas no effect on response shape.\n')
##        fileobj.write('\n\n')
#        fileobj.write(out)




def getSrDampingDiff(freq, sample_rates):
    
    sns.set_style('whitegrid')
    
#    c = ['red', 'orange',  'darkmagenta', 'blue']
#    all_sr = np.array([44100, 48000, 96000, 192000])
#    colours = dict(zip(all_sr, c))
#    
    c = ['darkgreen', 'red', 'orange',  'darkmagenta', 'lawngreen', 'blue']
    damping = np.linspace(0, 5e-4, num=6)
    d_str = ['{:.0e}'.format(d) for d in damping[1:]]
    d_str.insert(0, 'Undamped')
    colours = dict(zip(d_str, c))
#    damping = [0, 0.0005]
    
    out = ''
    
    for sr in sample_rates:
        
        for f0 in freq:
            
            f = np.array([f0])
        
            # make input
            # 'dur' is tone duration
            # 2 seconds of silence will automatically be appended
            dur = 3
            audio = make_audio(f, sr, dur)
            
            responses = []
            
            for i, d in enumerate(damping):
                
                r = get_response(sr, audio, f, damping=d)
                responses.append(r)
                
                t = np.linspace(0, len(audio)/sr, len(audio))
                t *= 1000
                t0 = 0
                t1 = int(sr * 0.2)
                
#                label = '{:g} kHz'.format(sr/1000)
#                plt.plot(t[t0:t1], r[t0:t1], color=colours[sr], label=label)
#                label = d_str[i]
#                plt.plot(t[t0:t1], r[t0:t1], color=colours[label], label=label)
                
            for n in range(1, len(responses)):
                    
                diff = (responses[0] - responses[n]) / responses[0]
                diff *= 100
                
                idx = np.where(diff >= 10)[0][0]
                tenpcnt = t[idx]
                
                out += 'Damping: {:.0e}\n'.format(damping[n])
                out += 'Difference exceeds 10% after {:.4g} ms\n'.format(tenpcnt)
                
                label = '{:.0e}'.format(damping[n])
                plt.plot(t[t0:t1], diff[t0:t1], color=colours[label], label=label)
#                         label='{:g} kHz'.format(sr/1000))
#                
                
#        with open('results/response_differences_divergence.txt', 'w') as fileobj:
#            funcname = sys._getframe().f_code.co_name
#            fileobj.write('Generated by {}, {}()\n\n'.format(__file__, funcname))
#            fileobj.write('Analysis of initial_response_diff_from_undamped.pdf\n')
#            fileobj.write('Sample rate: {:g}kHz\n'.format(sr/1000))
#            fileobj.write('Times at which the difference between damped and '
#                          'undamped response exceeds 10%:\n\n')
#            fileobj.write(out)
        print(out)
        
        plt.grid(True)
#        plt.title('{:g} kHz'.format(sr/1000))
        plt.xlabel('Time (ms)')
        plt.ylabel('Difference (%)')
#        plt.ylabel('|z|', rotation='horizontal')
        plt.legend(title='Damping factor')
    
        plt.show()
        plt.close()


def testSR(f, sample_rates):
    
    sns.set_style('whitegrid')
    
    c = ['darkgreen', 'red', 'orange',  'darkmagenta', 'lawngreen', 'blue']
    damping = np.linspace(0, 5e-4, num=6)
    d_str = ['{:.0e}'.format(d) for d in damping[1:]]
    d_str.insert(0, 'Undamped')
    d_iter = it.cycle(d_str)
    colours = dict(zip(d_str, c))
    
    for sr in sample_rates:
        
        # make input
        # 'dur' is tone duration
        # 2 seconds of silence will automatically be appended
        dur = 3
        audio = make_audio(f, sr, dur)
        
        responses = []
        
        for d in damping:
            
            r = get_response(sr, audio, f, damping=d)
            responses.append(r)
            
            t = np.linspace(0, len(audio)/sr, len(audio))
            t *= 1000
            t0 = 0
            t1 = int(sr * 0.2)
            label = next(d_iter)
            
            plt.plot(t[t0:t1], r[t0:t1], color=colours[label], label=label)
            
#        plt.ylim(-0.03, 0.59)
        
        plt.grid(True)
        plt.xlabel('Time (ms)')
        plt.ylabel('|z|', rotation='horizontal')
        plt.legend(loc='upper left', title='Damping factor')
            
        ax = plt.gca()
        ax.yaxis.labelpad = 10
        
        plt.show()
        plt.close()
        
        
def testSRconstantDamping(f, sample_rates):
    
    sns.set_style('whitegrid')
    
    c = ['orange',  'darkmagenta', 'blue']
    damping = 1e-4
    sr_str = ['{} kHz'.format(int(sr/1000)) for sr in sample_rates]
    sr_iter = it.cycle(sr_str)
    colours = dict(zip(sr_str, c))
    
    for sr in sample_rates:
        
        # make input
        # 'dur' is tone duration
        # 2 seconds of silence will automatically be appended
        dur = 3
        audio = make_audio(f, sr, dur)
        
        r = get_response(sr, audio, f, damping=damping)
            
        t = np.linspace(0, len(audio)/sr, len(audio))
        t *= 1000
        t0 = 0
        t1 = int(sr * 0.2)
        label = next(sr_iter)
        
        plt.plot(t[t0:t1], r[t0:t1], color=colours[label], label=label)
            
#        plt.ylim(-0.03, 0.59)
        
    plt.grid(True)
    plt.xlabel('Time (ms)')
    plt.ylabel('|z|', rotation='horizontal')
    plt.legend(loc='upper left', title='Sample rate')
        
    ax = plt.gca()
    ax.yaxis.labelpad = 10

    plt.show()
    plt.close()
    

if __name__ == '__main__':
    
#    testSR([440], [48000])
#    getSrDampingDiff([440], [48000])
    testSRconstantDamping([440], [48000, 96000, 192000])
    
##    f = np.array([100, 1000])
#    sr = 48000
#    
#    f = np.array([440])
#    
#    sr = np.array([48000, 96000, 192000])
#    testSRconstantDamping(f, sr)
#    
##    f = np.array([200, 5000])
#    sr = np.array([48000])
##    testSR(f, sr)
##    getSrDampingDiff(f, sr)
    

                