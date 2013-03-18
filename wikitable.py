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
        
    def end(self):
        '''Finish up the table.'''
        self.table_text = self.begin_table + "\\\\\n\\end{tabularx}"
        print(self.table_text)
        
    def set_width(self, w):
        if w == '100':
            width = "{\\textwidth}"
        else:
            width = "{." + w + "\\textwidth}"
        self.begin_table += width
            