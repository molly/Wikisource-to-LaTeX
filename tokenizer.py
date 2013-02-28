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

__all__ = ['Tokenizer']

import codecs, logging, os, re
import lex

class Tokenizer(object):
    #Token list
    tokens = (
              'NOINCLUDE', # <noinclude>
              'E_NOINCLUDE', # </noinclude>
              'PAGEQUALITY', # <pagequality level="4" user="GorillaWarfare" />
              'EXTRANEOUS_HTML', # <div>, <p>, etc.
              'DECLASSIFIED', # Declassified per Executive Order... Date: 2011
              'SECRET', # TOP SECRET - Sensitive
              'TABLE', # Beginning of table <table>
              'E_TABLE', # End of table </table>
              'TROW', # Beginning of table row <tr>
              'E_TROW', # End of table row </tr>
              'TITEM', # Beginning of table item <td>
              'E_TITEM', # End of table item, indicated by a newline in table state
              'OLIST', # Ordered list <ol>
              'E_OLIST', # End of ordered list </ol>
              'LITEM', # List item <li>
              'E_LITEM', # End of list item </li>
              'WLINK', # For links to Wikipedia, Wiktionary, etc.
              'UNDERLINED', # {{u|...}}
              'ITALICIZED', # ''...''
              'BOLDED', # '''...'''
              'WHITESPACE',
              'WORD',
              'PUNCT',
              'NUMBER',
              'LTGT' # TEMPORARY
              )
    
    states = (
              ('table', 'inclusive'),
              )

    # Matches
    def t_NOINCLUDE(self, token):
        r'<noinclude>\n?'
        return token
    
    def t_E_NOINCLUDE(self, token):
        r'</noinclude>\n?'
        return token
    
    def t_SECRET(self, token):
        r'[{]{2}center\|\<u\>TOP(?:.*?)[}]{2}'
        return token
    
    def t_TABLE(self, token):
        r'<table(?:.*?)>\n'
        token.lexer.begin('table') # Begin table state
        return token
        
    def t_E_TABLE(self, token):
        r'</table>\n'
        token.lexer.begin('INITIAL') # End table state
        return token
    
    def t_table_TROW(self, token):
        r'<tr>\n?'
        return token
    
    def t_table_E_TROW(self, token):
        r'</tr>\n?'
        return token
    
    def t_table_TITEM(self, token):
        r'<td(.*?)>'
        return token
    
    def t_table_E_TITEM(self, token):
        r'\n'
        return token
    
    def t_OLIST(self, token):
        r'<ol>'
        return token
    
    def t_E_OLIST(self, token):
        r'</ol>'
        return token
    
    def t_LITEM(self,token):
        r'<li>'
        return token
    
    def t_E_LITEM(self, token):
        r'</li>'
        return token
    
    def t_PAGEQUALITY(self, token):
        r'<pagequality\slevel="(?P<level>\d)"\suser="(?:\S*?)"\s?/>'
        token.value = token.lexer.lexmatch.group('level')
        return token
    
    def t_DECLASSIFIED(self, token):
        r'<b>Declassified(?:.*?)Date\:\s2011'
        return token
    
    def t_UNDERLINED(self, token):
        r'[{]{2}u\|(?P<word>.*?)[}]{2}'
        token.value = token.lexer.lexmatch.group('word')
        return token
    
    def t_BOLDED(self, token):
        r"""'{3}(?P<word>.*?)'{3}"""
        token.value = token.lexer.lexmatch.group('word')
        return token
    
    def t_ITALICIZED(self, token):
        r"""'{2}(?P<word>.*?)'{2}"""
        token.value = token.lexer.lexmatch.group('word')
        return token
    
    def t_WLINK(self, token):
        r'[[]{2}w(?:ikt)?:(?:.*?)[]]{2}'
        return token
     
    # Ignores
    def t_EXTRANEOUS_HTML(self, token):
        r'</?(?:div|p)(?:\s(?:.*?))?>'
        pass
    
    # VERY basic matches that have to be checked last.
    def t_PUNCT(self, token):
        r"""[!@\#\$\%\^&\*\(\)\-–—\+=\[\]\{\}\\\|\:;"',\.\?/~]"""
        return token
    
    def t_WORD(self, token):
        r'[a-zA-Z]+'
        return token
    
    def t_NUMBER(self, token):
        r'[0-9]+'
        return token
    
    def t_WHITESPACE(self, token):
        r'(?:\s|\t|\r|\n|<br\s?/?>)+'
        return token
    
    def t_LTGT(self, token):
        r'[<>]' # TEMPORARY
        return token
        
    # Error handling
    def t_error(self, token):
        print ("Illegal character {}".format(token.value[0]))
        token.lexer.skip(1)
        
    def __init__(self):
        self.logger = logging.getLogger("W2L")
    
    def analyze(self, data):
        self.lexer.input(data)
        while True:
            token = self.lexer.token()
            if not token:
                break      # No more input
            print(token)
        
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, reflags=re.DOTALL, **kwargs)