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

import codecs, logging, os, pickle, re
from sys import exit
from urllib import parse, request
from collections import OrderedDict
from math import ceil

class Document(object):
    '''This class reads each page (in the main namespace, not the Index pages) and creates an
    ordered dictionary. The keys in this dictionary are the names of the .djvu files, and the values
    are lists of the page numbers each main page uses.'''
    
    def __init__(self):
        # Bare API call, minus the page title
        self.api = "http://en.wikisource.org/w/api.php?format=txt&action=query&titles={0}&prop=revisions&rvprop=content"
        self.prefix = parse.quote("United States – Vietnam Relations, 1945–1967: A Study Prepared by the Department of Defense".encode())
        self.pages = OrderedDict()
        
        self.directory = os.curdir
        self.logger = logging.getLogger("W2L")
        
    def call(self):
        '''Performs the calls to the API and stores the results as numbered text files. This
        function checks if the /raw directory already exists to avoid querying the API multiple
        times. Files are stored in the following format:
        
        /Wikipedia-to-LaTeX        <-- project folder
        +-- /raw                   <-- folder for all raw text files pulled from the API 
        |   +-- /0                 <-- folder for the first main page (in this case, '/Front matter')
        |   |   +-- 0.txt          <-- text from the first API call (in this case, pages 1-7)
        |   |   +-- 1.txt          <-- text from the second API call (in this case, page 11)
        |   +-- /1                 <-- folder for the second main page ('/')
        |   |   +-- 0.txt          <-- text from the first API call (page 9)
        |   |   +-- 1.txt          <-- text from the second API call (page 10)
        |   +-- /2                 <-- folder for the third main page ('/I. Vietnam and the U.S., 1940–1950')
        |   |   +-- 0.txt          <-- text from the first API call (in this case, pages 1-4)
        |   +-- /3                 <-- folder for the fourth main page ('/I. A. U.S. Policy, 1940–50')
        |   |   +-- 0.txt          <-- text from the first API call (pages 5-9)
        |   |   +-- 1.txt          <-- text from the second API call (pages 10-59)
        |   |   +-- 2.txt          <-- text from the third API call (pages 60-73)
        
        ...and so on.
        '''
        
        # Attempt to create /raw folder
        try:
            os.mkdir(self.directory + '/raw')
        except OSError:
            self.logger.exception("Folder /raw already exists.")
            exit("Cannot create file structure.")
          
        pages_count = 0  
        # Iterate through each entry in the self.pages dict to perform the API calls
        for key in self.pages.keys():
            calls = self.form_call()
            os.mkdir(self.directory + '/raw/' + (str(pages_count)))
            call_count = 0
            for call in calls:
                filename = self.directory + '/raw/' + str(pages_count) + "/" + str(call_count) + ".txt"
                with codecs.open(filename, 'w', 'utf-8') as file:
                    text = request.urlopen(call).read().decode('utf-8')
                    file.write(text)
                file.close()
                call_count += 1
            pages_count += 1
            
    def form_call(self):
        '''Form the URLs to pull data from the API. The API supports calls of up to fifty pages
        at a time; if necessary, this will create multiple URLs in case the list of pages is too
        long. Returns a list containing one or more URLs, each of which requests the content of
        1-50 pages.'''
        
        current_page = self.pages.popitem(False)
        self.logger.info("Forming API call for {}.".format(current_page))
        filename = parse.quote(current_page[1].pop(0))
        pages = self.split_calls(current_page[1])

        titles = ""
        api_calls = list()
        for group in pages:
            for number in group:
                titles += "Page:" + filename + "/" + str(number) + "|"
            titles = titles[:-1]
            api_calls.append(self.api.format(titles))
            titles = ""
        return api_calls
        
    def organize(self):
        '''Creates the ordered dictionary containing the filenames and page numbers. If possible,
        it uses a pickled version of this pagelist from a previous run to avoid querying the API
        repeatedly. This is mostly for debugging and will probably be removed in the release.'''
        if not os.path.exists('pagelist.pkl'):
            self.logger.debug("No page list found. Querying API.")
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
                pages_r = re.findall("""<pages\sindex="(.*?)"\sfrom=(\d+)\sto=(\d+)\s\/>""",
                                     current_page)
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
            with open('pagelist.pkl', 'wb') as file:
                try:
                    pickle.dump(self.pages, file)
                except Exception as e:
                    self.logger.exception("Exception occurred when trying to pickle the page list:"
                                          "{}".format(e.strerror))
            file.close()
            
        else:
            self.logger.debug("Page list found. Unpickling.")
            with open('pagelist.pkl', 'rb') as file:
                try:
                    self.pages = pickle.load(file)
                except Exception as e:
                    print ("Error occurred when trying to unpickle the page list: {}"
                           .format(e.strerror))
            file.close()
            
        self.logger.debug("{} main pages organized.".format(len(self.pages)))
        
    def split_calls(self,pagelist):
        '''The API only accepts 50 calls at a time, so this function splits the lists of pages
        into groups of 50 or fewer. Because the API sorts results alphabetically, this
        function also splits page numbers <10 or >99 into separate groups to preserve order.
        
        Returns a list of lists of page numbers. Each list of page numbers contains fewer than
        50 pages, and page numbers <10 or >99 get their own list.'''
        splitlist = list()
        low_index, high_index = None, None

        # Find the index of the first number >=10
        for idx,page in enumerate(pagelist):
            if int(page) >= 10:
                low_index = idx
                break
            
        # Find the index of the first number >=100
        for idx,page in enumerate(pagelist):
            if int(page) >= 100:
                high_index = idx
                break
        
        # Split page numbers <10   
        if low_index == None:
            splitlist.append(pagelist)
            return splitlist # The list has no page numbers >=10
        elif low_index > 0:
            splitlist.append(pagelist[:low_index])
            
        # Split page numbers that are >=10 and <100
        if high_index == None:
            top = len(pagelist)
        else:
            top = high_index
            
        number = top-low_index # Number of items in the list containing numbers 10-99
        list_count = ceil(number/50) # Number of sublists needed for this
        first_index = low_index # First index to include in the next list
        for i in range(list_count):
            sublist = list()
            if i == list_count-1:
                page_range = top - first_index
            else:
                page_range = 50
            for j in range(page_range):
                sublist.append(pagelist[first_index+j])
            first_index = first_index + page_range # Update first_index with new index
            splitlist.append(sublist)
            del sublist
        
        # Split page numbers that are >=100        
        if high_index != None:
            number = len(pagelist) - high_index # Number of items containing numbers >=100
            list_count = ceil(number/50) # Number of sublists needed for this
            for i in range(list_count):
                sublist = list()
                if i == list_count-1:
                    page_range = len(pagelist) - first_index
                else:
                    page_range = 50
                for j in range(page_range):
                    sublist.append(pagelist[first_index+j])
                first_index = first_index + page_range
                splitlist.append(sublist)
                del sublist
                
        return splitlist