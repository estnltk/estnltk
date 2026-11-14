from typing import Tuple, Optional

# Hard-wired prefixes that are needed to form verb phrases:
# - positive verb phrases for pefect tenses
# - negation verb phrases for pefect tenses.

# Index values for the dictionary
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import PERSONS
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import POLARITY
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import PRONOUN

PERFECT_MOODS = ('indicative', 'conditional', 'quotative')
PERFECT_TENSES = ('present_perfect', 'past_perfect')


# Prefixes of olema forms in the present and past perfect tense phrases.
# The dictionary is indexed by mood, tense, polarity and person.
# Only three moods are present: indicative, conditional, quotative.
# Present and past perfect tenses do not exist for imperative and jussive moods.
# Wildcard None aggregates all forms in specified index. The result is in no paricular order.
# The only exception is person axis where
# - None denotes the set of all prefixes for active forms.
# - '--' denotes prefixes for passive forms.
# This exception makes downstream code more efficient and readable.

PERFECT_TENSE_PREFIX = dict()
PERFECT_TENSE_PREFIX['indicative'] = dict()
PERFECT_TENSE_PREFIX['conditional'] = dict()
PERFECT_TENSE_PREFIX['quotative'] = dict()
PERFECT_TENSE_PREFIX['indicative']['present_perfect'] = dict()
PERFECT_TENSE_PREFIX['indicative']['past_perfect'] = dict()
PERFECT_TENSE_PREFIX['conditional']['present_perfect'] = dict()
PERFECT_TENSE_PREFIX['conditional']['past_perfect'] = dict()
PERFECT_TENSE_PREFIX['quotative']['present_perfect'] = dict()
PERFECT_TENSE_PREFIX['quotative']['past_perfect'] = dict()


PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive'] = dict()
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive']['1s'] = (('olen',),)
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive']['2s'] = (('oled',),)
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive']['3s'] = (('on',),)
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive']['1p'] = (('oleme',),)
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive']['2p'] = (('olete',),)
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive']['3p'] = (('on',),)
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['positive']['--'] = (('on',),)

PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative'] = dict()
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative']['1s'] = (('ei', 'ole'), ('pole',))
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative']['2s'] = (('ei', 'ole'), ('pole',))
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative']['3s'] = (('ei', 'ole'), ('pole',))
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative']['1p'] = (('ei', 'ole'), ('pole',))
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative']['2p'] = (('ei', 'ole'), ('pole',))
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative']['3p'] = (('ei', 'ole'), ('pole',))
PERFECT_TENSE_PREFIX['indicative']['present_perfect']['negative']['--'] = (('ei', 'ole'), ('pole',))

PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive'] = dict()
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive']['1s'] = (('olin',),)
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive']['2s'] = (('olid',),)
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive']['3s'] = (('oli',),)
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive']['1p'] = (('olime',),)
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive']['2p'] = (('olite',),)
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive']['3p'] = (('olid',),)
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['positive']['--'] = (('oli',),)

PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative'] = dict()
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative']['1s'] = (('ei', 'olnud'), ('polnud',))
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative']['2s'] = (('ei', 'olnud'), ('polnud',))
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative']['3s'] = (('ei', 'olnud'), ('polnud',))
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative']['1p'] = (('ei', 'olnud'), ('polnud',))
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative']['2p'] = (('ei', 'olnud'), ('polnud',))
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative']['3p'] = (('ei', 'olnud'), ('polnud',))
PERFECT_TENSE_PREFIX['indicative']['past_perfect']['negative']['--'] = (('ei', 'olnud'), ('polnud',))


PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive'] = dict()
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive']['1s'] = (('oleks',), ('oleksin',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive']['2s'] = (('oleks',), ('oleksid',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive']['3s'] = (('oleks',),)
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive']['1p'] = (('oleks',), ('oleksime',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive']['2p'] = (('oleks',), ('oleksite',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive']['3p'] = (('oleks',),)
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['positive']['--'] = (('oleks',),)

PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative'] = dict()
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative']['1s'] = (('ei', 'oleks'), ('poleks',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative']['2s'] = (('ei', 'oleks'), ('poleks',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative']['3s'] = (('ei', 'oleks'), ('poleks',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative']['1p'] = (('ei', 'oleks'), ('poleks',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative']['2p'] = (('ei', 'oleks'), ('poleks',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative']['3p'] = (('ei', 'oleks'), ('poleks',))
PERFECT_TENSE_PREFIX['conditional']['present_perfect']['negative']['--'] = (('ei', 'oleks'), ('poleks',))

PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive'] = dict()
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive']['1s'] = (('olnuks',), ('olnuksin',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive']['2s'] = (('olnuks',), ('olnuksite',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive']['3s'] = (('olnuks',),)
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive']['1p'] = (('olnuks',), ('olnuksime',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive']['2p'] = (('olnuks',), ('olnuksite',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive']['3p'] = (('olnuks',),)
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['positive']['--'] = (('olnuks',),)

PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative'] = dict()
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative']['1s'] = (('ei', 'olnuks'), ('polnuks',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative']['2s'] = (('ei', 'olnuks'), ('polnuks',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative']['3s'] = (('ei', 'olnuks'), ('polnuks',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative']['1p'] = (('ei', 'olnuks'), ('polnuks',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative']['2p'] = (('ei', 'olnuks'), ('polnuks',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative']['3p'] = (('ei', 'olnuks'), ('polnuks',))
PERFECT_TENSE_PREFIX['conditional']['past_perfect']['negative']['--'] = (('ei', 'olnuks'), ('polnuks',))


PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive'] = dict()
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive']['1s'] = (('olevat',),)
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive']['2s'] = (('olevat',),)
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive']['3s'] = (('olevat',),)
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive']['1p'] = (('olevat',),)
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive']['2p'] = (('olevat',),)
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive']['3p'] = (('olevat',),)
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['positive']['--'] = (('olevat',),)

PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative'] = dict()
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative']['1s'] = (('ei', 'olevat'), ('polevat',))
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative']['2s'] = (('ei', 'olevat'), ('polevat',))
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative']['3s'] = (('ei', 'olevat'), ('polevat',))
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative']['1p'] = (('ei', 'olevat'), ('polevat',))
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative']['2p'] = (('ei', 'olevat'), ('polevat',))
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative']['3p'] = (('ei', 'olevat'), ('polevat',))
PERFECT_TENSE_PREFIX['quotative']['present_perfect']['negative']['--'] = (('ei', 'olevat'), ('polevat',))

PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive'] = dict()
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive']['1s'] = (('olnuvat',),)
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive']['2s'] = (('olnuvat',),)
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive']['3s'] = (('olnuvat',),)
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive']['1p'] = (('olnuvat',),)
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive']['2p'] = (('olnuvat',),)
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive']['3p'] = (('olnuvat',),)
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['positive']['--'] = (('olnuvat',),)

PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative'] = dict()
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative']['1s'] = (('ei', 'olnuvat'), ('polnuvat',))
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative']['2s'] = (('ei', 'olnuvat'), ('polnuvat',))
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative']['3s'] = (('ei', 'olnuvat'), ('polnuvat',))
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative']['1p'] = (('ei', 'olnuvat'), ('polnuvat',))
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative']['2p'] = (('ei', 'olnuvat'), ('polnuvat',))
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative']['3p'] = (('ei', 'olnuvat'), ('polnuvat',))
PERFECT_TENSE_PREFIX['quotative']['past_perfect']['negative']['--'] = (('ei', 'olnuvat'), ('polnuvat',))


def merge_perfect_tense_prefixes(mood: Optional[str], tense: Optional[str], polarity: Optional[str], person: Optional[str]) -> Tuple[str]:
    if mood == '*' and tense != "*" and polarity != '*'  and person != '*':
        return tuple({element for mood in PERFECT_MOODS for element in PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    if tense == '*' and mood != "*" and polarity != "*" and person != "*":
        return tuple({element for tense in PERFECT_TENSES for element in PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    if polarity == '*' and mood != "*" and tense != "*" and person != "*":
        return tuple({element for polarity in POLARITY for element in PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    # We deliberately aggregate only over persons of active voice as we treat active and passive voice separately in downstream
    if person == '*' and mood != "*" and tense != "*" and polarity != "*":
        return tuple({element for person in PERSONS for element in PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    raise ValueError('Invalid input')


# Aggregations over pronoun axis. Aggregation is done only for active voice
for mood in PERFECT_MOODS:
    for tense in PERFECT_TENSES:
        for polarity in POLARITY:
            PERFECT_TENSE_PREFIX[mood][tense][polarity][None] = merge_perfect_tense_prefixes(mood, tense, polarity, '*')

# Aggregation over polarity axis. Passive voice is still kept separate
for mood in PERFECT_MOODS:
    for tense in PERFECT_TENSES:
        PERFECT_TENSE_PREFIX[mood][tense][None] = dict()
        for person in PERSONS + ('--', None,):
            PERFECT_TENSE_PREFIX[mood][tense][None][person] = merge_perfect_tense_prefixes(mood, tense, '*', person)

# Aggregation over tense axis. Passive voice is still kept separate.
for mood in PERFECT_MOODS:
    PERFECT_TENSE_PREFIX[mood][None] = dict()
    for polarity in POLARITY + (None,):
        PERFECT_TENSE_PREFIX[mood][None][polarity] = dict()
        for person in PERSONS + ('--', None,):
            PERFECT_TENSE_PREFIX[mood][None][polarity][person] = merge_perfect_tense_prefixes(mood, '*', polarity, person)

# Aggregation over mood axis. Passive voice is still kept separate
PERFECT_TENSE_PREFIX[None] = dict()
for tense in PERFECT_TENSES + (None,):
    PERFECT_TENSE_PREFIX[None][tense] = dict()
    for polarity in POLARITY + (None,):
        PERFECT_TENSE_PREFIX[None][tense][polarity] = dict()
        for person in PERSONS + ('--', None,):
            PERFECT_TENSE_PREFIX[None][tense][polarity][person] = merge_perfect_tense_prefixes('*', tense, polarity, person)


# Prefixes of olema forms in the present and past perfect tense phrases as strings.
# The dictionary is indexed by mood, tense, polarity and person.
# Only three moods are present: indicative, conditional, quotative.
# Present and past perfect tenses do not exist for imperative and jussive moods.
# Wildcard None aggregates all forms in specified index. The result is in no paricular order.
# The only exception is person axis where
# - None denotes the set of all prefixes for active forms.
# - '--' denotes prefixes for passive forms.
# This exception makes downstream code more efficient and readable.

PERFECT_TENSE_FLAT_PREFIX = dict()
for mood in PERFECT_MOODS + (None,):
    PERFECT_TENSE_FLAT_PREFIX[mood] = dict()
    for tense in PERFECT_TENSES + (None,):
        PERFECT_TENSE_FLAT_PREFIX[mood][tense] = dict()
        for polarity in POLARITY + (None,):
            PERFECT_TENSE_FLAT_PREFIX[mood][tense][polarity] = dict()
            for person in PERSONS + ('--', None):
                PERFECT_TENSE_FLAT_PREFIX[mood][tense][polarity][person] = tuple({
                    ' '.join(prefix) for prefix in PERFECT_TENSE_PREFIX[mood][tense][polarity][person]
                })


# Prefixes of olema forms in the present and past perfect tense together with subjects.
# The dictionary is indexed by mood, tense, polarity and person.
# Only three moods are present: indicative, conditional, quotative.
# Present and past perfect tenses do not exist for imperative and jussive moods.
# Wildcard None aggregates all forms in specified index. The result is in no paricular order.
# The only exception is person axis where
# - None denotes the set of all prefixes for active forms.
# - '--' denotes prefixes for passive forms.
# This exception makes downstream code more efficient and readable.

FULL_PERFECT_TENSE_PREFIX = dict()
for mood in PERFECT_MOODS:
    FULL_PERFECT_TENSE_PREFIX[mood] = dict()
    for tense in PERFECT_TENSES:
        FULL_PERFECT_TENSE_PREFIX[mood][tense] = dict()
        for polarity in POLARITY:
            FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity] = dict()
            FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity]['--'] = PERFECT_TENSE_PREFIX[mood][tense][polarity]['--']
            for person in PERSONS:
                FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity][person] = tuple(
                    ((PRONOUN[person],) + prefix) for prefix in PERFECT_TENSE_PREFIX[mood][tense][polarity][person])


def merge_full_perfect_tense_prefixes(mood: Optional[str], tense: Optional[str], polarity: Optional[str], person: Optional[str]) -> Tuple[str]:
    if mood == '*' and tense != "*" and polarity != '*'  and person != '*':
        return tuple({element for mood in PERFECT_MOODS for element in FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    if tense == '*' and mood != "*" and polarity != "*" and person != "*":
        return tuple({element for tense in PERFECT_TENSES for element in FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    if polarity == '*' and mood != "*" and tense != "*" and person != "*":
        return tuple({element for polarity in POLARITY for element in FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    # We deliberately aggregate only over persons of active voice as we treat active and passive voice separately in downstream
    if person == '*' and mood != "*" and tense != "*" and polarity != "*":
        return tuple({element for person in PERSONS for element in FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity][person]})
    raise ValueError('Invalid input')


# Aggregations over pronoun axis. Aggregation is done only for active voice
for mood in PERFECT_MOODS:
    for tense in PERFECT_TENSES:
        for polarity in POLARITY:
            FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity][None] = merge_full_perfect_tense_prefixes(mood, tense, polarity, '*')

# Aggregation over polarity axis. Passive voice is still kept separate
for mood in PERFECT_MOODS:
    for tense in PERFECT_TENSES:
        FULL_PERFECT_TENSE_PREFIX[mood][tense][None] = dict()
        for person in PERSONS + ('--', None,):
            FULL_PERFECT_TENSE_PREFIX[mood][tense][None][person] = merge_full_perfect_tense_prefixes(mood, tense, '*', person)

# Aggregation over tense axis. Passive voice is still kept separate
for mood in PERFECT_MOODS:
    FULL_PERFECT_TENSE_PREFIX[mood][None] = dict()
    for polarity in POLARITY + (None,):
        FULL_PERFECT_TENSE_PREFIX[mood][None][polarity] = dict()
        for person in PERSONS + ('--', None,):
            FULL_PERFECT_TENSE_PREFIX[mood][None][polarity][person] = merge_full_perfect_tense_prefixes(mood, '*', polarity, person)

# Aggregation over mood axis. Passive voice is still kept separate
FULL_PERFECT_TENSE_PREFIX[None] = dict()
for tense in PERFECT_TENSES + (None,):
    FULL_PERFECT_TENSE_PREFIX[None][tense] = dict()
    for polarity in POLARITY + (None,):
        FULL_PERFECT_TENSE_PREFIX[None][tense][polarity] = dict()
        for person in PERSONS + ('--', None,):
            FULL_PERFECT_TENSE_PREFIX[None][tense][polarity][person] = merge_full_perfect_tense_prefixes('*', tense, polarity, person)


# Prefixes of olema forms in the present and past perfect tense together with subjects as strings
# The dictionary is indexed by mood, tense, polarity and person.
# Only three moods are present: indicative, conditional, quotative.
# Present and past perfect tenses do not exist for imperative and jussive moods.
# Two non-standard conventions are used for persons:
# - '--' denotes prefixes of passive forms.
# - None denotes the set of all prefixes for active forms.
# This makes downstream code more efficient and readable.
# In each level wildcard None aggregates all forms in this level. The result is in no paricular order.

FULL_PERFECT_TENSE_FLAT_PREFIX = dict()
for mood in PERFECT_MOODS + (None,):
    FULL_PERFECT_TENSE_FLAT_PREFIX[mood] = dict()
    for tense in PERFECT_TENSES + (None,):
        FULL_PERFECT_TENSE_FLAT_PREFIX[mood][tense] = dict()
        for polarity in POLARITY + (None,):
            FULL_PERFECT_TENSE_FLAT_PREFIX[mood][tense][polarity] = dict()
            for person in PERSONS + ('--', None):
                FULL_PERFECT_TENSE_FLAT_PREFIX[mood][tense][polarity][person] = tuple({
                    ' '.join(prefix) for prefix in FULL_PERFECT_TENSE_PREFIX[mood][tense][polarity][person]
                })
