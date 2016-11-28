# -*- coding: utf-8 -*- 
#
#   A set of utilities to support processing and post-processing with  
#   Estonian syntactic parsers:
#
#    *) normalise_alignments() -- normalises syntactic information provided  
#                  in  different  formats  (CONLL  and  VISLCG3) into a 
#                  common format of labelled dependency relations;
#
#    *) read_text_from_cg3_file(),   -- reads syntactically annotated
#       read_text_from_conll_file()     texts into EstNLTK Text objects;
#
#    *) Tree datastructure : provides tree representations for accessing
#                            and exploring syntactically annotated data;
#
#    *) build_trees_from_sentence(), -- builds trees from syntactically
#       build_trees_from_text()         annotated sentence or text;
#

from __future__ import unicode_literals, print_function

import re, json
import os, os.path
import codecs, sys

#from nltk.tokenize.regexp import WhitespaceTokenizer
from nltk.tokenize.simple import LineTokenizer
from nltk.tokenize.regexp import RegexpTokenizer

from estnltk.names import *

from estnltk.mw_verbs.utils import WordTemplate

from estnltk.syntax.maltparser_support import align_CONLL_with_Text
from estnltk.syntax.vislcg3_syntax import cleanup_lines, align_cg3_with_Text


# ==================================================================================
# ==================================================================================
#   Normalising  dependency syntactic information in the alignments
# ==================================================================================
# ==================================================================================

pat_cg3_surface_rel = re.compile('(@\S+)')
pat_cg3_dep_rel     = re.compile('#(\d+)\s*->\s*(\d+)')

def _fix_out_of_sentence_links( alignments, sent_start, sent_end ):
    ''' Fixes out-of-the-sentence links in the given sentence.
        The sentence is a sublist of *alignments*, starting from 
        *sent_start* and ending one token before *sent_end*;
    ''' 
    sent_len = sent_end - sent_start
    j = sent_start
    while j < sent_start + sent_len:
        for rel_id, rel in enumerate( alignments[j][PARSER_OUT] ):
            if int( rel[1] ) >= sent_len:
                # If the link points out-of-the-sentence, fix
                # the link so that it points inside the sentence
                # boundaries:
                wid = j - sent_start
                if sent_len == 1:
                    # a single word becomes a root
                    rel[1] = -1
                elif wid-1 > -1:
                    # word at the middle/end is linked to the previous
                    rel[1] = wid - 1
                elif wid-1 == -1:
                    # word at the beginning is linked to the next
                    rel[1] = wid + 1
                alignments[j][PARSER_OUT][rel_id] = rel
        j += 1


