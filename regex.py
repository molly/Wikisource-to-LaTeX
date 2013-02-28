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
import codecs, logging, os, re

class Parser(object):
    def __init__(self):
        self.patterns = dict()
        self.logger = logging.getLogger("W2L")
        
    def build_dict(self):
        #self.patterns['[[]{2}w(?:ikt)?:(?:.*?)\|(.*?)[]]{2}']='\1'
        self.patterns = {
                         'e' : 'MEOW',
                         }
        
    def test(self):
        self.logger.debug("Copying to test text file.")
        pattern = re.compile('|'.join(self.patterns.keys()))
#        with codecs.open(os.curdir+'/text/3/0.txt', 'r', 'utf-8') as original:
#            original_text = original.read()
#            with codecs.open(os.curdir+'/test.txt', 'w', 'utf-8') as new:
#                parsed_text = pattern.sub(lambda m: self.patterns[m.group(0)], original_text)
#                new.write(parsed_text)
#        parsed = pattern.sub(lambda m: self.patterns[m.group(0)], 'this is the best policy if')
        m = re.sub('b(.)st', '\1', 'this is the best policy if')
        print(m)