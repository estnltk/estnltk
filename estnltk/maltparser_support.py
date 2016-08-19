# -*- coding: utf-8 -*- 
#
#      Support for parsing EstNLTK texts with Java-based Maltparser
#     with the goal of obtaining syntactic dependencies between words;
#
#     Current performance:
#     1) model 'estnltkBasedDep2' (default):
#      (adds both dependency relations, and surface syntactic labels)
#      accuracy / Metric:LA   accuracy / Metric:UAS   accuracy / Metric:LAS   Token
#      --------------------------------------------------------------------------------
#      0.789                  0.801                   0.72                    Row mean
#      24208                  24208                   24208                   Row count
#      --------------------------------------------------------------------------------
#
#     2) model 'estnltkBasedDep' (former model):
#      (only adds dependency relations, no syntactic labels)
#      accuracy / Metric:UAS     Token
#      -------------------------------------
#      0.786                     Row mean
#      24208                     Row count
#      -------------------------------------
#


from __future__ import unicode_literals, print_function
from .names import *
from .text import Text

from .core import PACKAGE_PATH

import re, json
import os, os.path
import codecs
import tempfile
import subprocess

MALTPARSER_PATH  = os.path.join(PACKAGE_PATH, 'java-res', 'maltparser')
MALTPARSER_MODEL = 'estnltkBasedDep2'
MALTPARSER_JAR   = 'maltparser-1.8.jar'


# =============================================================================
# =============================================================================
#  Converting data from estnltk JSON to CONLL
# =============================================================================
# =============================================================================

def __sort_analyses(sentence):
    ''' Sorts analysis of all the words in the sentence. 
        This is required for consistency, because by default, analyses are 
        listed in arbitrary order; '''
    for word in sentence:
        if ANALYSIS not in word:
            raise Exception( '(!) Error: no analysis found from word: '+str(word) )
        else:
            word[ANALYSIS] = sorted(word[ANALYSIS], \
                key=lambda x : "_".join( [x[ROOT],x[POSTAG],x[FORM],x[CLITIC]] ))
    return sentence


