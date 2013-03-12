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
            else:
                self.write(self.value)
                
    def write(self, text):
        self.output.write(text)
        
#===================================================================================================
# PARSING FUNCTIONS
#===================================================================================================
    # TABLE FUNCTIONS
    def table(self):
        #TODO: TABLE
        pass
    
    def table_e_table(self):
        #TODO: E_TABLE
        pass
    
    def table_trow(self):
        #TODO: TROW
        pass
    
    def table_e_trow(self):
        #TODO: E_TROW
        pass
    
    def table_titem(self):
        #TODO: TITEM
        pass
    
    def table_e_titem(self):
        #TODO: E_TITEM
        pass
    
    def table_tnoinclude(self):
        #TODO: TNOINCLUDE
        pass
    
    def table_te_noinclude(self):
        #TODO: TE_NOINCLUDE
        pass
    
    def table_tolist(self):
        #TODO: TOLIST
        pass
    
    def table_te_olist(self):
        #TODO: TE_OLIST
        pass
    
    def table_tlitem(self):
        #TODO: TLITEM
        pass
    
    def table_te_litem(self):
        #TODO: TE_LITEM
        pass
    
    def table_tforced_whitespace(self):
        #TODO: TFORCED_WHITESPACE
        pass
    
    # WIKITABLE FUNCTIONS
    def wikitable_wikitable(self):
        #TODO: WIKITABLE
        pass
    
    def wikitable_e_wikitable(self):
        #TODO: E_WIKITABLE
        pass
    
    # PRE-HTML TOKENS
    def internallink(self):
        #TODO: INTERNAL LINK
        pass
    
    def pagequality(self):
        #TODO: PAGEQUALITY
        pass
    
    def declassified(self):
        #TODO: DECLASSIFIED
        pass
    
    def secret(self):
        #TODO: SECRET
        pass
        
    def runhead(self):
        #TODO: RUNHEAD
        pass
    
    # HTML TOKENS
    def html_olist(self):
        '''Begin ordered list.'''
        self.value = '\\begin{enumerate}'
    
    def html_e_olist(self):
        '''End ordered list.'''
        self.value = '\\end{enumerate}'
    
    def html_litem(self):
        '''Format list item.'''
        self.value = "\item " + self.value
        
    def html_e_litem(self):
        '''Do nothing.'''
        self.value = ""
        
    def noinclude(self):
        # TODO: NOINCLUDE
        pass
    
    def html_e_noinclude(self):
        # TODO: E_NOINCLUDE
        pass
    
    def html_reflist(self):
        #TODO: REFLIST
        pass
    
    def html_ref(self):
        #TODO: REF
        pass
    
    def html_forced_whitespace(self):
        '''Add whitespace.'''
        self.value = ' \\\\\n'
    
    # POST-HTML TOKENS
    def pspace(self):
        '''Replace {{nop}} with \\.'''
        self.value = ' \\\\\n'
        
    def cindent(self):
        # TODO: CONTINUE INDENT FROM PREVIOUS PAGE
        pass
    
    def indent(self):
        # TODO: BLOCK INDENT
        pass
    
    def pagenum(self):
        # TODO: PAGE NUMBER
        pass
    
    def pent(self):
        # TODO: NOTE
        pass
    
    def centered(self):
        '''Center text.'''
        # TODO: Check that there is a '\\' before and after centered text
        self.value = "\\begin{center}" + self.value + "\\end{center}"
        
    def underlined(self):
        '''Replace underlined text with italicized text.'''
        self.italicized()
        
    def bolded(self):
        '''Bold text.'''
        self.value = "\\textbf{" + self.value + "}"
    
    def italicized(self):
        '''Italicize text.'''
        self.value = "\\textit{" + self.value + "}"
        
    def wlink(self):
        '''Print only the display text of the wikilink.'''
        pass
    
    # BASIC TOKENS
    def ellipses(self):
        '''Ellipses (three and four dots)'''
        if self.value == "...":
            self.value == "\\lips"
        else:
            self.value == "\\lips."
    
    def punct(self):
        # TODO: Figure out `` and " for quotes
        '''Write punctuation to file, escaping any characters with special functions in LaTeX.'''
        escape = ["#", "$", "%", "&", "~", "_", "^", "\\", "{", "}"]
        if self.value in escape:
            self.value = "\\" + self.value
        elif self.value == "°":
            self.value = "\\degree"
        elif self.value == "–":
            self.value = "--"
        elif self.value == "—":
            self.value = "---"
    
    def word(self):
        # TODO: Fix large spaces after abbreviations (i.e., e.g., etc.)
        '''Write word to file, using compose codes for any accented characters.'''
        if "é" in self.value:
            self.value = self.value.replace("é", "\\'{e}")
        
    def number(self):
        '''Write number(s) to file without changing anything.'''
        pass
        
    def whitespace(self):
        '''Replace newlines with '\\', replace tabs with spaces, leave spaces the same.'''
        if '\r' in self.value or '\n' in self.value:
            self.value = ' \\\\\n'
        else:
            self.value = ' '