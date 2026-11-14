from typing import List, Tuple, Literal, Optional, Union

from estnltk.vabamorf.form_generators.morph_tables.nouns.common_indices import CASES
from estnltk.vabamorf.form_generators.morph_tables.nouns.noun_forms import CASE_WILDCARDS
from estnltk.vabamorf.form_generators.morph_tables.nouns.noun_forms import ILLATIVE_SUBCASES
from estnltk.vabamorf.form_generators.morph_tables.nouns.noun_forms import VM_NOUN_FORMS

def generate_noun_forms(
        lemma: Union[str, List[str]],
        case: Optional[str] = None,
        number: Optional[Literal['singular', 'plural']] = None,
        *args, **kwargs
) -> List[str]:
    """
    Generates specified forms for specified lemma or list of lemmas.
    Lemma must be noun or list of nouns. Does not work with pronouns!
    One can specify case and grammatical number. There are several wildcards for case:
    - base_cases: first three cases
    - location_cases: six location cases
    - peripheral_cases: the remaining five cases
    - paradigm_cases: cases together with grammatical number that fully specify other cases

    If some aspect is not specified then all possible variants are considered.
    The result is a list of noun forms in no specific order.

    All additional arguments are passed to Vabamorf synthesize function.
    Use these additional arguments to finetune synthesis only if you really know what you are doing!
    """
    from estnltk.vabamorf.morf import synthesize
    
    if not isinstance(lemma, str) and not isinstance(lemma, list):
        raise ValueError('Invalid input: lemma must be a string or list of strings')
    if case == 'paradigm_cases' and number is not None:
        raise ValueError('One cannot specify grammatical number for paradigm cases')
    if case not in CASES + CASE_WILDCARDS + ILLATIVE_SUBCASES + (None,):
        raise ValueError('Invalid case')
    if case == 'short_illative' and number != 'singular':
        raise ValueError('Short illative is defined only for singular')

    if isinstance(lemma, str):
        return tuple({
            element for form in VM_NOUN_FORMS[number][case]
            for element in synthesize(lemma, partofspeech='S', form=form, *args, **kwargs)
        })
    elif isinstance(lemma, list):
        return tuple({
            output_element for form in VM_NOUN_FORMS[number][case]
            for lemma_element in lemma
            for output_element in synthesize(lemma_element, partofspeech='S', form=form, *args, **kwargs)
        })