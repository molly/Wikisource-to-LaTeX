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

import logging

class Parser(object):
    def __init__(self, outputfile):
        self.logger = logging.getLogger("W2L")
        self.output = outputfile
        
    def dispatch(self, t_list):
        for token in t_list:
            self.value = token[1]
            command = 'self.{0}()'.format(token[0].lower())
            try:
                exec(command)
            except AttributeError:
                self.logger.debug("No function.")
                
    def write(self, text):
        self.output.write(text)
        
#===================================================================================================
# PARSING FUNCTIONS
#===================================================================================================
    # TABLE FUNCTIONS
    
    # WIKITABLE FUNCTIONS
    
    # PRE-HTML TOKENS
    
    # HTML TOKENS
    
    # POST-HTML TOKENS
    
    # BASIC TOKENS
    def ellipses(self):
        '''Write ellipses to file without changing anything.'''
        self.write(self.value)
    
    def punct(self):
        '''Write punctuation to file, escaping any characters with special functions in LaTeX.'''
        escape = ["#", "$", "%", "&", "~", "_", "^", "\\", "{", "}"]
        if self.value in escape:
            self.value = "\\" + self.value
        self.write(self.value)
    
    def word(self):
        '''Write word to file, using compose codes for any accented characters.'''
        if "é" in self.value:
            self.value = self.value.replace("é", "\\'{e}")
        self.write(self.value)
        
    def number(self):
        '''Write number(s) to file without changing anything.'''
        self.write(self.value)
        
    def whitespace(self):
        '''Replace newlines with '\\', replace tabs with spaces, leave spaces the same.'''
        if '\r' in self.value or '\n' in self.value:
            self.value = ' \\\\\n'
        else:
            self.value = ' '
        self.write(self.value)