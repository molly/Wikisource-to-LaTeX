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

class Wikitable(object):
    def __init__(self):
        self.rows = [] # List containing each row of the table
        self.row_entries = [] # List containing each entry in the row
        self.table_text = '' # Full table text to be appended to output file
        
        self.begin_table = '\\begin{tabularx}' # First line of table (\begin{tabularx}...)
        self.table_body = '' # Body text
        self.cell = '' # Current cell
        self.cellb = '' # Prepend to cell
        self.celle = '' # Append to cell
    
    def add_cell(self):
        self.cell = self.cellb + self.cell + self.celle
        self.row_entries.append(self.cell)
        self.cell = ''
        self.cellb = ''
        self.celle = ''
        
    def cell_append(self, text):
        self.cell += text
        
    def end(self):
        '''Finish up the table.'''
        if len(self.row_entries) > 0:
            self.rows.append(self.row_entries) # Append last row if it hasn't happened yet
        self.format_body()
        self.table_text = (self.begin_table + self.table_body + "\\end{tabularx} \\\\\n")
        return self.table_text
        
    def format_body(self):
        self.table_body = '\n'
        num_cols = self.get_num_cols()
        for row in self.rows:
            while len(row) < num_cols:
                row.append(' ')
            self.table_body += (' & '.join(row) + ' \\\\\n')
        self.begin_table += "{" + ' '.join(['X']*num_cols) + "}"
        
    def get_num_cols(self):
        '''Count the number of columns in the table.'''
        numcols = 0
        for row in self.rows:
            if len(row) > numcols:
                numcols = len(row)
        return numcols
        
    def larger(self):
        self.cellb="\\large{"
        self.celle="}"
    
    def new_row(self):
        print(self.row_entries)
        if len(self.row_entries) > 0:
            self.rows.append(self.row_entries)
            self.row_entries = []
        
    def set_width(self, w):
        if w == '100':
            width = "{\\textwidth}"
        elif int(w) < 70:
            width = "{.70\\textwidth}" # Forcing mininum table width of 70%
        else:
            width = "{." + w + "\\textwidth}"
        self.begin_table += width
        
    def strikeout(self):
        self.cellb = "\\begin{ulem}"
            