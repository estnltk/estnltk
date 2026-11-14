# Structured representation of Vabamorf syntesis directives for finite verb forms.
# The resulting dictionary is indexed by mood, tense, polarity, pronoun.
# Passive voice is represented through a dedicated empty pronoun '--'.
# This exception makes downstream code more efficient and readable.
# There are four distinct moods in Estonian: indicative, conditional, imperative, quotative.
# The jussive mood is only added for completeness as it coincides with imperative mood.
# There are four tenses in Estonian but present and past perfect are just regular compound phrases.
# Therefore, we omit them and use only two tenses here: present and past
# There are two polarities in Estonian: positive and negative.
# Negative polarity is represented by a phrase but here we specify only the form of the verb.
# The pronoun specifies what grammatical person is used here. For simplicity we use 1s, 2s, 3s, 1p, 2p, 3p, --
# In each level wildcard None aggregates all forms in this level. The result is in no paricular order.
# For pronouns the wildcard None denotes the set of all active forms. There are no wildcards for passive voice.  

from typing import Tuple, Optional

# Index values for the dictionary
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import MOODS
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import TENSES
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import POLARITY
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import PERSONS

# Base-level definition of Vabamorf syntesis directives
VM_FINITE_FORMS = dict()
VM_FINITE_FORMS['indicative'] = dict()
VM_FINITE_FORMS['indicative']['present'] = dict()
VM_FINITE_FORMS['indicative']['past'] = dict()
VM_FINITE_FORMS['conditional'] = dict()
VM_FINITE_FORMS['conditional']['present'] = dict()
VM_FINITE_FORMS['conditional']['past'] = dict()
VM_FINITE_FORMS['imperative'] = dict()
VM_FINITE_FORMS['imperative']['present'] = dict()
VM_FINITE_FORMS['imperative']['past'] = dict()
VM_FINITE_FORMS['quotative'] = dict()
VM_FINITE_FORMS['quotative']['present'] = dict()
VM_FINITE_FORMS['quotative']['past'] = dict()
VM_FINITE_FORMS['jussive'] = dict()
VM_FINITE_FORMS['jussive']['present'] = dict()
VM_FINITE_FORMS['jussive']['past'] = dict()


VM_FINITE_FORMS['indicative']['present']['positive'] = dict()
VM_FINITE_FORMS['indicative']['present']['positive']['1s'] = ('n',)
VM_FINITE_FORMS['indicative']['present']['positive']['2s'] = ('d',)
VM_FINITE_FORMS['indicative']['present']['positive']['3s'] = ('b',)
VM_FINITE_FORMS['indicative']['present']['positive']['1p'] = ('me',)
VM_FINITE_FORMS['indicative']['present']['positive']['2p'] = ('te',)
VM_FINITE_FORMS['indicative']['present']['positive']['3p'] = ('vad',)
VM_FINITE_FORMS['indicative']['present']['positive']['--'] = ('takse',)

VM_FINITE_FORMS['indicative']['present']['negative']= dict()
VM_FINITE_FORMS['indicative']['present']['negative']['1s'] = ('o',)
VM_FINITE_FORMS['indicative']['present']['negative']['2s'] = ('o',)
VM_FINITE_FORMS['indicative']['present']['negative']['3s'] = ('o',)
VM_FINITE_FORMS['indicative']['present']['negative']['1p'] = ('o',)
VM_FINITE_FORMS['indicative']['present']['negative']['2p'] = ('o',)
VM_FINITE_FORMS['indicative']['present']['negative']['3p'] = ('o',)
VM_FINITE_FORMS['indicative']['present']['negative']['--'] = ('ta',)

VM_FINITE_FORMS['indicative']['past']['positive'] = dict()
VM_FINITE_FORMS['indicative']['past']['positive']['1s'] = ('sin',)
VM_FINITE_FORMS['indicative']['past']['positive']['2s'] = ('sid',)
VM_FINITE_FORMS['indicative']['past']['positive']['3s'] = ('s',)
VM_FINITE_FORMS['indicative']['past']['positive']['1p'] = ('sime',)
VM_FINITE_FORMS['indicative']['past']['positive']['2p'] = ('site',)
VM_FINITE_FORMS['indicative']['past']['positive']['3p'] = ('sid',)
VM_FINITE_FORMS['indicative']['past']['positive']['--'] = ('ti',)

