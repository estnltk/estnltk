# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

"""Mid-level module for interacting with Estonian WordNet. Uses Neeme Kahusk's eurown module to parse WordNet file.
"""

import os
import re
import math
import codecs
from collections import defaultdict

try:
    from StringIO import StringIO
except ImportError: # Py3
    from io import StringIO
    
from estnltk.wordnet.eurown import Parser
from estnltk import analyze
from estnltk.core import PACKAGE_PATH
from estnltk.core import as_unicode

WORDNET_DIR = os.path.join(PACKAGE_PATH, 'wordnet')
DATA_DIR = os.path.join(WORDNET_DIR, "data")

_LIT_POS_FILE = os.path.join(DATA_DIR, "lit_pos_synidx.txt")
_SOI = os.path.join(DATA_DIR, "kb69a-utf8.soi")
_WN_FILE = os.path.join(DATA_DIR, "kb69a-utf8.txt")
_SENSE_FILE = os.path.join(DATA_DIR, "sense.txt")
_MAX_TAX_FILE = os.path.join(DATA_DIR, "max_tax_depths.cnf")

VERB = 'v'
NOUN = 'n'
ADJ = 'a'
ADV = 'b'

MAX_TAXONOMY_DEPTHS = {} # necessary for Leacock & Chodorow similarity measure

parser = None

with codecs.open(_MAX_TAX_FILE,'rb', 'utf-8') as fin:
    for line in fin:
        pos,max_depth = line.strip().split(':')
        MAX_TAXONOMY_DEPTHS[pos] = int(max_depth)

SYNSETS_DICT = {} # global dictionary which stores initialized synsets
LEMMAS_DICT = {}

LEM_POS_2_SS_IDX = defaultdict(lambda: defaultdict(list)) # map lemma and pos to synset index

LOADED_POS = set()

def _get_synset_offsets(synset_idxes):
    """Returs pointer offset in the WordNet file for every synset index.

    Notes
    -----
    Internal function. Do not call directly.
    Preserves order -- for [x,y,z] returns [offset(x),offset(y),offset(z)].

    Parameters
    ----------
    synset_idxes : list of ints
      Lists synset IDs, which need offset.
      
    Returns
    -------
    list of ints
      Lists pointer offsets in Wordnet file.


    """
    offsets = {}
    current_seeked_offset_idx = 0

    ordered_synset_idxes = sorted(synset_idxes)

    with codecs.open(_SOI,'rb', 'utf-8') as fin:
        for line in fin:
            split_line = line.split(':')
          
            while current_seeked_offset_idx < len(ordered_synset_idxes) and split_line[0] == str(ordered_synset_idxes[current_seeked_offset_idx]):
                # Looping on single line entries in case synset_indexes contains duplicates.
                offsets[synset_idxes[current_seeked_offset_idx]] = int(split_line[1])
                current_seeked_offset_idx += 1
            if current_seeked_offset_idx >= len(synset_idxes):
                break
    return [offsets[synset_idx] for synset_idx in synset_idxes]

def _get_synsets(synset_offsets):
    """Given synset offsets in the WordNet file, parses synset object for every offset.

    Notes
    -----
    Internal function. Do not call directly.
    Stores every parsed synset into global synset dictionary under two keys:
      synset's name lemma.pos.sense_no and synset's id (unique integer).

    Parameters
    ----------
    synset_offsets : list of ints
      Lists pointer offsets from which synset objects will be parsed.
      
    Returns
    -------
    list of Synsets
      Lists synset objects which synset_offsets point to.

    """
    global parser
    if parser is None:
        parser = Parser(_WN_FILE)
    synsets = []

    for offset in synset_offsets:
        raw_synset = parser.parse_synset(offset)
        synset = Synset(raw_synset)

        SYNSETS_DICT[_get_key_from_raw_synset(raw_synset)] = synset
        SYNSETS_DICT[synset.id] = synset

        synsets.append(synset)

    return synsets

