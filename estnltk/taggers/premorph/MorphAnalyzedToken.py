from estnltk.vabamorf.morf import Vabamorf
from estnltk.rewriting.syntax_preprocessing.syntax_preprocessing import PronounTypeRewriter

        
class MorphAnalyzedToken():
    def __init__(self, token: str) -> None:
        self.text = token

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

    def replace(self, *args):
        result = self.text.replace(*args)
        if result is self:
            return self
        return MorphAnalyzedToken(result)

    def split(self, *args):
        parts = self.text.split(*args)
        if len(parts) == 1:
            return [self]
        return [MorphAnalyzedToken(part) for part in parts]

    def isalpha(self):
        return self.text.isalpha()
    
    analyze = Vabamorf.instance().analyze
    pronoun_lemmas = set(PronounTypeRewriter.load_pronoun_types())

    @property
    def analysis(self):
        return MorphAnalyzedToken.analyze([self.text],
                             guess=False,
                             propername=False,
                             disambiguate=False)[0]['analysis']

    @property
    def part_of_speeches(self):
        return {a['partofspeech'] for a in self.analysis}

    def lemmas(self, pos=None):
        if pos:
            return {a['lemma'] for a in self.analysis if a['partofspeech']==pos}
        return {a['lemma'] for a in self.analysis}
    
    all_cases = frozenset({'ab', 'abl', 'ad', 'adt', 'all', 'el', 'es', 'g',
                 'ill','in', 'kom', 'n', 'p', 'ter', 'tr', 'adt_or_ill'})
    
    def cases(self, pos=None):
        result = set()
        for a in self.analysis:
            if pos:
                if a['partofspeech'] == pos:
                    result.update((a['form']).split())
            else:
                result.update((a['form']).split())
        if {'adt', 'ill'} & result:
            result.add('adt_or_ill')
        return result & MorphAnalyzedToken.all_cases
    
    @property
    def is_word(self):
        return any(a['partofspeech'] not in {'Y', 'Z'} for a in self.analysis)

    @property
    def is_word_conservative(self):
        if '-' not in self:
            return self.is_word

        syllables = frozenset({'ta','te', 'ma', 'va', 'de', 'me', 'ka', 'sa',
                               'su', 'mu', 'ju', 'era', 'eri', 'eks', 'all',
                               'esi', 'oma', 'ees'})
        parts = self.split('-')
        if parts[0].text in syllables:
            return False
        if self.is_word:
            return all(part.is_word for part in parts)
        return False

    @property
    def is_conjunction(self):
        return any(a['partofspeech']=='J' for a in self.analysis)

    @property
    def is_simple_pronoun(self):
        '''dok kõigi is meetodite kohta'''
        return bool(MorphAnalyzedToken.pronoun_lemmas & self.lemmas('P'))
    
    @property
    def is_pronoun(self):
        '''dok'''
        if self.normal.is_simple_pronoun:
            return True
        if '-' in self.normal:
            parts = self.normal.split('-')
            if not parts[-1].is_simple_pronoun:
                return False
            if any('teadma' in part.lemmas() for part in parts):
                return True

            cases = MorphAnalyzedToken.all_cases
            for part in parts:
                if part.is_simple_pronoun:
                    cases &= part.cases('P')
                elif not part.is_conjunction:
                    return False
            if cases:
                return True

            if parts[-1].cases('P') in {'ter', 'es', 'ab', 'kom'}:
                for part in parts[:-1]:
                    if part.is_simple_pronoun and 'g' not in part.cases('P'):
                        return False
                    elif not part.is_conjunction:
                        return False
            return True            
        return False

    @property
    def remove_stammer(self):
        if '-' not in self:
            return self
        parts = self.text.split('-')
        
        removed = False
        while len(parts) > 1:
            if len(parts[0]) > 2:
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
    def normal_old(self):
        self._is_stammer = False
        self._is_hyphenated = False
        if '-' not in self:
            return self

        result = self.replace('-', '')
        if not result.isalpha():
            return self

        if result.is_word:
            self._is_hyphenated = True
            return result
        
        result = self.remove_stammer
        if result is not self and result.is_word:
            self._is_stammer = True

        if '-' in result:
            new_result = result.replace('-', '')
            if new_result.is_word:
                self._is_hyphenated = True
                return new_result

        return result

    @property
    def remove_hyphens_smart(self):
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
        if '-' not in self:
            return self

        if not self.replace('-', '').isalpha():
            return self

        result1 = self.remove_stammer
        if result1.is_word_conservative:
            return result1
        result2 = result1.remove_hyphens_smart
        if result2.is_word_conservative:
            return result2

        result3 = result2.replace('-', '')
        if result3.is_word:
            return result3

        if result1.is_word_conservative:
            return result1

        return self


    @property
    def is_stammer(self):
        self.normal
        return self._is_stammer

    @property
    def is_hyphenated(self):
        self.normal
        return self._is_hyphenated
