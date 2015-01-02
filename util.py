# -*- coding: utf-8 -*-
# Copyright (c) 2013–2015Molly White
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

def findall(string, substring, start_ind=0, end_ind=None):
    indexes = []
    if not end_ind:
        end_ind = len(string)
    while True:
        i = string.find(substring, start_ind, end_ind)
        if i != -1:
            indexes.append(i)
            start_ind = i+2
        else:
            break
    return indexes

class ProgressChecker(object):
    '''
    0: Without text
    1: Not proofread
    2: Problematic
    3: Proofread
    4: Validated
    '''
    def __init__(self):
        self.status = [0]*5
    
    def get_statistics(self):
        num_pages = sum(self.status)
        print("Number of pages parsed: " + str(num_pages))
        print("Pages without text: " + str(self.status[0]) + " (" + str(round((100*self.status[0]/num_pages), 2)) + "%)")
        print("Pages that have not been proofread: " + str(self.status[1]) + " (" + str(round((100*self.status[1]/num_pages), 2)) + "%)")
        print("Problematic pages: " + str(self.status[2]) + " (" + str(round((100*self.status[2]/num_pages), 2)) + "%)")
        print("Proofread pages: " + str(self.status[3]) + " (" + str(round((100*self.status[3]/num_pages), 2)) + "%)")
        print("Validated pages: " + str(self.status[4]) + " (" + str(round((100*self.status[4]/num_pages), 2)) + "%)")
    
    def page(self, level):
        index = int(level)
        self.status[index] += 1