def _get_key_from_raw_synset(raw_synset):
    """Derives synset key in the form of `lemma.pos.sense_no` from the provided eurown.py Synset class,

    Notes
    -----
    Internal function. Do not call directly.


    Parameters
    ----------
    raw_synset : eurown.Synset
      Synset representation from which lemma, part-of-speech and sense is derived.

    Returns
    -------
    string
      Key of the synset in the form of `lemma.pos.sense_no`.
      
    """
    pos = raw_synset.pos
    literal = raw_synset.variants[0].literal
    sense = "%02d"%raw_synset.variants[0].sense
    return '.'.join([literal,pos,sense])

def synset(synset_key):
    """Returns synset object with the provided key.

    Notes
    -----
    Uses lazy initialization - synsets will be fetched from a dictionary after the first request.

    Parameters
    ----------
    synset_key : string
      Unique synset identifier in the form of `lemma.pos.sense_no`.
      
    Returns
    -------
    Synset
      Synset with key `synset_key`.
      None, if no match was found.

    """

    if synset_key in SYNSETS_DICT:
        return SYNSETS_DICT[synset_key]

    def _get_synset_idx(synset_key):
        """Returns synset index for the provided key.

        Note
        ----
          Internal function. Do not call directly.

        """
        with codecs.open(_SENSE_FILE,'rb', 'utf-8') as fin:
            for line in fin:
                split_line = line.split(':')
                if split_line[0] == synset_key:
                    return int(split_line[1].strip())
        return None

    synset_idx = _get_synset_idx(synset_key)

    if synset_idx == None:
        return None

    synset_offset = _get_synset_offsets([synset_idx])
    synset = _get_synsets(synset_offset)

    return synset[0]


def synsets(lemma,pos=None):
    """Returns all synset objects which have lemma as one of the variant literals and fixed pos, if provided.

    Notes
    -----
    Uses lazy initialization - parses only those synsets which are not yet initialized, others are fetched from a dictionary.

    Parameters
    ----------
    lemma : str
      Lemma of the synset.
    pos : str, optional
      Part-of-speech specification of the searched synsets, defaults to None.

    Returns
    -------
    list of Synsets
      Synsets which contain `lemma` and of which part-of-speech is `pos`, if specified.
      Empty list, if no match was found.

    """

    def _get_synset_idxes(lemma,pos):
        line_prefix_regexp = "%s:%s:(.*)"%(lemma,pos if pos else "\w+") 
        line_prefix = re.compile(line_prefix_regexp)

        idxes = []

        with codecs.open(_LIT_POS_FILE,'rb', 'utf-8') as fin:
            for line in fin:
                result = line_prefix.match(line)
                if result:
                    res_indices = [int(x) for x in result.group(1).split(' ')]
                    idxes.extend(res_indices)
                    
        LEM_POS_2_SS_IDX[lemma][pos].extend(idxes)
        return sorted(idxes)

    synset_idxes = None

    if lemma in LEM_POS_2_SS_IDX:
        if pos in LEM_POS_2_SS_IDX[lemma]:
            synset_idxes = LEM_POS_2_SS_IDX[lemma][pos]
        else:
            synset_idxes = [idx for pos in LEM_POS_2_SS_IDX[lemma] for idx in LEM_POS_2_SS_IDX[lemma][pos]]
    if not synset_idxes:
        synset_idxes = _get_synset_idxes(lemma,pos)

    if len(synset_idxes) == 0:
        return []

    stored_synsets = [SYNSETS_DICT[synset_idxes[i]] for i in range(len(synset_idxes)) if synset_idxes[i] in SYNSETS_DICT]
    unstored_synset_idxes = [synset_idxes[i] for i in range(len(synset_idxes)) if synset_idxes[i] not in SYNSETS_DICT]

    synset_offsets = _get_synset_offsets(unstored_synset_idxes)
    synsets = _get_synsets(synset_offsets)
    
    return stored_synsets + synsets

