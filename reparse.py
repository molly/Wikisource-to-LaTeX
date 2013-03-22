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

class Reparser(object):
    def __init__(self):
        pass
    
    def left(self, text):
        offset = None
        o = re.search('\|offset=(?P<o>\d)em', text)
        if o:
            offset = o.group('o')
            ind = text.find('|offset')
            text=text[:ind]
            text = self.sub(text)
            text = "\\hspace*{" + offset + "em}" + text + " \\\\\n"
        return text
    
    def running_header(self, text):
        '''Parse out the insides of a {{rh}} template into a LaTeX table.'''
        # Remove {{rh and closing }}
        text = text[4:-2]
        # Find indexes of left, right, and center
        breaks = [text.find("|left=") if text.find("|left=") != -1 else None, text.find("|center=")
                  if text.find("|center=") != -1 else None, text.find("|right=") if
                  text.find("|right=") != -1 else None]
        # Break the string into list t containing left, right, and center
        t=list()
        if breaks[0] != None:
            if breaks[1]:
                t.append(text[breaks[0]+6:breaks[1]])
            elif breaks[2]:
                t.append(text[breaks[0]+6:breaks[2]])
            else:
                t.append(text[breaks[0]+6:])
        else:
            t.append(None)
        if breaks[1] != None:
            if breaks[2]:
                t.append(text[breaks[1]+8:breaks[2]])
            else:
                t.append(text[breaks[1]+8:])
        else:
            t.append(None)
        if breaks[2] != None:
            t.append(text[breaks[2]+7:])
        else:
            t.append(None)
        for index in range(3):
            if t[index] != None:
                t[index] = self.sub(t[index])
            else:
                t[index] = ' '
        runningheader = '\\hfline{' + t[0] + '}{' + t[1] + '}{' + t[2] + '} \\\\\n'
        return runningheader
    
    def sub(self, text):
        '''Perform common template substitutions'''
        text = re.sub(r'\{{2}larger\|(?P<text>.*?)\}{2}',
                      r'\\begin{large}\g<text>\\end{large}', text)
        text = re.sub(r'\{{2}x\-smaller\|(?P<text>.*?)\}{2}',
                      r'\\begin{footnotesize}\g<text>\\end{footnotesize}', text)
        text = re.sub(r'\{{2}x\-larger\|(?P<text>.*?)\}{2}',
                      r'\\begin{Large}\g<text>\\end{Large}', text)
        text = re.sub(r"'{3}(?P<text>.*?)'{3}", r'\\textbf{\g<text>}', text)
        return text