def normalise_alignments( alignments, data_type=VISLCG3_DATA, **kwargs ):
    ''' Normalises dependency syntactic information in the given list of alignments.
        *) Translates tree node indices from the syntax format (indices starting 
           from 1), to EstNLTK format (indices starting from 0);
        *) Removes redundant information (morphological analyses) and keeps only 
           syntactic information, in the most compact format;
        *) Brings MaltParser and VISLCG3 info into common format;
        
        Expects that the list of alignments contains dicts, where each dict has 
        following attributes (at minimum):
          'start'   -- start index of the word in Text;
          'end'     -- end index of the word in Text;
          'sent_id' -- index of the sentence in Text, starting from 0;
          'parser_out' -- list of analyses from the output of the syntactic parser;
        Assumes that dicts are listed in the order of words appearance in the text;
        ( basically, assumes the output of methods align_CONLL_with_Text() and 
          align_cg3_with_Text() )
        
        Returns the input list (alignments), where old analysis lines ('parser_out') have 
        been replaced with the new compact form of analyses (if keep_old == False), or where 
        old analysis lines ('parser_out') have been replaced the new compact form of analyses,
        and the old analysis lines are preserved under a separate key: 'init_parser_out' (if 
        keep_old == True);

        In the compact list of analyses, each item has the following structure:
           [ syntactic_label, index_of_the_head ]
         *) syntactic_label
                surface syntactic label of the word, e.g. '@SUBJ', '@OBJ', '@ADVL'
         *) index_of_the_head
                index of the head; -1 if the current token is root;


        Parameters
        -----------
        alignments : list of items
            A list of dicts, where each item/dict has following attributes:
            'start', 'end', 'sent_id', 'parser_out'

        data_type : str
            Type of data in list_of_analysis_lines; Possible types: 'vislcg3'
            (default), and 'conll';

        rep_miss_w_dummy : bool
            Optional argument specifying whether missing analyses should be replaced
            with dummy analyses ( in the form ['xxx', link_to_self] ); If False,
            an Exception is raised in case of a missing analysis;
            Default:True
            
        fix_selfrefs : bool
            Optional argument specifying  whether  self-references  in  syntactic 
            dependencies should be fixed;
            A self-reference link is firstly re-oriented as a link to the previous word
            in the sentence, and if the previous word does  not  exist,  the  link  is 
            re-oriented to the next word in the sentence; If the self-linked word is
            the only word in the sentence, it is made the root of the sentence;
            Default:True
        
        fix_out_of_sent : bool
            Optional argument specifying whether references pointing out of the sentence
            (the parent index exceeds the sentence boundaries) should be fixed; 
            The logic used in fixing out-of-sentence links is the same as the logic for 
            fix_selfrefs;
            Default:False
        
        keep_old : bool
            Optional argument specifying  whether the old analysis lines should be 
            preserved after overwriting 'parser_out' with new analysis lines;
            If True, each dict will be augmented with key 'init_parser_out' which
            contains the initial/old analysis lines;
            Default:False
        
        mark_root : bool
            Optional argument specifying whether the root node in the dependency tree 
            (the node pointing to -1) should be assigned the label 'ROOT' (regardless
            its current label).
            This might be required, if one wants to make MaltParser's and VISLCG3 out-
            puts more similar, as MaltParser currently uses 'ROOT' labels, while VISLCG3 
            does not;
            Default:False


        (Example text: 'Millega pitsat tellida ? Hea küsimus .')
        Example input (VISLC3):
        -----------------------
        {'end': 7, 'sent_id': 0, 'start': 0, 'parser_out': ['\t"mis" Lga P inter rel sg kom @NN> @ADVL #1->3\r']}
        {'end': 14, 'sent_id': 0, 'start': 8, 'parser_out': ['\t"pitsa" Lt S com sg part @OBJ #2->3\r']}
        {'end': 22, 'sent_id': 0, 'start': 15, 'parser_out': ['\t"telli" Lda V main inf @IMV #3->0\r']}
        {'end': 23, 'sent_id': 0, 'start': 22, 'parser_out': ['\t"?" Z Int CLB #4->4\r']}
        {'end': 27, 'sent_id': 1, 'start': 24, 'parser_out': ['\t"hea" L0 A pos sg nom @AN> #1->2\r']}
        {'end': 35, 'sent_id': 1, 'start': 28, 'parser_out': ['\t"küsimus" L0 S com sg nom @SUBJ #2->0\r']}
        {'end': 36, 'sent_id': 1, 'start': 35, 'parser_out': ['\t"." Z Fst CLB #3->3\r']}

        Example output:
        ---------------
        {'sent_id': 0, 'start': 0, 'end': 7, 'parser_out': [['@NN>', 2], ['@ADVL', 2]]}
        {'sent_id': 0, 'start': 8, 'end': 14, 'parser_out': [['@OBJ', 2]]}
        {'sent_id': 0, 'start': 15, 'end': 22, 'parser_out': [['@IMV', -1]]}
        {'sent_id': 0, 'start': 22, 'end': 23, 'parser_out': [['xxx', 2]]}
        {'sent_id': 1, 'start': 24, 'end': 27, 'parser_out': [['@AN>', 1]]}
        {'sent_id': 1, 'start': 28, 'end': 35, 'parser_out': [['@SUBJ', -1]]}
        {'sent_id': 1, 'start': 35, 'end': 36, 'parser_out': [['xxx', 1]]}

    '''
    if not isinstance( alignments, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    if data_type.lower() == VISLCG3_DATA:
       data_type = VISLCG3_DATA
    elif data_type.lower() == CONLL_DATA:
       data_type = CONLL_DATA
    else: 
       raise Exception('(!) Unexpected type of data: ', data_type)
    keep_old         = False
    rep_miss_w_dummy = True
    mark_root        = False
    fix_selfrefs     = True
    fix_out_of_sent  = False
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
        if argName in ['fix_out_of_sent']:
           #  Fix links pointing out of the sentence;
           fix_out_of_sent = bool(argVal)
    # Iterate over the alignments and normalise information
    prev_sent_id = -1
    wordID       = 0
    sentStart    = -1
    for i in range(len(alignments)):
        alignment = alignments[i]
        if prev_sent_id != alignment[SENT_ID]:
            # Detect and fix out-of-the-sentence links in the previous sentence (if required)
            if fix_out_of_sent and sentStart > -1:
                _fix_out_of_sentence_links( alignments, sentStart, i )
            # Start of a new sentence: reset word id
            wordID = 0
            sentStart = i
        # 1) Extract syntactic information
        foundRelations = []
        if data_type == VISLCG3_DATA:
            # *****************  VISLCG3 format
            for line in alignment[PARSER_OUT]:
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
        elif data_type == CONLL_DATA:
            # *****************  CONLL format
            for line in alignment[PARSER_OUT]:
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
                    # to the next word;
                    foundRelations[r][1] = \
                        wordID-1 if wordID-1 > -1 else wordID+1
                    # If the self-linked token is the only token in the sentence, 
                    # mark it as the root of the sentence:
                    if wordID-1 == -1 and (i+1 == len(alignments) or \
                       alignments[i][SENT_ID] != alignments[i+1][SENT_ID]):
                        foundRelations[r][1] = -1
        # Mark the root node in the syntactic tree with the label ROOT ( if requested )
        if mark_root:
            for r in range(len(foundRelations)):
                if foundRelations[r][1] == -1:
                    foundRelations[r][0] = 'ROOT'
        # 2) Replace existing syntactic info with more compact info
        if not keep_old:
            # Overwrite old info
            alignment[PARSER_OUT] = foundRelations
        else: 
            # or preserve the initial information, and add new compact information
            alignment[INIT_PARSER_OUT] = alignment[PARSER_OUT]
            alignment[PARSER_OUT]      = foundRelations
        alignments[i] = alignment
        prev_sent_id = alignment[SENT_ID]
        # Increase word id 
        wordID += 1
    # Detect and fix out-of-the-sentence links in the last sentence (if required)
    if fix_out_of_sent and sentStart > -1:
        _fix_out_of_sentence_links( alignments, sentStart, len(alignments) )
    return alignments


# ==================================================================================
# ==================================================================================
#   Importing  syntactically parsed text from file
# ==================================================================================
# ==================================================================================

pat_double_quoted  = re.compile('^".*"$')
pat_cg3_word_token = re.compile('^"<(.+)>"$')

def read_text_from_cg3_file( file_name, layer_name=LAYER_VISLCG3, **kwargs ):
    ''' Reads the output of VISLCG3 syntactic analysis from given file, and 
        returns as a Text object.
        
        The Text object has been tokenized for paragraphs, sentences, words, and it 
        contains syntactic analyses aligned with word spans, in the layer *layer_name* 
        (by default: LAYER_VISLCG3);
        
        Attached syntactic analyses are in the format as is the output of 
          utils.normalise_alignments();
        
        Note: when loading data from  https://github.com/EstSyntax/EDT  corpus,
        it  is  advisable  to  add  flags:  clean_up=True,  fix_sent_tags=True, 
        fix_out_of_sent=True  in order to ensure that well-formed data will be
        read from the corpus;
        
        Parameters
        -----------
        file_name : str
            Name of the input file; Should contain syntactically analysed text,
            following the format of the output of VISLCG3 syntactic analyser;
        
        clean_up : bool
            Optional argument specifying whether the vislcg3_syntax.cleanup_lines()
            should be applied in the lines of syntactic analyses read from the 
            file;
            Default: False
        
        layer_name : str
            Name of the Text's layer in which syntactic analyses are stored; 
            Defaults to 'vislcg3_syntax';
        
            For other parameters, see optional parameters of the methods:
            
             utils.normalise_alignments():          "rep_miss_w_dummy", "fix_selfrefs",
                                                    "keep_old", "mark_root";
             vislcg3_syntax.align_cg3_with_Text():  "check_tokens", "add_word_ids";
             vislcg3_syntax.cleanup_lines():        "remove_caps", "remove_clo",
                                                    "double_quotes", "fix_sent_tags"
        
        
    '''
    clean_up = False
    for argName, argVal in kwargs.items():
        if argName in ['clean_up', 'cleanup'] and argVal in [True, False]:
           #  Clean up lines
           clean_up = argVal
    # 1) Load vislcg3 analysed text from file
    cg3_lines = []
    in_f = codecs.open(file_name, mode='r', encoding='utf-8')
    for line in in_f:
        # Skip comment lines
        if line.startswith('#'):
            continue
        cg3_lines.append( line.rstrip() )
    in_f.close()
    # Clean up lines of syntactic analyses (if requested)
    if clean_up:
        cg3_lines = cleanup_lines( cg3_lines, **kwargs )

    # 2) Extract sentences and word tokens
    sentences = []
    sentence  = []
    for i, line in enumerate( cg3_lines ):
        if line == '"<s>"':
            if sentence:
                print('(!) Sentence begins before previous ends at line: '+str(i), \
                      file=sys.stderr)
            sentence  = []
        elif pat_double_quoted.match( line ) and line != '"<s>"' and line != '"</s>"':
            token_match = pat_cg3_word_token.match( line )
            if token_match:
                line = token_match.group(1)
            else:
                raise Exception('(!) Unexpected token format: ', line)
            sentence.append( line )
        elif line == '"</s>"':
            if not sentence:
                print('(!) Empty sentence at line: '+str(i), \
                      file=sys.stderr)
            # (!) Use double space instead of single space in order to distinguish
            #     word-tokenizing space from the single space in the multiwords
            #     (e.g. 'Rio de Janeiro' as a single word);
            sentences.append( '  '.join(sentence) )
            sentence = []

    # 3) Construct the estnltk's Text
    kwargs4text = {
      # Use custom tokenization utils in order to preserve exactly the same 
      # tokenization as was in the input;
      "word_tokenizer": RegexpTokenizer("  ", gaps=True),
      "sentence_tokenizer": LineTokenizer()
    }
    from estnltk.text import Text
    text = Text( '\n'.join(sentences), **kwargs4text )
    # Tokenize up to the words layer
    text.tokenize_words()
    
    # 4) Align syntactic analyses with the Text
    alignments = align_cg3_with_Text( cg3_lines, text, **kwargs )
    normalise_alignments( alignments, data_type=VISLCG3_DATA, **kwargs )
    # Attach alignments to the text
    text[ layer_name ] = alignments
    return text


def read_text_from_conll_file( file_name, layer_name=LAYER_CONLL, **kwargs ):
    ''' Reads the CONLL format syntactic analysis from given file, and returns as 
        a Text object.
        
        The Text object has been tokenized for paragraphs, sentences, words, and it 
        contains syntactic analyses aligned with word spans, in the layer *layer_name* 
        (by default: LAYER_CONLL);
        
        Attached syntactic analyses are in the format as is the output of 
          utils.normalise_alignments();
        
        Parameters
        -----------
        file_name : str
            Name of the input file; Should contain syntactically analysed text,
            following the CONLL format;
        
        layer_name : str
            Name of the Text's layer in which syntactic analyses are stored; 
            Defaults to 'conll_syntax';
        
            For other parameters, see optional parameters of the methods:
            
             utils.normalise_alignments():          "rep_miss_w_dummy", "fix_selfrefs",
                                                    "keep_old", "mark_root";
             maltparser_support.align_CONLL_with_Text():  "check_tokens", "add_word_ids";

    '''
    # 1) Load conll analysed text from file
    conll_lines = []
    in_f = codecs.open(file_name, mode='r', encoding='utf-8')
    for line in in_f:
        # Skip comment lines
        if line.startswith('#'):
            continue
        conll_lines.append( line.rstrip() )
    in_f.close()
    
    # 2) Extract sentences and word tokens
    sentences = []
    sentence  = []
    for i, line in enumerate( conll_lines ):
        if len(line) > 0 and '\t' in line:
            features = line.split('\t')
            if len(features) != 10:
                raise Exception(' In file '+in_file+', line '+str(i)+\
                                ' with unexpected format: "'+line+'" ')
            word_id = features[0]
            token   = features[1]
            sentence.append( token )
        elif len(line)==0 or re.match('^\s+$', line):
            # End of a sentence 
            if sentence:
               # (!) Use double space instead of single space in order to distinguish
               #     word-tokenizing space from the single space in the multiwords
               #     (e.g. 'Rio de Janeiro' as a single word);
               sentences.append( '  '.join(sentence) )
            sentence = []
    if sentence:
        sentences.append( '  '.join(sentence) )
    
    # 3) Construct the estnltk's Text
    kwargs4text = {
      # Use custom tokenization utils in order to preserve exactly the same 
      # tokenization as was in the input;
      "word_tokenizer": RegexpTokenizer("  ", gaps=True),
      "sentence_tokenizer": LineTokenizer()
    }
    from estnltk.text import Text
    text = Text( '\n'.join(sentences), **kwargs4text )
    # Tokenize up to the words layer
    text.tokenize_words()
    
    # 4) Align syntactic analyses with the Text
    alignments = align_CONLL_with_Text( conll_lines, text, None, **kwargs )
    normalise_alignments( alignments, data_type=CONLL_DATA, **kwargs )
    # Attach alignments to the text
    text[ layer_name ] = alignments
    return text

# ==================================================================================

# A hack for defining a string type common in Py 2 and Py 3
try:
    # Check whether basestring is supported (should be in Py 2.7)
    basestring
except NameError as e:
    # If not supported (in Py 3.x), redefine it as str
    basestring = str

# A hack for getting type of the regular expression object
RE_TYPE = type(re.compile('A'))

# ==================================================================================
# ==================================================================================
#   Building  syntactic trees from the syntactic analyses
# ==================================================================================
# ==================================================================================


class Tree(object):
    word_id     = None    # -> int    # index of the word/node in the sentence
    gen_word_id = None    # -> int    # index of the word/node in the text (if provided)
    sent_id     = None    # -> int    # index of the sentence this word/node belongs to

    labels      = None    # -> [str]  # list of syntactic functions (e.g. "@SUBJ", "@OBJ"); 
                          #           # associated with the node; in case of unsolved ambiguities,
                          #           # multiple functions can be associated with the node;

    parent      = None    # -> Tree   # direct parent / head (Tree object)
    children    = None    # -> [Tree] # list of all direct children (Tree objects)

    token       = None    # -> dict   # EstNLTK token corresponding to the node / tree
    text        = None    # -> str    # token's TEXT ( token[TEXT] )
    morph       = None    # -> [dict] # token's morphological analysis (token[ANALYSIS])
                          #           # (if the Text object was analysed morphologically);
    
    syntax_token = None   # -> dict   # Token in the layer of EstNLTK's syntactic analysis that
                          #           # this node is based on;

    parser        = None  # -> str    # used parser: 'maltparser' or 'vislcg3'
    parser_output = None  # -> [str]  # analysis lines from the output of the parser (if have been 
                          #           # preserved); in case of unsolved ambiguities, there can be 
                          #           # multiple analysis lines associated with the node;

    def __init__( self, token, word_id, sent_id, labels, parser, **kwargs ):
        ''' Creates a new tree node / subtree, corresponding to the given EstNLTK's 
            *token*, which has word index *word_id*, which is from the sentence 
            *sent_id*, and which bears syntactic functions listed in *labels*.
        '''
        #  Acquire mandatory input arguments 
        self.token   = token
        self.word_id = word_id
        self.sent_id = sent_id
        self.labels  = labels
        self.parser  = parser
        #  Acquire optional input arguments  
        for argName, argVal in kwargs.items():
            if argName in ['parent', 'head']:
                assert isinstance(argVal, Tree), \
                       '(!) Unexpected type of argument for '+argName+'! Should be Tree.'
                self.parent = argVal
            elif argName in ['children', 'subtrees']:
                assert isinstance(argVal, list), \
                       '(!) Unexpected type of argument for '+argName+'! Should be list of Trees.'
                if len(argVal) > 0:
                    assert all(isinstance(argVal, Tree) for t in argVal), \
                       '(!) Unexpected type of argument for '+argName+'! Should be list of Trees.'
                self.children = argVal
            elif argName in ['gen_word_id', 'text_word_id']:
                assert isinstance(argVal, int), \
                       '(!) Unexpected type of argument for '+argName+'! Should be int.'
                self.gen_word_id = argVal
            elif argName.lower() == PARSER_OUT:
                assert isinstance(argVal, list), \
                       '(!) Unexpected type of argument for '+argName+'! Should be list of str.'
                self.parser_output = argVal
            elif argName in ['syntax_token']:
                assert isinstance(argVal, dict), \
                       '(!) Unexpected type of argument for '+argName+'! Should be dict.'
                self.syntax_token = argVal
        assert self.token != None, '(!) Please provide a link to the estnltk\'s token!'
        self.text  = self.token[TEXT]
        if ANALYSIS in self.token:
            self.morph = self.token[ANALYSIS]


    def add_child_to_self( self, tree ):
        ''' Adds given *tree* as a child of the current tree. '''
        assert isinstance(tree, Tree), \
               '(!) Unexpected type of argument for '+argName+'! Should be Tree.'
        if (not self.children):
            self.children = []
        tree.parent = self
        self.children.append(tree)


    def add_child_to_subtree( self, parent_word_id, tree ):
        ''' Searches for the tree with *parent_word_id* from the current subtree 
            (from this tree and from all of its subtrees). If the parent tree is 
            found, attaches the given *tree* as its child. If the parent tree is
            not found, the current tree is not changed.
        '''
        if (self.word_id == parent_word_id):
            self.add_child_to_self( tree )
        elif (self.children):
            for child in self.children:
                child.add_child_to_subtree(parent_word_id, tree)


    def get_root( self, **kwargs ):
        ''' Returns this tree if it has no parents, or, alternatively, moves
            up via the parent links of this tree until reaching the tree with
            no parents, and returnes the parentless tree as the root.
        '''
        if self.parent == None:
            return self
        else:
            return self.parent.get_root( **kwargs )


    def _satisfies_conditions( self, tree_node, **kwargs ):
        ''' Check whether given *tree_node* satisfies the conditions given
            as arguments in *kwargs*.
            
            By default (if no conditions are given in *kwargs*), returns 
            True.
            
            If there are multiple conditions listed  (e.g.  'label_regexp'
            and 'word_template'),  *True*  is returned only when the node 
            satisfies all the conditions.
            
            Following conditions are supported:
            -----------------------------------
            label : str
                Syntactic label (e.g. '@SUBJ', '@OBJ' etc.) that the node 
                must have within its analysis; If the node does not have the
                label, the node will be discarded;
                
            label_regexp : str
                A regular expression pattern (as string) describing the 
                syntactic label (e.g. '@SUBJ', '@OBJ' etc.) that the node 
                must have within its analysis; 
                If none of the node's labels matches the pattern, the node
                will be discarded;
            
            word_template : estnltk.mw_verbs.utils.WordTemplate
                A WordTemplate describing morphological constraints imposed
                to the word of the node;
                If the word's morphological features do not match the template, 
                the node will be discarded;
            
        '''
        matches = []
        # A) Check syntactic label by matching a string
        syntactic_label = kwargs.get('label', None)
        if syntactic_label:
            matches.append( bool(tree_node.labels and syntactic_label in tree_node.labels) )

        # B) Check syntactic label by matching a regular expression
        synt_label_regexp = kwargs.get('label_regexp', None)
        if synt_label_regexp:
            if isinstance(synt_label_regexp, basestring):
                # Compile the regexp (if it hasn't been compiled yet)
                synt_label_regexp = re.compile(synt_label_regexp)
                kwargs['label_regexp'] = synt_label_regexp
            if isinstance(synt_label_regexp, RE_TYPE):
                # Apply the pre-compiled regexp
                if tree_node.labels:
                    matches.append( any([synt_label_regexp.match(label) != None for label in tree_node.labels]) )
                else:
                    matches.append( False )

        # C) Check whether the word token of the node matches a word template
        word_template = kwargs.get('word_template', None)
        if word_template:
            if isinstance(word_template, WordTemplate):
                matches.append( word_template.matches( tree_node.token ) )
            else:
                raise Exception('(!) Unexpected word_template. Should be from class WordTemplate.')
        return len(matches) == 0 or all(matches)


    def get_children( self, **kwargs ):
        ''' Recursively collects and returns all subtrees of given tree (if no 
            arguments are given), or, alternatively, collects and returns subtrees 
            satisfying some specific criteria (pre-specified in the arguments);
            
            Parameters
            -----------
            depth_limit : int
                Specifies how deep into the subtrees of this tree the search goes;
                Examples:
                 depth_limit=2 -- children of this node, and also children's
                                  direct children are considered as collectibles;
                 depth_limit=1 -- only children of this node are considered;
                 depth_limit=0 -- the end of search (only this node is considered);
                Default: unbounded ( the search is not limited by depth )
            
            include_self : bool 
                Specifies whether this tree should also be included as a collectible
                subtree. If this tree is includes, it still must satisfy all the 
                criteria before it is included in the collection;
                Default: False
            
            sorted : bool
                Specifies returned trees should be sorted in the ascending order of 
                word_ids (basically: by the order of words in the text);
                If sorting is not applied, there is no guarantee that resulting trees
                follow the order of words in text;
                Default: False
                
            Following parameters can be used to set conditions for subtrees:
            -----------------------------------------------------------------
            label : str
                Syntactic label (e.g. '@SUBJ', '@OBJ' etc.) that the node 
                must have within its analysis; If the node does not have the
                label, the node will be discarded;
            
            label_regexp : str
                A regular expression pattern (as string) describing the 
                syntactic label (e.g. '@SUBJ', '@OBJ' etc.) that the node 
                must have within its analysis; 
                If none of the node's labels matches the pattern, the node
                will be discarded;
            
            word_template : estnltk.mw_verbs.utils.WordTemplate
                A WordTemplate describing morphological constraints imposed
                to the word of the node;
                If the word's morphological features do not match the template, 
                the node will be discarded;
            
        '''
        depth_limit  = kwargs.get('depth_limit', 922337203685477580) # Just a nice big number to
                                                                     # assure that by default, 
                                                                     # there is no depth limit ...
        include_self = kwargs.get('include_self', False)
        sorted_by_word_ids = kwargs.get('sorted', False)
        subtrees = []
        if include_self:
            if self._satisfies_conditions( self, **kwargs ):
                subtrees.append( self )
        if depth_limit >= 1 and self.children:
            # 1) Add children of given tree
            for child in self.children:
                if self._satisfies_conditions( child, **kwargs ):
                    subtrees.append(child)
            # 2) Collect children of given tree's children
            kwargs['include_self'] = False
            kwargs['depth_limit']  = depth_limit - 1 
            for child in self.children:
                childs_results = child.get_children( **kwargs )
                if childs_results:
                    subtrees.extend(childs_results)
        if sorted_by_word_ids:
            # Sort by word_id-s, in ascending order
            subtrees = sorted(subtrees, key=lambda x: x.word_id)
        return subtrees


    def as_dependencygraph( self, keep_dummy_root=False, add_morph=True ):
        ''' Returns this tree as NLTK's DependencyGraph object.
            
            Note that this method constructs 'zero_based' graph,
            where counting of the words starts from 0 and the 
            root index is -1 (not 0, as in Malt-TAB format);
            
            Parameters
            -----------
            add_morph : bool
                Specifies whether the morphological information 
                (information about word lemmas, part-of-speech, and 
                features) should be added to graph nodes.
                Note that even if **add_morph==True**, morphological
                information is only added if it is available via
                estnltk's layer  token['analysis'];
                Default: True
            keep_dummy_root : bool
                Specifies whether the graph should include a dummy
                TOP / ROOT node, which does not refer to any word,
                and yet is the topmost node of the tree.
                If the dummy root node is not used, then the root 
                node is the word node headed by -1;
                Default: False
            
            For more information about NLTK's DependencyGraph, see:
             http://www.nltk.org/_modules/nltk/parse/dependencygraph.html
        '''
        from nltk.parse.dependencygraph import DependencyGraph
        graph = DependencyGraph( zero_based = True )
        all_tree_nodes = [self] + self.get_children()
        #
        # 0) Fix the root
        #
        if keep_dummy_root:
            #  Note: we have to re-construct  the root node manually, 
            #  as DependencyGraph's current interface seems to provide
            #  no easy/convenient means for fixing the root node;
            graph.nodes[-1] = graph.nodes[0]
            graph.nodes[-1].update( { 'address': -1 } )
            graph.root = graph.nodes[-1]
        del graph.nodes[0]
        #
        # 1) Update / Add nodes of the graph 
        #
        for child in all_tree_nodes:
            rel  = 'xxx' if not child.labels else '|'.join(child.labels)
            address = child.word_id
            word    = child.text
            graph.nodes[address].update(
            {
                'address': address,
                'word':  child.text,
                'rel':   rel,
            } )
            if not keep_dummy_root and child == self:
                # If we do not keep the dummy root node, set this tree
                # as the root node
                graph.root = graph.nodes[address]
            if add_morph and child.morph:
                # Add morphological information, if possible
                lemmas  = set([analysis[LEMMA] for analysis in child.morph])
                postags = set([analysis[POSTAG] for analysis in child.morph])
                feats   = set([analysis[FORM] for analysis in child.morph])
                lemma  = ('|'.join( list(lemmas)  )).replace(' ','_')
                postag = ('|'.join( list(postags) )).replace(' ','_')
                feats  = ('|'.join( list(feats) )).replace(' ','_')
                graph.nodes[address].update(
                {
                    'tag  ': postag,
                    'ctag' : postag,
                    'feats': feats,
                    'lemma': lemma
                } )

        #
        # 2) Update / Add arcs of the graph 
        #
        for child in all_tree_nodes:
            #  Connect children of given word
            deps = [] if not child.children else [c.word_id for c in child.children]
            head_address = child.word_id
            for dep in deps:
                graph.add_arc( head_address, dep )
            if child.parent == None and keep_dummy_root:
                graph.add_arc( -1, head_address )
            #  Connect the parent of given node
            head = -1 if not child.parent else child.parent.word_id
            graph.nodes[head_address].update(
            {
                'head':  head,
            } )
        return graph


    def as_nltk_tree( self ):
        ''' Returns this tree as NLTK's Tree object.
        
            For more information about NLTK's Tree, see:
              http://www.nltk.org/_modules/nltk/tree.html
        ''' 
        #from nltk.tree import Tree as NLTK_Tree
        return self.as_dependencygraph().tree()


    def get_tree_depth( self ):
        ''' Finds depth of this tree. '''
        if (self.children):
            depth = 1
            childDepths = []
            for child in self.children:
                childDepths.append( child.get_tree_depth() )
            return depth + max(childDepths)
        else:
            return 0


    def debug_print_tree( self, spacing='' ):
        ''' *Debug only* method for outputting the tree. '''
        print (spacing+" "+str(self.word_id)+" "+str(self.text))
        if (self.children):
            spacing=spacing+"  "
            for child in self.children:
                child.debug_print_tree(spacing)


# ===========================================

def build_trees_from_sentence( sentence, syntactic_relations, layer=LAYER_VISLCG3, \
                               sentence_id=0, **kwargs ):
    ''' Given a sentence ( a list of EstNLTK's word tokens ), and a list of 
        dependency syntactic relations ( output of normalise_alignments() ),
        builds trees ( estnltk.syntax.utils.Tree objects ) from the sentence,
        and returns as a list of Trees (roots of trees).
        
        Note that  there  is  one-to-many  correspondence  between  EstNLTK's 
        sentences and dependency syntactic trees, so the resulting list can 
        contain more than one tree (root);
    '''
    trees_of_sentence = []
    nodes = [ -1 ]
    while( len(nodes) > 0 ):
        node = nodes.pop(0)
        # Find tokens in the sentence that take this node as their parent
        for i, syntax_token in enumerate( syntactic_relations ):
            parents = [ o[1] for o in syntax_token[PARSER_OUT] ]
            # There should be only one parent node; If there is more than one, take the 
            # first node;
            parent = parents[0]
            if parent == node:
                labels  = [ o[0] for o in syntax_token[PARSER_OUT] ]
                estnltk_token = sentence[i]
                tree1 = Tree( estnltk_token, i, sentence_id, labels, parser=layer )
                if INIT_PARSER_OUT in syntax_token:
                    tree1.parser_output = syntax_token[INIT_PARSER_OUT]
                tree1.syntax_token = syntax_token
                if parent == -1:
                    # Add the root node
                    trees_of_sentence.append( tree1 )
                elif parent == i:
                    # If, for some strange reason, the node is unnormalised and is still 
                    # linked to itself, add it as a singleton tree
                    trees_of_sentence.append( tree1 )
                else:
                    # For each root node, attempt to add the child
                    for root_node in trees_of_sentence:
                        root_node.add_child_to_subtree( parent, tree1 )
                if parent != i:
                   # Add the current node as a future parent to be examined
                   nodes.append( i )
    return trees_of_sentence



def build_trees_from_text( text, layer, **kwargs ):
    ''' Given a text object and the name of the layer where dependency syntactic 
        relations are stored, builds trees ( estnltk.syntax.utils.Tree objects )
        from all the sentences of the text and returns as a list of Trees.
        
        Uses the method  build_trees_from_sentence()  for acquiring trees of each
        sentence;
        
        Note that there is one-to-many correspondence between EstNLTK's sentences
        and dependency syntactic trees: one sentence can evoke multiple trees;
    '''
    from estnltk.text import Text
    assert isinstance(text, Text), \
           '(!) Unexpected text argument! Should be Estnltk\'s Text object.'
    assert layer in text, \
           '(!) The layer '+str(layer)+' is missing from the input text.'
    text_sentences = list( text.divide( layer=WORDS, by=SENTENCES ) )
    all_sentence_trees = []  # Collected sentence trees
    prev_sent_id       = -1
    #  (!) Note: if the Text object has been split into smaller Texts with split_by(),
    #      SENT_ID-s still refer to old text, and thus are not useful as indices
    #      anymore; 
    #      Therefore, we also use another variable -- norm_prev_sent_id -- that always
    #      counts sentences starting from 0, and use  SENT_ID / prev_sent_id  only for 
    #      deciding whether one sentence ends and another begins;
    norm_prev_sent_id  = -1
    current_sentence   = []
    k = 0
    while k < len( text[layer] ):
        node_desc = text[layer][k]
        if prev_sent_id != node_desc[SENT_ID] and current_sentence:
            norm_prev_sent_id += 1
            # If the index of the sentence has changed, and we have collected a sentence, 
            # then build tree(s) from this sentence
            assert norm_prev_sent_id<len(text_sentences), '(!) Sentence with the index '+str(norm_prev_sent_id)+\
                                                          ' not found from the input text.'
            sentence = text_sentences[norm_prev_sent_id]
            trees_of_sentence = \
                build_trees_from_sentence( sentence, current_sentence, layer, sentence_id=norm_prev_sent_id, \
                                           **kwargs )
            # Record trees constructed from this sentence
            all_sentence_trees.extend( trees_of_sentence )
            # Reset the sentence collector
            current_sentence = []
        # Collect sentence
        current_sentence.append( node_desc )
        prev_sent_id = node_desc[SENT_ID]
        k += 1
    if current_sentence:
        norm_prev_sent_id += 1
        assert norm_prev_sent_id<len(text_sentences), '(!) Sentence with the index '+str(norm_prev_sent_id)+\
                                                      ' not found from the input text.'
        sentence = text_sentences[norm_prev_sent_id]
        # If we have collected a sentence, then build tree(s) from this sentence
        trees_of_sentence = \
            build_trees_from_sentence( sentence, current_sentence, layer, sentence_id=norm_prev_sent_id, \
                                       **kwargs )
        # Record trees constructed from this sentence
        all_sentence_trees.extend( trees_of_sentence )
    return all_sentence_trees

