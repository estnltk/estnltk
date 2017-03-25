from estnltk.vabamorf.morf import Vabamorf
from estnltk.rewriting.syntax_preprocessing.syntax_preprocessing import PronounTypeRewriter

        
class Token(str):
    def replace(self, *args):
        return Token(super().replace(*args))

    def split(self, *args):
        return [Token(t) for t in super().split(*args)]
    
    analyze = Vabamorf.instance().analyze
    pronoun_lemmas = set(PronounTypeRewriter.load_pronoun_types())

    @property
    def analysis(self):
        return Token.analyze([self.normal],
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
        return result & Token.all_cases            
    
    @property
    def is_word(self):
        return any(a['partofspeech'] not in {'Y', 'Z'} for a in self.analysis)

    @property
    def is_conjunction(self):
        return any(a['partofspeech']=='J' for a in self.analysis)

    @property
    def is_simple_pronoun(self):
        return bool(Token.pronoun_lemmas & self.lemmas('P'))
    
    @property
    def is_pronoun(self):
        if self.normal.is_simple_pronoun:
            return True
        if '-' in self.normal:
            parts = self.normal.split('-')
            if not parts[-1].is_simple_pronoun:
                return False
            if any('teadma' in part.lemmas() for part in parts):
                return True

            cases = Token.all_cases
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
        parts = self.split('-')
        
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
            return Token('-'.join(parts))
        return self

    @property
    def normal(self):
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
    def is_stammer(self):
        self.normal
        return self._is_stammer

    @property
    def is_hyphenated(self):
        self.normal
        return self._is_hyphenated
