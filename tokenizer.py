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

import codecs, logging, re
import lex

class Tokenizer(object):
#===================================================================================================
# TOKEN DECLARATIONS
#===================================================================================================
    tokens = (
            # Table state
              'TABLE', # Beginning of table <table>
              'E_TABLE', # End of table </table>
              'TROW', # Beginning of table row <tr>
              'E_TROW', # End of table row </tr>
              'TITEM', # Beginning of table item <td>
              'E_TITEM', # End of table item, indicated by a newline in table state
              'TNOINCLUDE', # <noinclude> within table state
              'TE_NOINCLUDE', # </noinclude> within table state
              'TOLIST', # <ol> in table
              'TE_OLIST', # </ol> in table
              'TLITEM', # <li> in table
              'TE_LITEM', # </li> in table
              'TFORCED_WHITESPACE', # <br/> in a table
            # Wikitable state
              'WIKITABLE', # Beginning of table {|
              'E_WIKITABLE', # End of table |}
              'FORMAT', # Initial {| style="..."
              'NEWROW', # |-
              'TCELL', # Beginning of table cell
              'BOXEDCELL', # For individually boxed cells
              'E_TCELL', # End of table cell
            # Tokens to check before HTML state  
              'INTERNALLINK',
              'PAGEQUALITY', # <pagequality level="4" user="GorillaWarfare" />
              'DECLASSIFIED', # Declassified per Executive Order... Date: 2011
              'SECRET', # TOP SECRET - Sensitive
              'RUNHEAD', # Running header
              'FORCED_WHITESPACE', # <br />; checked before HTML state b/c it's often nested
            # HTML state
              'HTML', # Beginning of HTML tag
              'E_HTML', # Ending of HTML tag
              'OLIST', # Ordered list <ol>
              'E_OLIST', # End of ordered list </ol>
              'LITEM', # List item <li>
              'E_LITEM', # End of list item </li>
              'NOINCLUDE', # <noinclude>
              'E_NOINCLUDE', # </noinclude>
              'REFLIST', # <references/>
              'REF', # <ref>
              'E_REF', # </ref>
              'EXTRANEOUS_HTML', # <div>, <p>, etc.
              # Centered state
              'CENTERED', # {{center|...}} or {{c|...}}
              'E_CENTERED', # End of centered state
              # General tokens (INITIAL state)
              'PSPACE', # {{nop}}
              'CINDENT', # Continued indent from prev page <noinclude>:</noinclude>
              'INDENT', # Line preceded by one or more :'s
              'PAGENUM', # Taken from running header
              'PENT', # {{Pent|I. A.|1}}
              'SIZE', # Size templates, such as {{x-larger}}
              'UNDERLINED', # {{u|...}}
              'BOLDED', # '''...'''
              'ITALICIZED', # ''...''
              'WLINK', # For links to Wikipedia, Wiktionary, etc.
              # Very basic tokens
              'ELLIPSES', # ... or ....
              'CHECKBOX_EMPTY',
              'CHECKBOX_CHECKED',
              'PUNCT',
              'WORD',
              'NUMBER',
              'WHITESPACE',
              )
#===================================================================================================
# STATES
#===================================================================================================
    states = (
              ('table', 'inclusive'),
              ('wikitable', 'inclusive'),
              ('tcell', 'inclusive'),
              ('html', 'exclusive'),
              ('centered', 'inclusive')
              )

