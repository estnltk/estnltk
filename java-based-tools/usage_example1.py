# -*- coding: utf-8 -*-
#
#    Usage example on how to initialize and use Java-based program - Clause segmenter 
#  (Osalausestaja) - with Python and java-bridge.
#
#   NB! Tool configuration has been tested with Java version 1.7.0_02 (at least version 
#  1.7.x is expected) and with Python 2.7.8 (32 bit);
#   NB! If there are multiple Java installations available in the system, it might be 
#  necessary to set correct JAVA_HOME path before starting the Python with javabridge; 
#  E.g. on the Windows it was necessary to set:
#      SET JAVA_HOME=C:\Program Files (x86)\Java\jdk1.7.0_02
#

import os
import json
import sys

from pyvabamorf import analyze_sentence
from pprint import pprint

import javabridge_support   # More details about requirements in "javabridge_support.py"

javaResourcesDir = os.path.join( os.getcwd(), 'java-res' ) # Java resources: necessary jar files + XML rule files 
javabridge_support.initializeJVM(javaResourcesDir)

from clause_segmenter import ClauseSegmenter
segmenter = ClauseSegmenter()

sentence = analyze_sentence( u'Homme hommikul palun tulge ikka kohale, et saaksime asjaga alustada! (muidu kisub jamaks)'.split() )
#sentence = analyze_sentence( 'Näiteks tudengite küsimustele vastamise korral (olenemata asjaolust, et mitu tudengit esitab sama küsimust, usun, et see ei ole pedagoogiliselt õige)'.decode(sys.stdin.encoding).split() )

result1 = segmenter.detect_clause_boundaries(sentence)
pprint( result1 )

# This must be called after all work is done
javabridge_support.terminateJVM()
