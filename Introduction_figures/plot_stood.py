# -*- coding: utf-8 -*-
"""
Plot waveform and spectrogram of 'stood' sung at A4.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_wave(audio, sr, colour):
    
    sns.set_style('whitegrid')  
    
    t = np.linspace(0, len(audio)/sr, len(audio))
    plt.plot(t, audio, color=colour)
    plt.grid(True)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    
    ytx = np.linspace(-1, 1, num=5)
    plt.yticks(ytx)
    
    plt.show()
    plt.close()
    
    
def plot_spectrogram(audio, sr, colour):
    
    sns.set_style('white')  
    
    fig, ax = plt.subplots()
    _, _, _, cax = ax.specgram(audio, Fs=sr, NFFT=256, noverlap=128, cmap=colour)
    fig.colorbar(cax).set_label('Intensity (dB)')
    
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (kHz)')
    
    plt.xticks(np.linspace(0, 0.5, num=6))
    
    ytx = np.linspace(0, 20000, num=5)
    ytxlab = ['{:.0f}'.format(y/1000) for y in ytx]
    plt.yticks(ytx, ytxlab)
    
    plt.show()
    plt.close()