VM_FINITE_FORMS['indicative']['past']['negative'] = dict()
VM_FINITE_FORMS['indicative']['past']['negative']['1s'] = ('nud',)
VM_FINITE_FORMS['indicative']['past']['negative']['2s'] = ('nud',)
VM_FINITE_FORMS['indicative']['past']['negative']['3s'] = ('nud',)
VM_FINITE_FORMS['indicative']['past']['negative']['1p'] = ('nud',)
VM_FINITE_FORMS['indicative']['past']['negative']['2p'] = ('nud',)
VM_FINITE_FORMS['indicative']['past']['negative']['3p'] = ('nud',)
VM_FINITE_FORMS['indicative']['past']['negative']['--'] = ('tud',)


VM_FINITE_FORMS['conditional']['present']['positive'] = dict()
VM_FINITE_FORMS['conditional']['present']['positive']['1s'] = ('ks', 'ksin')
VM_FINITE_FORMS['conditional']['present']['positive']['2s'] = ('ks', 'ksid')
VM_FINITE_FORMS['conditional']['present']['positive']['3s'] = ('ks',)
VM_FINITE_FORMS['conditional']['present']['positive']['1p'] = ('ks', 'ksime')
VM_FINITE_FORMS['conditional']['present']['positive']['2p'] = ('ks', 'ksite')
VM_FINITE_FORMS['conditional']['present']['positive']['3p'] = ('ks', 'ksid')
VM_FINITE_FORMS['conditional']['present']['positive']['--'] = ('taks',)

VM_FINITE_FORMS['conditional']['present']['negative'] = dict()
VM_FINITE_FORMS['conditional']['present']['negative']['1s'] = ('ks',)
VM_FINITE_FORMS['conditional']['present']['negative']['2s'] = ('ks',)
VM_FINITE_FORMS['conditional']['present']['negative']['3s'] = ('ks',)
VM_FINITE_FORMS['conditional']['present']['negative']['1p'] = ('ks',)
VM_FINITE_FORMS['conditional']['present']['negative']['2p'] = ('ks',)
VM_FINITE_FORMS['conditional']['present']['negative']['3p'] = ('ks',)
VM_FINITE_FORMS['conditional']['present']['negative']['--'] = ('taks',)

VM_FINITE_FORMS['conditional']['past']['positive'] = dict()
VM_FINITE_FORMS['conditional']['past']['positive']['1s'] = ('nuks', 'nuksin')
VM_FINITE_FORMS['conditional']['past']['positive']['2s'] = ('nuks', 'nuksid')
VM_FINITE_FORMS['conditional']['past']['positive']['3s'] = ('nuks',)
VM_FINITE_FORMS['conditional']['past']['positive']['1p'] = ('nuks', 'nuksime')
VM_FINITE_FORMS['conditional']['past']['positive']['2p'] = ('nuks', 'nuksite')
VM_FINITE_FORMS['conditional']['past']['positive']['3p'] = ('nuks', 'nuksid')
VM_FINITE_FORMS['conditional']['past']['positive']['--'] = ('tuks',)

VM_FINITE_FORMS['conditional']['past']['negative'] = dict()
VM_FINITE_FORMS['conditional']['past']['negative']['1s'] = ('nuks',)
VM_FINITE_FORMS['conditional']['past']['negative']['2s'] = ('nuks',)
VM_FINITE_FORMS['conditional']['past']['negative']['3s'] = ('nuks',)
VM_FINITE_FORMS['conditional']['past']['negative']['1p'] = ('nuks',)
VM_FINITE_FORMS['conditional']['past']['negative']['2p'] = ('nuks',)
VM_FINITE_FORMS['conditional']['past']['negative']['3p'] = ('nuks',)
VM_FINITE_FORMS['conditional']['past']['negative']['--'] = ('tuks',)



VM_FINITE_FORMS['imperative']['present']['positive'] = dict()
VM_FINITE_FORMS['imperative']['present']['positive']['1s'] = ()
VM_FINITE_FORMS['imperative']['present']['positive']['2s'] = ('o',)
VM_FINITE_FORMS['imperative']['present']['positive']['3s'] = ('gu',)
VM_FINITE_FORMS['imperative']['present']['positive']['1p'] = ('gem',)
VM_FINITE_FORMS['imperative']['present']['positive']['2p'] = ('ge',)
VM_FINITE_FORMS['imperative']['present']['positive']['3p'] = ('gu',)
VM_FINITE_FORMS['imperative']['present']['positive']['--'] = ('tagu',)

