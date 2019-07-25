#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to help make the DetectorBank from the selected parameters
"""

def getNoteNum(name, edo=12):
    """ Find the number of chromatic steps between a given note `name` and A4,
        as well as the number of chromatic steps between the pitch class of
        `name` and A.
    """
    
    name = name.lower()
    
    pitches = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    
    pitch_class = name[0]
    octave = int(name[-1])
    
    if len(name) == 3:
        alter = name[1]
    else:
        alter = ''
        
    # find number of notes between A4 and given note (`note_num`)
    # and between pitch class and A (`pitch_diff`)
    
    # difference between given octave and 4th octave, in chromatic steps
    octave_diff = 4 - octave
    octave_diff *= edo
    
    # get pitch class diff
    pitch_idx = pitches.index(pitch_class)
    a_idx = pitches.index('a')
    pitch_diff = a_idx-pitch_idx
    
    # adjust octave diff by pitch_diff
    note_num = -(octave_diff + pitch_diff)
    
    # sharpen or flatten
    if alter == 'b':
        note_num -= 1
    elif alter == '#':
        note_num += 1
    
    return note_num, pitch_diff


def centsToHz(f0, cents, edo=12):
    """ Convert a bandwidth given in cents to Hertz """
    # Work out the difference in Hertz between f0 and f0+cents/2 (i.e. upper
    # half) and double it, as we want to be centred on f0
    h_cents = cents/200
    semitone = 2**(1/edo)
    f1 = f0*h_cents*(semitone-1)
    f1 *= 2
    return f1
    
    
    