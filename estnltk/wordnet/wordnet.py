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

    '''def get_synset(self, synset_name, pos, sense):
        with self.conn:
            if pos:
                self.cur.execute("SELECT id FROM wordnet_entry WHERE pos = ? AND sense = ? AND synset_name = ? LIMIT 1",
                                 (pos, sense, synset_name))
                synset_id = self.cur.fetchone()
                if synset_id is not None:
                    return Synset(self, synset_id[0])
                else:
                    return
            else:
                return'''

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            if isinstance(key[1], int):
                synset_name, id = key
                self.cur.execute("SELECT id FROM wordnet_entry WHERE synset_name = ?", (synset_name,))
                synset_id = []
                for ss_id in self.cur.fetchall():
                    if ss_id not in synset_id:
                        synset_id.append(ss_id)
                if synset_id is not None and id <= len(synset_id):
                    return Synset(self, synset_id[id - 1][0])
            else:
                synset_name, pos = key
                self.cur.execute("SELECT id FROM wordnet_entry WHERE synset_name = ? AND pos = ?", (synset_name, pos))
        else:
            self.cur.execute("SELECT id FROM wordnet_entry WHERE synset_name = ?", (key,))
        synset_id = set(self.cur.fetchall())
        if synset_id is not None:
            return [Synset(self, id[0]) for id in synset_id]
        return
