import re
import math
from eurown import Parser


_DATA_DIR = "data"
_LIT_POS_FILE = "lit-pos-synidx2.txt"
_SOI = "kb69a-utf8.soi"
_WN_FILE = "kb69a-utf8.txt"
_SENSE_FILE = "sense.txt"

VERB = 'v'
NOUN = 'n'
ADJ = 'a'
ADV = 'b'

MAX_TAXONOMY_DEPTHS = {'n':1, 'v':1, 'a':1, 'b':1} # TODO calculate real values

def _getSynsetOffsets(synset_idxes):

	offsets = []
	current_seeked_offset_idx = 0

	with open("%s/%s"%(_DATA_DIR,_SOI),'r') as fin:
		for line in fin:
			split_line = line.split(':')
			while current_seeked_offset_idx < len(synset_idxes) and split_line[0] == str(synset_idxes[current_seeked_offset_idx]):
				offsets.append(int(split_line[1]))
				current_seeked_offset_idx += 1
		if current_seeked_offset_idx >= len(synset_idxes):
			break

	return offsets

def _getSynsets(synset_offsets):

	synsets = []

	parser = Parser("%s/%s"%(_DATA_DIR,_WN_FILE))
	for offset in synset_offsets:
		raw_synset = parser.parse_synset(offset)
		synset = Synset(raw_synset)
		synsets.append(synset)

	return synsets

def synset(name):
	
	"""
	name in the form word.pos.nn,
	
	where nn is the sense number
	"""

	def _getSynsetIdx(name):
		with open("%s/%s"%(_DATA_DIR,_SENSE_FILE),'r') as fin:
			for line in fin:
				split_line = line.split(':')
				if split_line[0] == name:
					return split_line[1].strip()
		return None

	synset_idx = _getSynsetIdx(name)
	synset_offsets = _getSynsetOffsets(synset_idxes)
	synset = _getSynsets(synset_offsets)

	return synset[0]

def synsets(name,pos=None):

	def _getSynsetIdxes(name,pos):
		line_prefix_regexp = "%s:%s:(.*)"%(name,pos if pos else "\w+") 
		line_prefix = re.compile(line_prefix_regexp)
		
		idxes = []

		with open("%s/%s"%(_DATA_DIR,_LIT_POS_FILE),'r') as fin:
			for line in fin:
				result = line_prefix.match(line)
				if result:
					idxes.extend([int(x) for x in result.group(1).split(' ')])				
		print sorted(idxes)
		return sorted(idxes)

	synset_idxes = _getSynsetIdxes(name,pos)

	if len(synset_idxes) == 0:
		return []

	synset_offsets = _getSynsetOffsets(synset_idxes)
	synsets = _getSynsets(synset_offsets)
	
	return synsets

def all_synsets(pos):

	def _getSynsetIdxes(pos):
                line_prefix_regexp = "\w+:%s:(.*)"%pos
                line_prefix = re.compile(line_prefix_regexp)

                idxes = []

                with open("%s/%s"%(_DATA_DIR,_LIT_POS_FILE),'r') as fin:
                        for line in fin:
                                result = line_prefix.match(line)
                                if result:
                                        idxes.extend([int(x) for x in result.group(1).split(' ')])
                return sorted(idxes)


	
	synset_idxes = _getSynsetIdxes(pos)

	if len(synset_idxes) == 0:
		return []

	synset_offsets = _getSynsetOffsets(synset_idxes)
	synsets = _getSynsets(synset_offsets)

	return synsets

def lemma_from_key(key):
	pass

