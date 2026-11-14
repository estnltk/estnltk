from typing import List, Tuple, Literal, Optional, Union

from itertools import chain, product

from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import VOICES
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import MOODS
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import TENSES
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import PERSONS
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import POLARITY
from estnltk.vabamorf.form_generators.morph_tables.verbs.common_indices import PRONOUN
from estnltk.vabamorf.form_generators.morph_tables.verbs.non_finite_forms import TYPES
from estnltk.vabamorf.form_generators.morph_tables.verbs.non_finite_forms import CASES

from estnltk.vabamorf.form_generators.morph_tables.verbs.finite_forms import VM_FINITE_FORMS
from estnltk.vabamorf.form_generators.morph_tables.verbs.non_finite_forms import VM_NON_FINITE_FORMS

from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_negations import IMPERATIVE_NEGATION_RECIPE
from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_negations import IMPERATIVE_NEGATION_FLAT_RECIPE
from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_negations import FULL_IMPERATIVE_NEGATION_RECIPE
from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_negations import FULL_IMPERATIVE_NEGATION_FLAT_RECIPE

from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_perfect_tenses import PERFECT_MOODS
from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_perfect_tenses import PERFECT_TENSE_PREFIX
from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_perfect_tenses import PERFECT_TENSE_FLAT_PREFIX
from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_perfect_tenses import FULL_PERFECT_TENSE_PREFIX
from estnltk.vabamorf.form_generators.morph_tables.verbs.prefixes_of_perfect_tenses import FULL_PERFECT_TENSE_FLAT_PREFIX

def generate_finite_verb_forms(
        lemma: Union[str, List[str]],
        voice: Optional[Literal['active', 'passive']] = None,
        mood: Optional[Literal['indicative', 'conditional', 'imperative', 'quotative', 'jussive']] = None,
        tense: Optional[Literal['present', 'past']] = None,
        person: Optional[Literal['1s', '2s', '3s', '1p', '2p', '3p']] = None,
        polarity: Optional[Literal['positive', 'negative']] = 'positive',
        *args, **kwargs
) -> List[str]:
    """
    Generates specified finite forms for specified lemma or list of lemmas.
    One can specify voice, mood, tense, grammatical person and polarity.

    By default the function considers verb forms for positive phrases.
    It is also possible to consider verb forms in negation phrases but some of them are not finite forms.
    For the negation, only the forms of the main verb are returned and the forms of 'olema' verb are ignored.

    If some aspect is not specified then all possible variants are considered.
    The result is a list of finite forms in no specific order.

    Note that present perfect and past perfect tenses are achived by standard phrases that contain
    non-finite verb forms and matching form of 'olema' verb. This function does generate these forms
    as they are multi-word constructs. Use genarate_verb_phrases instead.

    All additional arguments are passed to Vabamorf synthesize function.
    Use these additional arguments to finetune synthesis only if you really know what you are doing!
    """
    if voice is not None and voice not in VOICES:
        raise ValueError("Invalid voice.")
    if mood is not None and mood not in MOODS:
        raise ValueError("Invalid mood.")
    if tense is not None and tense not in TENSES:
        raise ValueError("Invalid tense.")
    if person is not None and person not in PERSONS:
        raise ValueError("Invalid person.")
    if polarity is not None and polarity not in POLARITY:
        raise ValueError("Invalid polarity.")
    if voice in ('passive', None) and person is not None:
        raise ValueError('Person cannot be specified for passive voice')

    from estnltk.vabamorf.morf import synthesize
    result = []
    if voice in ('active', None):
        if isinstance(lemma, str):
            result.extend({element for form in VM_FINITE_FORMS[mood][tense][polarity][person]
                          for element in synthesize(lemma, partofspeech='V', form=form, *args, **kwargs)
                          })
        elif isinstance(lemma, list):
            result.extend({output_element for form in VM_FINITE_FORMS[mood][tense][polarity][person]
                          for lemma_element in lemma
                          for output_element in synthesize(lemma_element, partofspeech='V', form=form, *args, **kwargs)
                          })
        else:
            raise ValueError('Invalid input: lemma must be a string or list of strings')

    if voice in ('passive', None):
        if isinstance(lemma, str):
            result.extend({element for form in VM_FINITE_FORMS[mood][tense][polarity]['--']
                          for element in synthesize(lemma, partofspeech='V', form=form, *args, **kwargs)
                          })
        elif isinstance(lemma, list):
            result.extend({output_element for form in VM_FINITE_FORMS[mood][tense][polarity]['--']
                          for lemma_element in lemma
                          for output_element in synthesize(lemma_element, partofspeech='V', form=form, *args, **kwargs)
                          })
        else:
            raise ValueError('Invalid input: lemma must be a string or list of strings')

    return result


