import os
import regex as re
from pandas import read_csv
from estnltk.vabamorf.morf import Vabamorf
from estnltk.taggers.standard.text_segmentation.patterns import MACROS

def load_pronoun_lemmas(pronoun_file):
    """
    Load a set of prnoun lemmas from the first column of a csv file.
    """
    assert os.path.exists(pronoun_file),\
        'Unable to find *pronoun_file* from location ' + pronoun_file
    df = read_csv(pronoun_file, header=None, index_col=False)
    return set(df[0])

# Pattern for detecting a halved word ("poolitatud sõna")
_halved_word_pattern = re.compile(r'''^([{LETTERS}]+)-$'''.format(**MACROS), re.X)

class MorphAnalyzedToken():
    """A class that provides (proxy) morphological analysis for a token. ( only for internal usage )
       Contains methods that can be used to validate and normalize a token.
       For morphological analysis Vabamorf is used with the configuration:
           guess=False
           propername=False
           disambiguate=False
    """
    _dir = os.path.dirname(__file__)
    DEFAULT_PRONOUN_FILE = os.path.join(_dir, '../../syntax/preprocessing/rules_files/pronouns.csv')
    DEFAULT_PRONOUN_LEMMAS = load_pronoun_lemmas(DEFAULT_PRONOUN_FILE)
    
    def __init__(self, token:str, pronoun_file:str=None) -> None:
        self.text = token
        if pronoun_file:
            self._pronoun_lemmas = load_pronoun_lemmas(pronoun_file)
        else:
            self._pronoun_lemmas = self.DEFAULT_PRONOUN_LEMMAS

    def __eq__(self, other):
        if isinstance(other, str):
            return self.text == other
        if isinstance(other, MorphAnalyzedToken):
            return self.text == other.text
        return False

    def __contains__(self, s):
        return s in self.text

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.text

    def __repr__(self):
        return "MorphAnalyzedToken('{}')".format(self.text)

    def _replace(self, *args):
        result = self.text.replace(*args)
        if result == self.text:
            return self
        return MorphAnalyzedToken(result)

    def _split(self, *args):
        parts = self.text.split(*args)
        if len(parts) == 1:
            return [self]
        return [MorphAnalyzedToken(part) for part in parts]

    @property
    def _split_by_hyphen(self):
        return self._split('-')

    def _strip(self, *args):
        result = self.text.strip(*args)
        if result == self.text:
            return self
        return MorphAnalyzedToken(result)

    def _isalpha(self):
        return self.text.isalpha()
    
    _analyze = Vabamorf.instance().analyze

    @property
    def _analysis(self):
        return MorphAnalyzedToken._analyze([self.text],
                             guess=False,
                             propername=False,
                             disambiguate=False)[0]['analysis']

    @property
    def _part_of_speeches(self):
        return {a['partofspeech'] for a in self._analysis}

    def _lemmas(self, pos=None):
        if pos:
            return {a['lemma'] for a in self._analysis if a['partofspeech']==pos}
        return {a['lemma'] for a in self._analysis}
    
    _all_cases = frozenset({'ab', 'abl', 'ad', 'adt', 'all', 'el', 'es', 'g',
                        'ill','in', 'kom', 'n', 'p', 'ter', 'tr', 'adt_or_ill'})
    
    def _cases(self, pos=None):
        result = set()
        for a in self._analysis:
            if pos:
                if a['partofspeech'] == pos:
                    result.update((a['form']).split())
            else:
                result.update((a['form']).split())
        if {'adt', 'ill'} & result:
            result.add('adt_or_ill')
        return result & MorphAnalyzedToken._all_cases
    
    @property
    def is_word(self):
        return any(a['partofspeech'] not in {'Y', 'Z'} for a in self._analysis)

    @property
    def _is_word_conservative(self):
        '''
        Returns True if the token is a word and all hyphen-separated parts are
        words. The token is not conservative word if the first hyphen-separated
        part is in the set of special short words ('ta','te', 'ma', ...).
        '''
        if '-' not in self:
            return self.is_word

        syllables = frozenset({'ta', 'te', 'ma', 'va', 'de', 'me', 'ka', 'sa',
                               'su', 'mu', 'ju', 'era', 'eri', 'eks', 'all',
                               'esi', 'oma', 'ees'})
        parts = self._split_by_hyphen
        if parts[0].text in syllables:
            return False
        if self.is_word:
            return all(part.is_word for part in parts)
        return False

    @property
    def is_conjunction(self):
        '''
        Returns True if self has at least one analysis where the part of
        speech is 'J', False otherwise
        '''
        return any(a['partofspeech']=='J' for a in self._analysis)

    @property
    def _is_simple_pronoun(self):
        '''
        Returns True if the token has an analysis where the part of speech is
        'P' and the lemma is listed in
        estnltk/taggers/standard/syntax/preprocessing/rules_files/pronouns.csv,
        False otherwise.
        '''
        return bool(self._pronoun_lemmas & self._lemmas('P'))
    
    @property
    def is_pronoun(self):
        '''
        Returns True if the token is a word and
        - it is a simple pronoun
        or
        - it consists of hyphen-separated parts such that the last part is
          a simple pronoun and
            - one of the parts has a lemma `'teadma'`
            or
            - all the parts are either conjunctions or simple pronouns and the
              simple pronouns have a common case
            or
            - the last part has the case 'ter', 'es', 'ab', or 'kom' and the
              rest of the parts are either conjunctions or simple pronouns with
              case 'g'.
        '''
        if not self.is_word:
            return False
        if self._is_simple_pronoun:
            return True
        if '-' in self:
            parts = self._split_by_hyphen
            if not parts[-1]._is_simple_pronoun:
                return False
            if any('teadma' in part._lemmas() for part in parts):
                return True

            cases = MorphAnalyzedToken._all_cases
            for part in parts:
                if part._is_simple_pronoun:
                    cases &= part._cases('P')
                elif not part.is_conjunction:
                    return False
            if cases:
                return True

            if parts[-1]._cases('P') & {'ter', 'es', 'ab', 'kom'}:
                for part in parts[:-1]:
                    if part._is_simple_pronoun:
                        if 'g' not in part._cases('P'):
                            return False
                    elif not part.is_conjunction:
                        return False
                return True
        return False

    def _remove_stammer(self, max_stammer_length=2):
        '''
        Removes the stammer.

        if max_stammer_length==2 (the default)
            v-v-v-ve-ve-ve-vere-taoline --> vere-taoline

        if max_stammer_length==1
            k-k-kõik --> kõik
            kõ-kõ-kõik --> kõ-kõ-kõik

            v-v-v-ve-ve-ve-vere-taoline --> v-v-v-ve-ve-ve-vere-taoline
            because 've-ve-ve-vere-taoline' is not a word
        '''
        if '-' not in self or not max_stammer_length:
            return self
        parts = self.text.split('-')
        
        removed = False
        while len(parts) > 1:
            if len(parts[0]) > max_stammer_length:
                break
            if parts[1].startswith(parts[0]):
                del parts[0]
                removed = True
            else:
                break
        if len(parts[0]) < 3:
            return self
        if removed:
            return MorphAnalyzedToken('-'.join(parts))
        return self

    @property
    def _remove_hyphens_smart(self):
        '''
        Remove all hyphens except those that separate three or more identical
        consecutive letters.

        -maa-a-lu--ne-      -->     maa-alune
        -m-a-a-a-l-u-n-e-   -->     maaalune

        -q-q-qqwer-ty-      -->    -q-q-qqwer-ty-
        because '-q-q-qqwer-ty-' is not a word
        '''
        if '-' not in self:
            return self
        parts = self.text.split('-')

        for i in range(len(parts)-1, 0, -1):
            if len(parts[i-1]) > 0 and len(parts[i]) > 0:
                if parts[i-1][-1] == parts[i][0]:
                    if (len(parts[i-1]) > 1 and parts[i-1][-2] == parts[i-1][-1]
                        or len(parts[i]) > 1 and parts[i][0] == parts[i][1]):
                        parts.insert(i,'-')
        token = ''.join(parts)
        if self == token:
            return self
        return MorphAnalyzedToken(token)

    @property
    def normal(self):
        '''
        Return MorphAnalyzedToken without hyphenation and stammer.
        Return self if nothing changes.

        Double application of normal is equivalent with single application.
        '''
        if '-' not in self:
            return self

        if not self._replace('-', '')._isalpha():
            return self
        
        # do not delete hyphens from halved words, such as:
        #    "kindlustus- , väärtpaberi- ja pangainspektsioon"
        if _halved_word_pattern.match(self.text):
            return self
        
        result1 = self._strip('-')
        result1 = result1._remove_stammer()
        if result1._is_word_conservative:
            return result1
        result2 = result1._remove_hyphens_smart
        if result2._is_word_conservative:
            return result2

        result3 = result2._replace('-', '')
        if result3.is_word:
            return result3

        if result1._is_word_conservative:
            return result1

        return self
