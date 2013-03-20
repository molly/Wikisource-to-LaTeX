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

__all__ = ['Wikitable']

import re

class Wikitable(object):
    def __init__(self):
        self.rows = [] # List containing each row of the table
        self.row_entries = [] # List containing each entry in the row
        self.table_text = '' # Full table text to be appended to output file
        
        self.begin_table = '\n\\begin{tabularx}' # First line of table (\begin{tabularx}...)
        self.table_body = '' # Body text
        self.cell = '' # Current cell
        self.cellb = '' # Prepend to cell
        self.celle = '' # Append to cell
        self.formatters = '' # Formatting keys
        self.hline = '' # Borders
        self.center = '' # Center for entire row
        self.centere = '' # End center
        self.width = None
        self.numcols = None
    
    def add_cell(self):
        ''' Compile the parts of the cell, add it to the list of row entries.'''
        self.cell = self.center + self.cellb + self.cell + self.celle + self.centere
        self.row_entries.append(self.cell)
        self.cell = ''
        self.cellb = ''
        self.celle = ''
        
    def cell_append(self, text):
        '''Append string to existing text in the current cell.'''
        self.cell += text
        
    def end(self):
        '''Finish up the table by appending the last row, formatting the body, and concatenating
        the table text.'''
        if len(self.row_entries) > 0:
            self.rows.append(self.row_entries) # Append last row if it hasn't happened yet
        self.format_body()
        self.table_text = (self.begin_table + self.table_body + "\\end{tabularx} \\\\\n")
        return self.table_text
        
    def format_body(self):
        '''Create the LaTeX table declaration with the table width, number of columns, etc.'''
        self.table_body = '\n'
        num_cols = self.get_num_cols()
        joiner = ' '
        if 'border' in self.formatters:
            joiner = ' | '
        for row in self.rows:
            length = int()
            for entry in row:
                c = re.match(r'\\multicolumn\{(?P<number>\d)\}', entry)
                if c:
                    length += int(c.group('number')) - 1
            while (len(row) + length) < num_cols:
                row.append(' ')
            if 'center' in self.formatters:
                self.table_body += (' & '.join(row) + ' \\\\ ' + self.hline + ' \n')
            else:
                self.table_body += (' & '.join(row) + ' \\\\' + self.hline + ' \n')
        if 'center' in self.formatters:
            self.begin_table += "{" + joiner.join(['>{\\centering\\arraybackslash}X']*num_cols) + "}"
        else:
            self.begin_table += "{" + joiner.join(['X']*num_cols) + "}"
        if self.hline:
            self.begin_table += '\n' + self.hline
        
    def get_num_cols(self):
        '''Count the number of columns in the table.'''
        numcols = 0
        for row in self.rows:
            if len(row) > numcols:
                numcols = len(row)
        self.numcols = numcols
        return numcols
        
    def larger(self):
        '''Begin larger text.''' # Get rid of this later?
        self.cellb="\\begin{large}"
        self.celle="\\end{large}"
    
    def new_row(self, center=None):
        '''End the current row by appending row_entries to rows, then clearing row_entries.'''
        if len(self.row_entries) > 0:
            self.rows.append(self.row_entries)
            self.row_entries = []
        
    def set_width(self, w):
        '''Set the width of the table.'''
        if w == '100':
            width = "{\\textwidth}"
            self.width = 1
        elif int(w) < 70:
            width = "{.70\\textwidth}" # Forcing mininum table width of 70%
            self.width = .7
        else:
            width = "{." + w + "\\textwidth}"
            self.width = w/100
        self.begin_table += width
            