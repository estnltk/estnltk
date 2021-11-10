#
#    This is a part of the verb chain detector source from the version 1.4.1:
#       https://github.com/estnltk/estnltk/blob/a8f5520b1c4d26fd58223ffc3f0a565778b3d99f/estnltk/mw_verbs/utils.py
#       ( ported with slight modifications )
#
#     *   *   *   *
#
#     Various utilities that provide support for:
#      *) indexing words (adding wordIDs, clauseIDs);
#      *) processing/filtering morphologically annotated text tokens;
#

import re

from estnltk.taggers.miscellaneous.verb_chains.v1_4_1.vcd_common_names import *

# ================================================================
#    Indexing word tokens: add WORD_ID to each word 
#    (unique within the sentence)
# ================================================================
def addWordIDs(jsonSent):
    for i in range(len(jsonSent)):
        if WORD_ID in jsonSent[i]:
            assert jsonSent[i][WORD_ID] == i, ' Unexpected existing wordID: '+str(jsonSent[i][WORD_ID])
        jsonSent[i][WORD_ID] = i
    return jsonSent

def removeWordIDs(jsonSent):
    for i in range(len(jsonSent)):
        del jsonSent[i][WORD_ID]
    return jsonSent

def getWordIDrange(a, b, jsonSent):
    tokens = []
    for i in range(len(jsonSent)):
        assert WORD_ID in jsonSent[i], "Missing wordID in "+str(jsonSent[i])
        if a <= jsonSent[i][WORD_ID] and jsonSent[i][WORD_ID] < b:
            tokens.append( jsonSent[i] )
    return tokens


# ================================================================
#    Separating sentence into clauses: for each clause,
#    return a group of words belonging to that clause
# ================================================================
def getClausesByClauseIDs(jsonSent):
    clauses   = dict()
    for tokenStruct in jsonSent:
        assert CLAUSE_IDX in tokenStruct, ' clauseID not found in: '+str(tokenStruct)
    clauseIDs = [tokenStruct[CLAUSE_IDX] for tokenStruct in jsonSent]
    for i in range(len(jsonSent)):
        tokenJson = jsonSent[i]
        clauseId  = tokenJson[CLAUSE_IDX]
        if clauseId not in clauses:
            clauses[clauseId] = []
        clauses[clauseId].append( tokenJson )
    return clauses


