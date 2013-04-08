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

import logging, re, wikitable, util
from reparse import Reparser
from toc import TOC

class Parser(object):
    def __init__(self, progress):
        self.logger = logging.getLogger("W2L")
        self.output = None
        self.reparser = Reparser()
        self.indented = False
        self.progress = progress
    
    def begin(self, outputfile):
        self.output = outputfile
        
    def dispatch(self, t_list):
        for token in t_list:
            self.value = token[1]
            if self.value:
                command = 'self.{0}()'.format(token[0].lower())
                try:
                    exec(command)
                except:
                    self.logger.exception("Unable to run command " + command);
                    break;
                else:
                    self.write(self.value)
                    
    def end_matter(self, contributors, outputfile):
        #TODO: Will need to add image attribution, when I get to including images.
        self.output = outputfile
        self.logger.debug("Appending license information.")
        
        for contributor in contributors:
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', contributor):
                contributors.remove(contributor)
                anonymous = True
        if anonymous:
            contributors.append("anonymous users")
        
        begin = ("\n\\newpage\n\\rule{\\textwidth}{1px}\nContent available online at " + 
                 "http://en.wikisource.org/wiki/Pentagon\_Papers.\n")
        license = ("\\section*{License} \\\\\nCreative Commons Attribution-Share Alike 3.0 " +
                   "Unported.\\\\\nhttp://creativecommons.org/licenses/by-sa/3.0/\n")
        contribs = ("\\section*{Contributors}\n" + ", ".join(contributors) + ".")
        
        self.output.write(begin + license + contribs)
                    
    def write(self, text):
        if type(text) is str:
            self.output.write(text)
        