#===================================================================================================
# TOKEN DEFINITIONS
#===================================================================================================
    # TABLE STATE    
    def t_TABLE(self, token):
        r'<table(?:.*?)>\n'
        token.lexer.begin('table') # Begin table state
        return token
        
    def t_table_E_TABLE(self, token):
        r'</table>\n?'
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
        r'\n+'
        return token
    
    def t_table_TNOINCLUDE(self, token):
        r'<noinclude>'
        return token
    
    def t_table_TE_NOINCLUDE(self, token):
        r'</noinclude>'
        return token
    
    def t_table_TOLIST(self, token):
        r'<ol>'
        return token
    
    def t_table_TE_OLIST(self, token):
        r'</ol>'
        return token
    
    def t_table_TLITEM(self,token):
        r'<li>'
        return token
    
    def t_table_TE_LITEM(self, token):
        r'</li>'
        return token
    
    def t_table_TFORCED_WHITESPACE(self, token):
        r'<br/s?/?>'
        return token
    
    
    # Wikitable state
    def t_WIKITABLE(self, token):
        r'\{\|'
        token.lexer.begin('wikitable')
        return token
    
    def t_wikitable_E_WIKITABLE(self, token):
        r'\|\}'
        token.lexer.begin('INITIAL')
        return token
    
    def t_wikitable_FORMAT(self, token):
        # TODO: This regex will need to become much more complex as more instances are found
        r'(?:\s?style\=")(?:\s?width\:\s?(?P<width>\d{1,3})%;?\s?)?(?:text\-align\:\s?(?P<textalign>center);?\s?)(?:")'
        token.value = (token.lexer.lexmatch.group('width', 'textalign'))
        return token
    
    def t_wikitable_NEWROW(self, token):
        r'(\n?\|\-\s?\n)'
        return token
    
    def t_wikitable_TCELL(self, token):
        r'\|{1,2}\s?'
        token.lexer.begin('tcell')
        return token
    
    def t_tcell_BOXEDCELL(self, token):
        r'(?:style="border:\s1px\ssolid;"\s?\|\s?)(?:\{{2}popup\snote\|(?:.*?)\|)?(?P<text>.*?)(?:\}{2})?\s?(?=\s?\||\n)'
        token.value = token.lexer.lexmatch.group('text')
        return token
    
    def t_tcell_E_TCELL(self, token):
        r'\s?(?=\s?\||\n)'
        token.lexer.begin('wikitable')
        return token
    
    # Tokens to be checked before HTML state
    def t_INTERNALLINK(self, token):
        r'[[]{2}United\sStates(?:.*?)Defense/(?P<subpage>.*?)\#(?P<anchor>.*?)\|(?P<title>.*?)[]]{2}'
        token.value = (token.lexer.lexmatch.group('subpage','anchor','title'))
        return token 
    
    def t_PAGEQUALITY(self, token):
        r'<pagequality\slevel="(?P<level>\d)"\suser="(?:\S*?)"\s?/>'
        token.value = token.lexer.lexmatch.group('level')
        return token
    
    def t_DECLASSIFIED(self, token):
        r'<b>Declassified(?:.*?)Date\:\s2011'
        return token
    
    def t_SECRET(self, token):
        r'[{]{2}c(?:enter)?\|(?:<u>|[{]{2}u\|)TOP(?:.*?)[}]{2,4}'
        return token
    
    def t_RUNHEAD(self, token):
        r'[{]{2}rh(?:\|left=\s?(?P<left>.*?)\s?)?(?:\|center=\s?(?P<center>.*?)\s?)?(?:\|right=\s?(?P<right>.*?)\s?)?[}]{2}(?!\})'
        token.value = token.lexer.lexmatch.group('left','center','right')
        return token
    
    def t_FORCED_WHITESPACE(self, token):
        r'<br\s?/?>'
        return token
     
    # HTML STATE
    def t_HTML(self, token):
        r'<'
        token.lexer.begin('html')
        pass
    
    def t_html_E_HTML(self, token):
        r'>'
        token.lexer.begin('INITIAL')
        pass
    
    def t_html_OLIST(self, token):
        r'ol'
        return token
    
    def t_html_E_OLIST(self, token):
        r'/ol'
        return token
    
    def t_html_LITEM(self,token):
        r'li'
        return token
    
    def t_html_E_LITEM(self, token):
        r'/li'
        return token
    
    def t_html_NOINCLUDE(self, token):
        r'noinclude'
        return token
    
    def t_html_E_NOINCLUDE(self, token):
        r'/noinclude'
        return token
    
    def t_html_REFLIST(self, token):
        r'references\s?/'
        pass # Ignore
    
    def t_html_REF(self, token):
        r'ref(?:\sname=\s?(?P<name>.*?)\s?/?)?(?=>)'
        token.value = token.lexer.lexmatch.group('name')
        return token
        
    def t_html_E_REF(self, token):
        r'/ref'
        return token
    
    def t_html_EXTRANEOUS_HTML(self, token):
        r'/?(?:div|p|span)(?:(?:\s.*?)(?=>))?'
        pass # Ignore
    
    # CENTERED STATE
    def t_CENTERED(self, token):
        r'[{]{2}c(?:enter)?\|'
        token.lexer.begin('centered')
        return token
    
    def t_centered_E_CENTERED(self, token):
        r'[}]{2}'
        token.lexer.begin('INITIAL')
        return token
    
    # INITIAL STATE
    def t_PSPACE(self, token):
        r'[{]{2}nop[}]{2}'
        return token
    
    def t_CINDENT(self, token):
        r'(?<=<noinclude>):(?=</noinclude>)'
        return token
    
    def t_INDENT(self, token):
        r'(?:\n|\r)+(?P<colons>\:+)'
        token.value = token.lexer.lexmatch.group('colons')
        return token
    
    def t_PAGENUM(self, token):
        r'[{]{2}rh\|center=\s?(?P<num>[A-Z]+\-[\d]+)\s?\|right=(.*?)[}]{2,}'
        token.value = token.lexer.lexmatch.group('num')
        return token
    
    def t_PENT(self, token):
        r'[{]{2}Pent\|(?P<sect>.*?)\|(?P<subsect>(\d\.\d)\|)?(?P<num>\d+)[}]{2}'
        token.value = token.lexer.lexmatch.group('sect', 'subsect', 'num')
        return token
    
    def t_SIZE(self, token):
        r'[{]{2}(?:(?P<x>[x]{1,4})\-)?(?P<ls>larger|smaller)\|(?P<text>.*?)[}]{2}'
        x = token.lexer.lexmatch.group('x')
        ls = token.lexer.lexmatch.group('ls')
        if ls == 'smaller':
            if x == 'xx':
                token.value = 'scriptsize',
            elif x == 'x':
                token.value = 'footnotesize',
            else:
                token.value = 'small',
        elif ls == 'larger':
            if x == 'x':
                token.value = 'Large',
            elif x == 'xx':
                token.value = 'LARGE',
            elif x == 'xxx':
                token.value = 'huge',
            elif x == 'xxxx':
                token.value = 'Huge',
            else:
                token.value = 'large',
        text = token.lexer.lexmatch.group('text'),
        token.value = token.value + text
        return token
        
    def t_UNDERLINED(self, token):
        r'(?:[{]{2}u\||<u>)(?P<word>.*?)(?:[}]{2}|</u>)'
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
        r'[[]{2}w(?:ikt)?:(?:.*?)\|(?P<link>.*?)[]]{2}'
        token.value = token.lexer.lexmatch.group('link')
        return token
    
    # VERY basic matches that have to be checked last.
    def t_ELLIPSES(self, token):
        r'[.]{3,4}'
        return token
    
    def t_CHECKBOX_EMPTY(self, token):
        r'□'
        return token
    
    def t_CHECKBOX_CHECKED(self,token):
        r'▣'
        return token
    
    def t_PUNCT(self, token):
        r"""[!@\#\$\%\^&\*\(\)\-;\+=\[\]\{\}\\\|\:;"',\.\?/~°–—]"""
        return token
    
    def t_WORD(self, token):
        r'[a-zA-Zé]+'
        return token
    
    def t_NUMBER(self, token):
        r'[0-9]+'
        return token
    
    def t_WHITESPACE(self, token):
        r'[\s\t\r\n]+'
        return token
        
#===================================================================================================
# ERROR HANDLING
#===================================================================================================
    def t_ANY_error(self, token):
        token.lexer.skip(1)
        self.logger.info("Illegal character {} at line {}, position {}."
                         .format(token.value[0], token.lineno, token.lexpos))
#===================================================================================================
# MISCELLANEOUS FUNCTIONS
#===================================================================================================
    def __init__(self):
        '''Initiate logging, open a file to store tokens, build the lexer.'''
        self.logger = logging.getLogger("W2L")
        self.lexer = lex.lex(module=self, reflags=re.DOTALL)
    
    def analyze(self, data):
        '''Read through the text file and tokenize.'''
        self.lexer.input(data)
        self.token_list = list()
        while True:
            token = self.lexer.token()
            if not token:
                break      # No more input
            l_token = [token.type, token.value]
            self.token_list.append(l_token)
            print(token)
        return self.token_list