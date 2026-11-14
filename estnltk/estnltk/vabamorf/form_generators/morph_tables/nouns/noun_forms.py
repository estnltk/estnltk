# Structured representation of Vabamorf syntesis directives for finite noun forms.
# The resulting dictionary is indexed by grammatical number and case
# There are to grammatical numbers: singular and plural
# There are 15 cases. We use here English case names and some specific wildcards.
# In each level wildcard None aggregates all forms in this level. The result is in no paricular order.
# On top level, we have additional wildcard 'paradigm_forms' for the four forms that form the basis of all other forms.
# For cases, we use additional wildcards: 'base_cases', 'location_cases', 'peripheral_cases'

# Index values for the dictionary
from estnltk.vabamorf.form_generators.morph_tables.nouns.common_indices import CASES
from estnltk.vabamorf.form_generators.morph_tables.nouns.common_indices import BASE_CASES
from estnltk.vabamorf.form_generators.morph_tables.nouns.common_indices import LOCATION_CASES
from estnltk.vabamorf.form_generators.morph_tables.nouns.common_indices import PERIPHERAL_CASES
from estnltk.vabamorf.form_generators.morph_tables.nouns.common_indices import GRAMMATICAL_NUMBERS

CASE_WILDCARDS = ('base_cases', 'location_cases', 'peripheral_cases', 'paradigm_cases')
ILLATIVE_SUBCASES = ('short_illative', 'long_illative')

# Base-level definition of Vabamorf syntesis directives
VM_NOUN_FORMS = dict()
VM_NOUN_FORMS['singular'] = dict()
VM_NOUN_FORMS['plural'] = dict()

VM_NOUN_FORMS['singular']['nominative'] = ('sg n',)
VM_NOUN_FORMS['singular']['genitive'] = ('sg g',)
VM_NOUN_FORMS['singular']['partitive'] = ('sg p',)
VM_NOUN_FORMS['singular']['illative'] = ('sg ill', 'adt')
VM_NOUN_FORMS['singular']['long_illative'] = ('sg ill',)
VM_NOUN_FORMS['singular']['short_illative'] = ('adt',)
VM_NOUN_FORMS['singular']['inessive'] = ('sg in',)
VM_NOUN_FORMS['singular']['elative'] = ('sg el',)
VM_NOUN_FORMS['singular']['allative'] = ('sg all',)
VM_NOUN_FORMS['singular']['adessive'] = ('sg ad',)
VM_NOUN_FORMS['singular']['ablative'] = ('sg abl',)
VM_NOUN_FORMS['singular']['translative'] = ('sg tr',)
VM_NOUN_FORMS['singular']['terminative'] = ('sg ter',)
VM_NOUN_FORMS['singular']['essive'] = ('sg es',)
VM_NOUN_FORMS['singular']['abessive'] = ('sg ab',)
VM_NOUN_FORMS['singular']['comitative'] = ('sg kom',)

VM_NOUN_FORMS['plural']['nominative'] = ('pl n',)
VM_NOUN_FORMS['plural']['genitive'] = ('pl g',)
VM_NOUN_FORMS['plural']['partitive'] = ('pl p',)
VM_NOUN_FORMS['plural']['illative'] = ('pl ill',)
VM_NOUN_FORMS['plural']['inessive'] = ('pl in',)
VM_NOUN_FORMS['plural']['elative'] = ('pl el',)
VM_NOUN_FORMS['plural']['allative'] = ('pl all',)
VM_NOUN_FORMS['plural']['adessive'] = ('pl ad',)
VM_NOUN_FORMS['plural']['ablative'] = ('pl abl',)
VM_NOUN_FORMS['plural']['translative'] = ('pl tr',)
VM_NOUN_FORMS['plural']['terminative'] = ('pl ter',)
VM_NOUN_FORMS['plural']['essive'] = ('pl es',)
VM_NOUN_FORMS['plural']['abessive'] = ('pl ab',)
VM_NOUN_FORMS['plural']['comitative'] = ('pl kom',)

# Aggregations over cases axis.
for number in GRAMMATICAL_NUMBERS:
    VM_NOUN_FORMS[number][None] = tuple({element for case in CASES for element in VM_NOUN_FORMS[number][case]})
    VM_NOUN_FORMS[number]['base_cases'] = tuple({element for case in BASE_CASES for element in VM_NOUN_FORMS[number][case]})
    VM_NOUN_FORMS[number]['location_cases'] = tuple({element for case in LOCATION_CASES for element in VM_NOUN_FORMS[number][case]})
    VM_NOUN_FORMS[number]['peripheral_cases'] = tuple({element for case in PERIPHERAL_CASES for element in VM_NOUN_FORMS[number][case]})

# Aggregation over grammatical numbers
VM_NOUN_FORMS[None] = dict()
for case in CASES + ('base_cases', 'location_cases', 'peripheral_cases', None):
    VM_NOUN_FORMS[None][case] = tuple({element for number in GRAMMATICAL_NUMBERS for element in VM_NOUN_FORMS[number][case]})

# Special wildcard for paragigm cases
VM_NOUN_FORMS[None]['paradigm_cases'] = ('sg n', 'sg g', 'sg p', 'sg adt', 'pl g', 'pl p')
