from collections import defaultdict
from dataclasses import dataclass
from itertools import product
import json


@dataclass
class Token:
    span: tuple[int, int]
    form: str
    lemma: str
    pos: set[str]
    features: dict[str, str]
    sentence: int
    clause: int
    identifier: int
    head: int
    deprel: str


def load_lexicon(path, max_components):
    entries = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(entries, list):
        raise ValueError(f'{path}: expected a JSON list of expressions.')
    by_lemma = defaultdict(list)
    for index, entry in enumerate(entries):
        parts = entry['components']
        anchors = [part for part in parts if part['is_anchor']]
        if len(parts) < 2 or len(anchors) != 1:
            raise ValueError(f"{entry['expression']!r}: expected one anchor and at least one other component.")
        if len(parts) - 1 > max_components:
            raise ValueError(f"{entry['expression']!r} exceeds max_components={max_components}.")
        lemmas = anchors[0]['lemmas']
        if not anchors[0]['match_by_lemma'] or not isinstance(lemmas, list) or not lemmas:
            raise ValueError(f"{entry['expression']!r}: the anchor must match by lemma and have lemmas.")
        for lemma in lemmas:
            by_lemma[lemma.casefold()].append(index)
    return entries, by_lemma


def is_finite(token):
    """Return True, False, or None when finiteness is unspecified."""
    if 'VerbForm' in token.features:
        return token.features['VerbForm'] == 'Fin'
    labels = set(token.features) | set(token.features.values())
    if labels & {'indic', 'imper', 'cond', 'quot'}:
        return True
    if labels & {'inf', 'sup', 'ger', 'partic'}:
        return False
    if 'neg' in labels:
        labels |= {'neg ' + label for label in labels}
    if labels & {
        'b', 'd', 'n', 'me', 'te', 'vad', 's', 'sin', 'sid', 'sime', 'site',
        'o', 'gu', 'gem', 'ge', 'ks', 'ksin', 'ksid', 'ksime', 'ksite',
        'nuks', 'nuksin', 'nuksid', 'nuksime', 'nuksite', 'vat', 'nuvat',
        'ta', 'tagu', 'taks', 'takse', 'tavat', 'ti', 'tuks', 'tuvat',
        'neg o', 'neg gu', 'neg gem', 'neg ge', 'neg me', 'neg ks',
        'neg nud', 'neg nuks', 'neg vat', 'neg da',
    }:
        return True
    if labels & {
        'da', 'des', 'ma', 'maks', 'mas', 'mast', 'mata', 'tama',
        'nud', 'tud', 'v', 'tav', 'neg tud',
    }:
        return False


def verb_lemmas(token, include_nonfinite, participle_lemmas):
    if token.pos & {'V', 'VERB', 'AUX'}:
        return {token.lemma} if token.lemma not in {'ei', 'ära'} else set()
    if include_nonfinite and token.pos & {'A', 'ADJ'}:
        lemmas = set(participle_lemmas(token.form, token.lemma))
        if token.features.get('VerbForm') == 'Part':
            lemmas.add(token.lemma)
        return lemmas
    return set()


def dependency_graph(tokens):
    by_id = {(token.sentence, token.identifier): i for i, token in enumerate(tokens)}
    parents = [by_id[token.sentence, token.head] if token.head else None for token in tokens]
    children = [[] for token in tokens]
    for child, parent in enumerate(parents):
        if parent is not None:
            children[parent].append(child)
    return parents, children


def subtree(tokens, children, start, clause):
    found, pending = [], [start]
    while pending:
        index = pending.pop()
        if tokens[index].clause == clause:
            found.append(index)
            pending.extend(children[index])
    return found


def find_matches(tokens, entries, by_lemma, participle_lemmas, *,
                 include_nonfinite=False, include_compound_verbs=False,
                 include_copula_heads=False):
    parents, children = dependency_graph(tokens)
    verbs = [verb_lemmas(token, include_nonfinite, participle_lemmas) for token in tokens]
    for anchor, token in enumerate(tokens):
        if not verbs[anchor]:
            continue
        rule_indices = sorted({i for lemma in verbs[anchor] for i in by_lemma.get(lemma, [])})
        particles = [i for i in children[anchor]
                     if tokens[i].clause == token.clause and tokens[i].deprel == 'compound:prt'
                     ] if include_compound_verbs else []
        if not rule_indices and not particles:
            continue
        if not include_nonfinite and is_finite(token) is False:
            continue

        central, ancestor = True, parents[anchor]
        while ancestor is not None and tokens[ancestor].clause == token.clause:
            if verbs[ancestor]:
                central = False
                break
            ancestor = parents[ancestor]

        root = anchor
        if include_copula_heads and token.lemma == 'olema' and token.deprel == 'cop':
            parent = parents[anchor]
            if parent is not None and tokens[parent].clause == token.clause:
                root = parent
        candidates = sorted(i for i in subtree(tokens, children, root, token.clause) if i != anchor)
        lemma_index, form_index = defaultdict(list), defaultdict(list)
        for i in candidates:
            lemma_index[tokens[i].lemma].append(i)
            form_index[tokens[i].form.casefold()].append(i)

        for rule_index in rule_indices:
            entry = entries[rule_index]
            choices = []
            for part in entry['components']:
                if part['is_anchor']:
                    continue
                if part['match_by_lemma']:
                    choices.append(sorted({i for lemma in part['lemmas']
                                           for i in lemma_index.get(lemma.casefold(), [])}))
                else:
                    choices.append(form_index.get(part['form'].casefold(), []))
            for assignment in product(*choices):
                if len(set(assignment)) != len(assignment):
                    continue
                match = dict(verb=token.span, expression=entry['expression'],
                             is_inflected=entry['is_inflected'], is_central_verb=central)
                match.update({f'comp_{i}': tokens[word].span
                              for i, word in enumerate(assignment, 1)})
                if include_compound_verbs:
                    match['is_compound_verb'] = False
                yield match

        for particle in particles:
            yield dict(verb=token.span, comp_1=tokens[particle].span,
                       expression=f'{tokens[particle].lemma} {token.lemma}',
                       is_inflected=None, is_central_verb=central, is_compound_verb=True)