def convertTextToCONLLstr( text, addDepLabels = False, addAmbiguousPos = False, \
                                 addKSubCatRels = None ):
    ''' Converts given estnltk Text object into CONLL format data and
        returns as a string.
        
        Parameters
        -----------
        addDepLabels : bool
            If True, adds information about the syntactic parent of each token 
            to the data (required for training). 
            The parent's index should be accessible from estnltkWord[SYNTAX_HEAD].
            Also adds the name of the syntactic relation, if it is accessible 
            via  estnltkWord[DEPREL];
        addAmbiguousPos : bool
            If True, additional feature (fine-grained POS tag) will be added to 
            tokens with ambiguous POS, which contains contatenation of all POS 
            tags;
        addKSubCatRels : dict
            This should point to the dictionary loaded with the method
            _loadKSubcatRelations(), which is used to provide more fine-grained 
            information about postposition/preposition tokens (K tokens); 
            If None, then the functionality is not used;
            
    '''
    sentenceStrs = []
    for sentence in text.divide( layer=WORDS, by=SENTENCES ):
        sentence  = __sort_analyses(sentence)
        kFeatures = dict()
        if addKSubCatRels:
            kFeatures = \
                _findKsubcatFeatures( sentence, addKSubCatRels, addFeaturesToK = True )
        for i in range(len(sentence)):
            #
            #  Aimed CONLL format:
            # 1	Öö	öö	S	S	sg|nom	2	xxx	_	_
            # 2	oli	ole	V	V	indic|impf|ps3|sg	0	ROOT	_	_
            # 3	täiesti	täiesti	D	D	_	4	xxx	_	_
            # 4	tuuletu	tuuletu	A	A	sg|nom	2	xxx	_	_
            # 5	.	.	Z	Z	Fst	4	xxx	_	_
            #          
            estnltkWord = sentence[i]
            strForm = []
            if addDepLabels:
                strForm.append( estnltkWord[SYNTAX_LABEL] )
            else:
                strForm.append( str(i+1) )
            strForm.append( '\t' )
            strForm.append( estnltkWord[TEXT] )
            strForm.append( '\t' )
            
            # Pick the first analysis
            firstAnalysis = estnltkWord[ANALYSIS][0]
            # Root
            wordRoot = firstAnalysis[ROOT]
            if len(wordRoot) == 0:
                wordRoot = "??"
            strForm.append( wordRoot )
            strForm.append( '\t' )
            # Part of speech
            strForm.append( firstAnalysis[POSTAG] )
            strForm.append( '\t' )
            finePos = firstAnalysis[POSTAG]
            if addAmbiguousPos and len(estnltkWord[ANALYSIS]) > 1:
                pos_tags = sorted(list(set([ a[POSTAG] for a in estnltkWord[ANALYSIS] ])))
                finePos  = '_'.join(pos_tags)
            if i in kFeatures:
                finePos += '|'+kFeatures[i]
            strForm.append( finePos )
            strForm.append( '\t' )
            # Grammatical categories
            grammCats = '_'
            if len(firstAnalysis[FORM]) != 0:
                forms = firstAnalysis[FORM].split()
                grammCats = '|'.join(forms)
            strForm.append( grammCats )
            strForm.append( '\t' )
            # Syntactic parent
            parentLabel = ''
            if addDepLabels:
                parentLabel = (estnltkWord[SYNTAX_HEAD]).strip()
                strForm.append( parentLabel )
                strForm.append( '\t' )
            else:
                strForm.append( '_' )
                strForm.append( '\t' )
            # Label of the syntactic relation
            if parentLabel == '0':
                strForm.append( 'ROOT' )
                strForm.append( '\t' )
            else:
                if addDepLabels and DEPREL in estnltkWord:
                   strForm.append( estnltkWord[DEPREL] )
                else:
                   strForm.append( 'xxx' )
                strForm.append( '\t' )
            # Last features, PHEAD and PDEPREL, are not available:
            strForm.append( '_' )
            strForm.append( '\t' )
            strForm.append( '_' )
            sentenceStrs.append( ''.join( strForm ) )
        sentenceStrs.append( '' )
    return '\n'.join( sentenceStrs )

# =============================================================================
# =============================================================================
#  Executing MaltParser on CONLL formatted estnltk Text
# =============================================================================
# =============================================================================

