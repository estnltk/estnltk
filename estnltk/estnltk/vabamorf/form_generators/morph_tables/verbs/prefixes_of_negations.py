from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import PERSONS
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import PRONOUN

# Hard-wired recipes that are needed to form negation phrases for present imperative where prefix is a tuple of strings.
# The dictionary is indexed by person
# - None denotes the set of all prefixes for active forms.
# - '--' denotes prefixes for passive forms.
# This exception makes downstream code more efficient and readable.
# Each key contains pairs of negation prefix together with Vabamorf syntesis directives.

IMPERATIVE_NEGATION_RECIPE = dict()
IMPERATIVE_NEGATION_RECIPE['1s'] = ()
IMPERATIVE_NEGATION_RECIPE['2s'] = ((('ära',), 'o'),)
IMPERATIVE_NEGATION_RECIPE['3s'] = ((('ärgu',), 'gu'),)
IMPERATIVE_NEGATION_RECIPE['1p'] = ((('ärgem',), 'gem'),)
IMPERATIVE_NEGATION_RECIPE['2p'] = ((('ärge',), 'ge'),)
IMPERATIVE_NEGATION_RECIPE['3p'] = ((('ärgu',), 'gu'),)
IMPERATIVE_NEGATION_RECIPE['--'] = ((('ärgu',), 'tagu'),)

# Aggregations over pronoun axis. Aggregation is done only for active voice
IMPERATIVE_NEGATION_RECIPE[None] = tuple({recipe for person in PERSONS for recipe in IMPERATIVE_NEGATION_RECIPE[person]})


# Hard-wired recipes that are needed to form negation phrases for present imperative where prefix is a string.
# The dictionary is indexed by person
# - None denotes the set of all prefixes for active forms.
# - '--' denotes prefixes for passive forms.
# This exception makes downstream code more efficient and readable.
# Each key contains pairs of negation prefix together with Vabamorf syntesis directives.

IMPERATIVE_NEGATION_FLAT_RECIPE = dict()
for person in PERSONS + ('--',):
    IMPERATIVE_NEGATION_FLAT_RECIPE[person] = tuple((' '.join(recipe[0]), recipe[1]) for recipe in IMPERATIVE_NEGATION_RECIPE[person])

# Aggregations over pronoun axis. Aggregation is done only for active voice
IMPERATIVE_NEGATION_FLAT_RECIPE[None] = tuple({recipe for person in PERSONS for recipe in IMPERATIVE_NEGATION_FLAT_RECIPE[person]})


# Hard-wired recipes that are needed to form negation phrases for present imperative with subject where prefix is a tuple of strings.
# The dictionary is indexed by person
# - None denotes the set of all prefixes for active forms.
# - '--' denotes prefixes for passive forms.
# This exception makes downstream code more efficient and readable.
# Each key contains pairs of negation prefix together with Vabamorf syntesis directives.

FULL_IMPERATIVE_NEGATION_RECIPE = dict()
FULL_IMPERATIVE_NEGATION_RECIPE['--'] = IMPERATIVE_NEGATION_RECIPE['--']
for person in PERSONS:
    FULL_IMPERATIVE_NEGATION_RECIPE[person] = tuple(((PRONOUN[person],) + recipe[0], recipe[1]) for recipe in IMPERATIVE_NEGATION_RECIPE[person])

# Aggregations over pronoun axis. Aggregation is done only for active voice
FULL_IMPERATIVE_NEGATION_RECIPE[None] = tuple({recipe for person in PERSONS for recipe in FULL_IMPERATIVE_NEGATION_RECIPE[person]})


# Hard-wired recipes that are needed to form negation phrases for present imperative with subject where prefix is a string.
# The dictionary is indexed by person
# - None denotes the set of all prefixes for active forms.
# - '--' denotes prefixes for passive forms.
# This exception makes downstream code more efficient and readable.
# Each key contains pairs of negation prefix together with Vabamorf syntesis directives.

FULL_IMPERATIVE_NEGATION_FLAT_RECIPE = dict()
for person in PERSONS + ('--',):
    FULL_IMPERATIVE_NEGATION_FLAT_RECIPE[person] = tuple((' '.join(recipe[0]), recipe[1]) for recipe in FULL_IMPERATIVE_NEGATION_RECIPE[person])

# Aggregations over pronoun axis. Aggregation is done only for active voice
FULL_IMPERATIVE_NEGATION_FLAT_RECIPE[None] = tuple({
    recipe for person in PERSONS for recipe in FULL_IMPERATIVE_NEGATION_FLAT_RECIPE[person]})
