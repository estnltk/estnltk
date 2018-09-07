import requests
import json
import os


class TextaExporter:

    def __init__(self, index, doc_type, facts_layer=None, fact_attr=None, value_attr=None, textapass='~/.textapass'):
        # index is like a schema

        # doc_type is like a table name

        # format of the first line of .textapass file:
        # <hostname>:<port>:<username>:<password>
        # for example:
        # localhost:9200:mari:secret

        with open(os.path.expanduser(textapass)) as in_f:
            self.host, self.port, username, password = in_f.readline().rstrip().split(':')

        login = {
            'username': username,
            'password': password
        }
        r = requests.post('http://{}:{}/account/get_auth_token'.format(self.host, self.port), data=json.dumps(login))
        self._auth_token = r.json()['auth_token']

        self.index = index
        self.doc_type = doc_type
        self.facts_layer = facts_layer
        self.fact_attr = fact_attr
        self.value_attr = value_attr

    def export(self, text, meta=None):
        data = {**meta,
                'text': text.text}
        if 'morph_analysis' in text.layers:
            words = ' '.join(sp.text for sp in text.words)
            lemmas = ' '.join('|'.join(sorted(set(sp.lemma))) for sp in text.morph_analysis)
            partofspeech = ' '.join('|'.join(sorted(set(sp.partofspeech))) for sp in text.morph_analysis)
            data['morph_analysis'] = {'words': words,
                                      'lemmas': lemmas,
                                      'partofspeech': partofspeech}
        if self.facts_layer is not None:
            data['texta_facts'] = self.extract_facts(text)

        d = {'auth_token': self._auth_token,
             'index': self.index,
             'doc_type': self.doc_type,
             'data': data
             }
        return requests.post('http://{}:{}/import_api/document_insertion'.format(self.host, self.port), json.dumps(d))

    def extract_facts(self, text):
        facts = []
        fact_attr = self.fact_attr
        value_attr = self.value_attr
        fact = None
        value = None
        for span in text[self.facts_layer]:
            start = span.start
            end = span.end
            for annotation in span:
                if fact_attr is not None:
                    fact = getattr(annotation, fact_attr)
                if value_attr is not None:
                    value = getattr(annotation, value_attr)
                facts.append({'doc_path': 'text',
                              'fact': fact,
                              'spans': "[[{}, {}]]".format(start, end),
                              'str_val': value,
                              'num_val': None
                             })
        return facts
