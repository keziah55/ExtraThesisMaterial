#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 11:00:32 2019

@author: keziah

Read precision, recall and onsets from all onset_analysis files in a directory
and write a Latex table.
"""

def make_table(dictionary, outfile, header=None, comment=None, fmt=None,
               mode='table'):
    """ Make LaTeX table of values from `dictionary', where the keys are the
        categories (first columns) and each category's value is another dict
        of precision, recall and F-measure for that category.
        
        The resulting table will be written to outfile.
        
        If a header is not provided, it will default to 
        "Category, Precision %, Recall %, F-measure %"
        
        If a comment if provided, it will be put at the top of the tex file.
        
        'fmt' will be used as the string format, if provided.
        
        'mode' gives the outer evironment in which to wrap the table; either
        'ctabular' or 'table'. In the latter case, the ctabular enviroment 
        will be wrapped in the table env.
    """
    
    if fmt is not None:
        fmt_str = '{{{}}}'.format(fmt)
    else:
        fmt_str = '{}'
    
    report = ''
    
#    measures = ['Precision', 'Recall', 'F-measure']
    # dictionary is dict of dicts
    # measures in the keys of each inner dict
    k = list(dictionary.keys())[0]
    measures = list(dictionary[k].keys())
    
    if header is None:
        header = ['Category'] + [m+' \%' for m in measures]
        
    header = [_make_bold(h) for h in header]
    
    report += _make_table_line(header)
    
    for category, results_dict in dictionary.items():
        
        measures_lst = [fmt_str.format(results_dict[measure]) 
                        for measure in measures]
        
        results_lst = [category] + measures_lst
            
        report += _make_table_line(results_lst, linesep=' \\\\ \n')
        
    report += '\\hline \n'
        
    if mode == 'table':
        incTable = True
    else:
        incTable = False
    table = _wrap_table(report, numCols=len(header), incTable=incTable)
    if comment:
        comment_str = '% {}\n'.format(comment) 
    else:
        comment_str = ''
    texstr = comment_str + table
    
    with open(outfile, 'w') as fileobj:
        fileobj.write(texstr)
        
        
def _make_table_line(lst, colsep=' & ', linesep=' \\\\ \\hline \n'):
    line = colsep.join(lst)
    line += linesep
    return line


def _make_bold(s):
    return '\\textbf{' + s + '}'

def _wrap_table(s, numCols, incTable=True):
    
    cols = '|c'*numCols
    cols = '{' + cols + '|}'
    
    begin_table = '\\begin{table}[]\n\\centering\n\\caption[]{}\n\\label{}\n'
    begin_tabular = '\\begin{ctabular}' + cols + '\n\\hline\n'
    end_tabular = '\\end{ctabular}\n'
    end_table = '\\end{table}'
    
    tabular = begin_tabular + s + end_tabular 
    
    if incTable:
        return begin_table + tabular + end_table
    else:
        return tabular

