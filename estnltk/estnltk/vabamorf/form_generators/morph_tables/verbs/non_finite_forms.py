# Structured representation of Vabamorf syntesis directives for non-finite verb forms.
# The resulting dictionary is indexed by voice, type and subtype
# There are four types of non-finite forms in Estonian: infinitive, participles, gerund, supine.
# Each type has a different list of subtypes.
# Infintitives and gerunds have no subtypes and have also no voice specifications.
# Participles are indexed by tense which is either present or past.
# Active voice supines are indexed by case. We use here standard abbrevations of EstNLTK and Vabamorf.
# In each level wildcard None aggregates all forms in this level. The result is in no paricular order.

import itertools
from typing import Tuple, Optional

# Indices of the dictionary
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import VOICES
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import TENSES
TYPES = ('infinitive', 'participle', 'gerund', 'supine')
CASES = ('ill', 'tr', 'in', 'el', 'ab')

# Base-level definition of Vabamorf syntesis directives
VM_NON_FINITE_FORMS = dict()
VM_NON_FINITE_FORMS['active'] = dict()
VM_NON_FINITE_FORMS['passive'] = dict()
VM_NON_FINITE_FORMS[None] = dict()

# By tradition only da-infintive is reported as ma-infinitive is classified as supine.
VM_NON_FINITE_FORMS[None]['infinitive'] = dict()
VM_NON_FINITE_FORMS[None]['infinitive'][None] = ('da',)

# There are only four positive participle forms in Estonian.
VM_NON_FINITE_FORMS['active']['participle'] = dict()
VM_NON_FINITE_FORMS['active']['participle']['present'] = ('v',)
VM_NON_FINITE_FORMS['active']['participle']['past'] = ('nud',)
VM_NON_FINITE_FORMS['passive']['participle'] = dict()
VM_NON_FINITE_FORMS['passive']['participle']['present'] = ('tav',)
VM_NON_FINITE_FORMS['passive']['participle']['past'] = ('tud',)

# There is only asingle gerund and it is voiceless
VM_NON_FINITE_FORMS[None]['gerund'] = dict()
VM_NON_FINITE_FORMS[None]['gerund'][None] = ('des',)

# Only active voice supines have case subntypes.
VM_NON_FINITE_FORMS['active']['supine'] = dict()
VM_NON_FINITE_FORMS['active']['supine']['ill'] = ('ma',)
VM_NON_FINITE_FORMS['active']['supine']['tr'] = ('maks',)
VM_NON_FINITE_FORMS['active']['supine']['in'] = ('mas',)
VM_NON_FINITE_FORMS['active']['supine']['el'] = ('mast',)
VM_NON_FINITE_FORMS['active']['supine']['ab'] = ('mata',)
VM_NON_FINITE_FORMS['passive']['supine'] = dict()
VM_NON_FINITE_FORMS['passive']['supine'][None] = ('tama',)


# Aggregations over subtype axis. Only participle and supline have subtypes. Other types are already aggregated
# The passive voice is already aggreagted for supine
VM_NON_FINITE_FORMS['active']['supine'][None] = tuple({
    element for case in CASES for element in VM_NON_FINITE_FORMS['active']['supine'][case]})
# Both voices are present for participle
for voice in VOICES:
    VM_NON_FINITE_FORMS[voice]['participle'][None] = tuple({
        element for tense in TENSES for element in VM_NON_FINITE_FORMS[voice]['participle'][tense]})


# Aggreagtion over type axis. We do it only for completeness!
VM_NON_FINITE_FORMS['active'][None] = dict()
VM_NON_FINITE_FORMS['passive'][None] = dict()

# Cases are present only in supine and thus the aggregation is trivial
for case in CASES:
    VM_NON_FINITE_FORMS['active'][None][case] = VM_NON_FINITE_FORMS['active']['supine'][case]
    VM_NON_FINITE_FORMS['passive'][None][case] =  ()

# Tenses are present only in participle and thus the aggregation is trivial
for tense in TENSES:
    for voice in VOICES:
        VM_NON_FINITE_FORMS[voice][None][tense] = VM_NON_FINITE_FORMS[voice]['participle'][tense]

# Aggregation to all active and passive forms
VM_NON_FINITE_FORMS['active'][None][None] = tuple({
    element for type in ('participle', 'supine') for element in VM_NON_FINITE_FORMS['active'][type][None]
})
VM_NON_FINITE_FORMS['passive'][None][None] = tuple({
    element for type in ('participle', 'supine') for element in VM_NON_FINITE_FORMS['passive'][type][None]
})


# Aggregation over voice axis. Applicable only for participle and supine
VM_NON_FINITE_FORMS[None]['participle'] = dict()
for tense in TENSES + (None,):
    VM_NON_FINITE_FORMS[None]['participle'][tense] = tuple({
        element for voice in VOICES for element in VM_NON_FINITE_FORMS[voice]['participle'][tense]
    })

VM_NON_FINITE_FORMS[None]['supine'] = dict()
for case in CASES:
    VM_NON_FINITE_FORMS[None]['supine'][case] = VM_NON_FINITE_FORMS['active']['supine'][case]
VM_NON_FINITE_FORMS[None]['supine'][None] = tuple({
    element for voice in VOICES for element in VM_NON_FINITE_FORMS[voice]['supine'][None]
})

# Fake aggregation over voice and type for fixed subtype
VM_NON_FINITE_FORMS[None][None] = dict()
for tense in TENSES:
    VM_NON_FINITE_FORMS[None][None][tense] = VM_NON_FINITE_FORMS[None]['participle'][tense]
for case in CASES:
    VM_NON_FINITE_FORMS[None][None][case] =  VM_NON_FINITE_FORMS[None]['supine'][case]

# Aggregation of all non-finite forms
VM_NON_FINITE_FORMS[None][None][None] = tuple({element for type in TYPES for element in VM_NON_FINITE_FORMS[None][type][None]})