def generate_non_finite_verb_forms(
        lemma: Union[str, List[str]],
        voice: Literal['active', 'passive'] = None,
        type: Literal['infinitive', 'participle', 'gerund', 'supine'] = None,
        tense: Optional[str] = None,
        case: Optional[str] = None,
        *args, **kwargs
) -> List[str]:
    """
    Generates specified non-finite forms for specified lemma or list of lemmas.
    One can specify voice, type and subtype through tense and case.
    The argument tense is meaningful only if the type is participle.
    The argument case is meaningful only if type is supine.
    If some aspect is not specified then all possible variants are considered.
    The result is a list of finite forms in no specific order.

    All additional arguments are passed to Vabamorf synthesize function.
    Use these additional arguments to finetune synthesis only if you really know what you are doing!
    """
    if voice is not None and voice not in VOICES:
        raise ValueError("Invalid voice.")
    if type is not None and type not in TYPES:
        raise ValueError("Invalid type.")

    if case is not None:
        if type not in ('supine', None):
            raise ValueError("The argument case cannot specified for the specified type")
        if voice not in ('active', None):
            raise ValueError("The argument case cannot specified for the specified voice")
        if case not in CASES:
            raise ValueError("Invalid value for case type.")
    if tense is not None:
        if type not in ('participle', None):
            raise ValueError("The argument tense cannot specified for the specified type")
        if tense not in TENSES:
            raise ValueError("Invalid value for tense type.")

    from estnltk.vabamorf.morf import synthesize
    subtype = case if case is not None else tense
    if isinstance(lemma, str):
        return list({element for form in VM_NON_FINITE_FORMS[voice][type][subtype]
                      for element in synthesize(lemma, partofspeech='V', form=form, *args, **kwargs)
                      })
    elif isinstance(lemma, list):
        return list({output_element for form in VM_NON_FINITE_FORMS[voice][type][subtype]
                      for lemma_element in lemma
                      for output_element in synthesize(lemma_element, partofspeech='V', form=form, *args, **kwargs)
                      })

    raise ValueError('Invalid input: lemma must be a string or list of strings')


