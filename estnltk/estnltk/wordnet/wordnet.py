import sqlite3
import os.path
import math
import networkx as nx
from typing import Union, List
from estnltk.wordnet.synset import Synset

MAX_TAXONOMY_DEPTHS = {'a': 2, 'n': 13, 'r': 0, 'v': 10}


class WordnetException(Exception):
    pass


class WordnetIterator:
    def __init__(self, wordnet):
        self._wordnet = wordnet
        self._index = 1

    def __next__(self):
        if self._index < len(self._wordnet.iloc):
            result = self._wordnet.iloc[self._index]
            self._index += 1
            return result
        raise StopIteration


class Wordnet:
    '''
    Wordnet class which implements sqlite database connection.
    Attributes
    ----------
    version: str
        Version of Wordnet to use. Currently only version 2.3.2 (default) is supported
    _relation_graph: Networkx.MultiDiGraph
        Graph where nodes are synset ids and edges are relations between nodes.
    '''

    def __init__(self, version: str ='2.3.2', load_graph: bool = False) -> None:
        self.conn = None
        self.cur = None
        self.version = version
        self._synsets_dict = dict()
        self._relation_graph = None
        self._hyponym_graph = None

        wn_dir = '{}/data/estwn-et-{}'.format(os.path.dirname(os.path.abspath(__file__)), self.version)
        wn_entry = '{}/wordnet_entry.db'.format(wn_dir)
        wn_relation = '{}/wordnet_relation.db'.format(wn_dir)
        wn_example = '{}/wordnet_example.db'.format(wn_dir)
        wn_definition = '{}/wordnet_definition.db'.format(wn_dir)

        if not os.path.exists(wn_dir):
            raise WordnetException("Invalid wordnet version: missing directory: {}".format(wn_dir))
        if not os.path.exists(wn_entry):
            raise WordnetException("Invalid wordnet version: missing file: {}".format(wn_entry))
        if not os.path.exists(wn_relation):
            raise WordnetException("Invalid wordnet version: missing file: {}".format(wn_relation))

        try:
            self.conn = sqlite3.connect(wn_entry)
            self.cur = self.conn.cursor()
            self.conn.execute("ATTACH DATABASE ? AS wordnet_relation", (wn_relation,))
            self.conn.execute("ATTACH DATABASE ? AS wordnet_example", (wn_example,))
            self.conn.execute("ATTACH DATABASE ? AS wordnet_definition", (wn_definition,))

        except sqlite3.OperationalError as e:
            raise WordnetException("Invalid wordnet file: sqlite connection error: {}".format(e))

        except Exception as e:
            raise WordnetException("Unexpected error: {}: {}".format(type(e), e))

        self.iloc

        if load_graph:
            self.relation_graph
            self.hyponym_graph

    def __iter__(self):
        return WordnetIterator(self)

    @property
    def iloc(self) -> dict:
        """
        If not created already, creates a dictionary of all synsets from the database. Keys are
        synset ids and values are corresponding Synset objects.

        Returns
        -------
        Dictionary of all synsets if it has been created beforehand, None otherwise.
        """
        if len(self._synsets_dict) == 0:
            self.cur.execute(
                "SELECT id, synset_name, estwn_id, pos, sense, literal FROM wordnet_entry WHERE is_name = 1")
            synset_entries = self.cur.fetchall()
            for row in synset_entries:
                self._synsets_dict[row[0]] = Synset(self, row)
        else:
            return self._synsets_dict

    @property
    def relation_graph(self) -> nx.MultiDiGraph:
        """
        If not created already, creates Networkx graph from the database. The graph includes
        Synset id's as nodes and relations as edges between them. Otherwise returns the graph.

        Returns
        -------
        Networkx graph if it has been created beforehand, None otherwise.
        """
        if self._relation_graph is None:
            self.cur.execute("SELECT start_vertex, end_vertex, relation FROM wordnet_relation")
            wn_relations = self.cur.fetchall()
            self._relation_graph = nx.MultiDiGraph()
            for i, r in enumerate(wn_relations):
                self._relation_graph.add_edge(r[0], r[1], relation=r[2])
        else:
            return self._relation_graph

    @property
    def hyponym_graph(self) -> nx.Graph:
        """
        If not created already, creates Networkx graph from the database. The graph includes
        Synset id's as nodes and relations as edges between them. Edges are only added, if two
        nodes are connected in a hyponym-hypernym relationship.

        Returns
        -------
        Networkx graph if it has been created beforehand, None otherwise.
        """
        if self._hyponym_graph is None:
            self.cur.execute("SELECT start_vertex, end_vertex, relation FROM wordnet_relation")
            wn_relations = self.cur.fetchall()
            self._hyponym_graph = nx.Graph()
            for i, r in enumerate(wn_relations):
                if r[2] == 'hyponym' or r[2] == 'hypernym':
                    self._hyponym_graph.add_edge(r[0], r[1])
        else:
            return self._hyponym_graph

    def __del__(self) -> None:
        self.conn.close()

    def __getitem__(self, key: Union[tuple, str]) -> Union[Synset, list, None]:
        """Returns synset object or list of synset objects with the provided key.

        Parameters
        ----------
        key : string or tuple
          If key is a string, it is a lemma.
          If key is a tuple, it is either (lemma, pos) or (lemma, index)

        Returns
        -------
        Synset if second element of tuple is index.
            The synset returned is on the place of the index in the list of all synsets with provided lemma.
        List of synsets which contain lemma and pos if provided if key is string or second element of key is pos.
        None, if no match was found.
        """
        if isinstance(key, tuple) and len(key) == 2:
            if isinstance(key[1], int):
                synset_name, id = key
                self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ?", (synset_name,))
                synsets = self.cur.fetchall()
                if synsets is not None and id <= len(synsets) and id - 1 >= 0:
                    return Synset(self, synsets[id - 1][0])
            else:
                synset_name, pos = key
                self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ? AND pos = ?", (synset_name, pos))
        else:
            self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ?", (key,))
        synsets = self.cur.fetchall()
        if synsets is not None:
            return [Synset(self, entry[0]) for entry in synsets]
        return

    def synsets_with_pos(self, pos: str):
        """Return all the synsets which have the provided pos.

        Notes
        -----
        Function returns a generator which yields synsets. They can be retrieved with a for-cycle.

        Parameters
        ----------
        pos : str
          Part-of-speech of the sought synsets.
          Possible part-of-speech tags are: 'n' for noun, 'v' for verb, 'a' for adjective and 'r' for adverb.

        Yields
        ------
        Synset objects with specified part-of-speech tag.
        """
        self.cur.execute(
            "SELECT id, synset_name, estwn_id, pos, sense, literal FROM wordnet_entry WHERE pos = ? AND is_name = 1",
            (pos,))
        synset_entries = self.cur.fetchall()

        for row in synset_entries:
            yield Synset(self, row)

    def get_synset_by_name(self, synset_name: str):
        """Finds Synset object by its name.

        Parameters
        ----------
        synset_name: str
          Format of the name must be: '{literal}.{pos}.{sense_index:%02d}'
          Possible pos tags are: 'n' for noun, 'v' for verb, 'a' for adjective and 'r' for adverb.

        Returns
        ------
        Synset object corresponding to the name, or None, if the object could not be found.
        """
        target_lemma = []
        for c in synset_name:
            if c == '.':
                break
            target_lemma.append( c )
        target_lemma = ''.join( target_lemma )
        if target_lemma:
            for synset in self[target_lemma]:
                if synset.name == synset_name:
                    return synset
        return None

    def _min_depth(self, synset) -> int:
        """Finds minimum path length from the root.
        Notes
        -----
          Internal method. Do not call directly.

        Returns
        -------
          int
        Minimum path length from the root.
        """

        if self._relation_graph is None:
            self.relation_graph

        if type(synset) is not int:
            synset = synset.id

        min_depth = 0
        relations = self.relation_graph.in_edges(synset, data=True)
        hypernyms = [r[0] for r in relations if r[2]['relation'] == 'hypernym']
        if hypernyms:
            min_depth = 1 + min(self._min_depth(h) for h in hypernyms)

        return min_depth

    def _recursive_hypernyms(self, synset, hypernyms):
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

        hypernyms |= set(synset.hypernyms)

        for s in synset.hypernyms:
            hypernyms |= self._recursive_hypernyms(s, hypernyms)
        return hypernyms

    def lowest_common_hypernyms(self, start_synset: Synset, target_synset: Synset) -> Union[list, None]:
        """Returns the common hypernyms of the synset and the target synset, which are furthest from the closest roots.

        Parameters
        ----------
          start_synset  : Synset
          target_synset : Synset
        Synset with which the common hypernyms are sought.

        Returns
        -------
          list of Synsets
        Common synsets which are the furthest from the closest roots.

        """
        self_hypernyms = self._recursive_hypernyms(start_synset, set())
        other_hypernyms = self._recursive_hypernyms(target_synset, set())
        common_hypernyms = self_hypernyms.intersection(other_hypernyms)

        annot_common_hypernyms = [(hypernym, self._min_depth(hypernym)) for hypernym in common_hypernyms]

        annot_common_hypernyms.sort(key=lambda annot_hypernym: annot_hypernym[1], reverse=True)

        max_depth = annot_common_hypernyms[0][1] if len(annot_common_hypernyms) > 0 else None

        if max_depth != None:
            return [annot_common_hypernym[0] for annot_common_hypernym in annot_common_hypernyms if
                    annot_common_hypernym[1] == max_depth]
        return None

    def path_similarity(self, start_synset: Synset, target_synset: Synset) -> Union[float, None]:
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

        if self._hyponym_graph is None:
            self.hyponym_graph

        try:
            distance = nx.shortest_path_length(self.hyponym_graph, start_synset.id, target_synset.id)
            return 1.0 / (distance + 1)
        except:
            return None

    def lch_similarity(self, start_synset: Synset, target_synset: Synset) -> Union[float, None]:
        """Calculates Leacock and Chodorow's similarity between the two synsets.
        Notes
        -----
          Similarity is calculated using the formula -log( (dist(synset1,synset2)+1) / (2*maximum taxonomy depth) ).
        Parameters
        ----------
          target_synset : Synset
        Synset from which the similarity is calculated.
        Returns
        -------
          float
        Leacock and Chodorow's from `synset`.
        None, if synsets are not connected via hypernymy/hyponymy relations. Obvious, if part-of-speeches don't match.

        """

        if self._hyponym_graph is None:
            self.hyponym_graph

        if start_synset.pos != target_synset.pos:
            return None

        depth = MAX_TAXONOMY_DEPTHS[start_synset.pos]

        try:
            distance = nx.shortest_path_length(self.hyponym_graph, start_synset.id, target_synset.id)
            return -math.log((distance + 1) / (2.0 * depth))
        except:
            return None

    def wup_similarity(self, start_synset: Synset, target_synset: Synset) -> Union[float, None]:
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

        lchs = self.lowest_common_hypernyms(start_synset, target_synset)
        lcs_depth = self._min_depth(lchs[0]) if lchs and len(lchs) else None
        self_depth = self._min_depth(start_synset)
        other_depth = self._min_depth(target_synset)
        if lcs_depth is None or self_depth is None or other_depth is None:
            return None

        return (2.0 * lcs_depth) / (self_depth + other_depth)

    def all_relation_types(self) -> List[str]:
        """
        Finds and returns all relation types used in this Wordnet.
        
        Returns
        -------
        A list of strings: relation types used in this Wordnet.
        """
        self.cur.execute("SELECT DISTINCT relation FROM wordnet_relation")
        wn_all_relation_types = self.cur.fetchall()
        return [r[0] for r in wn_all_relation_types]

    def __str__(self):
        return "Wordnet version {}".format(self.version)

    def __repr__(self):
        return "Wordnet version {}".format(self.version)

    def _html_repr(self):
        return "Wordnet version {}".format(self.version)