VM_FINITE_FORMS['imperative']['present']['negative'] = dict()
VM_FINITE_FORMS['imperative']['present']['negative']['1s'] = ()
VM_FINITE_FORMS['imperative']['present']['negative']['2s'] = ('o',)
VM_FINITE_FORMS['imperative']['present']['negative']['3s'] = ('gu',)
VM_FINITE_FORMS['imperative']['present']['negative']['1p'] = ('gem',)
VM_FINITE_FORMS['imperative']['present']['negative']['2p'] = ('ge',)
VM_FINITE_FORMS['imperative']['present']['negative']['3p'] = ('gu',)
VM_FINITE_FORMS['imperative']['present']['negative']['--'] = ('tagu',)

VM_FINITE_FORMS['imperative']['past']['positive'] = dict()
VM_FINITE_FORMS['imperative']['past']['positive']['1s'] = ()
VM_FINITE_FORMS['imperative']['past']['positive']['2s'] = ()
VM_FINITE_FORMS['imperative']['past']['positive']['3s'] = ()
VM_FINITE_FORMS['imperative']['past']['positive']['1p'] = ()
VM_FINITE_FORMS['imperative']['past']['positive']['2p'] = ()
VM_FINITE_FORMS['imperative']['past']['positive']['3p'] = ()
VM_FINITE_FORMS['imperative']['past']['positive']['--'] = ()

VM_FINITE_FORMS['imperative']['past']['negative'] = dict()
VM_FINITE_FORMS['imperative']['past']['negative']['1s'] = ()
VM_FINITE_FORMS['imperative']['past']['negative']['2s'] = ()
VM_FINITE_FORMS['imperative']['past']['negative']['3s'] = ()
VM_FINITE_FORMS['imperative']['past']['negative']['1p'] = ()
VM_FINITE_FORMS['imperative']['past']['negative']['2p'] = ()
VM_FINITE_FORMS['imperative']['past']['negative']['3p'] = ()
VM_FINITE_FORMS['imperative']['past']['negative']['--'] = ()