# ================================================================
#   A Template for filtering word tokens based on textual and 
#   morphological constraints;
# ================================================================
class WordTemplate:
    ''' A template for filtering word tokens based on morphological and other constraints.
        WordTemplate can be used, for example, to extract words that have a special 
        part-of-speech (e.g verb, noun), or a special morphological case (e.g. inessive, 
        allative).
        
        It is required that the input word token has been morphologically analysed by 
        pyvabamorf, and is in corresponding JSON-style data structure, which contains 
        morphological analyses of the word and its surface textual information:
            {ANALYSIS: [{'clitic': ...,
                           'ending': ...,
                           'form':   ...,
                           'lemma':  ...,
                           'partofspeech': ...,
                           'root': ...,
                           'root_tokens': ... },
                           ... ],
             'text': ... 
            }
        
        Constraints are defined as regular expressions which are used to check whether 
        the string value of the key (e.g. value of "root", "partofspeech") matches the 
        regular expression. 
        
    '''
    analysisRules  = None
    analysisFields = [ROOT, POSTAG, ENDING, FORM, CLITIC, LEMMA]
    otherRules     = None
    def __init__(self, newRules):
        '''A template for filtering word tokens based on morphological and other constraints.
        
           Parameters
           ----------
           newRules: dict of str
                Pairs consisting of an analysis keyword (e.g. 'partofspeech', 'root', 'text' 
                etc) and a regular expression describing required value of that keyword.
        '''
        assert isinstance(newRules, dict), "newRules should be dict!"
        for ruleKey in newRules:
            self.addRule(ruleKey, newRules[ruleKey])

    def addRule(self, field, regExpPattern):
        '''Adds new rule for checking whether a value of the field matches given regular 
           expression regExpPattern;
        
           Parameters
           ----------
           field: str
                keyword, e.g. 'partofspeech', 'root', 'text' etc
           regExpPattern: str
                a regular expression that the value of the field must match (using method 
                re.match( regExpPattern, token[field]) ).
        '''
        compiled = re.compile( regExpPattern )
        if field in self.analysisFields:
            if self.analysisRules == None:
                self.analysisRules = dict()
            self.analysisRules[field] = compiled
        else:
            if self.otherRules == None:
                self.otherRules = dict()
            self.otherRules[field] = compiled

    # =============================================
    #    Matching a single token
    # =============================================
    
    def matches(self, tokenJson):
        '''Determines whether given token (tokenJson) satisfies all the rules listed 
           in the WordTemplate. If the rules describe tokenJson[ANALYSIS], it is 
           required that at least one item in the list tokenJson[ANALYSIS] satisfies 
           all the rules (but it is not required that all the items should satisfy). 
           Returns a boolean value.
        
           Parameters
           ----------
           tokenJson: pyvabamorf's analysis of a single word token;
        '''
        if self.otherRules != None:
            otherMatches = []
            for field in self.otherRules:
                match = field in tokenJson and ((self.otherRules[field]).match(tokenJson[field]) != None)
                otherMatches.append( match )
            if not otherMatches or not all(otherMatches):
                return False
            elif self.analysisRules == None and all(otherMatches):
                return True
        if self.analysisRules != None:
            assert ANALYSIS in tokenJson, "No ANALYSIS found within token: "+str(tokenJson)
            totalMatches = []
            for analysis in tokenJson[ANALYSIS]:
                # Check whether this analysis satisfies all the rules 
                # (if not, discard the analysis)
                matches = []
                for field in self.analysisRules:
                    value = analysis[field] if field in analysis else ""
                    match = (self.analysisRules[field]).match(value) != None
                    matches.append( match )
                    if not match:
                        break
                totalMatches.append( all(matches) )
            #  Return True iff there was at least one analysis that 
            # satisfied all the rules;
            return any(totalMatches)
        return False

    def matchingAnalyses(self, tokenJson):
        '''Determines whether given token (tokenJson) satisfies all the rules listed 
           in the WordTemplate and returns a list of analyses (elements of 
           tokenJson[ANALYSIS]) that are matching all the rules. An empty list is 
           returned if none of the analyses match (all the rules), or (!) if none of 
           the rules are describing the ANALYSIS part of the token;
        
           Parameters
           ----------
           tokenJson: pyvabamorf's analysis of a single word token;
        '''
        matchingResults = []
        if self.otherRules != None:
            otherMatches = []
            for field in self.otherRules:
                match = field in tokenJson and ((self.otherRules[field]).match(tokenJson[field]) != None)
                otherMatches.append( match )
            if not otherMatches or not all(otherMatches):
                return matchingResults
        if self.analysisRules != None:
            assert ANALYSIS in tokenJson, "No ANALYSIS found within token: "+str(tokenJson)
            for analysis in tokenJson[ANALYSIS]:
                # Check whether this analysis satisfies all the rules 
                # (if not, discard the analysis)
                matches = []
                for field in self.analysisRules:
                    value = analysis[field] if field in analysis else ""
                    match = (self.analysisRules[field]).match(value) != None
                    matches.append( match )
                if matches and all(matches):
                    matchingResults.append( analysis )
            #  Return True iff there was at least one analysis that 
            # satisfied all the rules;
            return matchingResults
        return matchingResults

    def matchingAnalyseIndexes(self, tokenJson):
        '''Determines whether given token (tokenJson) satisfies all the rules listed 
           in the WordTemplate and returns a list of analyse indexes that correspond 
           to tokenJson[ANALYSIS] elements that are matching all the rules. 
           An empty list is returned if none of the analyses match (all the rules), 
           or (!) if none of the rules are describing the ANALYSIS part of the 
           token;

           Parameters
           ----------
           tokenJson: pyvabamorf's analysis of a single word token;
        '''
        matchingResults = self.matchingAnalyses(tokenJson)
        if matchingResults:
            indexes = [ tokenJson[ANALYSIS].index(analysis) for analysis in matchingResults ]
            return indexes
        return matchingResults

    # =============================================
    #    Matches from a list of tokens
    # =============================================

    def matchingPositions(self, tokenArray):
        '''Returns a list of positions (indexes) in the tokenArray where this WordTemplate
           matches (the method self.matches(token) returns True). Returns an empty list if
           no matching tokens appear in the input list.

           Parameters
           ----------
           tokenArray: list of word tokens;
                A list of word tokens along with their pyvabamorf's analyses;
        '''
        assert isinstance(tokenArray, list), "tokenArray should be list "+str(tokenArray)
        matchingPos = []
        for i in range( len(tokenArray) ):
            token = tokenArray[i]
            if self.matches(token):
                matchingPos.append( i )
        return matchingPos

    def matchingTokens(self, tokenArray):
        '''Returns a list of tokens in the tokenArray that match this WordTemplate (the 
           method self.matches(token) returns True). Returns an empty list if no matching 
           tokens appear in the input list.

           Parameters
           ----------
           tokenArray: list of word tokens;
                A list of word tokens along with their pyvabamorf's analyses;
        '''
        assert isinstance(tokenArray, list), "tokenArray should be list "+str(tokenArray)
        matchingTok = []
        for i in range( len(tokenArray) ):
            token = tokenArray[i]
            if self.matches(token):
                matchingTok.append( token )
        return matchingTok
