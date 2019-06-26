#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get numbers from onset_analysis files.
"""

import subprocess
import re

def read_onset_analysis(file):
    """ Returns a dictionary of Precision, Recall and F-measure floats from  
        given onset_analysis.txt file.
    """
    
    out = subprocess.run(["tail", file], capture_output=True, 
                             encoding='utf-8')
        
    tail = out.stdout
    
    results = {}
    
    measures = ['Precision', 'Recall', 'F-measure']
    
    for measure in measures:
        
        regex = re.compile(r'{}: +(\d+.?\d*)%'.format(measure))
        m = regex.search(tail)
        if m is not None:
            pcnt = m.group(1)
        else:
            raise RuntimeError('Could not find {} in tail of {}'
                               .format(measure.lower(), file))

        results[measure] = float(pcnt)
        
    return results


if __name__ == '__main__':
    
    import os.path
    
    path = '/home/keziah/onsets/hsj/Sandpit/results/Iowa/6_Apr_2/'
    file = os.path.join(path, 'onset_analysis.txt')
    
    results = read_onset_analysis(file)
    print(results)
    