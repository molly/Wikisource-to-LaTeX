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
        # Text containing the full table that will be returned
        self.table = ''
        
        # Storage for various parts of the table. These are all strings that will later be
        # concatenated in order.
        self.t = OrderedDict()
        self.t['begin'] = '\\begin{small}\n\\begin{spacing}{0.8}\n\\begin{tabularx}' # Begin table environment
        self.t['width'] = '{\\textwidth}'       # Width of the full table
        self.t['table_spec'] = ''               # Table column specifications
        self.t['hline'] = ''                    # A beginning /hline in case the table is bordered
        self.t['table_text'] = ''               # self.rows in its final text form
        self.t['end'] = '\\end{tabularx}\\\\\n\\end{spacing}\n\\end{small}\n' # End table environment
        
        # Storage that is useful in creating the tables, but don't contain the final strings.
        self.rows = []                          # List containing each row of the table
        self.row_entries = []                   # List containing each entry in the row
        
        # Table format settings, initialized with the default values
        self.format = dict()
        self.format['twidth'] = 1               # Width of entire table as coefficient of /textwidth
        self.format['border'] = False           # Entire table is bordered
        self.format['multicol'] = False         # True if table contains ANY multicolumns
        self.format['colnum'] = None            # Number of columns in the table
        self.format['colwidth'] = None          # Width of each col in multicolumn table as coefficient of /textwidth
        self.format['alignment'] = 'left'       # Text alignment of ALL the cells
        self.format['contents'] = False         # Is the table a contents table?

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
        # Append last row if necessary
        if len(self.row_entries) > 0:
            self.rows.append(self.row_entries)
        # Determine column length
        if not self.format['multicol']:
            self.set_columns()
            for row in self.rows:
                while len(row) < self.format['colnum']:
                    row.append(' ')
        # Adjust table if it contains multicolumns
        if self.format['multicol']:
            self.multicolumn()
        # Add table_spec
        if not self.format['contents']:
            if self.format['border']:
                    self.t['table_spec'] = '{|*{' + str(self.format['colnum']) + '}{X|}}\n'
            else:
                    self.t['table_spec'] = '{*{' + str(self.format['colnum']) + '}{X}}\n'
        else:
            self.t['table_spec'] = '{*{' + str(self.format['colnum']) + '}{X}}\n'
        # Combine self.rows into string
        for row in self.rows:
            if self.format['border']:
                self.t['table_text'] += ' & '.join(row) + ' \\\\ \\hline \n'
            else:
                self.t['table_text'] += ' & '.join(row) + ' \\\\\n'
        for value in self.t:
            self.table += self.t[value]
        return self.table
    
    def multicolumn(self):
        # Find number of columns in the table
        for row in self.rows:
            cols = int()
            for member in row:
                if type(member) is list:
                    cols += int(member[0])
                else:
                    cols += 1
            if not self.format['colnum'] or cols > self.format['colnum']:
                self.format['colnum'] = cols
        # Add multicolumn formatting
        for i in range(len(self.rows)):
            new_row = []
            for ind, member in enumerate(self.rows[i]):
                arw = '2' if ind==0 else ''
                if type(member) is list:
                    if self.format['border']:
                        new_row.append('\\multicolumn{' + member[0] + '}{|p{\\dimexpr' +
                                       str(int(member[0])/self.format['colnum']) +
                                       '\\linewidth-2\\tabcolsep-' + arw + '\\arrayrulewidth}|}{'
                                       + member[1] + '}')
                    else:
                        new_row.append('\\multicolumn{' + member[0] + '}{p{\\dimexpr' +
                                       str(int(member[0])/self.format['colnum']) +
                                       '\\linewidth-2\\tabcolsep-' + arw + '\\arrayrulewidth}}{'
                                       + member[1] + '}')
                else:
                    new_row.append(member)
            self.rows[i] = new_row
        
    def set_alignment(self, a):
        if a == 'center':
            self.format['alignment'] = 'center'
    
    def set_columns(self):
        '''Set columns only for tables without multicolumns.'''
        for row in self.rows:
            if self.format['colnum'] == None or len(row) > self.format['colnum']:
                self.format['colnum'] = len(row)
    
    def set_width(self, w):
        w = round(float(w)/100, 2)
        if w == 1:
            self.format['twidth'] = 1
        elif w < .7:
            self.format['twidth'] = 0.7
            self.t['width'] = '{0.7\\textwidth}'
        else:
            self.format['twidth'] = w
            self.t['width'] = '{' + str(w) + '\\textwidth}'
        