def all_synsets(pos=None):
    """Return all the synsets which have the provided pos.

    Notes
    -----
    Returns thousands or tens of thousands of synsets - first time will take significant time.
    Useful for initializing synsets as each returned synset is also stored in a global dictionary for fast retrieval the next time.

    Parameters
    ----------
    pos : str
      Part-of-speech of the sought synsets. Sensible alternatives are wn.ADJ, wn.ADV, wn.VERB, wn.NOUN and `*`.
      If pos == `*`, all the synsets are retrieved and initialized for fast retrieval the next time.
      
    Returns
    -------
    list of Synsets
      Lists the Synsets which have `pos` as part-of-speech.
      Empty list, if `pos` not in [wn.ADJ, wn.ADV, wn.VERB, wn.NOUN, `*`].

    """
    def _get_unique_synset_idxes(pos):
        idxes = []

        with codecs.open(_LIT_POS_FILE,'rb', 'utf-8') as fin:
            if pos == None:
                for line in fin:
                  split_line = line.strip().split(':')
                  idxes.extend([int(x) for x in split_line[2].split()])
            else:
                for line in fin:
                    split_line = line.strip().split(':')
                    if split_line[1] == pos:
                        idxes.extend([int(x) for x in split_line[2].split()])
        idxes = list(set(idxes))
        idxes.sort()
        return idxes

    if pos in LOADED_POS:
        return [SYNSETS_DICT[idx] for lemma in LEM_POS_2_SS_IDX for idx in LEM_POS_2_SS_IDX[lemma][pos]]
    else:
        synset_idxes = _get_unique_synset_idxes(pos)

        if len(synset_idxes) == 0:
            return []

        stored_synsets = [SYNSETS_DICT[synset_idxes[i]] for i in range(len(synset_idxes)) if synset_idxes[i] in SYNSETS_DICT]
        unstored_synset_idxes = [synset_idxes[i] for i in range(len(synset_idxes)) if synset_idxes[i] not in SYNSETS_DICT]
        
        synset_offsets = _get_synset_offsets(unstored_synset_idxes)
        synsets = _get_synsets(synset_offsets)

        for synset in synsets:
            for variant in synset.get_variants():
                LEM_POS_2_SS_IDX[variant.literal][synset.pos].append(synset.id)

        LOADED_POS.add(pos)

        return stored_synsets + synsets

def lemma(lemma_key):
    """Returns the Lemma object with the given key.

    Parameters
    ----------
    lemma_key : str
      Key of the returned lemma.

    Returns
    -------
    Lemma
      Lemma matching the `lemma_key`.

    """
    if lemma_key in LEMMAS_DICT:
        return LEMMAS_DICT[lemma_key]
    split_lemma_key = lemma_key.split('.')

    synset_key = '.'.join(split_lemma_key[:3])
    lemma_literal = split_lemma_key[3]

    lemma_obj = Lemma(synset_key,lemma_literal)
    LEMMAS_DICT[lemma_key] = lemma_obj
    return lemma_obj

def lemma_from_key(lemma_key):
    """Just for comformance with the NLTK WordNet API. No necessary lexical information.
    """
    return None

def lemmas(lemma,pos=None):
    """Returns all the Lemma objects of which name is `lemma` and which have `pos` as part
    of speech.

    Parameters
    ----------
    lemma : str
      Literal of the sought Lemma objects.
    pos : str, optional
      Part of speech of the sought Lemma objects. If None, matches any part of speech.
      Defaults to None
      
    Returns
    -------
    list of Lemmas
      Lists all the matched Lemmas.
    """
    lemma = lemma.lower()
    return [lemma_obj
        for synset in synsets(lemma,pos)
        for lemma_obj in synset.lemmas()
        if lemma_obj.name.lower() == lemma]
  

def morphy(word):
    """Performs morphological analysis on the `word`.

    Parameters
    ----------
    word : str
      Word to be lemmatized.

    Returns
    -------
    str
      Lemma of the `word`.

    """
    analyzed = analyze([word])
    return analyzed[-1]['analysis'][0]['lemma'] if len(analyzed) else None


