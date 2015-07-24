# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'
import re

def balancedSlicer(text, openDelim='[', closeDelim=']'):
    """
    Assuming that text contains a properly balanced expression using
    :param openDelim: as opening delimiters and
    :param closeDelim: as closing delimiters.
    :return: text between the delimiters
    """
    openbr = 0
    cur = 0
    for char in text:
        cur +=1
        if char == openDelim:
            openbr += 1
        if char == closeDelim:
            openbr -= 1
        if openbr == 0:
            break
    return text[:cur], cur

#From https://github.com/bwbaugh/wikipedia-extractor

def findBalanced(text, openDelim='[', closeDelim=']'):
    """
    Assuming that text contains a properly balanced expression using
    :param openDelim: as opening delimiters and
    :param closeDelim: as closing delimiters.
    :return: an iterator producing pairs (start, end) of start and end
    positions in text containing a balanced expression.
    """
    openPat = '|'.join([re.escape(x) for x in openDelim])
    # pattern for delimiters expected after each opening delimiter
    afterPat = {o: re.compile(openPat+'|'+c, re.DOTALL) for o,c in zip(openDelim, closeDelim)}
    stack = []
    start = 0
    cur = 0
    end = len(text)
    startSet = False
    startPat = re.compile(openPat)
    nextPat = startPat
    while True:
        next = nextPat.search(text, cur)
        if not next:
            return
        if not startSet:
            start = next.start()
            startSet = True
        delim = next.group(0)
        if delim in openDelim:
            stack.append(delim)
            nextPat = afterPat[delim]
        else:
            opening = stack.pop()
            # assert opening == openDelim[closeDelim.index(next.group(0))]
            if stack:
                nextPat = afterPat[stack[-1]]
            else:
                yield start, next.end()
                nextPat = startPat
                start = next.end()
                startSet = False
        cur = next.end()


if __name__ == '__main__':
    with open("armeenia.txt", encoding='utf-8') as f:
        text = f.read()

        spans = findBalanced(text)
        for start, end in spans:
            link = text[start:end]
            print(link)

def linkGetter(sectionObj):
    """
    takes sectionobj
    adds links:
    :return:
    """