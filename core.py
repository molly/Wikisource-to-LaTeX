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
import pickle
from os import path
from urllib import parse, request
from collections import OrderedDict

class Document(object):
    '''This class reads each page (in the main namespace, not the Index pages) and creates an
    ordered dictionary. The keys in this dictionary are the names of the .djvu files, and the values
    are lists of the page numbers each main page uses.'''
    
    def __init__(self):
        # Bare API call, minus the page title
        self.api = "http://en.wikisource.org/w/api.php?format=txt&action=query&titles={0}&prop=revisions&rvprop=content"
        self.prefix = parse.quote("United States – Vietnam Relations, 1945–1967: A Study Prepared by the Department of Defense".encode())
        self.pages = OrderedDict()
        
    def organize(self):
        '''Creates the ordered dictionary containing the filenames and page numbers.'''
        if not path.exists('pagelist.pkl'):
            current_url = "/Front matter".encode()
            while current_url != "":
                current_url = parse.quote(current_url)
                
                # Account for relative links
                if current_url[0] == "/":
                    current_url = self.prefix + current_url
                
                # Create API request    
                current_url = self.api.format(current_url)
                
                # Get the text of the request
                current_page = request.urlopen(current_url).read().decode('utf-8')
                
                # Search for the link to the next page in the document
                next_r = re.search("\|\snext\s*=\s?[[]{2}(.*?)[]]{2}", current_page)
                if next_r:
                    next_url = next_r.group(1).encode()
                else:
                    next_url = ""
                    
                # Get the nicely-formatted page title    
                title_r = re.search("\[title\]\s=>\s(.*?)\n", current_page)
                if title_r:
                    title = title_r.group(1)     
                    
                # Find each pages index tag and collect the page numbers for each
                pages_r = re.findall("""<pages\sindex="(.*?)"\sfrom=(\d+)\sto=(\d+)\s\/>""", current_page)
                if pages_r and title:
                    index = pages_r[0][0]
                    if title not in self.pages:
                        self.pages[title] = [index]
                    for page in pages_r:
                        page1 = int(page[1])
                        page2 = int(page[2])
                        if page1 == page2:
                            self.pages[title].append(page1)
                        else:
                            self.pages[title].extend(list(range(page1, page2+1)))
                
                title = None
                current_url = next_url
            
            # Saves to a text file to avoid having to query the API many times
            file = open('pagelist.pkl', 'wb')
            try:
                pickle.dump(self.pages, file)
            except:
                print("Error occurred when trying to pickle the page list.")
            file.close()
            
if __name__ == "__main__":
    doc = Document()
    doc.organize()