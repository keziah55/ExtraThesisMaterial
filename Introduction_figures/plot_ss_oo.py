# -*- coding: utf-8 -*-
"""
Plot waveform and spectrogram (as subplots) of portions of the audio.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import itertools as it
import seaborn as sns


def plot_wave_spec(audio, sr, t0, t1, wave_colour, spec_cmap):
    
    sns.set_style('whitegrid')
    
    i0, i1 = [int(t*sr) for t in [t0, t1]]
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)
    
    # plot waveform
    t = np.linspace(0, len(audio)/sr, len(audio))
    ax1.plot(t[i0:i1], audio[i0:i1], color=wave_colour)
    ax1.grid(True)
#    ax1.xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    
    ytx = np.linspace(-1, 1, num=5)
    c = it.cycle(['{:.0f}', ''])
    ytxlab = [next(c).format(y) for y in ytx]
    ax1.set_yticks(ytx)
    ax1.set_yticklabels(ytxlab)
    
    # plot spectrogram
    NFFT = 128
    _, _, _, cax = ax2.specgram(audio[i0:i1], Fs=sr, NFFT=NFFT, noverlap=32, 
                                xextent=(t0, t1), cmap=spec_cmap, window=np.blackman(NFFT),
                                scale='dB')
    
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Freq. (kHz)')
    
    xtx = np.linspace(t0, t1, num=9)
    c = it.cycle(['{:.3f}', ''])
    xtxlab = [next(c).format(x) for x in xtx]
    ax2.set_xticks(xtx)
    ax2.set_xticklabels(xtxlab)
    
    ytx = ax2.get_yticks()
    ytxlab = ['{:.0f}'.format(y/1000) for y in ytx]
    ax2.set_yticklabels(ytxlab)
    
    ax2.grid(False)
    
    plt.show()
    plt.close()
    
    # make colorbar legend separately
    fig_cbar = plt.figure(figsize=(8, 3))
    ax_cbar = fig_cbar.add_axes([0.05, 0.80, 0.9, 0.15])
    
    norm = mpl.colors.Normalize(vmin=-140, vmax=-40)
    
    cb1 = mpl.colorbar.ColorbarBase(ax_cbar, 
                                    cmap=spec_cmap, 
                                    norm=norm,
                                    orientation='horizontal')
    cb1.set_label('Intensity (dB)')
    
    plt.show()
    plt.close()
