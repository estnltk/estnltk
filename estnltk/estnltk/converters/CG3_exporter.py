def _esc_double_quotes(str1):
    """Escapes double quotes (").

    """
    return str1.replace('"', '\\"').replace('\\\\\\"', '\\"').replace('\\\\"', '\\"')


def _insert_pers(pronoun_type):
    pronoun_type = list(pronoun_type)
    for i, t in enumerate(pronoun_type):
        if t in {'ps1', 'ps2', 'ps3'}:
            pronoun_type.insert(i, 'pers')
            break
    return tuple(pronoun_type)


def _is_partic_suffix(suffix):
    return suffix in {'tud', 'nud', 'v', 'tav', 'mata'}


def export_CG3(text, sentences_layer: str = 'sentences',
               morph_layer: str = 'morph_extended'):
    """Converts text with morph_extended layer to cg3 input format.

        Returns
        -------
            A list of strings in the VISL CG3 input format.

    """
    assert sentences_layer in text.layers, 'sentences layer required'
    assert morph_layer in text.layers, 'morph_extended or equivalent layer required'

    morph_lines = []
    word_index = -1
    for sentence in text[sentences_layer]:
        morph_lines.append('"<s>"')
        for word in sentence:
            word_index += 1
            morph_lines.append('"<' + _esc_double_quotes(word.text) + '>"')
            for morph_extended in text[morph_layer][word_index].annotations:
                form_list = [morph_extended.partofspeech]
                if morph_extended.pronoun_type:
                    form_list.extend(_insert_pers(morph_extended.pronoun_type))
                if morph_extended.form:
                    form_list.append(morph_extended.form)
                if morph_extended.punctuation_type:
                    form_list.append(morph_extended.punctuation_type)
                if morph_extended.letter_case:
                    form_list.append(morph_extended.letter_case)
                if morph_extended.fin:
                    form_list.append('<FinV>')
                for ves in morph_extended.verb_extension_suffix:
                    if _is_partic_suffix(ves):
                        form_list.append('partic')
                    form_list.append(''.join(('<', ves, '>')))
                if morph_extended.subcat:
                    subcat = morph_extended.subcat
                    subcat = [''.join(('<', s, '>')) for s in subcat]
                    form_list.extend(subcat)

                form_list = ' '.join(form_list)

                if morph_extended.ending or morph_extended.clitic:
                    line = ''.join(('    "', _esc_double_quotes(morph_extended.root),
                                    '" L', morph_extended.ending, morph_extended.clitic,
                                    ' ', form_list))
                else:
                    if morph_extended.partofspeech == 'Z':
                        line = ''.join(('    "', _esc_double_quotes(morph_extended.root), '" ', form_list))
                    else:
                        line = ''.join(('    "', _esc_double_quotes(morph_extended.root), '+" ', form_list))
                morph_lines.append(line)
        morph_lines.append('"</s>"')
    return morph_lines
