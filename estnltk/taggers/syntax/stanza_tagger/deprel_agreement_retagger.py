import csv
import os
from typing import MutableMapping

from estnltk.core import PACKAGE_PATH
from estnltk.layer.layer import Layer
from estnltk.taggers.retagger import Retagger

RESOURCES = os.path.join(PACKAGE_PATH, 'taggers', 'syntax', 'stanza_tagger', 'agreement_resources')


class DeprelAgreementRetagger(Retagger):
    """
    Adds `agreement_deprel` attribute on layer. If deprel between head and dependant is specified in
    tables (in agreement_resources folder) and predicted deprel is not one of them, correct deprels
    are presented in `agreement_deprel`. Otherwise None.
    """

    conf_param = ['rules']

    def __init__(self, output_layer='stanza_syntax'):
        self.input_layers = [output_layer]
        self.output_layer = output_layer
        self.output_attributes = ()
        self.rules = create_rule_dict()

    def _change_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        attributes = list(layer.attributes)
        if 'agreement_deprel' not in layer.attributes:
            attributes.extend(('agreement_deprel',))
        layer.attributes = tuple(attributes)

        for i, span in enumerate(layer):
            annotation = span.annotations[0]
            annotation['agreement_deprel'] = None
            if annotation['head'] == 0 or annotation['feats'] is None:
                continue
            dependant_lemma = annotation['lemma']
            for case, rules in self.rules.items():
                # No rules exist for this case / these words.
                if case not in annotation['feats'].keys() or dependant_lemma not in rules:
                    continue
                head_lemma = annotation['parent_span'].annotations[0]['lemma']
                if head_lemma not in rules[dependant_lemma]:
                    continue

                # In case suitable rules exist:
                agreed_deprels = rules[dependant_lemma][head_lemma]
                if annotation['deprel'] not in agreed_deprels:
                    annotation['agreement_deprel'] = set(agreed_deprels)


def normalize_lemma(lemma):
    return lemma.replace('=', '').replace('_', '')


def master_list_to_rules(deprel_col: int, csv_file):
    """
    Makes dictionary of rules from csv-s based on master lists.
    Csv-s contain lemma of head (column 0) and lemma of dependant (column 1).
    Column that contains deprel must be specified.
    :param deprel_col: column no, where deprel is
    :param csv_file:
    :return: dictionary in the form of {dependant: {head: [deprel], head:[deprel1, deprel2]}}
    """
    rules = {}

    with open(csv_file, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            head_verb = normalize_lemma(row[0])
            dependant = normalize_lemma(row[1])
            deprel = row[deprel_col].lower()

            if dependant not in rules:
                rules[dependant] = dict()
            if head_verb not in rules[dependant]:
                rules[dependant][head_verb] = list()
            rules[dependant][head_verb].append(deprel)

    return rules


def create_rule_dict(translative_abbr='tr', essive_abbr='es'):
    """
    Creates dictionary of rules where key is abbreviation of case that is of interest
    and value is dictionary in the form of {dependant: {head: deprel, head:deprel}}.
    :param translative_abbr: abbreviation of translative case (e.g 'Tra' in case of UD features,
    'tr' in EstNLTK morph_analysis)
    :param essive_abbr: abbreviation of essive (e.g 'Ess' in case of UD POS-tags,
    'es' in EstNLTK morph_analysis)
    """
    # Rules about translative and essive case
    tr_rules = {**master_list_to_rules(2, os.path.join(RESOURCES, 'xcomp_errors_filtered_adjtrans.csv')),
                **master_list_to_rules(2, os.path.join(RESOURCES, 'xcomp_errors_filtered_mitteadj.csv'))}
    ess_rules = master_list_to_rules(2, os.path.join(RESOURCES, 'xcomp_errors_filtered_adjess.csv'))

    # Dictionary of rules. Key corresponds to the case of interest
    rules = {
        translative_abbr: tr_rules,
        essive_abbr: ess_rules,
    }

    return rules
