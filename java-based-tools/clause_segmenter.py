# -*- coding: utf-8 -*-
#
#   Wrapper class around Java-based clause segmenter (Osalausestaja). 
#  Allows to process results sentence by sentence. 
#
#   Requires javabridge, see module "javabridge_support.py" for more 
#  details on initializing JVM with necessary JAR files;
#
#   More on JNI notation:
#     ** http://docs.oracle.com/javase/1.5.0/docs/guide/jni/spec/types.html
#

import javabridge
import json
import os.path

import re

class ClauseSegmenter:
    ''' Wrapper class around Java-based clause segmenter (Osalausestaja). 
        Allows to process results sentence by sentence. 
        ''' 
    segmenter = None
    
    def __init__(self):
        ''' Initializes clause segmenter in Java. 
            javabridge_support.initializeJVM(jarFilesDir) must be called before calling 
            this method; '''
        try:
            # Create new java instance of the clause segmenter
            self.segmenter = javabridge.JWrapper(javabridge.make_instance("ee/ut/soras/osalau/Osalausestaja", "()V"))
        except:
            raise
    
    def prepareSentence(self, sentence):
        # Remove phonetic markings from the root
        for word in sentence:
            if 'analysis' in word:
                for analysis in word['analysis']:
                    if 'root' in analysis:
                        analysis['root'] = analysis['root'].replace("~", "")
                        analysis['root'] = re.sub('[?<\]]([aioueöäõü])', '\\1', analysis['root'])
        # Add "words" key (because segmenter looks for it)
        sentence = { "words": sentence }
        # convert from json to string
        return json.dumps(sentence, ensure_ascii=False)
    
    def detect_clause_boundaries(self, sentence):
        ''' Detects clause boundaries from given sentence. Assumes that the input
           sentence has been analyzed with pyvabamorf. '''
        sentence_str = self.prepareSentence(sentence)
        try:
            # Analyze the sentence by calling
            # -- public String osalausestaPyVabamorfJSON( String sisendJSON ) throws Exception;
            result = javabridge.call(self.segmenter.o, \
                     "osalausestaPyVabamorfJSON", \
                     "(Ljava/lang/String;)Ljava/lang/String;", \
                     sentence_str)
        except:
            raise
        # Convert back to json and return the 'words' part
        return json.loads( result )["words"]
        #return json.loads( javabridge.to_string(result) )["words"]
        
