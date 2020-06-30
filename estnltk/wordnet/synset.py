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

    def __init__(self, wordnet, synset_info):
        if isinstance(synset_info, int):
            self.wordnet = wordnet
            self.id = synset_info
            self.wordnet.cur.execute \
                ("SELECT estwn_id, pos, sense, synset_name, literal FROM wordnet_entry WHERE id = ? AND is_name = 1", (synset_info,))
            self.estwn_id, self.pos, self.sense, self.synset_name, self.literal = self.wordnet.cur.fetchone()
            self.name = '{}.{}.{}'.format(self.literal, self.pos, "%02d"%self.sense)
        elif len(synset_info) == 6:
            self.wordnet = wordnet
            self.id = synset_info[0]
            self.estwn_id = synset_info[2]
            self.pos = synset_info[3]
            self.sense = synset_info[4]
            self.literal = synset_info[5]
            self.name = '{}.{}.{}'.format(synset_info[5], self.pos, "%02d"%self.sense)
        else:
            raise SynsetException("Wrong arguments for Synset")

    def __eq__(self, other):
        return self.wordnet == other.wordnet and self.id is not None and self.id == other.id

    def get_related_synset(self, relation=None):
        '''Returns all relation names and start_vertex if relation not specified, else returns start_vertex of specified relation.
        Parameters
        ----------
        synset_id : int
        relation  : str
        '''

        if self.wordnet is None:
            return []
        if relation is None:
            self.wordnet.cur.execute \
                ('''SELECT start_vertex,relation FROM wordnet_relation WHERE end_vertex = '{}' '''.format(self.id))
            related_synsets = []
            for row in self.wordnet.cur.fetchall():
                if row[0] in self.wordnet.synsets_dict:
                    related_synsets.append((self.wordnet.synsets_dict[row[0]], row[1]))
                else:
                    ss = Synset(self.wordnet, row[0])
                    related_synsets.append((ss, row[1]))
                    self.wordnet.synsets_dict[row[0]] = ss
            return related_synsets
        if relation:
            self.wordnet.cur.execute \
                ('''SELECT start_vertex FROM wordnet_relation WHERE end_vertex = '{}' AND relation = '{}' '''.format
                    (self.id, relation))
            related_synsets = []
            for row in self.wordnet.cur.fetchall():
                if row[0] in self.wordnet.synsets_dict:
                    related_synsets.append(self.wordnet.synsets_dict[row[0]])
                else:
                    ss = Synset(self.wordnet, row[0])
                    related_synsets.append(ss)
                    self.wordnet.synsets_dict[row[0]] = ss
            return related_synsets

        return []

    def closure(self, relation, depth_threshold=float('inf'), return_depths=False):

        """Finds all the ancestors of the synset using provided relation.

        Parameters
        ----------
        relation : str
            Name of the relation which is recursively used to fetch the ancestors.

        depth_threshold : float
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
        depth_stack = [1] * len(node_stack)

        ancestors = []

        while len(node_stack):
            node = node_stack.pop()
            depth = depth_stack.pop()
            if depth > depth_threshold:
                continue
            parents = node.get_related_synset(relation)

            if not parents or depth == depth_threshold:
                if return_depths is not False:
                    ancestors.append((node, depth))
                else:
                    ancestors.append(node)
            else:
                node_stack.extend(parents)
                depth_stack.extend([depth +1] * len(parents))

        return ancestors

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

    def definition(self):
        """Returns the definition of the synset.

        Returns
        -------
          str
        Definition of the synset as a new-line separated concatenated string from all its variants' definitions.

        """
        self.wordnet.cur.execute("SELECT definition FROM wordnet_definition WHERE synset_name = ?", (self.synset_name,))
        return self.wordnet.cur.fetchone()[0]

    def examples(self):
        """Returns the examples of the synset.

        Returns
        -------
          list of str
        List of its variants' examples.

        """
        self.wordnet.cur.execute("SELECT example FROM wordnet_example WHERE synset_name = ?", (self.synset_name,))
        return [row[0] for row in self.wordnet.cur.fetchall()]

    def lemmas(self):
        """Returns the synset's lemmas/variants' literal represantions.

        Returns
        -------
          list of Lemmas
        List of its variations' literals as Lemma objects.

        """
        self.wordnet.cur.execute('''SELECT literal FROM wordnet_entry WHERE id = {} ''' .format(self.id))
        return [row[0] for row in self.wordnet.cur.fetchall()]

    def __str__(self):
        return "Synset('{}')".format(self.name)

    def __repr__(self):
        return repr("Synset('{}')".format(self.name))

    def _html_repr(self):
        return "Synset('{}')".format(self.name)

    def __hash__(self):
        return hash(str(self))
