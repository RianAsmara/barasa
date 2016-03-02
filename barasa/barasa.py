#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Barasa - Indonesian SentiWordNet.
Latest version can be found at https://github.com/neocl/barasa

References:
    Python documentation:
        https://docs.python.org/
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/
    Wordnet Bahasa:
        https://sourceforge.net/p/wn-msa/tab/HEAD/tree/trunk/

@author: David Moeljadi <davidmoeljadi@gmail.com>
'''

# Copyright (c) 2016, David Moeljadi <davidmoeljadi@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "David Moeljadi <davidmoeljadi@gmail.com>"
__copyright__ = "Copyright 2016, barasa"
__credits__ = [ "David Moeljadi" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "David Moeljadi"
__email__ = "<davidmoeljadi@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import argparse
import codecs
from collections import namedtuple
from collections import defaultdict

#-----------------------------------------------------------------------
# CONFIGURATION
#-----------------------------------------------------------------------

BAHASA_WORDNET_FILE = './data/wn-msa-all.tab'
SENTI_WORDNET_FILE  = './data/SentiWordNet_3.0.0_20130122.txt'
BARASA_FILE     = './data/barasa.txt'

#-----------------------------------------------------------------------
# DATA STRUCTURE
#-----------------------------------------------------------------------

SynsetInfo = namedtuple('SynsetInfo', ['synset', 'pos', 'neg'])
LemmaInfo  = namedtuple('LemmaInfo', ['lemma', 'pos', 'neg'])
BarasaInfo = namedtuple('BarasaInfo', ['synset', 'lang', 'goodness', 'lemma', 'pos', 'neg'])

#-----------------------------------------------------------------------
# FUNCTIONS
#-----------------------------------------------------------------------

def read_barasa():
    ''' This function checks the polarity scores of lemmas
    '''
    lemma_list = []
    with codecs.open(BARASA_FILE, encoding='utf-8', mode='r') as barasa_file:
        for line in barasa_file.readlines():
            items = line.strip().split('\t')
            lemma_list.append(items)
        lemma_dict = defaultdict(list)
        for synset, lang, goodness, lemma, pos, neg in lemma_list:
            # [2016-03-02 DM] information extracted from https://sourceforge.net/p/wn-msa/tab/HEAD/tree/trunk/
            # language: B=Indonesian and Malaysian, I=Indonesian, M=Malaysian
            # Goodness: Y=hand checked and good, O=good, M=OK, L=low, X=hand checked and bad
            if (lang=='I' or lang=='B') and (goodness=="Y" or goodness=="O"):
                lemma_dict[lemma].append(BarasaInfo(synset, lang, goodness, lemma, pos, neg))
    return lemma_dict

def gen_barasa():
    ''' This function generates a barasa.txt file with information of polarity scores
    '''
    print("Generating Barasa")

    SYNSET_SCORE = {}
    LEMMA_SCORE = {}

    with codecs.open(SENTI_WORDNET_FILE, encoding='utf-8', mode='r') as SentiWN:
        for line in SentiWN.readlines():
            if line.startswith('#'): # ignore comments
                continue
            # strip off end-of-line, then split
            pos, snum, pscore, nscore, lemma, definition = line.strip().split('\t')
            synset = '%s-%s' % (snum, pos)
            SYNSET_SCORE[synset] = SynsetInfo(synset, pscore, nscore)

    newlines = []
    with codecs.open(BAHASA_WORDNET_FILE, encoding='utf-8', mode='r') as BahasaWN:
        for line in BahasaWN.readlines():
            synset, lang, goodness, lemma = line.strip().split('\t')
            if synset in SYNSET_SCORE:
                sscore = SYNSET_SCORE[synset]
                LEMMA_SCORE[lemma] = LemmaInfo(lemma, sscore.pos, sscore.neg)                
                newline = ("%s\t" * 6) % (synset, lang, goodness, lemma, sscore.pos, sscore.neg)
            newlines.append(newline)

    with codecs.open(BARASA_FILE, encoding='utf-8', mode='w') as barasa_file:
        barasa_file.write('\n'.join(newlines))

#-----------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------

def main():
    '''Main entry of barasa toolkit.
    '''

    # It's easier to create a user-friendly console application by using argparse
    # See reference at the top of this script
    parser = argparse.ArgumentParser(description="Toolkit for creating Barasa.")
    
    # Positional argument(s)
    parser.add_argument('-g', '--gen', help='Generate Barasa', action='store_true')
    # Optional argument(s)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    # Main script
    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()

        if args.gen:
            gen_barasa()
    pass

if __name__ == "__main__":
    main()
