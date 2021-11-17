from collections import Counter
from typing import Union, List, Optional

from estnltk.layer.layer import Layer
from estnltk.text import Text
from taggers.standard.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger


def las_decomposition(gold_layer, predicted_layer, clauses_layer):
    """Finds E1, E2 and E3 types of errors"""
    e1 = 0
    e2 = 0
    e3 = 0
    for idx, clause in enumerate(clauses_layer):

        in_clause_heads = [gold_layer.get(span)['id'] for span in clause]
        for span in clause:
            gold_span = gold_layer.get(span)
            gold_pos = gold_span['xpostag']
            gold_head = gold_span['head']
            gold_deprel = gold_span['deprel']

            predicted_span = predicted_layer.get(span)
            predicted_head = predicted_span['head']
            predicted_deprel = predicted_span['deprel']

            if gold_pos == 'Z':
                continue

            if gold_span['id'] in in_clause_heads:
                if gold_head == predicted_head and gold_deprel == predicted_deprel:
                    continue
                else:
                    if predicted_head in in_clause_heads:
                        e1 += 1
                    else:
                        e2 += 2

            else:
                if gold_head == predicted_head and gold_deprel == predicted_deprel:
                    continue
                else:
                    e3 += 1

    return {'LAS_E1': e1, 'LAS_E2': e2, 'LAS_E3': e3}


def score_counts(gold_layer: Layer, predicted_layer: Layer, clauses_layer: Layer,
                 metrics: Optional[List], decomposition: Optional[str]):

    gold_pos = list(gold_layer['xpostag'])
    gold_deprels = list(gold_layer['deprel'])
    gold_heads = list(gold_layer['head'])

    predicted_deprels = list(predicted_layer['deprel'])
    predicted_heads = list(predicted_layer['head'])

    total_words = 0  # without punctuation
    scores = {'LAS': 0, 'UAS': 0, 'LA': 0}

    for pos, gold_head, predicted_head, gold_deprel, predicted_deprel in zip(gold_pos, gold_heads, predicted_heads,
                                                                             gold_deprels, predicted_deprels):
        if pos == 'Z':
            continue
        total_words += 1
        if predicted_head == gold_head and predicted_deprel == gold_deprel:
            scores['LAS'] += 1
            scores['UAS'] += 1
            scores['LA'] += 1
        elif predicted_head == gold_head:
            scores['UAS'] += 1
        elif predicted_deprel == gold_deprel:
            scores['LA'] += 1

    result = {}
    for metric in metrics:
        result[metric] = scores[metric]

    if decomposition == 'LAS':
        result.update(las_decomposition(gold_layer, predicted_layer, clauses_layer))

    return result, total_words


def calculate_scores(scores_dict, total_words):
    # From counts to percentages
    for key, value in scores_dict.items():
        scores_dict[key] = value / total_words * 100
    return scores_dict


def score_syntax(texts: Union[Text, List[Text]], gold_layer: str, predicted_layer: str, clauses_layer: str = None,
                 metrics: List[str] = None, decomposition: str = None):
    """
    Calculates syntax scores and decomposition of scores for two syntax layers with matching spans.
    :param texts: List of Texts or single Text for calculating scores
    :param gold_layer: name of gold layer
    :param predicted_layer: name of predicted layer
    :param clauses_layer: name of clauses layer (needed for decomposition)
    :param metrics: list of metrics, choose from following: 'LAS', 'UAS', 'LA'
    :param decomposition: metric to decompose, currently 'LAS' only
    :return: dictionary of scores
    """
    if metrics is None:
        metrics = ['LAS', 'UAS', 'LA']

    if decomposition is not None and clauses_layer is None:
        raise ValueError('Clauses layer must be given if decomposition is assigned.')

    if isinstance(texts, Text):
        las_counts, total_words = score_counts(texts[gold_layer], texts[predicted_layer], texts[clauses_layer],
                                               metrics, decomposition)

    else:
        counter = Counter()
        total_words = 0
        for text in texts:
            las_counts, text_words = score_counts(text[gold_layer], text[predicted_layer], text[clauses_layer],
                                                  metrics, decomposition)
            total_words += text_words
            counter.update(las_counts)

        las_counts = dict(counter)

    return calculate_scores(las_counts, total_words)