class Synset:
    """Represents a WordNet synset.

    Attributes
    ----------
    name : str
      Synset  string identifier in the form `lemma.pos.sense_id`.
    id : int
      Synset integer identifier.
    pos : str
      Synset's part-of-speech.
    _raw_synset: eurown.Synset
      Underlying Synset object. Not intended to access directly.
      
    """
    def __init__(self,raw_synset):
        """
        Parameters
        ----------
          raw_synset : eurown.Synset
        Underlying Synset.
          
        """
        self.name = _get_key_from_raw_synset(raw_synset)
        self._raw_synset = raw_synset
        self.id = raw_synset.number or -1
        self.pos = as_unicode(raw_synset.pos)

    def __eq__(self, other):
        return self._raw_synset.number == other._raw_synset.number

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return repr("Synset('%s')" % self.name)

    def _recursive_hypernyms(self, hypernyms):   
        """Finds all the hypernyms of the synset transitively.

        Notes
        -----
          Internal method. Do not call directly.

        Parameters
        ----------
          hypernyms : set of Synsets
        An set of hypernyms met so far.

        Returns
        -------
          set of Synsets
        Returns the input set.

        """
        hypernyms |= set(self.hypernyms())

        for synset in self.hypernyms():
            hypernyms |= synset._recursive_hypernyms(hypernyms)
        return hypernyms

    def _min_depth(self):
        """Finds minimum path length from the root.

        Notes
        -----
          Internal method. Do not call directly.

        Returns
        -------
          int
        Minimum path length from the root.

        """
        if "min_depth" in self.__dict__:
            return self.__dict__["min_depth"]

        min_depth = 0
        hypernyms = self.hypernyms()
        if hypernyms:
            min_depth = 1 + min(h._min_depth() for h in hypernyms)
        self.__dict__["min_depth"] = min_depth

        return min_depth

        #if 'min_depth' in self.__dict__:
          #return self.__dict__['min_depth']

        #min_depth = 0
        #hypernyms = [(0,hypernym) for hypernym in self.hypernyms()]

        #while len(hypernyms) > 0:
          #hypernym = hypernyms.pop()
          #hypernym_hypernyms = hypernym[1].hypernyms()
          #if len(hypernym_hypernyms) == 0:
        #min_depth = hypernym[0] if hypernym[0] < min_depth else min_depth
          #else:
        #hypernyms.extend([(hypernym[0]+1,hyp_hyp) for hyp_hyp in hypernym_hypernyms])
        #return min_depth

    def _shortest_path_distance(self, target_synset):
        """Finds minimum path length from the target synset.
      
        Notes
        -----
          Internal method. Do not call directly.
      
        Parameters
        ----------
          target_synset : Synset
        Synset from where the shortest path length is calculated.
      
        Returns
        -------
          int
        Shortest path distance from `target_synset`. Distance to the synset itself is 0, -1 if no path exists between the two synsets,
        >0 otherwise.
        
        """
        if "distances" not in self.__dict__:
            self.__dict__["distances"] = {}

        if "distances" not in target_synset.__dict__:
            target_synset.__dict__["distances"] = {}

        if target_synset in self.__dict__["distances"]:
            return self.__dict__["distances"][target_synset]

        distance = 0
        visited = set()
        neighbor_synsets = set([self])

        while len(neighbor_synsets) > 0:
            neighbor_synsets_next_level = set()
          
            for synset in neighbor_synsets:
                if synset in visited:
                    continue
        
                if synset == target_synset:
                    self.__dict__["distances"][target_synset] = distance
                    target_synset.__dict__["distances"][self] = distance
                    return distance
                neighbor_synsets_next_level |= set(synset.hypernyms())
                neighbor_synsets_next_level |= set(synset.hyponyms())
                visited.add(synset)
            distance += 1
            neighbor_synsets = set(neighbor_synsets_next_level)

        self.__dict__["distances"][target_synset] = -1
        target_synset.__dict__["distances"][self] = -1
        return -1            

    def get_related_synsets(self,relation):
        """Retrieves all the synsets which are related by given relation.

        Parameters
        ----------
          relation : str
        Name of the relation via which the sought synsets are linked.

        Returns
        -------
          list of Synsets
        Synsets which are related via `relation`.

        """
        results = []

        for relation_candidate in self._raw_synset.internalLinks:
            if relation_candidate.name == relation:
                linked_synset = synset(_get_key_from_raw_synset(relation_candidate.target_concept))
                relation_candidate.target_concept = linked_synset._raw_synset
                results.append(linked_synset)
        return results

    def closure(self, relation, depth=float('inf')):   
        """Finds all the ancestors of the synset using provided relation.

        Parameters
        ----------
          relation : str
        Name of the relation which is recursively used to fetch the ancestors.

        Returns
        -------
          list of Synsets
        Returns the ancestors of the synset via given relations.

        """
    
        ancestors = []
        unvisited_ancestors = [(synset,1) for synset in self.get_related_synsets(relation)]

        while len(unvisited_ancestors) > 0:
            ancestor_depth = unvisited_ancestors.pop()
            if ancestor_depth[1] > depth:
                continue    
            unvisited_ancestors.extend([(synset,ancestor_depth[1]+1) for synset in ancestor_depth[0].get_related_synsets(relation)])
            ancestors.append(ancestor_depth[0])

        return list(set(ancestors))

    def hypernyms(self):
        """Retrieves all the hypernyms.
        
        Returns
        -------
          list of Synsets
        Synsets which are linked via hypernymy relation.
        
        """
        return self.get_related_synsets("has_hyperonym")

    def hyponyms(self):
        """Retrieves all the hyponyms.
        
        Returns
        -------
          list of Synsets
        Synsets which are linked via hyponymy relation.
        
        """
        return self.get_related_synsets("has_hyponym")

    def holonyms(self):
        """Retrieves all the holonyms.
        
        Returns
        -------
          list of Synsets
        Synsets which are linked via holonymy relation.
        
        """
        return self.get_related_synsets("has_holonym")

    def meronyms(self):
        """Retrieves all the meronyms.
        
        Returns
        -------
          list of Synsets
        Synsets which are linked via meronymy relation.
        
        """
        return self.get_related_synsets("has_meronym")

    def member_holonyms(self):
        """Retrieves all the member holoynms.
        
        Returns
        -------
          list of Synsets
        Synsets which are "wholes" of what the synset represents.
        
        """
        return self.get_related_synsets("has_member_holo")

    def root_hypernyms(self):
        """Retrieves all the root hypernyms.
        
        Returns
        -------
          list of Synsets
        Roots via hypernymy relation.
        
        """
        visited = set()
        hypernyms_next_level = set(self.hypernyms())
        current_hypernyms = set(hypernyms_next_level)

        while len(hypernyms_next_level) > 0:
            current_hypernyms = set(hypernyms_next_level)
            hypernyms_next_level = set()
          
            for synset in current_hypernyms:
                if synset in visited:
                    continue
                visited.add(synset)
                hypernyms_next_level |= set(synset.hypernyms())

        return list(current_hypernyms)

    def path_similarity(self, target_synset):
        """Calculates path similarity between the two synsets.
        
        Parameters
        ----------
          target_synset : Synset
        Synset from which the distance is calculated.
        
        Returns
        -------
          float
        Path similarity from `target_synset`. Similarity with the synset itself is 1,
        similarity with ureachable synset is None, 1/(shortest_path_distance + 1) otherwise.
        
        """
        distance = self._shortest_path_distance(target_synset)
        if distance >= 0: 
            return 1.0 / (distance + 1) 
        else: 
            return None

    def lch_similarity(self, synset):
        """Calculates Leacock and Chodorow's similarity between the two synsets.

        Notes
        -----
          Similarity is calculated using the formula -log( (dist(synset1,synset2)+1) / (2*maximum taxonomy depth) ).

        Parameters
        ----------
          synset : Synset
        Synset from which the similarity is calculated.    

        Returns
        -------
          float
        Leacock and Chodorow's from `synset`.
        None, if synsets are not connected via hypernymy/hyponymy relations. Obvious, if part-of-speeches don't match.
        
        """

        if self._raw_synset.pos != synset._raw_synset.pos:
            return None

        depth = MAX_TAXONOMY_DEPTHS[self._raw_synset.pos] 

        distance = self._shortest_path_distance(synset)      

        if distance >= 0: 
            return -math.log((distance + 1) / (2.0 * depth)) 
        else: 
            return None

    def wup_similarity(self, target_synset):
        """Calculates Wu and Palmer's similarity between the two synsets.
        
        Notes
        -----
          Similarity is calculated using the formula ( 2*depth(least_common_subsumer(synset1,synset2)) ) / ( depth(synset1) + depth(synset2) )
        
        Parameters
        ----------
          synset : Synset
        Synset from which the similarity is calculated.
        
        Returns
        -------
          float
        Wu and Palmer's similarity from `synset`.
        
        """
        lchs = self.lowest_common_hypernyms(target_synset)
        lcs_depth = lchs[0]._min_depth() if lchs and len(lchs) else None
        self_depth = self._min_depth() 
        other_depth = target_synset._min_depth()
        if lcs_depth is None or self_depth is None or other_depth is None: 
            return None 

        return (2.0 * lcs_depth) / (self_depth + other_depth)
        
    def get_variants(self):
        """Returns variants/lemmas of the synset.
        
        Returns
        -------
          list of eurown.Variants
        Lemmas/variants of the synset.
        
        """
        return self._raw_synset.variants
      
    def definition(self):
        """Returns the definition of the synset.
        
        Returns
        -------
          str
        Definition of the synset as a new-line separated concatenated string from all its variants' definitions.
        
        """
        return '\n'.join([variant.gloss for variant in self._raw_synset.variants if variant.gloss])
      
    def examples(self):
        """Returns the examples of the synset.
        
        Returns
        -------
          list of str
        List of its variants' examples.
        
        """ 
        examples = []
        for example in [variant.examples for variant in self._raw_synset.variants if len(variant.examples)]:
            examples.extend(example)
        return examples
      
    def lemmas(self):
        """Returns the synset's lemmas/variants' literal represantions.
        
        Returns
        -------
          list of Lemmas
        List of its variations' literals as Lemma objects.
        
        """
        return [lemma("%s.%s"%(self.name,variant.literal)) for variant in self._raw_synset.variants]
      
    def lowest_common_hypernyms(self,target_synset):
        """Returns the common hypernyms of the synset and the target synset, which are furthest from the closest roots.
        
        Parameters
        ----------
          target_synset : Synset
        Synset with which the common hypernyms are sought.
        
        Returns
        -------
          list of Synsets
        Common synsets which are the furthest from the closest roots.
        
        """ 
        self_hypernyms = self._recursive_hypernyms(set())
        other_hypernyms = target_synset._recursive_hypernyms(set())
        common_hypernyms = self_hypernyms.intersection(other_hypernyms)
        
        annot_common_hypernyms = [(hypernym, hypernym._min_depth()) for hypernym in common_hypernyms]
       
        annot_common_hypernyms.sort(key = lambda annot_hypernym: annot_hypernym[1],reverse=True)
       
        max_depth = annot_common_hypernyms[0][1] if len(annot_common_hypernyms) > 0 else None
        
        if max_depth != None:
            return [annot_common_hypernym[0] for annot_common_hypernym in annot_common_hypernyms if annot_common_hypernym[1] == max_depth]
        else:
            return None
            
class Lemma(object):
    """Represents a lemma.

    Attributes
    ----------
    synset_literal : str
      Literal part of the synset's key (literal.pos.sense).
    synset_pos : str
      Pos part of the synset's key (literal.pos.sense).
    synset_sense : str
      Sense part of the synset's key (literal.pos.sense).
    name : str
      Literal/Name of the lemma.
      
    """
  
    def __init__(self,key,literal):
        self.synset_literal,self.synset_pos,self.synset_sense = key.split('.')
        self.name = literal 
      
    def derivationally_related_forms(self):
        """Just for comformance with the NLTK WordNet API. No relations between lemmas in Estonian WordNet.
        """
        return []
      
    def pertainyms(self):
        """Just for comformance with the NLTK WordNet API. No relations between lemmas in Estonian WordNet.
        """
        return []
      
    def antonyms(self):
        """Just for comformance with the NLTK WordNet API. No relations between lemmas in Estonian WordNet.
        """
        return []
      
    def synset(self):
        """Returns synset into which the given lemma belongs to.
        
        Returns
        -------
          Synset
        Synset into which the given lemma belongs to.
        
        """    
        return synset('%s.%s.%s.%s'%(self.synset_literal,self.synset_pos,self.synset_sense,self.literal))

