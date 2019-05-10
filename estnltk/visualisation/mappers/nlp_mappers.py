from typing import Tuple, Sequence


def word_bg_colour(segment: Tuple[str, Sequence]) -> str:
    """
    Default background colouring for words

    - Shows words that have been normalised in different colour
    - Shows places where tokenization is non-unique in red

    Ask input from Siim

    """

    # Tokenization conflict

    if len(segment[1]) != 1:
        return 'red'

    return 'blue'


def morph_bg_colour(segment: Tuple[str, Sequence]) -> str:
    """Default background colouring for Estmorph tag-system

    Ask Dage and Liisi what is the standard colour scheme
    It might be reasonable to define

    """

    # Tokenization conflict

    if len(segment[1]) != 1:
        return 'red'

    # It might be better to convert it to string
    pos_tags = getattr(segment[1][0], 'partofspeech')

    # Ambigous POS tagging
    if len(pos_tags) > 1:
        return 'orange'
    elif len(pos_tags) == 0:
        return 'gray'

    pos_bg_coloring = {'S': 'green', 'V': 'yellow', 'O': 'blue'}
    return pos_bg_coloring.get(pos_tags[0], 'gray')
