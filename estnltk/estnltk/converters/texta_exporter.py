import pandas
import requests
import json
from regex import sub
from contextlib import contextmanager


class TextaExporter:
    def __init__(self, texta_url, texta_username, texta_password, index, doc_type,
                 fact_mapping=None, session_username=None, session_password=None):
        """
        :param texta_url: str
            e.g. 'http://localhost:8000'
        :param index: str
            something like schema in a database
        :param doc_type: str
            something like a table name in a database
        :param fact_mapping: str (default: None)
           name of a csv file that contains fact mapping instructions

        """
        self.session = requests.Session()

        if session_username is not None and session_password is not None:
            self.session.auth = (session_username, session_password)

        self.textaurl = texta_url.rstrip('/')

        login = {
            'username': texta_username,
            'password': texta_password
        }
        r = self.session.post('{}/account/get_auth_token'.format(self.textaurl), data=json.dumps(login))
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

    def to_data(self, text, meta):
        meta = meta or {}

        # some values (e.g. datetime.date(2016, 2, 15)) are not JSON serializable
        data = {k: str(v) for k, v in meta.items()}
        data['text'] = text.text
        if 'morph_analysis' in text.layers:
            # words may contain whitespace (eg '25 000') but there should be equal number of words, lemmas and POS
            words = ' '.join(
                             sub(r'\s', '_', sp.text)
                             for sp in text.words)
            lemmas = ' '.join(
                              sub(r'\s', '_',
                                  '|'.join(sorted(set(sp.lemma))))
                              for sp in text.morph_analysis)
            partofspeech = ' '.join('|'.join(sorted(set(sp.partofspeech))) for sp in text.morph_analysis)
            data['morph_analysis'] = {'words': words,
                                      'lemmas': lemmas,
                                      'partofspeech': partofspeech}
        if self.fact_mapping is not None:
            data['texta_facts'] = self.extract_facts(text)
        return data

    def to_dict(self, text, meta):
        return {'auth_token': self._auth_token,
                'index': self.index,
                'doc_type': self.doc_type,
                'data': self.to_data(text, meta)
                }

    def export(self, text, meta=None):
        d = self.to_dict(text, meta)
        return self.session.post('{}/import_api/document_insertion'.format(self.textaurl), json.dumps(d))

    def _buffered_export(self, text, meta, buffer, buffer_size):
        buffer.append(self.to_data(text, meta))
        if len(buffer) >= buffer_size:
            return self._flush_export_buffer(buffer)

    def _flush_export_buffer(self, buffer):
        d = {'auth_token': self._auth_token,
             'index': self.index,
             'doc_type': self.doc_type,
             'data': buffer
             }
        response = self.session.post('{}/import_api/document_insertion'.format(self.textaurl), json.dumps(d))
        buffer.clear()
        return response

    @contextmanager
    def buffered_export(self, buffer_size=1000):
        buffer = []

        def wrap_buffered_export(text, meta=None):
            return self._buffered_export(text, meta, buffer=buffer, buffer_size=buffer_size)

        try:
            yield wrap_buffered_export
        finally:
            self._flush_export_buffer(buffer)

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
