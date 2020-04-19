#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot all figures of the 'stood' audio file
"""

import soundfile as sf
import matplotlib.pyplot as plt
import os.path
from plot_stood import plot_wave, plot_spectrogram
from plot_ss_oo import plot_wave_spec


def get_audio():
    """ Read 'stood_mono.wav' and return the audio data and sample rate """
    audio_path = os.path.join('..', 'Data')
    audio_file = os.path.join(audio_path, 'stood_mono.wav')
    audio, sr = sf.read(audio_file)
    
    if audio.dtype == 'int16':
        audio = audio/2**15
        
    # make exactly 500ms long
    audio = audio[:int(sr/2)]
        
    return audio, sr


if __name__ == '__main__':
    
    wave_colour = '#e02323'
    spec_cmap = plt.cm.inferno
    
    audio, sr = get_audio()
    
    # plot whole wave
    plot_wave(audio, sr, wave_colour)
    plot_spectrogram(audio, sr, spec_cmap)

    # plot ss and oo sounds
    times = [(0.02, 0.04), (0.25, 0.27)]
    
    for t0, t1 in times:
        plot_wave_spec(audio, sr, t0, t1, wave_colour, spec_cmap)
