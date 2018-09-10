import requests
import json
import os
from regex import sub


class TextaExporter:

    def __init__(self, index, doc_type, facts_layer=None, fact_attr=None, str_val_attr=None, num_val_attr=None,
                 textapass='~/.textapass'):
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
        self.str_val_attr = str_val_attr
        self.num_val_attr = num_val_attr

    def to_dict(self, text, meta):
        data = {**meta,
                'text': text.text}
        if 'morph_analysis' in text.layers:
            # words may contain whitespace (eg '25 000') but there shoud be equal number of words, lemmas and POS
            words = ' '.join(
                             sub('\s', '_', sp.text)
                             for sp in text.words)
            lemmas = ' '.join(
                              sub('\s', '_',
                                  '|'.join(sorted(set(sp.lemma))))
                              for sp in text.morph_analysis)
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
        return d

    def export(self, text, meta=None):
        d = self.to_dict(text, meta)
        return requests.post('http://{}:{}/import_api/document_insertion'.format(self.host, self.port), json.dumps(d))

    def extract_facts(self, text):
        facts = []
        fact_attr = self.fact_attr
        str_val_attr = self.str_val_attr
        num_val_attr = self.num_val_attr
        fact = 'None'
        str_val = 'None'
        num_val = None
        layer = text[self.facts_layer]
        ambiguous = layer.ambiguous
        for span in layer:
            spans = json.dumps(span.base_spans)
            if ambiguous:
                annotations = span.annotations
            else:
                annotations = [span]
            for annotation in annotations:
                if fact_attr is not None:
                    fact = getattr(annotation, fact_attr)
                if str_val_attr is not None:
                    str_val = getattr(annotation, str_val_attr)
                if num_val_attr is not None:
                    num_val = getattr(annotation, num_val_attr)
                facts.append({'doc_path': 'text',
                              'fact': fact,
                              'spans': spans,
                              'str_val': str_val,
                              'num_val': num_val})
        return facts
