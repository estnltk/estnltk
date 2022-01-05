from estnltk.taggers.system.dict_tagger_2.extraction_rules.ruleset import Ruleset

class AmbiguousRuleset(Ruleset):

    @property
    def is_valid(self):
        '''
        Ambiguous rulesets allow same left-hand side in rules.
        Returns true

        '''
        return True