#===================================================================================================
# PARSING FUNCTIONS
#===================================================================================================
    # TABLE FUNCTIONS        
    def table(self):
        #TODO: TABLE
        pass
    
    def e_table(self):
        #TODO: E_TABLE
        pass
    
    def trow(self):
        #TODO: TROW
        pass
    
    def e_trow(self):
        #TODO: E_TROW
        pass
    
    def titem(self):
        #TODO: TITEM
        pass
    
    def e_titem(self):
        #TODO: E_TITEM
        pass
    
    def tnoinclude(self):
        #TODO: TNOINCLUDE
        pass
    
    def te_noinclude(self):
        #TODO: TE_NOINCLUDE
        pass
    
    def tolist(self):
        #TODO: TOLIST
        pass
    
    def te_olist(self):
        #TODO: TE_OLIST
        pass
    
    def tlitem(self):
        #TODO: TLITEM
        pass
    
    def te_litem(self):
        #TODO: TE_LITEM
        pass
    
    def tforced_whitespace(self):
        #TODO: TFORCED_WHITESPACE
        pass
    
    # PRE-WIKITABLE FUNCTIONS
    def taskforce(self):
        '''Shamelessly hardcoding this in. It's not worth trying to dynamically generate tikz.'''
        self.value = ('\\vspace{10cm}\n\\begin{tabularx}{0.9\\textwidth}{ p{0.25\\textwidth}' +
                      ' >{\\centering\\arraybackslash}p{0.4\\textwidth} p{0.25\\textwidth} }\n' +
                      '\\begin{tikzpicture}\\draw (-.5,0) --(2.5,0);\\draw[ultra thick](-1,.2) ' +
                      '--(2.5,.2);\\draw (-.5,.4) --(2.5,.4);\\end{tikzpicture} & \\Large{' + 
                      'VIETNAM TASK FORCE} & \\begin{tikzpicture}\\draw (-1,0) --(2,0);\\draw' + 
                      '[ultra thick](-1,.2) --(2.5,.2);\\draw (-1,.4) --(2,.4);\\end{tikzpicture}' +
                      '\n\end{tabularx}')

        
    def ts(self):
        '''For the {{ts}} template. This is infrequently used, so I have not generalized it much.'''
        text = self.reparser.sub(self.value[1])
        self.value = ('\\setlength{\\fboxrule}{' + self.value[0] + 'px}\n\\begin{center}\n\\fbox{' 
                      + text + '}\n\\end{center}\n\\setlength{\\fboxrule}{1pt}\n')
        
    def toc(self):
        self.contents = TOC()
        self.value = ''
        
    def newpage(self):
        self.contents.append('---NEWPAGE---')
        self.value = ''
        
    def e_toc(self):
        self.value = self.contents.begin()
        del self.contents
        self.contents = TOC()
        
    def toc_text(self):
        self.contents.append(self.value)
        self.value = ''
    
    # WIKITABLE FUNCTIONS
    def wikitable(self):
        self.table = wikitable.Table()
        if self.value[1]:
            self.table.format['alignment'] = 'center'
        self.value = ''
    
    def e_wikitable(self):
        self.value = self.table.end()
        del self.table
        
    def tcell(self):
        self.cell = wikitable.Cell(self.table)
        self.value = ''
        
    def e_tcell(self):
        self.value = self.cell.end() # Get the final text of the cell
        self.table.append_cell(self.value) # Add the cell to the table
        self.cell.reset() # Reset cell values for next time
        self.value = ''
        
    def format(self):
        # TODO: Add cellpadding/cellspacing?
        if self.value[0]:                               # Table width
            self.table.set_width(self.value[0])
        if self.value[1]:                               # Text alignment
            self.table.set_alignment(self.value[1])
        if self.value[2]:                               # Border
            self.table.format['border'] = True
            self.table.t['hline'] = '\\hline\n'
        self.value = ''

    def wt_colspan(self):
        self.cell.c_format['colspan'] = self.value
        self.table.format['multicol'] = True
        self.value = ''
        
    def wt_style(self):
        self.cell.cell_style(self.value, self.row_center)
        self.value = ''
                
    def newrow(self):
        if 'align="center"' in self.value:
            self.row_center = True
        else:
            self.row_center = False
        self.table.append_row()
        self.value = ''
    
    def wt_file(self):
        # TODO: FILES
        self.cell.append(' FILE HERE ')
        self.value = ''
        
    def cell_contents(self):
        self.cell.append(self.value)
        self.value = ''
        
    # PRE-HTML TOKENS
    def internallink(self):
        #TODO: INTERNAL LINK
        self.value = self.reparser.sub(self.value[2])
    
    def pagequality(self):
        self.progress.page(self.value)
        if self.output.tell() != 0:
            self.value = "\n\\newpage\n"
        else:
            self.value = ""
    
    def declassified(self):
        self.value = ("\\begin{spacing}{0.7}\n\\begin{center}\n\\begin{scriptsize}\\textbf" 
        "{Declassified} per Executive Order 13526, Section 3.3\\\\NND Project Number: NND 63316. " 
        "By: NWD Date: 2011\n\\end{scriptsize}\n\\end{center}\n\\end{spacing}\n")
    
    def secret(self):
        self.value = ('\\begin{center}\n\\small{\\uline{TOP SECRET – Sensitive}}\n\\end{center}'
                      '\n\\vspace{1em}\n')
        
    def runhead(self):
        '''We have to call in the big guns for these ones.'''
        self.value = self.reparser.running_header(self.value)
    
    # HTML TOKENS
    def olist(self):
        '''Begin ordered list.'''
        self.value = '\\begin{enumerate}\n'
    
    def e_olist(self):
        '''End ordered list.'''
        self.value = '\\end{enumerate}'
    
    def litem(self):
        '''Format list item.'''
        self.value = "\item "
        
    def e_litem(self):
        '''End line'''
        self.value = "\n"
        
    def noinclude(self):
        #TODO: NOINCLUDE
        self.value = ""
        pass
    
    def e_noinclude(self):
        #TODO: E_NOINCLUDE
        self.value = ""
        pass
    
    def reflist(self):
        #TODO: REFLIST
        pass
    
    def ref(self):
        #TODO: REF
        pass
    
    def e_ref(self):
        #TODO: E_REF
        pass
    
    def forced_whitespace(self):
        '''Add whitespace.'''
        try: 
            self.output.seek(-1, 1)
            preceding = self.output.read(1)
            if preceding != "\n":
                self.value = '\\\\\n'
            else:
                self.value = ''
        except:
            pass
    
    # CENTERED TOKENS
    def centered(self):
        '''Begin centered text.'''
        # TODO: Check that there is a '\\' before and after centered text
        self.bc = True if self.value[1] else False
        self.value = "\\begin{center}\n"
        if self.bc:
            self.value += "\\begin{minipage}{.5\\textwidth}\n"
    
    def e_centered(self):
        '''End centered text.'''
        self.output.seek(-1, 1)
        preceding = self.output.read(1)
        if preceding != "\n":
            self.value = "\n"
        else:
            self.value = ""
        if self.bc:
            self.value += "\\end{minipage}\n"
        self.value += "\\end{center}\n\n"
            
    def c_right(self):
        self.value = self.reparser.traverse(self.value)
            
    def a_underlined(self):
        self.underlined()
            
    def left(self):
        self.value = self.reparser.left(self.value)
          
    def right(self):
        '''Begin right-aligned text.'''
        # TODO: Check that there is a '\\' before and after centered text
        self.value = "\\begin{flushright}\n"
    
    def e_right(self):
        '''End centered text.'''
        self.output.seek(-1, 1)
        preceding = self.output.read(1)
        if preceding == "\n":
            self.value = "\\end{flushright}\n"
        else:
            self.value = "\n\\end{flushright}\n"  
    
    
    # POST-HTML TOKENS
    def pspace(self):
        '''Replace {{nop}} with \\.'''
        try: 
            self.output.seek(-1, 1)
            preceding = self.output.read(1)
            if preceding != "\n" and preceding != "}":
                self.value = '\\\\\n'
            else:
                self.value = ''
        except:
            pass
        
    def cindent(self):
        self.indent()
    
    def indent(self):
        self.indented = True
        coeff = self.value.count(":")
        indent_width = 2 * coeff
        self.value = "\\begin{blockquote}{" + str(indent_width) + "em}\n"
    
    def pagenum(self):
        # TODO: PAGE NUMBER
        pass
    
    def pent(self):
        # TODO: NOTE
        pass
    
    def popup(self):
        self.value = self.reparser.sub(self.value)
        
    def size(self):
        '''Adjust the size of the text.'''
        self.value = ("\\begin{" + self.value[0] + "}\n" + self.reparser.sub(self.value[1]) +
                      " \\\\\n\\end{" + self.value[0] + "}\n")
        pass
        
    def underlined(self):
        '''Replace underlined text with italicized text.'''
        self.value = "\\uline{" + self.reparser.sub(self.value) + "}"
        
    def bolded(self):
        '''Bold text.'''
        self.value = "\\textbf{" + self.reparser.sub(self.value) + "}"
    
    def italicized(self):
        '''Italicize text.'''
        self.value = "\\textit{" + self.reparser.sub(self.value) + "}"
        
    def wlink(self):
        '''Print only the display text of the wikilink.'''
        pass
    
    def rule(self):
        '''Horizontal rule.'''
        if self.value[1]:
            self.value = ("\n\\rule{\\textwidth}{" + self.value[1] + "px} \\\\\n\n")
        else:
            self.value = "\\rule{\\textwidth}{1px} \\\\\n\n"
        
    def file(self):
        # TODO: FILES
        self.value = " FILE HERE "
        
    def gap(self):
        self.value = "\\hspace*{" + self.value + "}"
        
    def image_removed(self):
        self.value = ("\\vfill\n\\framebox[\\textwidth][c]{%\n\\parbox{0.9\\textwidth}{%\n\\vspace{15em}\n\\center{\\large{" 
                      + "A non-free image has been removed from this page.}}\n\\par\n\\bigskip\n" +
                      self.value[0] + "\n\\par\n\\bigskip\nThe removed content can be viewed in " +
                      "the original document \\href{" + self.value[1] + "}{here} (PDF).\n\\vspace{15em}}}\n\\vfill\n")
        
    def hi(self):
        # TODO: Implement hi instead of just passing along the text
        self.value = self.reparser.sub(self.value)
    
    # BASIC TOKENS
    def ellipses(self):
        '''Convert to proper ellipsis formatting.'''
        if self.value == "...":
            self.value = "{\\ldots}"
        else:
            self.value = "{\\ldots}."
            
    def checkbox_empty(self):
        self.value = "\\Square~"
    
    def checkbox_checked(self):
        self.value = "\\CheckedBox~"
        pass
    
    def punct(self):
        # TODO: Figure out `` and " for quotes
        '''Write punctuation to file, escaping any characters with special functions in LaTeX.'''
        escape = ["#", "$", "%", "&", "_", "\\"]
        if self.value in escape: # Precede the punctuation with a backslash
            self.value = "\\" + self.value
        elif self.value == "°": # Replace degree symbol
            self.value = "{\\degree}"
        elif self.value == "–": # Replace en dash
            self.value = "--"
        elif self.value == "—": # Replace em dash
            self.value = "---"
        elif self.value == "|": # Replace pipe
            self.value = "{\\textbar}"
        elif self.value == "}":
            self.value = ""
        elif self.value == "{":
            self.value = ""
        elif self.value == "✓":
            self.value = "{\\checked}"
    
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
            if self.indented:
                self.value = "\n\\end{blockquote}\n"
                self.indented = False
            else:
                try: 
                    self.output.seek(-1, 1)
                    preceding = self.output.read(1)
                    if preceding != "\n":
                        if self.value == '\n\n' or self.value==' \n\n':
                            self.value = '\n\n'
                        else:
                            self.value = '\\\\\n'
                    else:
                        self.value = ''
                except:
                    pass
        else:
            self.value = ' '