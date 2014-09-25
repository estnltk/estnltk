import os
import re
import math
from eurown import Parser

_MY_DIR = os.path.dirname(__file__)

_DATA_DIR = os.path.join(_MY_DIR, "data")

_LIT_POS_FILE = os.path.join(_DATA_DIR, "lit_pos_synidx.txt")
_SOI = os.path.join(_DATA_DIR, "kb69a-utf8.soi")
_WN_FILE = os.path.join(_DATA_DIR, "kb69a-utf8.txt")
_SENSE_FILE = os.path.join(_DATA_DIR, "sense.txt")

VERB = 'v'
NOUN = 'n'
ADJ = 'a'
ADV = 'b'

MAX_TAXONOMY_DEPTHS = {NOUN:1, VERB:1, ADJ:1, ADV:1} # TODO calculate real values

def _get_synset_offsets(synset_idxes):
  """Returs pointer offset in the WordNet file for every synset index. Preserves order.
  
  NotesTrue
  -----
    Internal function. Do not call directly.
  
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

  with open(_SOI,'r') as fin:
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
  """Given synset offset in the WordNet file, parses synset object for every offset.
  
  Notes
  -----
    Internal function. Do not call directly.

  Parameters
  ----------
    synset_offsets : list of ints
      Lists pointer offsets from which synset objects will be parsed.
      
  Returns
  -------
    list of Synsets
      Lists synset objects which synset_offsets point to.
  
  """
  synsets = []

  parser = Parser(_WN_FILE)
  for offset in synset_offsets:
    raw_synset = parser.parse_synset(offset)
    synset = Synset(raw_synset)
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
    
  Returns
  -------
    string
      Key of the synset in the form of `lemma.pos.sense_no`.
      
  """
  pos = raw_synset.pos
  literal = raw_synset.variants[0].literal
  sense = "%02d"%raw_synset.variants[0].sense
  return '.'.join([literal,pos,sense]).encode('utf8')

def synset(synset_key):
  """Returns synset object with the provided key.
  
  Parameters
  ----------
    synset_key : string
      Unique synset identifier in the form of `lemma.pos.sense_no`.
      
  Returns
  -------
    Synset
      Synset with key `synset_key`.
  
  """

  def _get_synset_idx(synset_key):
    """Returns synset index for the provided key.
    
    Note
    ----
      Internal function. Do not call directly.
    
    """
    with open(_SENSE_FILE,'r') as fin:
      for line in fin:
	split_line = line.split(':')
	if split_line[0] == synset_key:
	  return int(split_line[1].strip())
    return None

  synset_idx = _get_synset_idx(synset_key)
  synset_offset = _get_synset_offsets([synset_idx])
  synset = _get_synsets(synset_offset)

  return synset[0]

def synsets(lemma,pos=None):
  """Returns all synset objects which have lemma as one of the variant literals and fixed pos, if provided.
  
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
  
  """

  def _get_synset_idxes(lemma,pos):
    line_prefix_regexp = "%s:%s:(.*)"%(lemma,pos if pos else "\w+") 
    line_prefix = re.compile(line_prefix_regexp)
    
    idxes = []

    with open(_LIT_POS_FILE,'r') as fin:
      for line in fin:
	result = line_prefix.match(line)
	if result:
	  idxes.extend([int(x) for x in result.group(1).split(' ')])				
    return sorted(idxes)

  synset_idxes = _get_synset_idxes(lemma,pos)

  if len(synset_idxes) == 0:
    return []

  synset_offsets = _get_synset_offsets(synset_idxes)
  synsets = _get_synsets(synset_offsets)
  
  return synsets

