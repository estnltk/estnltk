import sqlite3
import os.path
from estnltk.wordnet.synset import Synset


class WordnetException(Exception):
    pass


class Wordnet:
    '''
    Wordnet class which implements sqlite database connection.
    '''

    def __init__(self, version='74'):
        self.conn = None
        self.cur = None
        self.version = version
        self.graph = None
        self.synsets_dict = dict()
        self.loaded_pos = set()

        wn_dir = '{}/data/estwn_kb{}'.format(os.path.dirname(os.path.abspath(__file__)), self.version)
        wn_entry = '{}/wordnet_entry.db'.format(wn_dir)
        wn_relation = '{}/wordnet_relation.db'.format(wn_dir)

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

        except sqlite3.OperationalError as e:
            raise WordnetException("Invalid wordnet file: sqlite connection error: {}".format(e))

        except Exception as e:
            raise WordnetException("Unexpected error: {}: {}".format(type(e), e))

    def __del__(self):
        self.conn.close()

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            if isinstance(key[1], int):
                synset_name, id = key
                #self.cur.execute("SELECT * FROM wordnet_entry WHERE literal = ?", (synset_name,))
                self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ?", (synset_name,))
                synsets = self.cur.fetchall()
                if synsets is not None and id <= len(synsets) and id - 1 >= 0:
                    #return Synset(self, synsets[id - 1])
                    return Synset(self, synsets[id - 1][0])
            else:
                synset_name, pos = key
                #self.cur.execute("SELECT * FROM wordnet_entry WHERE literal = ? AND pos = ?", (synset_name, pos))
                self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ? AND pos = ?", (synset_name, pos))
        else:
            #self.cur.execute("SELECT * FROM wordnet_entry WHERE literal = ?", (key,))
            self.cur.execute("SELECT id FROM wordnet_entry WHERE literal = ?", (key,))
        synsets = self.cur.fetchall()
        if synsets is not None:
            #return [Synset(self, entry) for entry in synsets]
            return [Synset(self, entry[0]) for entry in synsets]
        return

    def all_synsets(self, pos=None):
        if pos is None:
            self.cur.execute("SELECT * FROM wordnet_entry GROUP BY id HAVING MIN(ROWID)")
            synset_entries = self.cur.fetchall()
        else:
            self.cur.execute("SELECT * FROM wordnet_entry WHERE pos = ? GROUP BY id HAVING MIN(ROWID)", (pos,))
            synset_entries = self.cur.fetchall()

        synsets = []

        for row in synset_entries:
            if row[0] in self.synsets_dict:
                synsets.append(self.synsets_dict[row[0]])
            else:
                ss = Synset(self, row)
                synsets.append(ss)
                self.synsets_dict[row[0]] = ss

        return synsets
