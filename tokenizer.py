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

import codecs, logging, re, os
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
            # Tokens that must come before the wikitable state
              'TS', # For the {{ts}} template (infrequently used in this document)
              'TASKFORCE', # For the "VIETNAM TASK FORCE" logo on the front covers
              'TOC', # Table of contents
              'NEWPAGE', # Start of TOC on a new page
              'E_TOC', # End table of contents
              'TOC_TEXT', # Everything between TOC and E_TOC
            # Wikitable state
              'WIKITABLE', # Beginning of table {|
              'E_WIKITABLE', # End of table |}
              'FORMAT', # Initial {| style="..."
              'NEWROW', # |-
              'TCELL', # Beginning of table cell
              'WT_COLSPAN', # Number of columns for a cell to span
              'WT_STYLE',
              'E_TCELL', # End of table cell
              'WT_FILE', # For files in wikitables
              'CELL_CONTENTS', # Everything within a table cell
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
              # Aligned state
              'CENTERED', # {{center|...}} or {{c|...}}
              'E_CENTERED', # End of centered state
              'A_UNDERLINED', # Underlined text in aligned state
              'LEFT', # Left-aligned text
              'RIGHT', # Right-aligned text
              'E_RIGHT', # End of right aligned state
              # General tokens
              'PSPACE', # {{nop}}
              'CINDENT', # Continued indent from prev page <noinclude>:</noinclude>
              'INDENT', # Line preceded by one or more :'s
              'PAGENUM', # Taken from running header
              'PENT', # {{Pent|I. A.|1}}
              'POPUP', # {{popup note|...|...}}
              'SIZE', # Size templates, such as {{x-larger}}
              'UNDERLINED', # {{u|...}}
              'BOLDED', # '''...'''
              'ITALICIZED', # ''...''
              'WLINK', # For links to Wikipedia, Wiktionary, etc.
              'RULE', # For horizontal rules
              'FILE', # [[File:...]]
              'GAP', # {{gap|...}}
              'IMAGE_REMOVED', # {{image removed}}
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
              ('centered', 'inclusive'),
              ('right', 'inclusive'),
              ('contents', 'exclusive')
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
    
    # Has to come before wikitable state
    def t_TS(self, token):
        r'\{\|\{{2}ts\|(?:.*?)\|(?:border\:(?P<border>\d)px\ssolid\sblack;)\}{2}(?:.*?)\n\|(?P<text>.*?)\n\|\}'
        token.value = token.lexer.lexmatch.group('border', 'text')
        return token
    
    def t_TASKFORCE(self, token):
        r'(?P<group>\{\|)\salign=center\n\|\{{2}rule\|4em(.*?)\|\}'
        token.value = token.lexer.lexmatch.group('group')
        return token
    
    def t_TOC(self, token):
        r'(?<!<noinclude>)\{\|(?=(?:.*?)\n(?:\|-?\s?\n)*?\|([A-Za-z0-9]\.))'
        token.lexer.begin('contents')
        return token
    
    def t_contents_NEWPAGE(self, token):
        r'<noinclude>\s?\|\}\s?</noinclude>'
        return token
    
    def t_contents_E_TOC(self, token):
        r'(?<!<noinclude>)\|\}'
        token.lexer.begin('INITIAL')
        return token
    
    def t_contents_TOC_TEXT(self, token):
        r'(?:.|\n)'
        return token
    
    # Wikitable state
    def t_WIKITABLE(self, token):
        r'(?P<table>\{\|)\s?(?P<center>align=center)?'
        token.lexer.begin('wikitable')
        token.value = token.lexer.lexmatch.group('table', 'center')
        return token
    
    def t_wikitable_E_WIKITABLE(self, token):
        r'\|\}'
        token.lexer.begin('INITIAL')
        return token
    
    def t_wikitable_FORMAT(self, token):
        # TODO: This regex will need to become much more complex as more instances are found
        r'(?:\s?style\=")(?:\s?width\:\s?(?P<width>\d{1,3})%;?\s?)?(?:text\-align\:\s?(?P<textalign>center);?\s?)?(?:")(?:\s?border="(?P<border>\d)"\s?)?(?:\s?cellpadding="(?P<cellpadding>\d)"\s?)?(?:\s?cellspacing="(?P<cellspacing>\d)"\s?)?'
        token.value = (token.lexer.lexmatch.group('width', 'textalign',
                                                  'border', 'cellpadding', 'cellspacing'))
        return token
    
    def t_wikitable_TCELL(self, token):
        r'\|{1,2}'
        token.lexer.begin('tcell')
        return token
    
    def t_tcell_WT_COLSPAN(self, token):
        r'(?:colspan="(?P<colspan>\d)"\|?)'
        token.value = token.lexer.lexmatch.group('colspan')
        return token
    
    def t_tcell_WT_STYLE(self, token):
        r'style="(?P<style>.*?)"'
        token.value = token.lexer.lexmatch.group('style')
        return token
    
    def t_tcell_E_TCELL(self, token):
        r'\s?(?=\s?\|{2}|\n)'
        token.lexer.begin('wikitable')
        token.value = 'endcell'
        return token
    
    def t_wikitable_NEWROW(self, token):
        r'(?P<newrow>\n?\|\-(.*?)\n)'
        return token
    
    def t_tcell_WT_FILE(self, token):
        r'\[{2}File\:(.*?)\]{2}'
        return token
    
    def t_tcell_CELL_CONTENTS(self, token):
        r'(.+?)'
        return token
    
    # Tokens to be checked before HTML state
    def t_FILE(self, token):
        r'\[{2}File\:(.*?)\]{2}'
        return token  
    
    def t_INTERNALLINK(self, token):
        r'[[]{2}United\sStates(?:.*?)Defense/(?P<subpage>.*?)(?:\#(?P<anchor>.*?))?\|(?P<title>.*?)[]]{2}'
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
        r'(\{{2}rh(?:(?:\{{2}.*?\}{2})|(?:[^\{])*?)+\}{2})'
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
    
    # ALIGNED STATE
    def t_CENTERED(self, token):
        r'(?P<center>[{]{2})(?P<block>block\s)?c(?:enter)?\|'
        token.value = token.lexer.lexmatch.group('center', 'block')
        token.lexer.begin('centered')
        return token
    
    def t_centered_E_CENTERED(self, token):
        r'[}]{2}'
        token.lexer.begin('INITIAL')
        return token
    
    def t_centered_right_A_UNDERLINED(self, token):
        r'<u>(?P<text>.*?)</u>'
        token.value = token.lexer.lexmatch.group('text')
        return token
    
    def t_LEFT(self, token):
        r'[{]{2}left\|(?P<text>(?:(?:\{{2}.*?\}{2})|(?:[^\{])*?)+)\}{2}'
        token.value = token.lexer.lexmatch.group('text')
        return token
    
    def t_RIGHT(self, token):
        r'[{]{2}(?:block\s)?right\|\d?=?'
        token.lexer.begin('right')
        return token
    
    def t_right_E_RIGHT(self, token):
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
    
    def t_POPUP(self, token):
        r'[{]{2}popup\snote\|(.*?)\|\d?=?(?P<text>.*?)[}]{2}'
        token.value = token.lexer.lexmatch.group('text')
        return token
    
    def t_SIZE(self, token):
        r'[{]{2}(?:(?P<x>[x]{1,4})\-)?(?P<ls>larger|smaller)\|(?P<text>(?:(?:\{{2}.*?\}{2})|(?:[^\{])*?)+)[}]{2}'
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
        r'[[]{2}(?:(?:.*?)\|)?(?P<link>.*?)[]]{2}'
        token.value = token.lexer.lexmatch.group('link')
        return token
    
    def t_RULE(self, token):
        r'[{]{2}(?P<rule>rule)(?:\|height=(?P<height>\d{1,3})px)?[}]{2}'
        token.value = token.lexer.lexmatch.group('rule','height')
        return token
    
    def t_GAP(self, token):
        r'\{{2}gap\|(?P<width>.*?)\}{2}'
        token.value = token.lexer.lexmatch.group('width')
        return token
    
    def t_IMAGE_REMOVED(self, token):
        r'\{{2}Image\sremoved\|(?P<descrip>.*?)(?:\|url=\{{2}PDF\|\[(?P<url>.*?)\shere\]\}{2})?\}{2}'
        token.value = token.lexer.lexmatch.group('descrip', 'url')
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
        r"""[!@\#\$\%\^&\*\(\)\-;\+=\[\]\{\}\\\|\:;"',\.\?~°–—✓/]"""
        return token
    
    def t_WORD(self, token):
        r'[a-zA-Zéâ]+'
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
        with codecs.open(os.curdir + '/tokenout.txt', 'w+', 'utf-8') as tokenfile:
            while True:
                token = self.lexer.token()
                if not token:
                    break      # No more input
                l_token = [token.type, token.value]
                self.token_list.append(l_token)
                tokenfile.write(str(token) + '\n')
        return self.token_list