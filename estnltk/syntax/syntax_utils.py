# -*- coding: utf-8 -*- 
#
#   An unified interface for Estonian syntactic parsers;
#   
#   Aims to support:
#    *) VISL-CG3 based syntactic analysis;
#    *) MaltParser based syntactic analysis;
#

from __future__ import unicode_literals, print_function

from estnltk.names import *
from estnltk.text import Text

from estnltk.maltparser_support import MaltParser, align_CONLL_with_Text
from syntax_preprocessing import SyntaxPreprocessing
from vislcg3_syntax import VISLCG3Pipeline, cleanup_lines, align_cg3_with_Text

import re, json
import os, os.path
import codecs

# ==================================================================================
# ==================================================================================
#   Normalises dependency syntactic information in the alignments
# ==================================================================================
# ==================================================================================

pat_cg3_surface_rel = re.compile('(@\S+)')
pat_cg3_dep_rel     = re.compile('#(\d+)\s*->\s*(\d+)')

def normalise_alignments( alignments, type='VISLCG3', **kwargs ):
    ''' Normalises dependency syntactic information in the given list of alignments.
        *) Translates tree node indices from the syntax format (indices starting 
           from 1), to EstNLTK format (indices starting from 0);
        *) Removes redundant information (morphological analyses) and keeps only 
           syntactic information, in the most compact format;
        *) Brings MaltParser and VISLCG3 info into common format;
        
        Expects that the input list of alignments contains elements with the following 
        structure:
        [ general_WID, sentence_ID, word_ID, list_of_analysis_lines ]
        ( as in the output of methods align_CONLL_with_Text() and align_cg3_with_Text() )
        
        Returns the input list (alignments), where old analysis lines have been replaced 
        with the new compact form of analyses (if keep_old == False), or where new analysis 
        lines have been added just before the old analysis lines, so that the structure of 
        an alignment becomes:
        [ general_WID, sentence_ID, word_ID, list_of_compact_analyses, list_of_old_analyses ]
        
        In the compact list of analyses, each item has the following structure:
           [ syntactic_label, index_of_the_head ]
         *) syntactic_label
                surface syntactic label of the word, e.g. '@SUBJ', '@OBJ', '@ADVL'
         *) index_of_the_head
                index of the head; -1 if the current token is root;


        Parameters
        -----------
        alignments : list of items
            A list of alignments, where each item is in the format:
            [ general_WID, sentence_ID, word_ID, list_of_analysis_lines ]

        type : str
            Type of data in list_of_analysis_lines; Possible types: 'VISLCG3'
            (default), and 'CONLL';

        rep_miss_w_dummy : bool
            Optional argument specifying whether missing analyses should be replaced
            with dummy analyses (in the form ['xxx', link_to_self]); If False,
            an Exception is raised in case of a missing analysis;
            Default:True
            
        fix_selfrefs : bool
            Optional argument specifying  whether  self-references  in  syntactic 
            dependencies should be fixed;
            A self-reference link is firstly re-oriented as a link to the previous word
            in the sentence, and if the previous word does  not  exist,  the  link  is 
            re-oriented to the next word in the sentence (regardless whether the next 
            word exists or not);
            Default:True
        
        keep_old : bool
            Optional argument specifying  whether the new analysis lines should be added
            before the old analysis lines, instead of overwriting the old lines;
            If True, each item in the (returned) list of alignments obtains a form:
               [ general_WID, sentence_ID, word_ID, new_analyses, old_analyses ]
            Default:False
        
        mark_root : bool
            Optional argument specifying whether the root node in the dependency tree 
            (the node pointing to -1) should be assigned the label 'ROOT' (regardless
            its current label).
            This might be required, if one wants to make MaltParser's and VISLCG3 out-
            puts more similar, as MaltParser currently uses 'ROOT' labels, while VISLCG3 
            does not;
            Default:False


        (Example text: 'Millega pitsat tellida? Hea küsimus.')
        Example input (VISLC3):
        -----------------------
        [0, 0, 0, ['\t"mis" Lga P inter rel sg kom @NN> @ADVL #1->3\r']]
        [1, 0, 1, ['\t"pitsa" Lt S com sg part @OBJ #2->3\r']]
        [2, 0, 2, ['\t"telli" Lda V main inf @IMV #3->0\r']]
        [3, 0, 3, ['\t"?" Z Int CLB #4->4\r']]
        [4, 1, 0, ['\t"hea" L0 A pos sg nom @AN> #1->2\r']]
        [5, 1, 1, ['\t"küsimus" L0 S com sg nom @SUBJ #2->0\r']]
        [6, 1, 2, ['\t"." Z Fst CLB #3->3\r']]

        Example output:
        ---------------
        [0, 0, 0, [['@NN>', 2], ['@ADVL', 2]]]
        [1, 0, 1, [['@OBJ', 2]]]
        [2, 0, 2, [['@IMV', -1]]]
        [3, 0, 3, [['xxx', 2]]]
        [4, 1, 0, [['@AN>', 1]]]
        [5, 1, 1, [['@SUBJ', -1]]]
        [6, 1, 2, [['xxx', 1]]]

    '''
    if not isinstance( alignments, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    if type.lower() in ['vislcg3','cg3']:
       type = 1
    elif type.lower() in ['conll', 'malt', 'maltparser']:
       type = 2
    else: 
       raise Exception('(!) Unexpected type of data: ', type)
    keep_old         = False
    rep_miss_w_dummy = True
    mark_root        = False
    fix_selfrefs     = True
    for argName, argVal in kwargs.items():
        if argName in ['selfrefs', 'fix_selfrefs'] and argVal in [True, False]:
           #  Fix self-references
           fix_selfrefs = argVal
        if argName in ['keep_old'] and argVal in [True, False]:
           #  After the normalisation, keep also the original analyses;
           keep_old = argVal
        if argName in ['rep_miss_w_dummy', 'rep_miss'] and argVal in [True, False]:
           #  Replace missing analyses with dummy analyses;
           rep_miss_w_dummy = argVal
        if argName in ['mark_root', 'root'] and argVal in [True, False]:
           #  Mark the root node in the syntactic tree with the label ROOT;
           mark_root = argVal
    # Iterate over the alignments and normalise information
    for i in range(len(alignments)):
        alignment = alignments[i]
        wordID = alignment[2]
        #firstInSent = (i == 0) or (i>0 and alignments[i-1][1]!=alignments[i][1]);
        #lastInSent  = (i==len(alignments)-1) or \
        #              (i<len(alignments)-1 and alignments[i+1][1]!=alignments[i][1])
        # 1) Extract syntactic information
        foundRelations = []
        if type == 1:
            # *****************  VISLCG3 format
            for line in alignment[3]:
                # Extract info from VISLCG3 format analysis:
                sfuncs  = pat_cg3_surface_rel.findall( line )
                deprels = pat_cg3_dep_rel.findall( line )
                # If sfuncs is empty, generate an empty syntactic function (e.g. for 
                # punctuation)
                sfuncs = ['xxx'] if not sfuncs else sfuncs
                # Generate all pairs of labels vs dependency
                for func in sfuncs:
                    for (relS,relT) in deprels:
                        relS = int(relS)-1
                        relT = int(relT)-1
                        foundRelations.append( [func, relT] )
        elif type == 2:
            # *****************  CONLL format
            for line in alignment[3]:
                parts = line.split('\t')
                if len(parts) != 10:
                    raise Exception('(!) Unexpected line format for CONLL data:', line)
                relT = int( parts[6] ) - 1
                func = parts[7]
                foundRelations.append( [func, relT] )
        # Handle missing relations (VISLCG3 specific problem)
        if not foundRelations:
            # If no alignments were found (probably due to an error in analysis)
            if rep_miss_w_dummy:
                # Replace missing analysis with a dummy analysis, with dep link 
                # pointing to self;
                foundRelations.append( ['xxx', wordID] )
            else:
                raise Exception('(!) Analysis missing for the word nr.', alignment[0])
        # Fix self references ( if requested )
        if fix_selfrefs:
            for r in range(len(foundRelations)):
                if foundRelations[r][1] == wordID:
                    # Make it to point to the previous word in the sentence,
                    # and if the previous one does not exist, make it to point
                    # to the next word (regardless whether it exists or not);
                    foundRelations[r][1] = \
                        wordID-1 if wordID-1 > -1 else wordID+1
        # Mark the root node in the syntactic tree with the label ROOT ( if requested )
        if mark_root:
            for r in range(len(foundRelations)):
                if foundRelations[r][1] == -1:
                    foundRelations[r][0] = 'ROOT'
        # 2) Replace existing syntactic info with more compact info
        if not keep_old:
            # Overwrite old info
            alignment[3] = foundRelations
        else: 
            # or add compact information as an addition
            alignment.insert(3, foundRelations)
        alignments[i] = alignment
    return alignments



class SyntacticParser(object):
    """ TODO: add implementation here."""
    
    def parse_text(self, text):
        """ TODO: Tag the given text instance. """
        pass
