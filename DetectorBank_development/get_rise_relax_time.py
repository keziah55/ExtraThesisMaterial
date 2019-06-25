#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find detector rise and relaxation times.
"""


import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from save_plot import SavePlot
import os


def formatLabelFreq(label):
    if label == 27.5:
        return('{0:.1f} Hz'.format(label))
    else:
        return('{0:.3f} Hz'.format(label))
        
        
def formatLabelDamp(label):
    if label == 0:
        return '{0:.0f}'.format(label)
    else:
        return '{0:.0e}'.format(label)
        
    
def make_audio(f0, sr=48000, duration=1):
    
    for n in range(len(f0)):
    
        t = np.linspace(0, 2*np.pi*f0[n]*duration, sr*duration)
        audio = np.sin(t)
        
    audio = np.append(audio, np.zeros(2*sr))
    
    return audio
    
    
def plot(r, vlines, sr, audioLen, sp, t0=None, t1=None):
    """ Plot the rise or relaxation times
    
        Paramters
        ---------
        r : np.array
            Response array
        vlines : list
            List of info about rise/relaxation times
        sr : int
            Sample rate
        audioLen : int
            Size of audio buffer (in samples)
        sp : SavePlot object
            SavePlot object
        t0 : float, optional
            Time at which to start plot (in seconds). If not provided, defaults
            to zero seconds
        t1 : float, optional
            Time at which to end plot (in seconds). If not provided, defaults
            to length of audio
    """
     # vlines=rstms or vlines=rxtms
     # if t0 or t1 not specified, default to 0 and audio length
     # t1 = 2.8
    
    audioLen = int(audioLen)
    
    t = np.linspace(0, audioLen/sr, audioLen)
    
    plot_ms = False
    
    # t0 and t1 and times in seconds
    # ts0 and ts1 are times in samples
    
    if t0 is None:
        t0 = 0
        ts0 = 0
    else:
        ts0 = int(t0*sr)
    if t1 is None:
        t1 = audioLen/sr
        ts1 = audioLen
    else:
        ts1 = int(t1*sr)
        
    c = ['red', 'orange',  'darkmagenta', 'lawngreen', 'blue']
    
#    majorLocator = MultipleLocator(1)
#    minorLocator = MultipleLocator(0.5)
    
    bottom, top = 0, 1
    
    if plot_ms:
        t *= 1000
        m = 1000
        t0 *= 1000
        t1 *= 1000
        xlabel = 'Time (ms)'
    else:
        m = 1
        xlabel = 'Time (s)'
      
    for k in range(len(r)):
        line, = plt.plot(t[ts0:ts1], r[k][ts0:ts1], c[k], label=d[k])
        # rise/relaxation times
        plt.axvline(m*(vlines[k][0]/sr), ymax=r[k][vlines[k][0]]/top, 
                    color=c[k], linestyle='--')
        plt.axvline(m*(vlines[k][1]/sr), ymax=r[k][vlines[k][1]]/top, 
                    color=c[k], linestyle='--')

    plt.xlim(t0, t1)
    #plt.xlim(0, 2)
    plt.ylim(bottom, top)
    
    ax = plt.gca()
#    ax.xaxis.set_major_locator(majorLocator)
#    ax.xaxis.set_minor_locator(minorLocator)
    ax.grid(True, 'both')
    
    ax.yaxis.labelpad = 10
        
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(map(float,labels), handles)))
    labels = map(formatLabelDamp, labels)
#    plt.legend(handles, labels, title='Damping factor')#, bbox_to_anchor=(1.0, 1))
            
    
    plt.xlabel(xlabel)
    plt.ylabel('|z|', rotation='horizontal')
    
    sp.plot(plt)


def print_table(mode, times, damping, sr, save=False, savename=None):
    
    if len(times) != len(damping):
        raise ValueError("'times' and 'damping' should be the same size")
    
    if mode == 'rise':
        out = print_table_rise(times, damping, sr, save, savename)
    elif mode == 'relax':
        out = print_table_relax(times, damping, sr, save, savename)
    else:
        raise ValueError("'mode' should be 'rise' or 'relax'")
    
    print(out)
        
        
def print_table_rise(times, damping, sr, save, savename):
    
    size = len(times)
    srms = sr/1000
    
    out = ''
    
    fields = [ 'Damping', '10% time (ms)', '90% time (ms)', 'Rise time (ms)']
    header = '{} | {} | {} | {}'.format(*fields)
    out += header + '\n' + '-'*len(header) + '\n'
    
    if save:
        fileobj = open(savename, 'w')
        fileobj.write(','.join(fields))
        fileobj.write('\n')
    
    for n in range(size):
        
        t10, t90 = times[n]
        rise = t90-t10
        
        data = [t/srms for t in  [t10, t90, rise]]
        line = [damping[n], *data]
        
        out += ('  {:.0e} |    {:7.3f}    |    {:7.3f}    |   {:7.3f}\n'
                .format(*line))
        
        if save:
            line_s = list(map(str, line))
            fileobj.write(','.join(line_s))
            fileobj.write('\n')
            
    if save:
        fileobj.close()

    return out


def print_table_relax(times, damping, sr, save, savename):
    
    size = len(times)
    srms = sr/1000
    
    out = ''
    
    fields = ['Damping', 'Relax. time (ms)']
    header = '{} | {}'.format(*fields)
    out += header + '\n' + '-'*len(header) + '\n'
    
    if save:
        fileobj = open(savename, 'w')
        fileobj.write(','.join(fields))
        fileobj.write('\n')
    
    for n in range(size):
        relax = (times[n][1] - times[n][0]) / srms
        line = [damping[n], relax]
        out += '  {:.0e} |    {:7.3f}    \n'.format(*line)
        
        if save:
            line_s = list(map(str, line))
            fileobj.write(','.join(line_s))
            fileobj.write('\n')
            
    if save:
        fileobj.close()

    return out


def get_rise_relax_times(d, f0, sr, method, f_norm, a_norm, gain, plot_times, 
                         sp=None):
    """ Get rise and relax times for a DetectorBank at five damping factors
    
        Parameters
        ----------
        d : list
            List of damping factors to test
        f0 : float
            Centre frequency
        sr : int
            Sample rate
        method : { DetectorBank.runge_kutta, DetectorBank.central_difference }
            DetectorBank method
        f_norm : { DetectorBank.freq_unnormalized, DetectorBank.search_normalized}
            DetectorBank frequency normalisation
        a_norm : { DetectorBank.amp_unnormalized, DetectorBank.amp_normalized}
            DetectorBank amplitude normalisation
        gain : float
            Input gain
        plot_times : bool
            Whether or not to plot the responses
        sp : list of SavePlot object
            If plot=True, please also provide a SavePlot object for rise and
            relax
            
        Returns
        -------
        Two lists of tuples: rise times and relax times.
        
        In each case, the tuples are the boundary times (10% time and 90% time
        or max time and 1/e time). The rise and relaxation times are the
        difference between these values.
    """

    # make input
    # 'dur' is tone duration
    # 2 seconds of silence will automatically be appended
    dur = 3
    audio = make_audio([f0], sr, dur)

    # make frequency/bandwidth pairs    
    f = np.array([f0])
    b = np.zeros(len(f))
    det_char = np.array(list(zip(f, b)))
    
    # relaxation times
    rxtms = []
    # rise times
    rstms = []
    # rise time is time from 10% to 90% of final value
    r_min, r_max = 0.1, 0.9
    
    # if we're plotting, we'll have to store all the responses
    if plot_times:
        all_r = np.zeros((len(d), len(audio)))
        
        # also check there is a SavePlot object
        if sp is None:
            raise ValueError('Please provide a SavePlot object is you wish to '
                             'plot the responses')
    
    # get response for each damping factor
    for n in range(len(d)):
       
        z = np.zeros((len(f),len(audio)), dtype=np.complex128)  
        r = np.zeros(z.shape)
        
        det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                           method|f_norm|a_norm, d[n], gain)
        det.getZ(z)
        mx = det.absZ(r, z)
        
        if plot_times:
            all_r[n] = r
        
        # r is a 2D array. As there's only one channel, r[0] contains the output
        
        # rise time
        rise0 = np.where(r[0] >= r_min*mx)[0][0]
        rise1 = np.where(r[0] >= r_max*mx)[0][0]
        rstms.append((rise0, rise1))
        
        # relaxation time is time for amplitude to fall to 1/e of max
        rxamp = max(r[0]) / np.e
        # max is end of tone
        # NB can't say np.where(r[k]==mx), as this may return values before the 
        # end of the tone
        mxtm = sr * dur
        # samples from max time to 1/e
        rxtm = np.where(r[0][mxtm:]<=rxamp)[0][0]
        rxtms.append((mxtm, mxtm+rxtm))
        
    if plot_times:
        plot(all_r, rstms, sr, len(audio), sp[0], t0=0, t1=1.1)
        plot(all_r, rxtms, sr, len(audio), sp[1], t0=2.95, t1=3.65)
        
    return rstms, rxtms
    

if __name__ == '__main__':
    
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    
    sr = 48000
    f0 = 440 # 100 #
    gain = 1.35
    
    d = [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]
    
    # make SavePlot objects before calling get_rise_relax_times()
    sp0 = SavePlot(False)
    sp1 = SavePlot(False)
    
    sp = [sp0, sp1]
    
    rstms, rxtms = get_rise_relax_times(d, f0, sr, method, f_norm, a_norm, 
                                        gain, True, sp)
    
    if a_norm == 2**16:
        s = 'AMP UNNORMALIZED'
    elif a_norm == 2**17:
        s = 'AMP NORMALIZED'
        
#    print('Generated by ' + __file__ + '\n')
    
    print(s + '\n' + '-'*len(s) + '\n')
    
    print_table('rise', rstms, d, sr, False)#, 'results/rise_times.csv')
    print_table('relax', rxtms, d, sr, False)#, 'results/relax_times.csv')
    