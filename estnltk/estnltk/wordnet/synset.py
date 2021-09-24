from typing import Union


class SynsetException(Exception):
    pass


class Synset:
    """Represents a WordNet synset.
    Attributes
    ----------
    wordnet: Wordnet
    name : str
      Synset  string identifier in the form `lemma.pos.sense_id`.
    id : int
      Synset integer identifier.
    pos : str
      Synset's part-of-speech.
    estwn_id: eurown.Synset
      Underlying Synset object. Not intended to access directly.
    """

    def __init__(self, wordnet, synset_info: Union[int, tuple]) -> None:
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
            self.synset_name = synset_info[1]
            self.estwn_id = synset_info[2]
            self.pos = synset_info[3]
            self.sense = synset_info[4]
            self.literal = synset_info[5]
            self.name = '{}.{}.{}'.format(synset_info[5], self.pos, "%02d"%self.sense)
        else:
            raise SynsetException("Wrong arguments for Synset")

    def __eq__(self, other) -> bool:
        return self.wordnet == other.wordnet and self.id is not None and self.id == other.id

    def get_related_synset(self, relation: str = None) -> list:
        '''Returns all relation names and start_vertex if relation not specified, else returns start_vertex of specified relation.
        Parameters
        ----------
        synset_id : int
        relation  : str
        '''

        if self.wordnet is None:
            return []
        if self.wordnet._relation_graph is None:
            self.wordnet.relation_graph

        graph = self.wordnet.relation_graph

        if not graph.has_node(self.id):
            return []

        relations = graph.in_edges(self.id, data=True)
        related_synsets = []

        if relation is None:
            for r in relations:
                ss = self.wordnet.iloc[r[0]]
                related_synsets.append((ss, r[2]['relation']))
            return related_synsets
        if relation:
            with_relation = [r[0] for r in relations if r[2]['relation'] == relation]
            for r in with_relation:
                ss = self.wordnet.iloc[r]
                related_synsets.append(ss)
            return related_synsets

    def closure(self, relation: str, depth_threshold: float = float('inf'), return_depths: bool = False) -> Union[list, None]:

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

            if return_depths is False:
                ancestors.append(node)
            else:
                ancestors.append((node, depth))

            node_stack.extend(parents)
            depth_stack.extend([depth + 1] * len(parents))

        return ancestors

    def root_hypernyms(self, depth_threshold: float = float('inf'), return_depths: bool = False) -> Union[tuple, None]:

        """Retrieves all the root hypernyms.

        Returns
        -------
          list of Synsets
        Roots via hypernymy relation.

        """
        if depth_threshold < 1:
            return

        node_stack = self.hypernyms
        depth_stack = [1] * len(node_stack)

        while len(node_stack):
            node = node_stack.pop()
            depth = depth_stack.pop()
            if depth > depth_threshold:
                continue
            parents = node.hypernyms

            if not parents or depth == depth_threshold:
                if return_depths is not False:
                    return (node, depth)
                else:
                    return node
            else:
                node_stack.extend(parents)
                depth_stack.extend([depth + 1] * len(parents))

    @property
    def hypernyms(self) -> list:
        """Retrieves all the hypernyms, which are words with a more broad meaning, that the lemma of
        the current synset falls under.

        Returns
        -------
          list of Synsets
        Synsets which are linked via hypernymy relation.

        """

        return self.get_related_synset("hypernym")

    @property
    def hyponyms(self) -> list:
        """Retrieves all the hyponyms, which are words with a more narrow meaning, that fall under the
        lemma of the current synset.

        Returns
        -------
          list of Synsets
        Synsets which are linked via hyponymy relation.

        """

        return self.get_related_synset("hyponym")

    @property
    def holonyms(self) -> list:
        """Retrieves all the holonyms, which are words that denote a whole, whose part is denoted
        by the lemma of the current synset.

        Returns
        -------
          list of Synsets
        Synsets which are linked via holonymy relation.

        """
        return self.get_related_synset("holonym")

    @property
    def meronyms(self) -> list:
        """Retrieves all the meronyms, which are words that denote a part of the lemma of the current synset.

        Returns
        -------
          list of Synsets
        Synsets which are linked via meronymy relation.

        """
        return self.get_related_synset("meronym")

    @property
    def member_holonyms(self) -> list:
        """Retrieves all the member holoynms. Member holonyms are a specific type of holonyms and they denote
        a group to which a word (the lemma of the current synset on which this function is called) belongs.

        Returns
        -------
          list of Synsets
        Synsets which are "wholes" of what the synset represents.

        """
        return self.get_related_synset("holo_member")

    @property
    def definition(self) -> list:
        """Returns the definition of the synset.

        Returns
        -------
          str
        Definition of the synset as a new-line separated concatenated string from all its variants' definitions.

        """
        self.wordnet.cur.execute("SELECT definition FROM wordnet_definition WHERE synset_name = ?", (self.synset_name,))
        result = self.wordnet.cur.fetchone()
        if result is not None:
            return result[0]
        else:
            return None

    @property
    def examples(self) -> list:
        """Returns the examples of the synset.

        Returns
        -------
          list of str
        List of its variants' examples.

        """
        self.wordnet.cur.execute("SELECT example FROM wordnet_example WHERE synset_name = ?", (self.synset_name,))
        return [row[0] for row in self.wordnet.cur.fetchall()]

    @property
    def lemmas(self) -> list:
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
