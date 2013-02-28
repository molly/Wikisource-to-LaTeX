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

__all__ = ['Parser']

import codecs, logging, os
import ply.lex as lex

logger = logging.getLogger("W2L")
tokens = (
          'WLINK', # For links to Wikipedia, Wiktionary, etc.
          'WORD',
          'SPACE',
          )
t_WLINK = r'[[]{2}w(?:ikt)?:(?:.*?)[]]{2}'
t_WORD = r'[<>a-zA-Z]+'
t_SPACE = r'[\s\t\r\n]'

def t_error(token):
    print ("Illegal character {}".format(token.value[0]))
    token.lexer.skip(1)

with codecs.open(os.curdir+'/text/3/0.txt', 'r', 'utf-8') as original:
    test_data = original.read()
original.close()

lexer = lex.lex()
lexer.input(test_data)
while True:
    token = lexer.token()
    if not token:
        break      # No more input
    print(token)