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

import re
from reparse import Reparser
from exceptions import TOCError

class TOC(object):
    def __init__(self):
        self.reparser = Reparser()
        
        self.text = ''          # Raw wikitext
        self.lines = []
        self.levels = dict()
        self.props = ''
        self.latex = ''
        self.is_newpage = False
        self.is_page_list = False
        self.declassified = ("\\begin{spacing}{0.7}\n\\begin{center}\n\\begin{scriptsize}\\textbf" 
        "{Declassified} per Executive Order 13526, Section 3.3\\\\NND Project Number: NND 63316." 
        "By: NWD Date: 2011\n\\vspace{2em}\n\\end{scriptsize}\n\\end{center}\n\\end{spacing}\n")
        
    def append(self, text):
        self.text += text
        
    def begin(self):
        ind = self.text.find("|")
        self.text = self.text[ind:]
        self.lines = self.text.replace('\n','').split("|-")
        if len(self.lines[0]) == 0:
            self.lines.pop(0)
        self.parse()
        self.make_props()
        return self.end()
    
    def end(self):
        latex = ('\\begin{small}\n\\begin{easylist}\n' + self.props + self.latex + 
                 '\\end{easylist}\n\\end{small}')
        return latex
        
    def make_props(self):
        if self.is_page_list:
            page_key = sorted(list(self.levels.keys()))[-1]
            del self.levels[str(page_key)]
        self.props += '\ListProperties(Space=-2.3mm,Space*=-2.3mm,Hang=true,Progressive*=2em,'
        num_levels = len(self.levels)
        for level in range(1,num_levels+1):
            try:
                val = self.levels[str(level)]
            except:
                print(self.levels)
                print(val, level)
                print(self.lines)
            else:
                if re.match(r'[I]', val):
                    self.props += 'Numbers' + str(level) + '=R,'
                    if level > 1:
                        self.props += 'Hide' + str(level) + '=' + str(level-1) + ','
                elif re.match(r'[A]', val):
                    self.props += 'Numbers' + str(level) + '=L,'
                    if level > 1:
                        self.props += 'Hide' + str(level) + '=' + str(level-1) + ','
                elif re.match(r'[1]+', val):
                    if level > 1:
                        self.props += 'Hide' + str(level) + '=' + str(level-1) + ','
                elif re.match(r'[a]', val):
                    self.props += 'Numbers' + str(level) + '=l,'
                    if level > 1:
                        self.props += 'Hide' + str(level) + '=' + str(level-1) + ','
                else:
                    if level > 1:
                        self.props += 'Hide' + str(level) + '=' + str(level) + ','
        self.props = self.props[:-1] + ')\n'
        
    def newpage(self, line):
        self.is_newpage = True
        ind = line.find("---NEWPAGE---")
        list_text = line[:ind]
        return list_text
        
    def parse(self):
        if "Page" in self.lines[0]:
            self.is_page_list = True
        for line in self.lines:
            if len(line) > 0:
                if "---NEWPAGE---" in line:
                    line = self.newpage(line)
                level = 0
                ind = 0
                while line[ind] == "|":
                    level += 1
                    ind += 1
                if str(level) not in self.levels:
                    self.levels[str(level)] = line[ind]
                line = line[ind:]
                r = re.match(r'([A-Za-z0-9]{1,4}\.\s?\|)?(?:colspan="\d"\|)?(?P<text>.*)', line, flags=re.MULTILINE)
                if r != None:
                    line = r.group('text')
                else:
                    raise TOCError
                line = self.reparser.sub(line)
                line = line.replace("{\\textbar}", " ")
                if self.is_page_list:
                    if r'\uline{Page}' in line:
                        self.latex += "\\hfill " + line + "\n"
                    else:
                        line = re.sub('(?P<num>[A-Z]-\d{1,3})', '\\hfill \g<num>', line)
                        self.latex += "@"*level + " " + line + "\n"
                        if self.is_newpage:
                            self.latex += "\\newpage\n"
                            self.latex += self.declassified
                            self.is_newpage = False
                else:
                    self.latex += "@"*level + " " + line + "\n"
                    if self.is_newpage:
                        self.latex += "\\newpage\n"
                        self.latex += self.declassified
                        self.is_newpage = False
        print(self.latex)