def all_synsets(pos):
  """Return all the synsets which have the provided pos.
  
  Parameters
  ----------
    pos : str
      Part-of-speech of the sought synsets.
      
  Returns
  -------
    list of Synsets
      Lists the Synsets which have `pos` as part-of-speech.
  
  """
  def _get_unique_synset_idxes(pos):
    line_prefix_regexp = "\w+:%s:(.*)"%pos
    line_prefix = re.compile(line_prefix_regexp)

    idxes = []

    with open(_LIT_POS_FILE,'r') as fin:
      for line in fin:
	result = line_prefix.match(line)
	if result:
	  idxes.extend([int(x) for x in result.group(1).split(' ')])
	  #if line.split(':')[0] == 'aina':
	     #print [int(x) for x in result.group(1).split(' ')]
    
    idxes.sort()
    return list(set(idxes))


  
  synset_idxes = _get_unique_synset_idxes(pos)

  if len(synset_idxes) == 0:
    return []

  synset_offsets = _get_synset_offsets(synset_idxes)
  synsets = _get_synsets(synset_offsets)

  return synsets

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
    _dict_ : dict
      XXXXXXXXXXXXXXXXXXXx
      
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
    self._dict_ = {}
    self.id = raw_synset.number or -1
    self.pos = raw_synset.pos

  def __eq__(self, other):
    return self._raw_synset.number == other._raw_synset.number

  def __hash__(self):
    return hash(str(self))

  def __repr__(self):
    return ("Synset('%s')"%self.name)

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
    if "min_depth" in self._dict_:
      return self._dict_["min_depth"]

    min_depth = 0
    hypernyms = self.hypernyms()
    if hypernyms:
      min_depth = 1 + min(h._min_depth() for h in hypernyms)
    self._dict_["min_depth"] = min_depth

    return min_depth

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
	shortest path distance from `target_synset`.
	
    """
    if "distances" not in self._dict_:
      self._dict_["distances"] = {}

    if "distances" not in target_synset._dict_:
      target_synset._dict_["distances"] = {}

    if target_synset in self._dict_["distances"]:
      return self._dict_["distances"][target_synset]

    distance = 0
    visited = set()
    neighbor_synsets = set([self])

    while len(neighbor_synsets) > 0:
      neighbor_synsets_next_level = set()
      
      for synset in neighbor_synsets:
	if synset in visited:
	  continue
	
	if synset == target_synset:
	  self._dict_["distances"][target_synset] = distance
	  target_synset._dict_["distances"][self] = distance
	  return distance
	
	neighbor_synsets_next_level |= set(synset.hypernyms())
	neighbor_synsets_next_level |= set(synset.hyponyms())
	visited.add(synset)
      distance += 1
      neighbor_synsets = set(neighbor_synsets_next_level)

    self._dict_["distances"][target_synset] = -1
    target_synset._dict_["distances"][self] = -1
    return -1			

  def get_by_relation(self,sought_relation):
    """Retrieves all the synsets which are related by given relation.
    
    Parameters
    ----------
      sought_relation : str
	Name of the relation via which the sought synsets are linked.
    
    Returns
    -------
      list of Synsets
	Synsets which are related via sought_relation.
    
    """
    results = []

    for relation_candidate in self._raw_synset.internalLinks:

      if relation.name() == sought_relation:
	linked_synset = synset(_get_key_from_raw_synset(relation.target_concept))
	relation.target_concept = linked_synset._raw_synset
	results.append(linked_synset)
    return results

  def get_ancestors(self, relation):   
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
    unvisited_ancestors = self.get_by_relation(relation)
    
    while len(unvisited_ancestors) > 0:
      ancestor = unvisited_ancestors.pop()
      unvisited_ancestors.extend(ancestor.get_by_relation(relation))
      ancestors.append(ancestor)

    return list(set(ancestors))

  def hypernyms(self):
    """Retrieves all the hypernyms.
    
    Returns
    -------
      list of Synsets
	Synsets which are hypernyms.
    
    """
    return get_by_relation("has_hyperonym")

  def hyponyms(self):
    """Retrieves all the hyponyms.
    
    Returns
    -------
      list of Synsets
	Synsets which are hyponyms.
	
    """
    return get_by_relation("has_hyponym")

  def holoynms(self):
    """Retrieves all the holonyms.
    
    Returns
    -------
      list of Synsets
	Synsets which are holonyms.
    
    """
    return get_by_relation("has_holonym")

  def meronyms(self):
    """Retrieves all the meronyms.
    
    Returns
    -------
      list of Synsets
	Synsets which are meronyms.
    
    """
    return get_by_relation("has_meronym")

  def member_holonyms(self):
    """Retrieves all the member holoynms.
    
    Returns
    -------
      list of Synsets
	Synsets which are member_holonyms. TODO OOOOOOOOOOOO
    
    """
    return get_by_relation("has_member_holo")

  def root_hypernyms(self):
    """Retrieves all the root hypernyms.
    
    Returns
    -------
      list of Synsets
	Synsets which are root_hypernyms.
    
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

  def path_similarity(self, synset):
    """Calculates path similarity between the two synsets.
    
    Parameters
    ----------
      synset : Synset
	Synset from which the distance is calculated.
    
    Returns
    -------
      float
	Path similarity from `synset`.
	TODO details
    
    """
    distance = self._shortest_path_distance(synset)
    if distance >= 0: 
      return 1.0 / (distance + 1) 
    else: 
      return None

  def lch_similarity(self, synset):
    """Calculates lch similarity between the two synsets.

    Parameters
    ----------
      synset : Synset
	Synset from which the similarity is calculated.    

    Returns
    -------
      float
	LCH similarity from `synset`.
	TODO details
    
    """
    # TODO error handling

    if self._raw_synset.pos != synset._raw_synset.pos:
      print 'Computing the lch similarity requires synsets to have the same part of speech.'
      return None

    depth = MAX_TAXONOMY_DEPTHS[self._raw_synset.pos] 

    distance = self._shortest_path_distance(synset)      

    if distance >= 0: 
      return -math.log((distance + 1) / (2.0 * depth)) 
    else: 
      return None

  def wup_similarity(self, synset):
    """Calculates wup similarity between the two synsets.
    
        Parameters
    ----------
      synset : Synset
	Synset from which the similarity is calculated.
    
    Returns
    -------
      float
	WUP similarity from `synset`.
    
    """
    self_hypernyms = self._recursive_hypernyms(set())
    other_hypernyms = synset._recursive_hypernyms(set())
    common_hypernyms = self_hypernyms.intersection(other_hypernyms)
    lcs_depth = max(s._min_depth() for s in common_hypernyms)
    self_depth = self._min_depth() 
    other_depth = synset._min_depth()
    if lcs_depth is None or self_depth is None or other_depth is None: 
	    return None 

    return (2.0 * lcs_depth) / (self_depth + other_depth)
	
  def get_variants(self):
    """Returns variants.
    
    Returns
    -------
      list of eurown.Variants
	Lemmas/variants of the synset.
    
    """
    return _raw_synset.variants
