# -*- coding: utf-8 -*- 
#
#   An unified interface for Estonian syntactic parsers;
#   
#   Aims to support:
#    *) VISL-CG3 based syntactic analysis;
#    *) MaltParser based syntactic analysis;
#

from __future__ import unicode_literals, print_function

import re, json
import os, os.path
import codecs, sys

#from nltk.tokenize.regexp import WhitespaceTokenizer
from nltk.tokenize.simple import LineTokenizer
from nltk.tokenize.regexp import RegexpTokenizer

from estnltk.names import *
from estnltk.text  import Text

from estnltk.maltparser_support import MaltParser, align_CONLL_with_Text
from syntax_preprocessing import SyntaxPreprocessing
from vislcg3_syntax import VISLCG3Pipeline, cleanup_lines, align_cg3_with_Text

# Used constants
CONLL_DATA    = 'conll'
VISLCG3_DATA  = 'vislcg3'
LAYER_CONLL   = 'conll_syntax'
LAYER_VISLCG3 = 'vislcg3_syntax'

SENT_ID         = 'sent_id'
PARSER_OUT      = 'parser_out'
INIT_PARSER_OUT = 'init_parser_out'

# ==================================================================================
# ==================================================================================
#   Normalising  dependency syntactic information in the alignments
# ==================================================================================
# ==================================================================================

