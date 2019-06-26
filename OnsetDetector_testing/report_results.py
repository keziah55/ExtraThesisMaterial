#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Make LaTeX tables of results and comparison of results with functions
make_results_tables() and make_comparison_tables()
"""

import os
from make_report import make_table
from read_onset_analysis import read_onset_analysis


def compare(dir1, dir2, categories, cat_name=None):
    """ Read onset_analysis files in directories for the given categories.
    
        Any filenames that do not follow the naming pattern 
        'onset_analysis_Category.txt' should be provided in the cat_name dict.
        
        Returns dict of category : results_dict
    """
    measures = ['Precision', 'Recall', 'F-measure']
    
    # dict of all comparisons to be filled and returned
    comparision = {}
    
    # for each given category, get P, R and F
    for category in categories:
        
        if category in cat_name.keys():
            fcat = cat_name[category]
        else:
            fcat = '_' + category
           
        # dict of each dir's P, R and F
        tmp = {}
            
        # get P, R and F for each dir
        for dr in (dir1, dir2):
            
            file = 'onset_analysis' + fcat + '.txt'
            file = os.path.join(dr, file)
            
            results_dict = read_onset_analysis(file)
            
            tmp[dr] = results_dict
            
        # dict of (dir1-dir2)/dir1 for each measure
        cmpr = {}
            
        # get dir1/dir2 for each measure
        for measure in measures:
            
            m1 = tmp[dir1][measure]
            m2 = tmp[dir2][measure]
            try:
                m = (m1-m2)
            except ZeroDivisionError:
                if m1 == m2:
                    m = 1
                else:
                    m = 0
            cmpr[measure] = m
        
        # store comparison for this category
        comparision[category] = cmpr
        
    return comparision


def read_results(resultspath, categories, cat_name=None):
    """ Read onset_analysis files in 'resultspath' for the given categories.
    
        Any filenames that do not follow the naming pattern 
        'onset_analysis_Category.txt' should be provided in the cat_name dict.
        
        Returns a dictionary of category : results_dict pairs, where each value
        is itself a dictionary of precision, recall and F-measure values
    """
        
    d = {}
    
    for category in categories:
        
        if category in cat_name.keys():
            fcat = cat_name[category]
        else:
            fcat = '_' + category
            
        file = 'onset_analysis' + fcat + '.txt'
        file = os.path.join(resultspath, file)
        
        results_dict = read_onset_analysis(file)
        
        d[category] = results_dict
        
    return d


def make_results_tables(resultsdir):
    
    resultssubdir = 'result_analysis'
    
    resultssubdir = os.path.join(resultsdir, resultssubdir)
    
    tablesdir = os.path.join(resultsdir, 'results_tables')
    
    if not os.path.exists(tablesdir):
        os.makedirs(tablesdir)
        
    inst_cat_header = "\\begin{tabular}[c]{@{}c@{}}Instrument\\\\ Category\\end{tabular}"
    
    cat_fname = {'all':('results_table.tex', "`last-first'"), 
                 'instruments':('results_table_categories.tex', inst_cat_header), 
                 'rolls':('results_table_rolls.tex', 'Instrument'), 
                 'roll_noroll':('results_table_roll_noroll.tex', 'Instrument'), 
                 'octaves':('results_table_octave.tex', 'Octave no.'), 
                 'piano_dyn':('results_table_piano_dyn.tex', 'Dynamic'), 
                 'guitar_dyn':('results_table_guitar_dyn.tex', 'Dynamic'), 
                 'arco_pizz':('results_table_arcopizz.tex', 'Style'), 
                 'strings_arco':('results_table_arco.tex', 'Instrument'), 
                 'strings_pizz':('results_table_pizz.tex', 'Instrument'),
                 'brass':('results_table_brass.tex', 'Instrument'), 
                 'woodwind':('results_table_woodwind.tex', 'Instrument'),
                 'percussion_no_rolls':('results_table_percussion.tex', 
                                        'Instrument'),
                 'vibrato':('results_table_vibrato.tex', 'Style')
                 }
    
    for category, info in cat_fname.items():
        
        fname, h0 = info
        
        if category == 'percussion':
            header = [h0, 'P \%', 'R \%', 'F \%']
        else:
            header = [h0, 'Precision \%', 'Recall \%', 'F-measure \%']
    
        categories, cat_name = get_categories(category)
        outfile = os.path.join(tablesdir, fname)
        d = read_results(resultssubdir, categories, cat_name)
        make_table(d, outfile, comment=resultssubdir, header=header, 
                   mode='ctabular')#, fmt=':.6g')
        
    
def make_comparison_tables(dirs, resultspath, outpath=None):
    """ Compare results in dirs """
    
    resultssubdir = 'result_analysis'
    resultssubdirs = [os.path.join(resultspath, d, resultssubdir) for d in dirs]
    
    comment = 'Results from {}/{}'.format(*dirs)
    if outpath is None:
        outpath = resultspath
        
    header = ['Category', 'P \%-pt. diff.', 'R \%-pt. diff.', 'F \%-pt. diff.']
        
    cat_fname = {'instruments':('comparison_table.tex', 'Category'), 
                 'octaves':('comparison_table_octave.tex', 'Octave no.'), 
                 'piano_dyn':('comparison_table_piano_dyn.tex', 'Dynamic'), 
                 'guitar_dyn':('comparison_table_guitar_dyn.tex', 'Dynamic'),
                 'arco_pizz':('comparison_table_arcopizz.tex', 'Style'),
                 'strings_arco':('comparison_table_arco.tex', 'Instrument'), 
                 'strings_pizz':('comparison_table_pizz.tex', 'Instrument'),
                 'brass':('comparison_table_brass.tex', 'Instrument'), 
                 'woodwind':('comparison_table_woodwind.tex', 'Instrument'),
                 'percussion':('comparison_table_percussion.tex', 
                               'Instrument'),
                 'vibrato':('comparison_table_vibrato.tex', 'Style')}
    
    for category, info in cat_fname.items():
        
        fname, h0 = info
        
        header = [h0, 'Precision \%', 'Recall \%', 'F-measure \%']
    
        categories, cat_name = get_categories(category)
        outfile = os.path.join(outpath, fname)
        d = compare(*resultssubdirs, categories, cat_name)
        
        make_table(d, outfile, comment=comment, fmt=':.6g', header=header,
                   mode='ctabular')
        

def get_categories(key):
    """ Get 'categories' list and 'cat_name' dict for given key.
    
        Valid keys are: 'all', 'instruments', 'octaves', 'arco_pizz', 
        'strings_arco', 'strings_pizz', 'brass', 'woodwind', 'vibrato', 
        'percussion_all', 'percussion_no_rolls', 'piano_dyn', 'guitar_dyn', 
        'rolls' and 'roll_noroll'.
        
        'cat_name' is a dict of filename endings that are not simply
        'onset_analysis_Category.txt'
    """
    
    valid = ['all', 'instruments', 'octaves', 'arco_pizz', 'strings_arco',
             'strings_pizz', 'brass', 'woodwind', 'vibrato', 'percussion_all',
             'piano_dyn', 'guitar_dyn', 'rolls', 'roll_noroll', 
             'percussion_no_rolls']
    if key not in valid:
        raise ValueError("Key '{}' not valid. Valid keys are: {}"
                         .format(key, valid))
        
    if key == 'all':
        categories = ['All']
        cat_name = {'All':''}
        
    elif key == 'instruments':
        categories = ['Brass', 'Guitar', 'Piano', 'Percussion',  'Strings', 
                      'Woodwind']
        # filenames that are not 'onset_analysis_Category.txt'
        cat_name = {}
        
    elif key == 'roll_noroll':
        categories = ['Rolls', 'Single note']
        # filenames that are not 'onset_analysis_Category.txt'
        cat_name = {'Rolls':'_Percussion_roll', 
                    'Single note':'_Percussion_no_roll'}
        
    elif key == 'piano_dyn':
        categories = ['\\dynmark{pp}', '\\dynmark{mf}', '\\dynmark{ff}']
        cat_name = {'\\dynmark{pp}':'_Piano.pp', '\\dynmark{mf}':'_Piano.mf', 
                    '\\dynmark{ff}':'_Piano.ff'}
        
    elif key == 'guitar_dyn':
        categories = ['\\dynmark{pp}', '\\dynmark{mf}', '\\dynmark{ff}']
        cat_name = {'\\dynmark{pp}':'_Guitar.pp', '\\dynmark{mf}':'_Guitar.mf', 
                    '\\dynmark{ff}':'_Guitar.ff'}
    
    elif key == 'octaves':
        categories = [str(i) for i in range(9)]
        cat_name = {c:'_octave_{}'.format(c) for c in categories}
    
    elif key == 'arco_pizz':
        categories = ['Arco', 'Pizzicato']
        cat_name = {'Arco':'_arco', 'Pizzicato':'_pizz'}
    
    elif key == 'vibrato':
        categories = ['Vibrato', 'No vibrato']
        cat_name = {'Vibrato':'_vib', 'No vibrato':'_novib'}
        
    elif key == 'strings_arco':
        categories = ['Bass', 'Cello', 'Viola', 'Violin']
        cat_name = {item:'_{}.arco.ff'.format(item) for item in categories}
        
    elif key == 'strings_pizz':
        categories = ['Bass', 'Cello', 'Viola', 'Violin']
        cat_name = {item:'_{}.pizz.ff'.format(item) for item in categories}
        
    elif key == 'brass':
        categories = ['Bass trombone', 'Horn', 'Tenor trombone', 
                      'Trumpet (vibrato)', 'Trumpet (no vibrato)', 'Tuba']
        cat_name = {'Bass trombone':'_BassTrombone', 
                    'Tenor trombone':'_TenorTrombone',  
                    'Trumpet (vibrato)':'_Trumpet.vib',
                    'Trumpet (no vibrato)':'_Trumpet.novib'}
        
    elif key == 'woodwind':
        categories = ['Alto flute (vibrato)', 'Alto sax. (vibrato)',
                      'Alto sax. (no vibrato)', 'Bass clarinet', 'Bass flute',
                      'Bassoon', 'B$\\flat$ clarinet', 'E$\\flat$ clarinet',
                      'Flute (vibrato)', 'Flute (no vibrato)', 'Oboe', 
                      'Soprano sax. (vibrato)', 'Soprano sax. (no vibrato)']
        
        cat_name = {'Alto flute (vibrato)':'_AltoFlute.vib.ff', 
                    'Alto sax. (vibrato)':'_AltoSax.NoVib.ff',
                    'Alto sax. (no vibrato)':'_AltoSax.vib.ff',
                    'Bass clarinet':'_BassClarinet.ff', 
                    'Bass flute':'_BassFlute.ff', 'Bassoon':'_Bassoon.ff', 
                    'B$\\flat$ clarinet':'_BbClarinet.ff', 
                    'E$\\flat$ clarinet':'_EbClarinet.ff',
                    'Flute (vibrato)':'_Flute.vib.ff', 
                    'Flute (no vibrato)':'_Flute.nonvib.ff', 'Oboe':'_Oboe.ff', 
                    'Soprano sax. (vibrato)':'_SopSax.vib.ff', 
                    'Soprano sax. (no vibrato)':'_SopSax.nonvib.ff'}
    
    elif key == 'percussion_all':
        categories = ['Bells (brass)', 'Bells (plastic)', 'Crotale',
                      'Marimba (cord)', 'Marimba (deadstroke)',
                      'Marimba (roll)', 'Marimba (rubber)', 'Marimba (yarn)',
                      'Thai gong', 'Vibraphone (bow)', 'Vibraphone (dampen)',
                      'Vibraphone (shortsustain)', 'Vibraphone (sustain)',
                      'Xylophone (gliss)', 'Xylophone (hardrubber)',
                      'Xylophone (hardrubber, roll)', 'Xylophone (rosewood)',
                      'Xylophone (rosewood, roll)']
        
        cat_name = {'Bells (brass)': '_bells.brass',
                    'Bells (plastic)': '_bells.plastic',
                    'Marimba (cord)': '_Marimba.cord',
                    'Marimba (deadstroke)': '_Marimba.deadstroke',
                    'Marimba (roll)': '_Marimba.roll',
                    'Marimba (rubber)': '_Marimba.rubber',
                    'Marimba (yarn)': '_Marimba.yarn',
                    'Thai gong': '_thaigong',
                    'Vibraphone (bow)': '_Vibraphone.bow',
                    'Vibraphone (dampen)': '_Vibraphone.dampen',
                    'Vibraphone (shortsustain)': '_Vibraphone.shortsustain',
                    'Vibraphone (sustain)': '_Vibraphone.sustain',
                    'Xylophone (gliss)': '_Xylophone.gliss',
                    'Xylophone (hardrubber)': '_Xylophone.hardrubber',
                    'Xylophone (hardrubber, roll)': '_Xylophone.hardrubber.roll',
                    'Xylophone (rosewood)': '_Xylophone.rosewood',
                    'Xylophone (rosewood, roll)': '_Xylophone.rosewood.roll'}
        
    elif key == 'rolls':
        categories = ['Marimba', 'Xylophone (hardrubber)', 
                      'Xylophone (rosewood)']
        
        cat_name = {'Marimba': '_Marimba.roll',
                    'Xylophone (hardrubber)': '_Xylophone.hardrubber.roll',
                    'Xylophone (rosewood)': '_Xylophone.rosewood.roll'}
        
    elif key == 'percussion_no_rolls':
        categories = ['Bells (brass)', 'Bells (plastic)', 'Crotale',
                      'Marimba (cord)', 'Marimba (deadstroke)',
                      'Marimba (rubber)', 'Marimba (yarn)',
                      'Thai gong', 'Vibraphone (bow)', 'Vibraphone (dampen)',
                      'Vibraphone (shortsustain)', 'Vibraphone (sustain)',
                      'Xylophone (gliss)', 'Xylophone (hardrubber)',
                       'Xylophone (rosewood)']
        
        cat_name = {'Bells (brass)': '_bells.brass',
                    'Bells (plastic)': '_bells.plastic',
                    'Marimba (cord)': '_Marimba.cord',
                    'Marimba (deadstroke)': '_Marimba.deadstroke',
                    'Marimba (rubber)': '_Marimba.rubber',
                    'Marimba (yarn)': '_Marimba.yarn',
                    'Thai gong': '_thaigong',
                    'Vibraphone (bow)': '_Vibraphone.bow',
                    'Vibraphone (dampen)': '_Vibraphone.dampen',
                    'Vibraphone (shortsustain)': '_Vibraphone.shortsustain',
                    'Vibraphone (sustain)': '_Vibraphone.sustain',
                    'Xylophone (gliss)': '_Xylophone.gliss',
                    'Xylophone (hardrubber)': '_Xylophone.hardrubber',
                    'Xylophone (rosewood)': '_Xylophone.rosewood'}
    
    return categories, cat_name
    
    
if __name__ == '__main__':
    
    resultsdirs = ['results/low_damping/with_last-first', 
                   'results/high_damping/with_last-first',
                   'results/low_damping/without_last-first',  
                   'results/high_damping/without_last-first']
    
    for resultsdir in resultsdirs:
        print('Making results tables from {}'.format(resultsdir))
        make_results_tables(resultsdir)
    
    
#    print('Making comparison tables from {} and {}'.format(*resultsdirs))
#    outdir = 'compare_{}_and_{}'.format(*resultsdirs)
#    outpath = os.path.join(path, outdir)
#    if not os.path.exists(outpath):
#        os.makedirs(outpath)
#    make_comparison_tables(resultsdirs, path, outpath=outpath)
#    
    