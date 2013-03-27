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

class W2LError(Exception):
    '''Base exception class.'''
    
class APIError(W2LError):
    '''An error occurred during the API query process.'''
    
class NoPagesReturned(APIError):
    '''The query to the Wikimedia API returned 0 main pages. The query may have been formatted
    incorrectly.'''
    
class PickleEmpty(APIError):
    '''The pickle file containing the list of pages is empty. Delete the file, then re-run the
    program.'''

class ParseError(W2LError):
    '''There was an error while parsing the document.'''

class TOCError(ParseError):
    '''The parser has encountered an incorrectly-formatted outline or table of contents.'''