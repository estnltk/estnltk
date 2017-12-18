import regex as re
from collections import defaultdict
from pandas import read_csv, DataFrame
import os
import pickle
from estnltk.rewriting import MorphAnalyzedToken

class VabamorfCorrectionRewriter:

    DEFAULT_RULES = os.path.join(os.path.dirname(__file__),
                                 'rules_files/number_analysis_rules.csv')

    def __init__(self, replace:bool=True, rules_file:str=DEFAULT_RULES, pronoun_correction=True):
        """
        replace: bool (default True)
            If True, replace old analysis with new analysis
            If False, filter old analysis, that is, return the intersection of
            old analysis and new analysis
        """
        self._replace = replace
        self._rules_file = rules_file
        self.rules = self.load_number_analysis_rules(self._rules_file)
        self._pronoun_correction = pronoun_correction

    def __repr__(self):
        return "{}(replace={}, rules_file='{}', pronoun_correction={})".format(
                                                    self.__class__.__name__, 
                                                    self._replace, 
                                                    self._rules_file,
                                                    self._pronoun_correction)
    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        attributes = ['_replace', '_rules_file', '_pronoun_correction']
        values = [getattr(self, a) for a in attributes]
        df = DataFrame.from_items([('class', attributes), (self.__class__.__name__, values)])
        return df.to_html(index=False)

    @staticmethod
    def load_number_analysis_rules(file):
        cache = file + '.pickle'
        if not os.path.exists(cache) or os.stat(cache).st_mtime < os.stat(file).st_mtime:
            df = read_csv(file, na_filter=False, index_col=False)
            rules = defaultdict(dict)
            for _, r in df.iterrows():
                if r.suffix not in rules[r.number]:
                    rules[r.number][r.suffix] = []
                rules[r.number][r.suffix].append({'partofspeech': r.pos, 'form': r.form, 'ending':r.ending})
            with open(cache, 'wb') as out_file:
                pickle.dump(rules, out_file)
            return rules
        with open(cache, 'rb') as in_file:
            rules = pickle.load(in_file)
        return rules


    def analyze_number(self, token):
        m = re.match('-?(\d+\.?)-?(\D*)$', token)
        if not m:
            return []
        number = m.group(1)
        ordinal_number = number.rstrip('.') + '.'
        ending = m.group(2)
        result = []
        for number_re, analyses in self.rules.items():
            if re.match(number_re, number):
                for analysis in analyses.get(ending, []):
                    if analysis['partofspeech'] == 'O':
                        a = {'lemma':ordinal_number, 'root':ordinal_number, 'root_tokens':(ordinal_number,), 'clitic':''}
                    else:
                        a = {'lemma':number, 'root':number, 'root_tokens':(number,), 'clitic':''}
                    a.update(analysis)
                    result.append(a)
                break
        return result

    def rewrite(self, records):        
        # 'word_normal' should be equal for all records, so use the first one
        word_normal = records[0]['word_normal']
        start_end = {'start': records[0]['start'], 'end': records[0]['end']}

        # check pronoun analysis
        token = MorphAnalyzedToken(word_normal)
        records_new = []
        for rec in records:
            if rec['partofspeech'] == 'P':
                if token.is_pronoun:
                    records_new.append(rec)
            else:
                records_new.append(rec)
        #records = records_new

        # stop here if the normalized token consists of letters only
        if word_normal.isalpha():
            return records

        # check analysis of numeric tokens 
        analysis = self.analyze_number(word_normal)

        for a in analysis:
            a.update(start_end)
        if analysis:
            if self._replace:
                records = analysis
            else:
                records = [rec for rec in records if rec in analysis]

        return records
