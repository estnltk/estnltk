# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Andres'
import re
from .internalLink import urlBegin, findBalanced, addIntLinks
from .externalLink import addExternalLinks, ExtLinkBracketedRegex
from .wikiextra import balancedSlicer
from .cleaner import dropSpans

imageRegEx = re.compile(r'\[\[(Pilt|File|Image)\:.+?\]\]', re.IGNORECASE)

def imageParser(sectionObj):
    """return a sectionObj with image data added
         [
       {
             image_url = "http://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/R%C3%B5uge_Suurj%C3%A4rv_2011_10.jpg/1024px-R%C3%B5uge_Suurj%C3%A4rv_2011_10.jpg"
             text: "Rõuge Suurjärv on Eesti sügavaim järv (38 m)."
             links: [ ...] // sama loogika nagu sektsiooni tasemel lingid.
             links: [ ...] // sama loogika nagu sektsiooni tasemel lingid.
       }
   ]"""
    text = ''
    lastEnd = 0
    ends = []
    text = sectionObj['text']
    imageStarts = [x.start() for x in imageRegEx.finditer(text)]
    if imageStarts:
        images =  []
        for start in imageStarts:

            imgText, end = balancedSlicer(text[start:])
            end = start + end
            ends.append(end)

            #imgText = image.group(0).replace('[[', '').replace(']]', '')
            img =  {'text':imgText}
            imgText = imgText.split('|')

            #t= imgText[-1].replace(']]', '')
            t = imgText[-1][:-2]
            url = urlBegin + imgText[0].replace(' ', '_').replace('[[', '')
            img['text'] = t
            img['url'] = url

            if ExtLinkBracketedRegex.search(t):
                img = addExternalLinks(img)

            intlinks = [x for x in findBalanced(t, openDelim='[[', closeDelim=']]')]

            if intlinks:
                img = addIntLinks(img)

            images.append(img)


        sectionObj['images'] = images
        spans = []
        for i, j in zip(imageStarts, ends):
            spans.append((i, j))

        sectionObj['text'] = dropSpans(spans, text)
    return sectionObj


if __name__ == '__main__':
    pass