def _executeMaltparser( input_string, maltparser_dir, maltparser_jar, model_name ):
    ''' Executes Maltparser on given (CONLL-style) input string, and 
        returns the result. The result is an array of lines from Maltparser's 
        output.
        
        Parameters
        ----------
        input_string: string
              input text in CONLL format;
        maltparser_jar: string
              name of the Maltparser's jar file that should be executed;
        model_name: string
              name of the model that should be used;
        maltparser_dir: string
              the directory containing Maltparser's jar and the model file; 
        
        Few of the ideas were also borrowed from NLTK's MaltParser class,
        see  http://www.nltk.org/_modules/nltk/parse/malt.html   for the reference;
    '''

    temp_input_file = \
      tempfile.NamedTemporaryFile(prefix='malt_in.', mode='w', delete=False)
    temp_input_file.close()
    # We have to open separately here for writing, because Py 2.7 does not support
    # passing parameter   encoding='utf-8'    to the NamedTemporaryFile;
    out_f = codecs.open(temp_input_file.name, mode='w', encoding='utf-8')
    out_f.write( input_string )
    out_f.close()

    temp_output_file = tempfile.NamedTemporaryFile(prefix='malt_out.', mode='w', delete=False)
    temp_output_file.close()
    
    current_dir = os.getcwd()
    os.chdir(maltparser_dir)
    cmd = ['java', '-jar', os.path.join(maltparser_dir, maltparser_jar), \
           '-c', model_name, \
           '-i', temp_input_file.name, \
           '-o', temp_output_file.name, \
           '-m', 'parse' ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait() != 0: 
        raise Exception(' Error on running Maltparser: ', p.stderr.read() )
    os.chdir(current_dir)
    
    results = []
    in_f = codecs.open(temp_output_file.name, mode='r', encoding='utf-8')
    for line in in_f:
        results.append( line.rstrip() )
    in_f.close()

    if not temp_input_file.closed:
        raise Exception('Temp input file unclosed!')
    if not temp_output_file.closed:
        raise Exception('Temp input file unclosed!')
    if not out_f.closed:
        raise Exception('Output file unclosed!')
    if not in_f.closed:
        raise Exception('Input file unclosed!')
    # TODO: For some reason, the method gives "ResourceWarning: unclosed file"
    # in Python 3.4, although, apparently, all file handles seem to be closed;
    # Nothing seems to be wrong in Python 2.7;

    os.remove(temp_input_file.name)
    os.remove(temp_output_file.name)

    return results

# =============================================================================
# =============================================================================
#  Converting data from CONLL to estnltk JSON
# =============================================================================
# =============================================================================

def loadCONLLannotations( in_file, addDepRels = False, splitIntoSentences = True ):
    ''' Loads syntactically annotated text from CONLL format input file and 
        returns as an array of tokens, where each token is represented as 
        an array in the format:
           [sentenceID, wordID, tokenString, morphInfo, selfID, parentID]
        If addDepRels == True, then the dependency relation label is also extracted
        and added to the end of the array:
           [sentenceID, wordID, tokenString, morphInfo, selfID, parentID, depRel]
        If splitIntoSentences == True, the array of tokens is further divided
        into subarrays representing sentences.
        
         Example input:
        2	Monstrumteleskoobid	Monstrum_tele_skoop	S	S	prop|pl|nom	0	ROOT	_	_
        3	(	(	Z	Z	Opr	4	xxx	_	_
        4	mosaiik-	mosaiik	A	A	pos|sg|nom	2	@<AN	_	_
        5	ja	ja	J	J	crd	6	@J	_	_
        6	mitmepeeglilised	mitme_peegli=line	A	A	pos|pl|nom	4	@<NN	_	_
        7	)	)	Z	Z	Cpr	6	xxx	_	_
        8	.	.	Z	Z	Fst	7	xxx	_	_
        
    '''
    sentenceCount   = 0
    wordCountInSent = 0
    tokens = []
    in_f = codecs.open(in_file, mode='r', encoding='utf-8')
    for line in in_f:
        line = line.rstrip()
        if len(line) == 0 or re.match('^\s+$', line):
            sentenceCount += 1
            wordCountInSent = 0
            continue
        features = line.split('\t')
        if len(features) != 10:
            raise Exception(' In file '+in_file+', line with unexpected format: "'+line+'" ')
        selfLabel   = features[0]
        token       = features[1]
        lemma       = features[2]
        cpos        = features[3]
        pos         = features[4]
        form        = features[5]
        parentLabel = features[6]
        tokens.append( [ str(sentenceCount), str(wordCountInSent), \
                         token, lemma+" "+pos+" "+form, selfLabel, parentLabel ] )
        if addDepRels:
            tokens[-1].append( features[7] )
        wordCountInSent += 1
    in_f.close()
    if not splitIntoSentences:
        return tokens
    else:
        sentences = []
        lastSentID = ''
        for tok in tokens:
            if tok[0] != lastSentID:
                sentences.append([])
            sentences[-1].append(tok)
            lastSentID = tok[0]
        return sentences


def convertCONLLtoText( in_file, addDepRels = False, verbose = False, **kwargs ):
    ''' Loads CONLL format data from given input file, and creates
        estnltk Text objects from the data, one Text per each 
        sentence. Returns a list of Text objects.
        
        By default, applies estnltk's morphological analysis, clause 
        detection, and verb chain detection to each input sentence.
        
        If addDepRels == True, in addition to SYNTAX_LABEL and SYNTAX_HEAD,
        surface syntactic function (DEPREL) is also attributed to each 
        token;
    '''
    sentences = loadCONLLannotations( in_file, addDepRels = addDepRels, \
                                               splitIntoSentences = True )
    if verbose:
        print( str(len(sentences))+' sentences loaded. ')
    estnltkSentTexts = []
    for i in range(len(sentences)):
        s  = sentences[i]
        sentenceString = " ".join( [ t[2] for t in s ] )
        sentText = Text(sentenceString, **kwargs)
        sentText.tag_analysis()
        sentText.tag_clauses()
        sentText.tag_verb_chains()
        sentText = dict(sentText)
        if len(sentText[WORDS]) == len(s):
            # Add the dependency syntactic information
            for j in range(len(sentText[WORDS])):
                estnltkWord   = sentText[WORDS][j]
                depSyntaxWord = s[j]
                estnltkWord[SYNTAX_LABEL] = depSyntaxWord[4]
                estnltkWord[SYNTAX_HEAD]  = depSyntaxWord[5]
                if addDepRels:
                   estnltkWord[DEPREL] = depSyntaxWord[6]
            estnltkSentTexts.append( sentText )
            if verbose:
                print ('*', end = '')
        else:
            if verbose:
                print("The sentence segmentation of dependency syntax differs from the estnltk's sentence segmentation:", len(sentText[WORDS]), ' vs ',len(s))
    return estnltkSentTexts


def augmentTextWithCONLLstr( conll_str_array, text ):
    ''' Augments given Text object with the information from Maltparser's output.
        More specifically, adds information about SYNTAX_LABEL, SYNTAX_HEAD and
        DEPREL to each token in the Text object;
    '''
    j = 0
    for sentence in text.divide( layer=WORDS, by=SENTENCES ):
        sentence = __sort_analyses(sentence)
        for i in range(len(sentence)):
            estnltkToken    = sentence[i]
            maltparserToken = conll_str_array[j]
            if len( maltparserToken ) > 1:
                maltParserAnalysis = maltparserToken.split('\t')
                if estnltkToken[TEXT] == maltParserAnalysis[1]:
                    # Fetch information about the syntactic relation:
                    estnltkToken[SYNTAX_LABEL] = maltParserAnalysis[0]
                    estnltkToken[SYNTAX_HEAD]  = maltParserAnalysis[6]
                    # Fetch the name of the surface syntactic relation
                    estnltkToken[DEPREL]       = maltParserAnalysis[7]
                else:
                    raise Exception("A misalignment between Text and Maltparser's output: ",\
                        estnltkToken, maltparserToken )
            j += 1
        j += 1


def align_CONLL_with_Text( lines, text, **kwargs ):
    ''' Aligns CONLL format syntactic analysis (a list of strings) with given EstNLTK's Text 
        object.
        Basically, for each word position in the Text object, finds corresponding line(s) in
        the CONLL format output;

        Returns a list of dicts, where each dict has following attributes:
          'start'   -- start index of the word in Text;
          'end'     -- end index of the word in Text;
          'sent_id' -- index of the sentence in Text, starting from 0;
          'parser_out' -- list of analyses from the output of the syntactic parser;

        Parameters
        -----------
        lines : list of str
            The input text for the pipeline; Should be the CONLL format syntactic analysis;

        text : Text
            EstNLTK Text object containing the original text that was analysed with
            MaltParser;

        check_tokens : bool
            Optional argument specifying whether tokens should be checked for match 
            during the alignment. In case of a mismatch, an exception is raised.
            Default:False
            
        add_word_ids : bool
            Optional argument specifying whether each alignment should include attributes:
            * 'text_word_id' - current word index in the whole Text, starting from 0;
            * 'sent_word_id' - index of the current word in the sentence, starting from 0;
            Default:False
        
    ''' 
    if not isinstance( text, Text ):
        raise Exception('(!) Unexpected type of input argument! Expected EstNLTK\'s Text. ')
    if not isinstance( lines, list ):
        raise Exception('(!) Unexpected type of input argument! Expected a list of strings.')
    check_tokens = False
    add_word_ids = False
    for argName, argVal in kwargs.items() :
        if argName in ['check_tokens', 'check'] and argVal in [True, False]:
           check_tokens = argVal
        if argName in ['add_word_ids', 'word_ids'] and argVal in [True, False]:
           add_word_ids = argVal
    generalWID = 0
    sentenceID = 0
    # Iterate over the sentences and perform the alignment
    results = []
    j = 0
    for sentence in text.divide( layer=WORDS, by=SENTENCES ):
        for i in range(len(sentence)):
            estnltkToken    = sentence[i]
            maltparserToken = lines[j]
            if len( maltparserToken ) > 1:
                maltParserAnalysis = maltparserToken.split('\t')
                if check_tokens and estnltkToken[TEXT] != maltParserAnalysis[1]:
                    raise Exception("(!) A misalignment between Text and CONLL: ",\
                                    estnltkToken, maltparserToken )
                # Populate the alignment
                result_dict = { START:estnltkToken[START], END:estnltkToken[END], \
                                'sent_id':sentenceID, 'parser_out': [maltparserToken] }
                if add_word_ids:
                    result_dict['text_word_id'] = generalWID # word id in the text
                    result_dict['sent_word_id'] = i          # word id in the sentence
                results.append( result_dict )
            j += 1
            generalWID += 1
        sentenceID += 1
        j += 1
    return results


# =============================================================================
# =============================================================================
#   The Main Class
# =============================================================================
# =============================================================================

class MaltParser:
    '''  A wrapper around Java-based MaltParser. Allows to process estnltk Text
        objects with Maltparser in order to obtain dependency syntactic relations
        between the words in the sentence.
    '''

    maltparser_dir    = MALTPARSER_PATH
    model_name        = MALTPARSER_MODEL
    maltparser_jar    = MALTPARSER_JAR
    add_ambiguous_pos = True
    
    def __init__( self, **kwargs):
        ''' Initializes MaltParser's wrapper. 
        
            Parameters
            -----------
            maltparser_dir : str
                Directory that contains Maltparser jar file and model file;
                This directory is also used for storing temporary files, so 
                writing should be allowed in it;
                
            model_name : str
                Name of the Maltparser's model;
                
            maltparser_jar : str    
                Name of the Maltparser jar file (e.g. 'maltparser-1.8.jar');
                
            add_ambiguous_pos : boolean
                Whether ambiguous POS tags should be rewritten as a fine-grained 
                POS tags (see convertTextToCONLLstr() for details);
                NB! Requires that MaltParser has been trained with this setting;
        '''
        for argName, argVal in kwargs.items():
            if argName == 'maltparser_dir':
                self.maltparser_dir = argVal
            elif argName == 'model_name':
                self.model_name = argVal
            elif argName == 'maltparser_jar':
                self.maltparser_jar = argVal
            elif argName == 'add_ambiguous_pos':
                self.add_ambiguous_pos = bool(argVal)
            else:
                raise Exception(' Unsupported argument given: '+argName)
        if not self.maltparser_dir:
            raise Exception('Missing input argument: MaltParser directory')
        elif not os.path.exists(self.maltparser_dir):
            raise Exception('Invalid MaltParser directory:',self.maltparser_dir)
        elif not self.maltparser_jar:
            raise Exception('Missing input argument: MaltParser jar file name')
        elif not self.model_name:
            raise Exception('Missing input argument: MaltParser model name')


    def parse_text( self, text, **kwargs ):
        ''' Parses given text with Maltparser. 
        
            As a result of parsing, attributes indicating the dependency tree 
            structure will be attached to each word token in text: 
            the attribute SYNTAX_LABEL is the index of the token in the 
            tree, 
            the attribute SYNTAX_HEAD is the index of token's parent in the 
            tree, and 
            the attribute DEPREL is the name of the dependency relation 
            (ROOT, @SUBJ, @OBJ, @ADVL etc.);
            
            Parameters
            -----------
            text : estnltk.text.Text
               The input text that should be analysed for dependency relations;
            
            return_type : string
               If return_type=="text" (Default), 
                    returns the input Text object;
               If return_type=="conll", 
                    returns Maltparser's results as list of CONLL format strings, 
                    each element in the list corresponding to one line in 
                    MaltParser's output;
               If return_type=="dep_graphs", 
                    returns Maltparser's results as list of NLTK's DependencyGraph 
                    objects (nltk.parse.dependencygraph.DependencyGraph);
               Regardless the return type, words in the input Text will be 
               augmented with syntactic dependency information;

        '''
        all_return_types = ["text", "conll", "dep_graphs"]
        return_type      = all_return_types[0]
        for argName, argVal in kwargs.items():
            if argName == 'return_type':
                if argVal.lower() in all_return_types:
                    return_type = argVal.lower()
                else:
                    raise Exception(' Unexpected return type: ', argVal)
            else:
                raise Exception(' Unsupported argument given: '+argName)
        # If text has not been morphologically analysed yet, add the 
        # morphological analysis
        if not text.is_tagged(ANALYSIS):
            text.tag_analysis()
        # Obtain CONLL formatted version of the text
        textConllStr = convertTextToCONLLstr(text, addDepLabels = False, \
                                                   addAmbiguousPos = self.add_ambiguous_pos)
        # Execute MaltParser and get results as CONLL formatted string
        resultsConllStr = \
            _executeMaltparser( textConllStr, self.maltparser_dir, \
                                              self.maltparser_jar, \
                                              self.model_name )
        # Augment the input text with the dependency relation information 
        # obtained from MaltParser
        augmentTextWithCONLLstr( resultsConllStr, text )
        
        if return_type == "conll":
            # Return CONLL
            return resultsConllStr
        elif return_type == "dep_graphs":
            # Return DependencyGraphs
            from nltk.parse.dependencygraph import DependencyGraph
            all_trees = []
            for tree_str in ("\n".join(resultsConllStr)).split('\n\n'):
                t = DependencyGraph(tree_str)
                all_trees.append(t)
            return all_trees
        else:
            # Return Text
            return text


# =============================================================================
# =============================================================================
#   Experimental stuff:  Tuning maltparser with additional features
# =============================================================================
# =============================================================================

# =============================
#   K subcat relations
# =============================

def _loadKSubcatRelations( inputFile ):
    ''' Laeb sisendfailist (inputFile) kaassõnade rektsiooniseoste mustrid.
        Iga muster peab olema failis eraldi real, kujul:
        (sõnalemma);(sõnaliik);(post|pre);(nõutud_käänete_regexp)
        nt
            ees;_K_;post;g
            eest;_K_;post;g
            enne;_K_;pre;p
        Tagastab laetud andmed sõnastikuna;
    '''
    kSubCatRelations = dict()
    in_f = codecs.open(inputFile, mode='r', encoding='utf-8')
    for line in in_f:
        line = line.rstrip()
        if len(line) > 0 and not re.match("^#.+$", line):
            items = line.split(';')
            if len(items) == 4:
                root         = items[0]
                partofspeech = items[1]
                postPre      = items[2]
                morphPattern = items[3]
                fpattern = '(sg|pl)\s'+morphPattern
                if root not in kSubCatRelations:
                    kSubCatRelations[root] = []
                kSubCatRelations[root].append( [postPre, fpattern] )
                root_clean = root.replace('_', '')
                if root != root_clean:
                    if root_clean not in kSubCatRelations:
                        kSubCatRelations[root_clean] = []
                    kSubCatRelations[root_clean].append( [postPre, fpattern] )
            else:
                raise Exception(' Unexpected number of items in the input lexicon line: '+line)
    in_f.close()
    return kSubCatRelations


def _detectKsubcatRelType( sentence, i, kSubCatRelsLexicon ):
    ''' Given the adposition appearing in the sentence at the location i,
        checks whether the adposition appears in the kSubCatRelsLexicon, 
        and if so, attempts to further detect whether the adposition is a 
        preposition or a postposition;
         Returns a tuple (string, int), where the first item indicates the
        type of adposition ('pre', 'post', '_'), and the second item points
        to its possible child (index of the word in sentence, or -1, if 
        possible child was not detected from close range);
    ''' 
    curToken = sentence[i]
    root = curToken[ANALYSIS][0][ROOT]
    if root in kSubCatRelsLexicon:
        for [postPre, fpattern] in kSubCatRelsLexicon[root]:
            if postPre == 'post' and i-1 > -1:
                lastTokenAnalysis = sentence[i-1][ANALYSIS][0]
                if re.match(fpattern, lastTokenAnalysis[FORM]):
                    return ('post', i-1)
            elif postPre == 'pre' and i+1 < len(sentence):
                nextTokenAnalysis = sentence[i+1][ANALYSIS][0]
                if re.match(fpattern, nextTokenAnalysis[FORM]):
                    return ('pre', i+1)
        # If the word is not ambiguous between pre and post, but
        # the possible child was not detected, return only the
        # post/pre label:
        if len(kSubCatRelsLexicon[root]) == 1:
            return (kSubCatRelsLexicon[root][0][0], -1)
    return ('_', -1)


def _detectPossibleKsubcatRelsFromSent( sentence, kSubCatRelsLexicon, reverseMapping = False ):
    ''' Attempts to detect all possible K subcategorization relations from
        given sentence, using the heuristic method _detectKsubcatRelType();
        
        Returns a dictionary of relations where the key corresponds to the
        index of its parent node (the K node) and the value corresponds to 
        index of its child.
        
        If reverseMapping = True, the mapping is reversed: keys correspond
        to children and values correspond to parent nodes (K-s);
    '''
    relationIndex = dict()
    relationType  = dict()
    for i in range(len(sentence)):
        estnltkWord = sentence[i]
        # Pick the first analysis
        firstAnalysis = estnltkWord[ANALYSIS][0]
        if firstAnalysis[POSTAG] == 'K':
            (grammCats, kChild) = _detectKsubcatRelType( sentence, i, kSubCatRelsLexicon )
            if kChild != -1:
                if reverseMapping:
                    relationIndex[ kChild ] = i
                    relationType[ kChild ]  = grammCats
                else:
                    relationIndex[ i ] = kChild
                    relationType[ i ]  = grammCats
    return relationIndex, relationType


def _findKsubcatFeatures( sentence, kSubCatRelsLexicon, addFeaturesToK = True ):
    ''' Attempts to detect all possible K subcategorization relations from
        given sentence, using the heuristic methods _detectKsubcatRelType() 
        and _detectPossibleKsubcatRelsFromSent();
        
        Returns a dictionary where the keys correspond to token indices,
        and values are grammatical features related to K subcat relations.
        Not all tokens in the sentence are indexed, but only tokens relevant
        to K subcat relations;
        
        If addFeaturesToK == True, grammatical features are added to K-s,
        otherwise, grammatical features are added to K's child tokens.
    '''
    features = dict()
    # Add features to the K (adposition)
    if addFeaturesToK:
        for i in range(len(sentence)):
            estnltkWord = sentence[i]
            # Pick the first analysis
            firstAnalysis = estnltkWord[ANALYSIS][0]
            if firstAnalysis[POSTAG] == 'K':
                (grammCats, kChild) = _detectKsubcatRelType( sentence, i, kSubCatRelsLexicon )
                features[i] = grammCats
    # Add features to the noun governed by K
    else:
        relationIndex, relationType = \
            _detectPossibleKsubcatRelsFromSent( sentence, kSubCatRelsLexicon, reverseMapping = True )
        for i in relationIndex:
            features[i] = relationType[i]
    return features    

