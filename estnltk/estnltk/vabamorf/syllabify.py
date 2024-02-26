from estnltk.vabamorf import vabamorf as vm
from estnltk.vabamorf.morf_extra import analyze
from estnltk.vabamorf.morf import convert

# Note: dash and slash are special symbols for Vabamorf's syllabifier
# marking points where words are split.
# Analysing these characters alone causes syllabifier to crash, so
# we should refrain from analysing them and only analyse strings and
# symbols around them.
_SPECIAL_SYMBOL_SYLLABLES = {
    '-': {'syllable': '-', 'quantity': 3, 'accent': 1},
    '/': {'syllable': '/', 'quantity': 3, 'accent': 1}
}


def syllabify_word(word, as_dict=True, split_compounds=True, tolerance=2):
    # Split word by special symbols
    word_tokens = _split_word_for_syllabification(word)
    raw_syllables = []
    for token in word_tokens:
        if token in _SPECIAL_SYMBOL_SYLLABLES:
            # If the token is a special symbol, then do not apply
            # Vabamorf on it -- instead, take the symbol from
            # dictionary
            raw_syllables.append(_SPECIAL_SYMBOL_SYLLABLES[token])
        else:
            if not split_compounds:
                # The old syllabification: does not take account
                # of compound word boundaries
                # noinspection PyUnresolvedReferences
                syllables = vm.syllabify(convert(token))
                raw_syllables.extend(syllables)
            else:
                # Split word by compound word boundaries (heuristic)
                subwords = _split_compound_word_heuristically(token, tolerance=tolerance)
                # Syllabify each subword separately
                for subword in subwords:
                    # noinspection PyUnresolvedReferences
                    syllables = vm.syllabify(convert(subword))
                    raw_syllables.extend(syllables)
    if as_dict:
        return [syllable_as_dict(syllable) for syllable in raw_syllables]
    return [syllable_as_tuple(syllable) for syllable in raw_syllables]


def syllabify_words(words, as_dict=True, split_compounds=True, tolerance=2):
    return [syllabify_word(w, as_dict=as_dict, split_compounds=split_compounds, tolerance=tolerance) for w in words]


def syllable_as_dict(syllable):
    if isinstance(syllable, dict):
        return syllable
    return dict(syllable=syllable.syllable,
                quantity=syllable.quantity,
                accent=syllable.accent)


def syllable_as_tuple(syllable):
    if isinstance(syllable, dict):
        return syllable['syllable'], syllable['quantity'], syllable['accent']
    return syllable.syllable, syllable.quantity, syllable.accent


