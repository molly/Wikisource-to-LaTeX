# -*- coding: utf-8 -*-
# Copyright (c) 2013 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__all__ = ['Table', 'Cell']

import re
from collections import OrderedDict

class Table(object):
    def __init__(self):
        # Storage for various parts of the table. These are all strings that will later be
        # concatenated in order.
        self.t = OrderedDict()
        self.t['begin'] = '\\begin{tabularx}'   # Begin table environment
        self.t['width'] = ''                    # Width of the full table
        self.t['table_spec'] = ''               # Table column specifications
        self.t['hline'] = ''                    # A beginning /hline in case the table is bordered
        self.t['table_text'] = ''               # self.rows in its final text form
        self.t['end'] = '\\end{tabularx}'       # End table environment
        
        # Storage that is useful in creating the tables, but don't contain the final strings.
        self.rows = []                          # List containing each row of the table
        self.row_entries = []                   # List containing each entry in the row
        
        # Table format settings, initialized with the default values
        self.format = dict()
        self.format['border'] = False         # Entire table is bordered
        self.format['multicol'] = False         # True if table contains ANY multicolumns
        self.format['colwidth'] = None          # If multicolumn table, width of each column
        self.format['alignment'] = 'left'       # Text alignment of ALL the cells

    def append_cell(self, cell):
        '''Add a fully-formatted cell to the table.'''
        self.row_entries.append(cell)
        
    def append_row(self):
        if len(self.row_entries) > 0:
            self.rows.append(self.row_entries)
        self.row_entries = []
        
    def end(self):
        '''Perform the final formatting and concatenation, return the LaTeX table to write to
        the file.'''
        if len(self.row_entries) > 0:
            self.rows.append(self.row_entries)
        
    def set_alignment(self, a):
        if a == 'center':
            self.format['alignment'] = 'center'
    
    def set_width(self, w):
        w = round(float(w)/100, 2)
        if w == 1:
            self.t['width'] = '{\\textwidth}'
        elif w < .7:
            self.t['width'] = '{0.7\\textwidth}'
        else:
            self.t['width'] = '{' + str(w) + '\\textwidth}'
        
class Cell(object):
    def __init__(self, table):
        self.table = table                      # The table this cell will be a part of
        self.cell = ['', '', '']                # The cell's preceding, body, and ending strings
        
        # Row format settings, initialized with the default values
        self.r_format = dict()
        self.r_format['center'] = False
        
        # Cell format settings, initialized with the default values
        self.c_format = dict()
        self.c_format['colspan'] = None         # Number of columns to span
        self.c_format['border'] = None          # Border around just this cell?
        self.c_format['center'] = False         # Center just this cell?
    
    def append(self, text):
        self.cell[1] += text
        
    def end(self):
        '''Format and concatenate the cell, return it so it can be appended to the table.'''
        self.parse()
        return ''.join(self.cell)
    
    def parse(self):
        '''Parses out any formatting from the cell's content.'''
        self.cell[1] = re.sub('\{{2}popup\snote\|(.*?)\|(?P<text>.*?)\}{2}', '\g<text>', self.cell[1])
        print(self.cell)
    
    def reset(self):
        '''Resets only the cell details; retains row information.'''
        self.cell = ['', '', '']
        self.c_format['colspan'] = None