def generate_verb_phrases(
        lemma: Union[str, List[str]],
        voice: Literal['active', 'passive'] = None,
        mood: Literal['indicative', 'conditional', 'imperative', 'quotative', 'jussive'] = None,
        tense: Literal['present', 'past', 'present_perfect', 'past_perfect'] = None,
        person: Literal['1s', '2s', '3s', '1p', '2p', '3p'] = None,
        polarity: Literal['positive', 'negative'] = None,
        output_type: Literal['complete_phrase', 'verb_phrase', 'verb_form'] = 'verb_form',
        flatten_output:bool = True,
        *args, **kwargs
) -> Union[List[str], List[Tuple[str]]]:
    """
    Generates partial or complete verb phrases for specified lemma or list of lemmas.
    One can specify voice, mood, tense, grammatical person and polarity.
    If some aspect is not specified then all possible variants are considered.
    The result is a list of phrases in no specific order.

    There are three possible output types:
    - verb_form: returns only the form of the main verb (e.g. lugenud)
    - verb_phrase: return the verb phrase together without subject (e.g. ei olnud lugenud)
    - complete_phrase: return the verb phrase together with subject (e.g. ma ei olnud lugenud)

    The flag flatten_output tells if the phrase is a list of strings or a string where words 
    are separated by spaces. 
    For verb forms only flattened output is produced as generation of one-element tuples is 
    pointless. 

    All additional arguments are passed to Vabamorf synthesize function.
    Use these additional arguments to finetune synthesis only if you really know what you are doing!
    """
    if not isinstance(lemma, str) and not isinstance(lemma, list):
        raise ValueError('Invalid input: lemma must be a string or list of strings')
    if voice in ('passive', None) and person is not None:
        raise ValueError('Person cannot be specified for passive voice')
    if output_type not in ('complete_phrase', 'verb_phrase', 'verb_form'):
        raise ValueError('Invalid output_type value')
    if output_type == 'verb_form' and not flatten_output:
        raise ValueError("The flag flatten_output must be set for the output type 'verb_form'")

    from estnltk.vabamorf.morf import synthesize
    result = []
    if output_type == 'verb_form':
        if not flatten_output:
            raise ValueError("Flag flatten_output must be set if output type is 'verb_form'")

        # Handle present and past tenses first
        if tense in ('present','past', None):
            result.extend(generate_finite_verb_forms(
                lemma, voice=voice, mood=mood, tense=tense, person=person, polarity=polarity, *args, **kwargs))

        # Perect tenses have the same participle form regardless of polarity
        if tense in ('present_perfect', 'past_perfect', None) and mood in PERFECT_MOODS + (None,):
            result.extend(generate_non_finite_verb_forms(lemma, voice=voice, type='participle', tense='past'))

        return result

    # Handle all other output types

    # Negation of imperative mood and present tense is so different that it must be handled separately
    if  tense in ('present', None) and polarity in ('negative', None) and mood in ('imperative', 'jussive', None):

        # Proper cofigurarion of negation recipie
        if output_type == 'verb_phrase' and flatten_output:
            recipes = IMPERATIVE_NEGATION_FLAT_RECIPE
        if output_type == 'verb_phrase' and not flatten_output:
            recipes = IMPERATIVE_NEGATION_RECIPE
        if output_type == 'complete_phrase' and flatten_output:
            recipes = FULL_IMPERATIVE_NEGATION_FLAT_RECIPE
        if output_type == 'complete_phrase' and not flatten_output:
            recipes = FULL_IMPERATIVE_NEGATION_RECIPE

        if voice in ('active', None):
            if isinstance(lemma, str):
                if flatten_output:
                    result.extend(f'{prefix} {suffix}'
                                  for prefix, vm_form_directive in recipes[person]
                                  for suffix in synthesize(lemma, partofspeech='V', form=vm_form_directive, *args, **kwargs))
                else:
                    result.extend(prefix + (suffix,)
                                  for prefix, vm_form_directive in recipes[person]
                                  for suffix in synthesize(lemma, partofspeech='V', form=vm_form_directive, *args, **kwargs))
            elif isinstance(lemma, list):
                if flatten_output:
                    result.extend(f'{prefix} {suffix}'
                                  for prefix, vm_form_directive in recipes[person]
                                  for lemma_element in lemma
                                  for suffix in synthesize(lemma_element, partofspeech='V', form=vm_form_directive, *args, **kwargs))
                else:
                    result.extend(prefix + (suffix,)
                                  for prefix, vm_form_directive in recipes[person]
                                  for lemma_element in lemma
                                  for suffix in synthesize(lemma_element, partofspeech='V', form=vm_form_directive, *args, **kwargs))

        if voice in ('passive', None):
            if isinstance(lemma, str):
                if flatten_output:
                    result.extend(f'{prefix} {suffix}'
                                  for prefix, vm_form_directive in recipes['--']
                                  for suffix in synthesize(lemma, partofspeech='V', form=vm_form_directive, *args, **kwargs))
                else:
                    result.extend(prefix + (suffix,)
                                  for prefix, vm_form_directive in recipes['--']
                                  for suffix in synthesize(lemma, partofspeech='V', form=vm_form_directive, *args, **kwargs))
            elif isinstance(lemma, list):
                if flatten_output:
                    result.extend(f'{prefix} {suffix}'
                                  for prefix, vm_form_directive in recipes['--']
                                  for lemma_element in lemma
                                  for suffix in synthesize(lemma_element, partofspeech='V', form=vm_form_directive, *args, **kwargs))
                else:
                    result.extend(prefix + (suffix,)
                                  for prefix, vm_form_directive in recipes['--']
                                  for lemma_element in lemma
                                  for suffix in synthesize(lemma_element, partofspeech='V', form=vm_form_directive, *args, **kwargs))


    # Present and past tense cases follow universal patterns without subject
    # For passive voice the complete phrase and verb phrase coincide
    if tense in ('present', 'past', None) and (output_type == 'verb_phrase' or voice in ('passive', None)):

        if polarity in ('positive', None):
            suffixes = generate_finite_verb_forms(
                lemma, voice=voice, mood=mood, tense=tense, person=person, polarity='positive', *args, **kwargs)

            if flatten_output:
                result.extend(suffixes)
            else:
                result.extend((suffix,) for suffix in suffixes)

        # Exclude negative imperative forms as these have been already generated
        if polarity in ('negative', None) and mood not in ('imperative', 'jussive'):
            # We still need to exclude suffixes for negation of imperative mood and present tense
            if mood is None:
                suffixes = generate_finite_verb_forms(
                    lemma, voice=voice, mood='indicative', tense=tense, person=person, polarity='negative', *args, **kwargs)
                suffixes += generate_finite_verb_forms(
                    lemma, voice=voice, mood='conditional', tense=tense, person=person, polarity='negative', *args, **kwargs)
                suffixes += generate_finite_verb_forms(
                    lemma, voice=voice, mood='quotative', tense=tense, person=person, polarity='negative', *args, **kwargs)
            else:
                suffixes = generate_finite_verb_forms(
                        lemma, voice=voice, mood=mood, tense=tense, person=person, polarity='negative', *args, **kwargs)

            if flatten_output:
                result.extend(f'ei {suffix}' for suffix in suffixes)
            else:
                result.extend(('ei', suffix) for suffix in suffixes)

        # Abort if no perfect tense forms are ordered
        # For complete phrases we still need to generate active voice forms
        if tense is not None and (output_type == 'verb_phrase' or voice == 'passive'):
            return result

    # Present and past tense phrases with subject require additional care to get consistency
    # Phrases with passive voice are already generated we need to handle only active voice here
    if tense in ('present', 'past', None) and output_type == 'complete_phrase' and voice in ('active', None):

        # Exclude negative imperative forms as these have been already generated
        if polarity in ('negative', None) and mood not in ('imperative', 'jussive'):
            # We still need to exclude suffixes for negation of imperative mood and present tense
            if mood is None:
                suffixes = generate_finite_verb_forms(
                    lemma, voice=voice, mood='indicative', tense=tense, person=person, polarity='negative', *args, **kwargs)
                suffixes += generate_finite_verb_forms(
                    lemma, voice=voice, mood='conditional', tense=tense, person=person, polarity='negative', *args, **kwargs)
                suffixes += generate_finite_verb_forms(
                    lemma, voice=voice, mood='quotative', tense=tense, person=person, polarity='negative', *args, **kwargs)
            else:
                suffixes = generate_finite_verb_forms(
                    lemma, voice=voice, mood=mood, tense=tense, person=person, polarity='negative', *args, **kwargs)

            # We also need to generate pronoun prefixes
            prefixes = PRONOUN.values() if person is None else (PRONOUN[person],)
            if flatten_output:
                result.extend(f'{prefix} ei {suffix}' for prefix in prefixes for suffix in suffixes)
            else:
                result.extend((prefix, 'ei', suffix) for prefix in prefixes for suffix in suffixes)

        # For positive forms we need to assure consistency by fixing persons name
        if polarity in ('positive', None):
            for cycle_person in PERSONS if person is None else (person,):
                
                if not (voice in ('passive', None)): # Person cannot be specified for passive voice
                    suffixes = generate_finite_verb_forms(
                        lemma, voice=voice, mood=mood, tense=tense, person=cycle_person, polarity='positive', *args, **kwargs)

                    if flatten_output:
                        result.extend(f'{PRONOUN[cycle_person]} {suffix}' for suffix in suffixes)
                    else:
                        result.extend((PRONOUN[cycle_person], suffix,) for suffix in suffixes)

        # Abort if no perfect tense forms are ordered
        if tense is not None:
            return result


    # Generation of phrases for forms in perfect tenses
    # Proper cofigurarion of prefix maps for perfect tenses and output types
    if output_type not in ('complete_phrase', 'verb_phrase'):
        raise ValueError('Invalid output_type value')
    if output_type == 'verb_phrase' and flatten_output:
        prefixes = PERFECT_TENSE_FLAT_PREFIX
    if output_type == 'verb_phrase' and not flatten_output:
        prefixes = PERFECT_TENSE_PREFIX
    if output_type == 'complete_phrase' and flatten_output:
        prefixes = FULL_PERFECT_TENSE_FLAT_PREFIX
    if output_type == 'complete_phrase' and not flatten_output:
        prefixes = FULL_PERFECT_TENSE_PREFIX

    # Perfrect tense patterns for active and passive voice are different and do not mix!
    if voice in ('active', None) and mood in PERFECT_MOODS + (None,):

        # Select the right form for the main verb
        suffixes = generate_non_finite_verb_forms(lemma, voice='active', type='participle', tense='past')

        if flatten_output:
            result.extend(f'{prefix} {suffix}'
                          for prefix in prefixes[mood][tense][polarity][person]
                          for suffix in suffixes)
        else:
            result.extend((*prefix, suffix)
                          for prefix in prefixes[mood][tense][polarity][person]
                          for suffix in suffixes)

    if voice in ('passive', None) and mood in PERFECT_MOODS + (None,):

        # Select the right form for the main verb
        suffixes = generate_non_finite_verb_forms(lemma, voice='passive', type='participle', tense='past')

        if flatten_output:
            result.extend(f'{prefix} {suffix}'
                          for prefix in prefixes[mood][tense][polarity]['--']
                          for suffix in suffixes)
        else:
            result.extend((*prefix, suffix)
                          for prefix in prefixes[mood][tense][polarity]['--']
                          for suffix in suffixes)

    return result