# Heuristic: attempts to split the input word by its
# compound word boundaries. Only succeeds if:
#  a) the input word is unambiguously a compound word;
#  b) lemma and the surface form of the input word
#     match by prefix (to extent of compound word
#     boundaries);
# If tolerance is defined (default: tolerance=2), then
# allows the given amount of characters to be mismatched
# at the end of a sub word of the compound if the
# mismatch is followed by at least 2 matching characters
def _split_compound_word_heuristically(word_text, tolerance=2):
    # Discard unanalysable inputs
    if word_text is None or len(word_text) == 0 or word_text.isspace():
        return [word_text]
    # Apply morph analysis to determine if we have a compound
    analyses_of_word = analyze(word_text, guess=True, propername=True, disambiguate=False)

    all_root_tokens = []
    for a in analyses_of_word[0]['analysis']:
        if a['root_tokens'] not in all_root_tokens:
            all_root_tokens.append(a['root_tokens'])
    if len(all_root_tokens) == 1:

        # Find recursively next matching position within (small) edit radius
        # The next matching positions must cover at least 2 characters
        def _find_next_match(root_tokens, word, cur_c, cur_j, cur_i, eds):
            # Advance in root_tokens if needed
            if cur_j >= len(root_tokens[cur_i]):
                cur_j = 0
                cur_i += 1
            # Can we check this position?
            if cur_c < len(word) and \
                    cur_i < len(root_tokens) and \
                    cur_j < len(root_tokens[cur_i]):
                wc = word[cur_c]
                rc = all_root_tokens[cur_i][cur_j]
                if wc == rc:
                    # We've found a match!
                    # Check if the next chars also match
                    # (but don't do it recursively)
                    next_is_also_match = False
                    next_c = cur_c + 1
                    next_j = cur_j + 1
                    next_i = cur_i
                    if next_j >= len(root_tokens[next_i]):
                        next_j = 0
                        next_i += 1
                    next_is_also_match = (next_c < len(word) and
                                          next_i < len(root_tokens) and
                                          next_j < len(root_tokens[next_i]) and
                                          word[next_c] == all_root_tokens[next_i][next_j])
                    if next_is_also_match:
                        # Return a matching position only if
                        # the next position also matched
                        return cur_c, cur_j, cur_i
                elif eds > 0:
                    # Check next positions
                    next_positions = [
                        _find_next_match(root_tokens, word, cur_c+1, cur_j, cur_i, eds-1),
                        _find_next_match(root_tokens, word, cur_c, cur_j+1, cur_i, eds-1),
                        _find_next_match(root_tokens, word, cur_c+1, cur_j+1, cur_i, eds-1),
                    ]
                    for (nc, nj, ni) in next_positions:
                        if nc != -1:
                            # Return first position if we've found a match
                            return nc, nj, ni
            # return a mismatching position
            return -1, -1, -1

        # The compound is unambiguous
        all_root_tokens = all_root_tokens[0]
        # Throw out empty strings
        all_root_tokens = [rt for rt in all_root_tokens if len(rt) > 0]
        if len(all_root_tokens) < 2:
            # Nothing to split here: move along!
            return [word_text]
        # Assume prefix of the root can be matched to prefix of the
        # surface form; Split as long as there is a match:
        c = 0
        i = 0
        j = 0
        split_word_text = [[]]
        wc = ''
        rc = ''
        while c < len(word_text):
            wc = word_text[c]
            rc = all_root_tokens[i][j]
            if wc == rc:
                split_word_text[-1].append(wc)
            else:
                if tolerance > 0:
                    # If we have a tolerance, try to find next matching
                    # position
                    (next_c, next_j, next_i) = \
                        _find_next_match(all_root_tokens, word_text, c, j, i, tolerance)
                    if next_c > -1 and next_i - i < 2:
                        # Match at the start of the same or next root_token
                        if next_j == 0 and next_i == i:
                            # 1) We are at the start of the same root_token
                            # Add skipped positions
                            if len(split_word_text) > 1:
                                split_word_text[-2].append(word_text[c:next_c])
                            else:
                                split_word_text[-1].append(word_text[c:next_c])
                            split_word_text[-1].append(word_text[next_c])
                            # Update indexes
                            c = next_c
                            j = next_j
                            i = next_i
                        elif next_j == 0 and next_i != i:
                            # 2) We are at the start of the next root_token
                            # Add skipped positions with break
                            split_word_text[-1].append(word_text[c:next_c])
                            split_word_text.append([])
                            split_word_text[-1].append(word_text[next_c])
                            # Update indexes
                            c = next_c
                            j = next_j
                            i = next_i
                        elif next_j == len(all_root_tokens[next_i])-1 and next_i == i:
                            # 3)  We are at the end of the same root_token
                            # Add skipped positions
                            split_word_text[-1].append(word_text[c:next_c])
                            split_word_text[-1].append(word_text[next_c])
                            # Update indexes
                            c = next_c
                            j = next_j
                            i = next_i
                        else:
                            # break in case of no suitable matching position
                            # (unable to match inflected lemma)
                            break
                    else:
                        # break in case of no suitable matching position
                        # (unable to match inflected lemma)
                        break
                else:
                    # break in case of a mismatch or
                    # no tolerance for mismatches
                    # (unable to match inflected lemma)
                    break
            c += 1
            j += 1
            if j >= len(all_root_tokens[i]):
                j = 0
                i += 1
                if i >= len(all_root_tokens):
                    break
                    # Make a break in word_text
                if len(split_word_text[-1]) > 0 and \
                        c < len(word_text):
                    split_word_text.append([])
        while c < len(word_text):
            wc = word_text[c]
            split_word_text[-1].append(wc)
            c += 1
        return [''.join(chars) for chars in split_word_text]
    # If the compound was ambiguous, or there were problems with
    # determining the compound boundaries, the return the input
    # text without splitting:
    return [word_text]


# Prepares word for syllabification: tokenizes word in a way
# that dash and slash are separate symbols
def _split_word_for_syllabification(word_text):
    split_word = [[]]
    for cid, c in enumerate(word_text):
        if c not in ['-', '/']:
            split_word[-1].append(c)
        else:
            if len(split_word[-1]) > 0:
                split_word.append([])
            split_word[-1].append(c)
            if cid+1 < len(word_text):
                split_word.append([])
    return [''.join(chars) for chars in split_word]