class Cell(object):
    def __init__(self, table):
        # TODO: Though "center" is being stored, it is not being implemented in any way.
        self.table = table                      # The table this cell will be a part of
        self.cell = ''                          # The cell string
        
        # Row format settings, initialized with the default values
        self.r_format = dict()
        self.r_format['center'] = False
        
        # Cell format settings, initialized with the default values
        self.c_format = dict()
        self.c_format['colspan'] = None         # Number of columns to span
        self.c_format['border'] = None          # Border around just this cell?
        self.c_format['center'] = False         # Center just this cell?
    
    
    def append(self, text):
        self.cell += text
        
    def cell_style(self, style, row_center=False):
        # TODO: Allow border-left/right: 0px, if possible.
        if 'border: 1px solid' in style:
            self.c_format['border'] = True
        if 'text-align: center' in style or row_center:
            self.c_format['center'] = True
        
    def end(self):
        '''Format and concatenate the cell, return it so it can be appended to the table.'''
        self.parse()
        if len(self.table.rows) == 0 and len(self.table.row_entries) == 0:
            if self.cell == "I.":
                self.table.format['contents'] = True
        return self.cell
    
    def parse(self):
        '''Parses out any formatting from the cell's content.'''
        if ' |' in self.cell[0:2]:
            self.cell = self.cell[2:]
        self.cell = re.sub(r'\[{2}(?:(.*?)\|)?(?P<text>.*?)\]{2}', r'\g<text>', self.cell)
        self.cell = re.sub(r'\{{2}popup\snote\|(.*?)\|(?P<text>.*?)\}{2}', r'\g<text>', self.cell)
        self.cell = re.sub(r'&nbsp;', ' ', self.cell)
        self.cell = re.sub(r'\{{2}larger\|(?P<text>.*?)\}{2}',
                              r'\\begin{large}\g<text>\\end{large}', self.cell)
        self.cell = re.sub(r'{{2}x-smaller(?:\sblock)?\|(?P<text>.*?)\}{2}',
                              r'\\begin{footnotesize}\g<text>\\end{footnotesize}', self.cell)
        self.cell = re.sub(r'<s>(?P<text>.*?)</s>', r'\\sout{\g<text>}', self.cell)
        self.cell = re.sub(r"\s?'''(?P<text>.*?)'''", r'\\textbf{\g<text>}', self.cell)
        self.cell = re.sub(r"('')(?P<text>.*?)('')", r'\\textit{\g<text>}',
                           self.cell)
        self.cell = re.sub(r'(\{{2}u\||<u>)(?P<text>.*?)(\}{2}|</u>)', r'\\uline{\g<text>}',
                           self.cell)
        self.cell = re.sub(r'<br\s?/?>', r' \\newline ', self.cell)
        self.cell = self.cell.replace("#", "\#").replace("$", "\$").replace("%", "\%")
        self.cell = self.cell.replace("_", "\_").replace("^", "\^").replace("~", "\~")
        self.cell = self.cell.replace("&", "\&").replace("□", "\\Square~")
        self.cell = self.cell.replace("▣", "\\CheckedBox~").replace("|", "{\\textbar}")
        self.cell = self.cell.replace("–", "--").replace("—", "---").replace("✓", "{\\checked}")
        if self.c_format['border']:
            self.cell = '\\fbox{' + self.cell + '}'
        if self.c_format['colspan']:
            self.cell = [self.c_format['colspan'], self.cell]
    
    def reset(self):
        '''Resets only the cell details; retains row information.'''
        self.cell = ['', '', '']
        self.c_format['colspan'] = None