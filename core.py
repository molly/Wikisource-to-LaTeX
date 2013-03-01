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

import codecs, logging, os, lex
from api import Document
from tokenizer import Tokenizer

def setup_logging():
    logger=logging.getLogger("W2L")
    logger.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s"
                                          ": %(message)s", datefmt="%I:%M:%S %p")
    consolehandler = logging.StreamHandler() 
    consolehandler.setFormatter(console_formatter)
    logger.addHandler(consolehandler)
    return logger

if __name__ == "__main__":
    logger = setup_logging()
    doc = Document()
    doc.organize()
    if not os.path.exists(os.curdir + '/raw'):
        logger.debug("Getting raw text files.")
        doc.call()
    if not os.path.exists(os.curdir + '/text'):
        logger.debug("Parsing JSON to TXT.")
        doc.json_to_text()
        
    # Open and read test file
    with codecs.open(os.curdir+'/text/3/1.txt', 'r', 'utf-8') as original:
        test_data = original.read()
    original.close()

    # Begin!
    lexer = Tokenizer()
    lexer.build()
    lexer.analyze(test_data)