class Synset:

	definition = ""
	exmples = [None]
	lemmas = [None]	

	def __init__(self,raw_synset,name = ""):
		self.name = name
		self._raw_synset = raw_synset
		self.definition = raw_synset.definition
		self._dict_ = {}

	# TODO correct target_concept reference

	def hypernyms(self):
		hypernyms = []
		for relation in _raw_synset.internalLinks():
    			if relation.name() == "has_hypernym":
				hypernyms.append(Synset(relation.target_concept()))
		return hypernyms

	def hyponyms(self):
		hyponyms = []
                for relation in _raw_synset.internalLinks():
                        if relation.name() == "has_hyponym":
                                hyponyms.append(Synset(relation.target_concept()))
                return hyponyms

	def holoynms(self):
		holonyms = []
                for relation in _raw_synset.internalLinks():
                        if relation.name() == "has_holonym":
                                holonyms.append(Synset(relation.target_concept()))
                return holonyms

	def meronyms(self):
		meronyms = []
                for relation in _raw_synset.internalLinks():
                        if relation.name() == "has_hypernym":
                                meronyms.append(Synset(relation.target_concept()))
                return meronyms

	def member_holonyms(self):
		pass

	def root_hypernyms(self):
		pass

	def frame_ids(self):
		pass

	def _shortest_path_distance(target_synset):
		if "distances" not in self._dict_:
			self._dict_["distances"] = {}

		if "distances" not in target_synset._dict_:
			target_synset._dict_["distances"] = {}

		if target_synset._raw_synset.number in self._dict_["distances"]:
			return self._dict_["distances"][target_synset._raw_synset.number]

		target_number = target_synset._raw_synset.number
		distance = 0
		visited = set()
		neighbor_synsets = set([self])

		while len(neighbor_synsets) > 0:
			neighbor_synsets_next_level = set()
			
			for synset in neighbor_synsets:
				if synset._raw_synset.number in visited:
					continue
				
				if synset._raw_synset.number == target_number:
					self._dict_["distances"][target_synset._raw_synset.number] = distance
					target_synset._dict_["distances"][self._raw_synset.number] = distance
					return distance
				
				neighbor_synsets_next_level |= set(synset.hypernyms())
				neighbor_synsets_next_level |= set(synset.hyponyms())
				visited.add(synset._raw_synset.number)
			distance += 1
			neighbor_synsets = set(neighbor_synsets_next_level)

		self._dict_["distances"][target_synset._raw_synset.number] = -1
		target_synset._dict_["distances"][self._raw_synset.number] = -1
		return -1


	def path_similarity(synset):
		distance = self._shortest_path_distance(synset)
		if distance >= 0: 
			return 1.0 / (distance + 1) 
		else: 
			return None

	def lch_similarity(synset):
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

	def _recursive_hypernyms(self, hypernyms):
		hypernyms |= set(self.hypernyms())

		for synset in self.hypernyms():
			hypernyms = synset._recursive_hypernyms(hypernyms)
		return hypernyms 

	def _min_depth(self):
		if "min_depth" in self._dict_:
			return self._dict_["min_depth"]

		min_depth = 0
		hypernyms = self.hypernyms()
		
		min_depth = 1 + min(h._min_depth() for h in hypernyms) 
		self._dict_["min_depth"] = min_depth

  		return min_depth

	def wup_similarity(synset):
		self_hypernyms = self._recursive_hypernyms(set())
		other_hypernyms = synset._recursive_hypernyms(set())
		common_hypernyms = self_hypernyms.intersection(other_hypernyms)

		lcs_depth = max(s._min_depth for synset in common_hypernyms)
		self_depth = self._min_depth() 
		other_depth = synset._min_depth 

		if lcs_depth is None or self_depth is None or other_depth is None: 
			return None 

		return (2.0 * lcs_depth) / (self_depth + other_depth)

	def __repr__(self):
		return "Synset('%s')"%self.name # TODO derive from first lemma

class Lemma:

	# TODO complete indexing

	def __init__(self,name,synset):
		self.name = name
		self.synset = synset
		self.key = None

	def antonyms(self):
		pass

	def derivationally_related_forms(self):
		pass

	def pertainyms(self):
		pass

	def count(self):
		pass

	def frame_ids(self):
		pass

	def frame_strings(self):
		pass

	def __repr__(self):
		return "Lemma('%s.%s')"%(self.synset.name,self.name)