VM_FINITE_FORMS['quotative']['present']['positive'] = dict()
VM_FINITE_FORMS['quotative']['present']['positive']['1s'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['positive']['2s'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['positive']['3s'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['positive']['1p'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['positive']['2p'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['positive']['3p'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['positive']['--'] = ('tavat',)

VM_FINITE_FORMS['quotative']['present']['negative'] = dict()
VM_FINITE_FORMS['quotative']['present']['negative']['1s'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['negative']['2s'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['negative']['3s'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['negative']['1p'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['negative']['2p'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['negative']['3p'] = ('vat',)
VM_FINITE_FORMS['quotative']['present']['negative']['--'] = ('tavat',)

VM_FINITE_FORMS['quotative']['past']['positive'] = dict()
VM_FINITE_FORMS['quotative']['past']['positive']['1s'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['positive']['2s'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['positive']['3s'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['positive']['1p'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['positive']['2p'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['positive']['3p'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['positive']['--'] = ('tuvat',)

VM_FINITE_FORMS['quotative']['past']['negative'] = dict()
VM_FINITE_FORMS['quotative']['past']['negative']['1s'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['negative']['2s'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['negative']['3s'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['negative']['1p'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['negative']['2p'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['negative']['3p'] = ('nuvat',)
VM_FINITE_FORMS['quotative']['past']['negative']['--'] = ('tuvat',)


VM_FINITE_FORMS['jussive']['present']['positive'] = dict()
VM_FINITE_FORMS['jussive']['present']['positive']['1s'] = ()
VM_FINITE_FORMS['jussive']['present']['positive']['2s'] = ('o',)
VM_FINITE_FORMS['jussive']['present']['positive']['3s'] = ('ge',)
VM_FINITE_FORMS['jussive']['present']['positive']['1p'] = ('gem',)
VM_FINITE_FORMS['jussive']['present']['positive']['2p'] = ('ge',)
VM_FINITE_FORMS['jussive']['present']['positive']['3p'] = ('gu',)
VM_FINITE_FORMS['jussive']['present']['positive']['--'] = ('tagu',)

VM_FINITE_FORMS['jussive']['present']['negative'] = dict()
VM_FINITE_FORMS['jussive']['present']['negative']['1s'] = ()
VM_FINITE_FORMS['jussive']['present']['negative']['2s'] = ('o',)
VM_FINITE_FORMS['jussive']['present']['negative']['3s'] = ('gu',)
VM_FINITE_FORMS['jussive']['present']['negative']['1p'] = ('gem',)
VM_FINITE_FORMS['jussive']['present']['negative']['2p'] = ('ge',)
VM_FINITE_FORMS['jussive']['present']['negative']['3p'] = ('gu',)
VM_FINITE_FORMS['jussive']['present']['negative']['--'] = ('tagu',)

VM_FINITE_FORMS['jussive']['past']['positive'] = dict()
VM_FINITE_FORMS['jussive']['past']['positive']['1s'] = ()
VM_FINITE_FORMS['jussive']['past']['positive']['2s'] = ()
VM_FINITE_FORMS['jussive']['past']['positive']['3s'] = ()
VM_FINITE_FORMS['jussive']['past']['positive']['1p'] = ()
VM_FINITE_FORMS['jussive']['past']['positive']['2p'] = ()
VM_FINITE_FORMS['jussive']['past']['positive']['3p'] = ()
VM_FINITE_FORMS['jussive']['past']['positive']['--'] = ()

VM_FINITE_FORMS['jussive']['past']['negative'] = dict()
VM_FINITE_FORMS['jussive']['past']['negative']['1s'] = ()
VM_FINITE_FORMS['jussive']['past']['negative']['2s'] = ()
VM_FINITE_FORMS['jussive']['past']['negative']['3s'] = ()
VM_FINITE_FORMS['jussive']['past']['negative']['1p'] = ()
VM_FINITE_FORMS['jussive']['past']['negative']['2p'] = ()
VM_FINITE_FORMS['jussive']['past']['negative']['3p'] = ()
VM_FINITE_FORMS['jussive']['past']['negative']['--'] = ()


def merge_vm_directives(mood: Optional[str], tense: Optional[str], polarity: Optional[str], person: Optional[str]) -> Tuple[str]:
    if mood == '*' and tense != "*" and polarity != '*' and person != "*":
        return tuple({element for mood in MOODS for element in VM_FINITE_FORMS[mood][tense][polarity][person]})
    if tense == '*'  and mood != "*" and polarity != '*' and person != "*":
        return tuple({element for tense in TENSES for element in VM_FINITE_FORMS[mood][tense][polarity][person]})
    if polarity == '*'  and mood != "*" and tense != '*' and person != "*":
        return tuple({element for polarity in POLARITY for element in VM_FINITE_FORMS[mood][tense][polarity][person]})
    if person == '*' and tense != "*" and mood != "*" and polarity != '*':
        return tuple({element for person in PERSONS for element in VM_FINITE_FORMS[mood][tense][polarity][person]})
    raise ValueError('Invalid input')


# Aggregations over pronoun axis. Aggregation is done only for active voice
for mood in MOODS:
    for tense in TENSES:
        for polarity in POLARITY:
            VM_FINITE_FORMS[mood][tense][polarity][None] = merge_vm_directives(mood, tense, polarity,'*')

# Aggregation over polarity axis. Passive voice is still kept separate
for mood in MOODS:
    for tense in TENSES:
        VM_FINITE_FORMS[mood][tense][None] = dict()
        for person in PERSONS + ('--', None,):
            VM_FINITE_FORMS[mood][tense][None][person] = merge_vm_directives(mood, tense, '*', person)

# Aggregation over tense axis. Passive voice is still kept separate
for mood in MOODS:
    VM_FINITE_FORMS[mood][None] = dict()
    for polarity in POLARITY + (None,):
        VM_FINITE_FORMS[mood][None][polarity] = dict()
        for person in PERSONS + ('--', None,):
            VM_FINITE_FORMS[mood][None][polarity][person] = merge_vm_directives(mood, '*', polarity, person)

# Aggregation over moods axis. Passive voice is still kept separate
VM_FINITE_FORMS[None] = dict()
for tense in TENSES + (None,):
    VM_FINITE_FORMS[None][tense] = dict()
    for polarity in POLARITY + (None,):
        VM_FINITE_FORMS[None][tense][polarity] = dict()
        for person in PERSONS + ('--', None,):
            VM_FINITE_FORMS[None][tense][polarity][person] = merge_vm_directives('*', tense, polarity, person)
