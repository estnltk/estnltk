import pandas
import requests
import json
import os
from regex import sub


class TextaExporter:

    def __init__(self, index, doc_type, fact_mapping=None, textapass='~/.textapass'):
        # index is like a schema

        # doc_type is like a table name

        # fact_mapping: str (default: None)
        #   name of a csv file that contains fact mapping instructions

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
        if fact_mapping is None:
            self.fact_mapping = None
        else:
            self.fact_mapping = self._read_fact_mapping(fact_mapping)

    @staticmethod
    def _read_fact_mapping(file):
        df = pandas.read_csv(file)
        df = df.where((pandas.notnull(df)), None)
        fact_mapping = list(df.itertuples(index=False))
        for fm in fact_mapping:
            assert (fm.fact_attr is None) is not (fm.fact_name is None), (fm.fact_attr, fm.fact_name)
            assert (fm.value_attr is None) is not (fm.value is None), (fm.value_attr, fm.value)
            assert fm.fact_type in {'str', 'num'}, fm.fact_type
        return fact_mapping

    @property
    def fact_layers(self):
        if self.fact_mapping is not None:
            return list({fm.facts_layer for fm in self.fact_mapping})
        return []

    def to_dict(self, text, meta):
        data = {**meta,
                'text': text.text}
        if 'morph_analysis' in text.layers:
            # words may contain whitespace (eg '25 000') but there should be equal number of words, lemmas and POS
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
        if self.fact_mapping is not None:
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
        for fm in self.fact_mapping:

            fact_attr = fm.fact_attr
            fact_name = fm.fact_name
            layer = text[fm.facts_layer]

            str_val_attr = None
            num_val_attr = None
            str_val = 'None'
            num_val = None
            if fm.value_attr is None:
                if fm.fact_type == 'str':
                    str_val = fm.value
                else:
                    num_val = fm.value
            else:
                if fm.fact_type == 'str':
                    str_val_attr = fm.value_attr
                else:
                    num_val_attr = fm.value_attr
            ambiguous = layer.ambiguous

            facts = []
            for span in layer:
                spans = json.dumps(span.base_spans)
                if ambiguous:
                    annotations = span.annotations
                else:
                    annotations = [span]
                for annotation in annotations:
                    if fact_attr is not None:
                        fact_name = getattr(annotation, fact_attr)
                    if str_val_attr is not None:
                        str_val = getattr(annotation, str_val_attr)
                    if num_val_attr is not None:
                        num_val = getattr(annotation, num_val_attr)
                    facts.append({'doc_path': 'text',
                                  'fact': fact_name,
                                  'spans': spans,
                                  'str_val': str_val,
                                  'num_val': num_val})
            return facts
