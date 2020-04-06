import math
#import estnltk
#import estnltk.wordnet.wordnet.Wordnet

MAX_TAXONOMY_DEPTHS = {'a': 2, 'n': 13, 'b': 0, 'v': 10}

class SynsetException(Exception):
    pass

class Synset:
    """Represents a WordNet synset.
    Attributes
    ----------
    wordnet: wordnet version
    name : str
      Synset  string identifier in the form `lemma.pos.sense_id`.
    id : int
      Synset integer identifier.
    pos : str
      Synset's part-of-speech.
    estwn_id: eurown.Synset
      Underlying Synset object. Not intended to access directly.
    """

    def __init__(self, wordnet, id):

        '''if not isinstance(id, int):
            self.wordnet = None
            self.id = None
            self.estwn_id = None
            self.pos = None
            self.sense = None
            self.literal = None
            self.name = None
            return'''
        if not isinstance(id, int):
            raise SynsetException("invalid id type")
        #if not isinstance(wordnet, estnltk.wordnet.wordnet.Wordnet):
        #    raise SynsetException("invalid Wordnet type")


        self.wordnet = wordnet
        self.id = id
        '''self.wordnet.cur.execute \
            ("SELECT estwn_id, pos, sense, synset_name, literal FROM wordnet_entry WHERE id = ? LIMIT 1", (id,))
        self.estwn_id, self.pos, self.sense, name, self.literal = self.wordnet.cur.fetchone()'''
        self.wordnet.cur.execute \
            ("SELECT estwn_id, pos, sense, synset_name, literal FROM wordnet_entry WHERE id = ?", (id,))
        synsets = self.wordnet.cur.fetchall()
        self.estwn_id, self.pos, self.sense, name, self.literal = synsets[0]
        self.name = '{}.{}.{}'.format(name, self.pos, self.sense)

    def __eq__(self, other):
        return self.wordnet == other.wordnet and self.id != None and self.id == other.id

    def get_related_synset(self, relation=None):
        '''Returns all relation names and start_vertex if relation not specified, else returns start_vertex of specified relation.
        Parameters
        ----------
        synset_id : int
        relation  : str
        '''
        if self.wordnet is None:
            return [] #ilmselt pole seda asja vaja
        if relation is None:
            self.wordnet.cur.execute \
                ('''SELECT start_vertex,relation FROM wordnet_relation WHERE end_vertex = '{}' '''.format(self.id))
            return [(Synset(self.wordnet, row[0]), row[1]) for row in self.wordnet.cur.fetchall()]
        if relation:
            try:
                relation.isalnum()
            except Exception as e:
                raise SynsetException("Could not query database with: \n\t: {}.".format(e))

            self.wordnet.cur.execute \
                ('''SELECT start_vertex FROM wordnet_relation WHERE end_vertex = '{}' AND relation = '{}' '''.format
                    (self.id, relation))
            return [Synset(self.wordnet, row[0]) for row in self.wordnet.cur.fetchall()]

        return []

    '''
    def get_synset(self, synset_id=None):

        if synset_id is None:
            return Synset(self.wordnet, self.id)
        else:
            return Synset(self.wordnet, synset_id)    
    '''

    #VAATA ÜLE
    def closure(self, relation, depth_threshold=float('inf'), return_depths=False):

        """Finds all the ancestors of the synset using provided relation.

        Parameters
        ----------
        relation : str
            Name of the relation which is recursively used to fetch the ancestors.

        depth_treshold : int
            Amount of recursive relations to yield. If left unchanged, then yields all recursive relations.

        return_depths : bool
            'return_depths = True' yields synset and amount of recursions.
            'return_depths = False' yields only synset.
            Default value 'False'.

        Returns
        -------
        Synset recursions of given relation via generator.

        """
        if depth_threshold < 1:
            return

        node_stack = self.get_related_synset(relation)
        depth_stack = [1 ] *len(node_stack)

        while len(node_stack):
            node = node_stack.pop()
            depth = depth_stack.pop()
            if depth > depth_threshold:
                continue
            parents = node.get_related_synset(relation)

            if not parents or depth == depth_threshold:
                if return_depths is not False:
                    return (node, depth)
                else:
                    return node
            else:
                node_stack.extend(parents)
                depth_stack.extend([depth +1] * len(parents))

    #VAATA ÜLE
    def root_hypernyms(self, depth_threshold=float('inf'), return_depths=False):

        """Retrieves all the root hypernyms.

        Returns
        -------
          list of Synsets
        Roots via hypernymy relation.

        """
        if depth_threshold < 1:
            return

        node_stack = self.hypernyms()
        depth_stack = [1] * len(node_stack)

        while len(node_stack):
            node = node_stack.pop()
            depth = depth_stack.pop()
            if depth > depth_threshold:
                continue
            parents = node.hypernyms()

            if not parents or depth == depth_threshold:
                if return_depths is not False:
                    return (node, depth)
                else:
                    return node
            else:
                node_stack.extend(parents)
                depth_stack.extend([depth + 1] * len(parents))

    def hypernyms(self):
        """Retrieves all the hypernyms.

        Returns
        -------
          list of Synsets
        Synsets which are linked via hypernymy relation.

        """

        return self.get_related_synset("hypernym")

    def hyponyms(self):
        """Retrieves all the hyponyms.

        Returns
        -------
          list of Synsets
        Synsets which are linked via hyponymy relation.

        """

        return self.get_related_synset("hyponym")

    def holonyms(self):
        """Retrieves all the holonyms.

        Returns
        -------
          list of Synsets
        Synsets which are linked via holonymy relation.

        """
        return self.get_related_synset("holonym")

    def meronyms(self):
        """Retrieves all the meronyms.

        Returns
        -------
          list of Synsets
        Synsets which are linked via meronymy relation.

        """
        return self.get_related_synset("meronym")

    def member_holonyms(self):
        """Retrieves all the member holoynms.

        Returns
        -------
          list of Synsets
        Synsets which are "wholes" of what the synset represents.

        """
        return self.get_related_synset("holo_member")


    #SEE JA JÄRGMINE FUNKTS EI TÖÖTA
    '''def get_variants(self):
        """Returns variants/lemmas of the synset.

        Returns
        -------
          list of eurown.Variants
        Lemmas/variants of the synset.

        """
        #return self.estwn_id.variants
        raise NotImplementedError("synset get_variants not implemented")'''

    def definition(self):
        """Returns the definition of the synset.

        Returns
        -------
          str
        Definition of the synset as a new-line separated concatenated string from all its variants' definitions.

        """
        #parser = eurown.Parser()
        #return '\n'.join([variant.gloss for variant in self.estwn_id.variants if variant.gloss])
        raise NotImplementedError("synset definition not implemented")

    def lemmas(self):
        """Returns the synset's lemmas/variants' literal represantions.

        Returns
        -------
          list of Lemmas
        List of its variations' literals as Lemma objects.

        """
        self.wordnet.cur.execute('''SELECT literal FROM wordnet_entry WHERE id = {} ''' .format(self.id))
        return [row[0] for row in self.wordnet.cur.fetchall()]

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

    def lowest_common_hypernyms(self, target_synset):
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

        annot_common_hypernyms.sort(key=lambda annot_hypernym: annot_hypernym[1], reverse=True)

        max_depth = annot_common_hypernyms[0][1] if len(annot_common_hypernyms) > 0 else None

        if max_depth != None:
            return [annot_common_hypernym[0] for annot_common_hypernym in annot_common_hypernyms if
                    annot_common_hypernym[1] == max_depth]
        return None

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

        if self.pos != synset.pos:
            return None

        depth = MAX_TAXONOMY_DEPTHS[self.pos]

        distance = self._shortest_path_distance(synset)

        if distance >= 0:
            return -math.log((distance + 1) / (2.0 * depth))
        return None
        return

    def wup_similarity(self, target_synset):
        """Calculates Wu and Palmer's similarity between the two synsets.

        Notes
        -----
          Similarity is calculated using the formula ( 2*depth(least_common_subsumer(synset1,synset2)) ) / ( depth(synset1) + depth(synset2) )

        Parameters
        ----------
          target_synset : Synset
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr("Synset('{}')".format(self.name))

    def _html_repr(self):
        return self.name

    def __hash__(self):
        return hash(str(self))