pat_cg3_surface_rel = re.compile('(@\S+)')
pat_cg3_dep_rel     = re.compile('#(\d+)\s*->\s*(\d+)')

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
    prev_sent_id = -1
    wordID = 0
    for i in range(len(alignments)):
        alignment = alignments[i]
        if prev_sent_id != alignment[SENT_ID]:
            # Start of a new sentence: reset word id
            wordID = 0
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
                                                    "double_quotes";
        
        
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
    text = Text( '\n'.join(sentences), **kwargs4text )
    # Tokenize up to the words layer
    text.tokenize_words()
    
    # 4) Align syntactic analyses with the Text
    alignments = align_CONLL_with_Text( conll_lines, text, **kwargs )
    normalise_alignments( alignments, data_type=CONLL_DATA, **kwargs )
    # Attach alignments to the text
    text[ layer_name ] = alignments
    return text


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
                
        '''
        depth_limit  = kwargs.get('depth_limit', 922337203685477580) # Just a nice big number to
                                                                     # assure that by default, 
                                                                     # there is no depth limit ...
        include_self = kwargs.get('include_self', False)
        subtrees = []
        if include_self:
            # TODO: add here condition checking
            subtrees.append( self )
        if depth_limit >= 1 and self.children:
            # 1) Add children of given tree
            for child in self.children:
                # TODO: add here condition checking
                subtrees.append(child)
            # 2) Collect children of given tree's children
            kwargs['include_self'] = False
            kwargs['depth_limit']  = depth_limit - 1 
            for child in self.children:
                childs_results = child.get_children( **kwargs )
                if childs_results:
                    subtrees.extend(childs_results)
        # TODO: add sorting of the subtrees
        return subtrees


    def as_dependencygraph( self, keep_dummy_root=False ):
        ''' Returns this tree as NLTK's DependencyGraph object.
            
            Note that this method constructs 'zero_based' graph,
            where counting of the words starts from 0 and the 
            root index is -1 (not 0, as in Malt-TAB format);
            
            Parameters
            -----------
            keep_dummy_root : bool
                Specifies whether the graph should include a dummy
                TOP / ROOT node, which does not refer to any word,
                and yet is the topmost node of the tree.
                If the dummy root node is not used, then the root 
                node is the word node headed by the root node (-1);
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
    assert isinstance(text, Text), \
           '(!) Unexpected text argument! Should be Estnltk\'s Text object.'
    assert layer in text, \
           '(!) The layer '+str(layer)+' is missing from the input text.'
    text_sentences = list( text.divide( layer=WORDS, by=SENTENCES ) )
    all_sentence_trees = []  # Collected sentence trees
    prev_sent_id       = -1
    current_sentence   = []
    k = 0
    while k < len( text[layer] ):
        node_desc = text[layer][k]
        if prev_sent_id != node_desc[SENT_ID] and current_sentence:
            # If the index of the sentence has changed, and we have collected a sentence, 
            # then build tree(s) from this sentence
            assert prev_sent_id<len(text_sentences), '(!) Sentence with the index '+str(prev_sent_id)+\
                                                     ' not found from the input text.'
            sentence = text_sentences[prev_sent_id]
            trees_of_sentence = \
                build_trees_from_sentence( sentence, current_sentence, layer, sentence_id=prev_sent_id, \
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
        assert prev_sent_id<len(text_sentences), '(!) Sentence with the index '+str(prev_sent_id)+\
                                                 ' not found from the input text.'
        sentence = text_sentences[prev_sent_id]
        # If we have collected a sentence, then build tree(s) from this sentence
        trees_of_sentence = \
            build_trees_from_sentence( sentence, current_sentence, layer, sentence_id=prev_sent_id, \
                                       **kwargs )
        # Record trees constructed from this sentence
        all_sentence_trees.extend( trees_of_sentence )
    return all_sentence_trees



# ==================================================================================
# ==================================================================================
#   Applying  syntactic analyser / parser on Text
# ==================================================================================
# ==================================================================================

class VISLCG3Parser(object):
    ''' A wrapper for Estonian VISLCG3 based syntactic parsing pipeline. 
    
        Unifies processing done in SyntaxPreprocessing() and VISLCG3Pipeline(), and 
        post-processing done in  align_cg3_with_Text() and normalise_alignments() 
        into a common analysis pipeline, which produces a syntactic analyses for
        a Text object.
        
        Example usage:
            #
            # vislcg_cmd - provide full path to vislcg3 executable 
            #              ('vislcg3' or 'vislcg3.exe')
            # text       - EstNLTK Text object to be analysed;
            #
            parser = VISLCG3Parser( vislcg_cmd=vislcg_cmd )
            
            # parse text, and return results as list of lines from vislcg3's output
            results1 = parser.parse_text( text, return_type = "vislcg3" )
            for line in results1:
                print(line)
            
            # results are also packed in Text object, on the layer named LAYER_VISLCG3:
            for word_id_in_text, syntax_analysis in enumerate( text[LAYER_VISLCG3] ):
                parser_out = syntax_analysis[PARSER_OUT]
                print(word_id_in_text, parser_out)
            

    '''
    
    preprocessor      = None 
    vislcg3_processor = None
    
    def __init__( self, **kwargs):
       '''  Initializes VISLCG3 based syntactic analyzer's wrapper.
        
            Parameters
            -----------
            preprocessor : SyntaxPreprocessing
                A custom syntax pre-processing pipeline to be used in the parser.
                If omitted (default), the default constructor is used to create a new 
                SyntaxPreprocessing() object, and the created object is assigned to 
                preprocessor.
                
            vislcg3_processor : VISLCG3Pipeline
                A custom vislcg3 processing pipeline to be used in the parser.
                If omitted (default), a new VISLCG3Pipeline() object is created and 
                assigned to vislcg3_processor.               
            
            fs_to_synt_rules : str
                Name of the file containing rules for mapping from Filosoft's old mrf 
                format to syntactic analyzer's preprocessing mrf format;
                This argument is used in initiating SyntaxPreprocessing (preprocessor).
                (Defaults to: 'tmorftrtabel.txt' in 'syntax/files')
                
            subcat_rules : str
                Name of the file containing rules for adding subcategorization information
                to verbs/adpositions;
                This argument is used in initiating SyntaxPreprocessing (preprocessor).
                (Defaults to: 'abileksikon06utf.lx' in 'syntax/files')
                
            vislcg_cmd : str
                Name of visl_cg3 binary executable. If the executable is accessible from 
                system's PATH variable, full path can be omitted, otherwise, the name must 
                contain full path to the executable.
                This argument is used in initiating VISLCG3Pipeline (vislcg3_processor).
                Default: 'vislcg3'
            
            pipeline : list of str
                List of VISLCG3 rule file names. In the processing phase, these rules
                are executed exactly the same order as in the list.
                NB! If the rule file is given without path, it is assumed that the file
                resides in the directory *rules_dir*; Otherwise, a full path to the rule
                file must be provided within the name;
                This argument is used in initiating VISLCG3Pipeline (vislcg3_processor).
                
            rules_dir : str
                A default directory from where to find rules that are executed on the 
                pipeline.
                If a file name listed in *pipeline* does not contain path, it is assumed 
                to reside within *rules_dir*;
                This argument is used in initiating VISLCG3Pipeline (vislcg3_processor).
                Defaults to: 'syntax/files'

       '''
       # get custom pipelines (if provided)
       for argName, argVal in kwargs.items():
            if argName.lower in ['preprocessor', 'preproc']:
                assert isinstance(argVal, SyntaxPreprocessing), \
                    '(!) "preprocessor" must be from SyntaxPreprocessing class.'
                self.preprocessor = argVal
            elif argName.lower in ['vislcg3_processor', 'vislcg3_proc']:
                assert isinstance(argVal, VISLCG3Pipeline), \
                    '(!) "vislcg3_processor" must be from VISLCG3Pipeline class.'
                self.vislcg3_processor = argVal
       # initialize pre-processing pipeline
       if not self.preprocessor:
            new_kwargs = self._filter_kwargs( \
                ['subcat_rules','fs_to_synt_rules','allow_to_remove'], **kwargs )
            self.preprocessor = SyntaxPreprocessing( **new_kwargs )
       # initialize vislcg3 pipeline
       if not self.vislcg3_processor:
            new_kwargs = self._filter_kwargs( \
                ['pipeline','rules_dir','vislcg_cmd','vislcg'], **kwargs )
            self.vislcg3_processor = VISLCG3Pipeline( **new_kwargs )
    
    
    def parse_text(self, text, **kwargs):
        """ Parses given text with VISLCG3 based syntactic analyzer. 
        
            As a result of parsing, the input Text object will obtain a new 
            layer named LAYER_VISLCG3,  which  contains  a  list  of  dicts.
            Each dicts corresponds to analysis of a single word token, and
            has the following attributes (at minimum):
              'start'      -- start index of the word in Text;
              'end'        -- end index of the word in Text;
              'sent_id'    -- index of the sentence in Text, starting from 0;
              'parser_out' -- list of analyses from the output of the 
                              syntactic parser;
                In the list of analyses, each item has the following structure:
                    [ syntactic_label, index_of_the_head ]
                *) syntactic_label:
                       surface syntactic label of the word, e.g. '@SUBJ', 
                       '@OBJ', '@ADVL';
                *) index_of_the_head:
                       index of the head (in the sentence); 
                       -1 if the current token is root;
            
            Parameters
            -----------
            return_type : string
                If return_type=="text" (Default), 
                    returns the input Text object;
                If return_type=="vislcg3", 
                    returns VISLCG3's output: a list of strings, each element in 
                    the list corresponding to a line from VISLCG3's output;
                If return_type=="trees", 
                    returns all syntactic trees of the text as a list of 
                    EstNLTK's Tree objects (estnltk.syntax.utils.Tree);
                If return_type=="dep_graphs", 
                    returns all syntactic trees of the text as a list of NLTK's 
                    DependencyGraph objects 
                    (nltk.parse.dependencygraph.DependencyGraph);
                Regardless the return type, the layer containing dependency syntactic
                information ( LAYER_VISLCG3 ) will be attached to the text object;
            
            augment_words : bool
                Specifies whether words in the input Text are to be augmented with 
                the syntactic information (SYNTAX_LABEL, SYNTAX_HEAD and DEPREL);
                (!) This functionality is added to achieve a compatibility with the 
                old way syntactic processing, but it will be likely deprecated in 
                the future.
                Default: False
            
            Other arguments are the arguments that can be passed to methods:
               vislcg3_syntax.process_lines(), 
               vislcg3_syntax.align_cg3_with_Text(),
               normalise_alignments()
            
            keep_old : bool
                Optional argument specifying  whether the old analysis lines 
                should be preserved after overwriting 'parser_out' with new analysis 
                lines;
                If True, each dict will be augmented with key 'init_parser_out' 
                which contains the initial/old analysis lines;
                Default:False
            
        """
        # a) get the configuration:
        augment_words    = False
        all_return_types = ["text","vislcg3","trees","dep_graphs"]
        return_type      = all_return_types[0]
        for argName, argVal in kwargs.items():
            if argName.lower() == 'return_type':
                if argVal.lower() in all_return_types:
                    return_type = argVal.lower()
                else:
                    raise Exception(' Unexpected return type: ', argVal)
            elif argName.lower() == 'augment_words' and argVal in [True, False]:
                augment_words = argVal
        kwargs['split_result']  = True
        kwargs['clean_up']      = True
        kwargs['remove_clo']    = kwargs.get('remove_clo', True)
        kwargs['remove_cap']    = kwargs.get('remove_cap', True)
        kwargs['keep_old']      = kwargs.get('keep_old',  False)
        kwargs['double_quotes'] = 'unesc'
        
        # b) process:
        result_lines1 = \
            self.preprocessor.process_Text(text, **kwargs)
        result_lines2 = \
            self.vislcg3_processor.process_lines(result_lines1, **kwargs)
        alignments = \
            align_cg3_with_Text(result_lines2, text, **kwargs)
        alignments = \
            normalise_alignments( alignments, data_type=VISLCG3_DATA, **kwargs )
        
        # c) attach & return results
        text[LAYER_VISLCG3] = alignments
        if augment_words:
            self._augment_text_w_syntactic_info( text, text[LAYER_VISLCG3] )
        if return_type   == "vislcg3":
            return result_lines2
        elif return_type == "trees":
            return build_trees_from_text( text, layer=LAYER_VISLCG3, **kwargs )
        elif return_type == "dep_graphs":
            trees = build_trees_from_text( text, layer=LAYER_VISLCG3, **kwargs )
            graphs = [tree.as_dependencygraph() for tree in trees]
            return graphs
        else:
            return text
    
    
    def _filter_kwargs(self, keep_list, **kwargs):
        ''' Filters the dict of *kwargs*, keeping only arguments 
            whose keys are in *keep_list* and discarding all other
            arguments.
            
            Based on the filtring, constructs and returns a new 
            dict.
        '''
        new_kwargs = {}
        for argName, argVal in kwargs.items():
            if argName.lower() in keep_list:
                new_kwargs[argName.lower()] = argVal
        return new_kwargs


    def _augment_text_w_syntactic_info( self, text, text_layer ):
        ''' Augments given Text object with the syntactic information 
            from the *text_layer*. More specifically, adds information 
            about SYNTAX_LABEL, SYNTAX_HEAD and DEPREL to each token 
            in the Text object;
            
            (!) Note: this method is added to provide some initial
            consistency with MaltParser based syntactic parsing;
            If a better syntactic parsing interface is achieved in
            the future, this method will be deprecated ...
        '''
        j = 0
        for sentence in text.divide( layer=WORDS, by=SENTENCES ):
            for i in range(len(sentence)):
                estnltkToken = sentence[i]
                vislcg3Token = text_layer[j]
                parse_found = False
                if PARSER_OUT in vislcg3Token:
                    if len( vislcg3Token[PARSER_OUT] ) > 0:
                        firstParse = vislcg3Token[PARSER_OUT][0]
                        # Fetch information about the syntactic relation:
                        estnltkToken[SYNTAX_LABEL] = str(i)
                        estnltkToken[SYNTAX_HEAD]  = str(firstParse[1])
                        # Fetch the name of the surface syntactic relation
                        deprels = '|'.join( [p[0] for p in vislcg3Token[PARSER_OUT]] )
                        estnltkToken[DEPREL]       = deprels
                        parse_found = True
                if not parse_found:
                    raise Exception("(!) Unable to retrieve syntactic analysis for the ",\
                                    estnltkToken, ' from ', vislcg3Token )
                j += 1

