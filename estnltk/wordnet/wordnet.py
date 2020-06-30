import sqlite3
import os.path
import math
import networkx as nx
from estnltk.wordnet.synset import Synset

MAX_TAXONOMY_DEPTHS = {'a': 2, 'n': 13, 'b': 0, 'v': 10}


class WordnetException(Exception):
    pass


class Wordnet:
    '''
    Wordnet class which implements sqlite database connection.
    '''

    def __init__(self, version='2.3.2', load_graph=False):
        self.conn = None
        self.cur = None
        self.version = version
        self.synsets_dict = dict()
        self.loaded_pos = set()

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

        self._graph = None
        if load_graph:
            self.graph_initialize

    @property
    def graph_initialize(self):
        self.cur.execute("SELECT start_vertex, end_vertex, relation FROM wordnet_relation")
        wn_relations = self.cur.fetchall()
        self._graph = nx.DiGraph()
        for r in wn_relations:
            if r[2] == 'hypernym' or r[2] == 'hyponym':
                self._graph.add_edge(r[0], r[1], relation=r[2])

    @property
    def get_graph(self):
        return self._graph

    def __del__(self):
        self.conn.close()

    def __getitem__(self, key):
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

    def synsets(self, pos=None):
        if pos is None:
            self.cur.execute(
                "SELECT id, synset_name, estwn_id, pos, sense, literal FROM wordnet_entry WHERE is_name = 1")
            synset_entries = self.cur.fetchall()
        else:
            self.cur.execute(
                "SELECT id, synset_name, estwn_id, pos, sense, literal FROM wordnet_entry WHERE pos = ? AND is_name = 1", (pos,))
            synset_entries = self.cur.fetchall()

        for row in synset_entries:
            yield Synset(self, row)

    def _shortest_path_distance(self, start_synset, target_synset):
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

        if self._graph is None:
            self.graph_initialize

        if "distances" not in start_synset.__dict__:
            start_synset.__dict__["distances"] = {}

        if "distances" not in target_synset.__dict__:
            target_synset.__dict__["distances"] = {}

        if target_synset in start_synset.__dict__["distances"]:
            return start_synset.__dict__["distances"][target_synset]

        graph = self._graph
        distance = 0
        visited = set()
        neighbor_synsets = set([start_synset.id])

        while len(neighbor_synsets) > 0:
            neighbor_synsets_next_level = set()

            for synset in neighbor_synsets:
                if synset in visited:
                    continue

                if synset == target_synset.id:
                    return distance
                relations = list(graph.in_edges(synset, data=True))
                hypernyms = [r[0] for r in relations if r[2]['relation'] == 'hypernym']
                hyponyms = [r[0] for r in relations if r[2]['relation'] == 'hyponym']
                neighbor_synsets_next_level |= set(hypernyms)
                neighbor_synsets_next_level |= set(hyponyms)
                visited.add(synset)
            distance += 1
            neighbor_synsets = set(neighbor_synsets_next_level)

        return -1

    def _min_depth(self, synset):
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
        hypernyms = synset.hypernyms()
        if hypernyms:
            min_depth = 1 + min(self._min_depth(h) for h in hypernyms)
        synset.__dict__["min_depth"] = min_depth

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
        hypernyms |= set(synset.hypernyms())

        for s in synset.hypernyms():
            hypernyms |= self._recursive_hypernyms(s, hypernyms)
        return hypernyms

    def lowest_common_hypernyms(self, start_synset, target_synset):
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

    def path_similarity(self, start_synset, target_synset):
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

        distance = self._shortest_path_distance(start_synset, target_synset)
        if distance >= 0:
            return 1.0 / (distance + 1)
        return None

    def lch_similarity(self, start_synset, target_synset):
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

        if start_synset.pos != target_synset.pos:
            return None

        depth = MAX_TAXONOMY_DEPTHS[start_synset.pos]

        distance = self._shortest_path_distance(start_synset, target_synset)

        if distance >= 0:
            return -math.log((distance + 1) / (2.0 * depth))
        return None

    def wup_similarity(self, start_synset, target_synset):
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

    def __str__(self):
        return "Wordnet version {}".format(self.version)

    def __repr__(self):
        return "Wordnet version {}".format(self.version)

    def _html_repr(self):
        return "Wordnet version {}".format(self.version)
