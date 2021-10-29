import os
from collections import defaultdict

from estnltk import Annotation
from estnltk.taggers import Retagger


class SubcatRetagger(Retagger):
    """ Adds subcategorization information (hashtags) to verbs and adpositions.

        Subcategorization describes the necessary arguments that are required by the word.

        In verbs, this is related to both valency and transitivity.

        Transitivity is a property of verbs that defines whether they take a direct object:
         e.g 'vaatama' takes a direct object ("Ma vaatan filmi".)
             'suhtlema' does not take a direct object (but it takes other syntactic arguments - "Jüri suhtleb Mariga."
        SubcatRewriter adds a tag #Intr to intransitive verbs (verbs that cannot take a direct object)

        Valency is the number of syntactic arguments required by the predicate:
         e.g 'andma' requires three:
            "Jüri annab Marile raamatu." is a correct sentence, arguments Jüri, Mari and raamat are all necessary
            "Jüri annab.", "Jüri annab Marile.", "Jüri annab raamatu." are missing some arguments and feel incomplete
         e.g 'jooksma' requires one:
            "Jüri jookseb." is a correct sentence.
            "Jüri jookseb Tartus maratoni." is correct as well, but the location and distance are not
            necessary in the sentence and are therefore not arguments
        SubcatRewriter specifies the cases/types of verbs' syntactic arguments:
            #Part, #NGP-P, #Part-P direct object (can be nominative, genitive, partitive, a clause or construction)
            #Ill illative ("Eestlased emigreerusid **Kanadasse**.")
            #In inessive ("Vanaema kahtleb **müüja jutus**.")
            #El elative ("Tibu koorus **munast**.")
            #All allative ("Aasta läheneb **lõpule**.")
            #Ad adessive ("Järeldused põhinevad **eeldustel**.")
            #Abl ablative ("Õpilane küsib **õpetajalt** küsimuse.")
            #Tr translative ("Elevant külmub **kringliks**.")
            #Ter terminative ("Laps ei küündi **kraanikausini**.")
            #Es essive ("Jüri käitus **tõelise metslasena**.")
            #Kom comitative ("Võistleja leppis **tulemusega**.")
            #InfP infinite verb form ("Laps ei viitsi **õppda**.")

        For adpositions (laua **peal**, eilsest **saadik**, **mööda** põldu), subcategorization denotes
        the case of the noun phrase that it appears with: in the previous examples, postposition 'peal'
        needs a noun phrase in genitive form, 'saadik' needs a noun phrase in elative form and  preposition
        'mööda' needs a noun phrase in partitive case.
        The tags used for adpositions:
            #gen genitive (**laua** peal)
            #part partitive (mööda **põldu**)
            #nom nominative (**päev** otsa)
            #el (**eilsest** saadik)
            #all (tänu **emale**)
            #term (kuni **õhtuni**)
            #abes (ilma **hariduseta**)

        Argument subcat_rules must be a dict containing subcategorization information,
        loaded via method load_subcat_info();

        Performs word lemma lookups in subcat_rules, and in case of a match, checks
        word part-of-speech conditions. If the POS conditions match, adds subcategorization
        information either to a single analysis line, or to multiple analysis lines
        (depending on the exact conditions in the rule);

        Returns the input list where verb/adposition analyses have been augmented
        with available subcategorization information;

    """
    conf_param = ['check_output_consistency', 'v_rules', 'k_rules']

    def __init__(self, subcat_rules_file=None):
        if subcat_rules_file:
            assert os.path.exists(subcat_rules_file),\
                'Unable to find *subcat_rules_file* from location ' + subcat_rules_file
        else:
            subcat_rules_file = os.path.dirname(__file__)
            subcat_rules_file = os.path.join(subcat_rules_file,
                                             'rules_files/abileksikon06utf.lx')
            assert os.path.exists(subcat_rules_file),\
                'Missing default *subcat_rules_file* ' + subcat_rules_file
        self.v_rules, self.k_rules = self._load_subcat_info(subcat_rules_file)

        self.input_layers = ['morph_extended']
        self.output_layer = 'morph_extended'
        self.output_attributes = ['subcat']
        self.check_output_consistency = False

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]
        if self.output_attributes[0] not in layer.attributes:
            layer.attributes = layer.attributes + self.output_attributes
        for span in layer:
            annotations = list(span.annotations)
            span.clear_annotations()
            for annotation in annotations:
                rules = None
                if annotation['partofspeech'] == 'V':
                    # nii pole õige teha, aga see võimaldab jäljendada eelmist versiooni
                    # kasutamata abileksikon_extrat
                    root = annotation['root'].split('+')[0]  # 'Avatakse-suletakse'
                    rules = self.v_rules.get((root, annotation['partofspeech']), None)
                elif annotation['partofspeech'] == 'K':
                    root = annotation['root'].split('+')[0]
                    rules = self.k_rules.get((root, annotation['partofspeech'], annotation['form']), None)

                if rules is None:
                    annotation['subcat'] = None
                    span.add_annotation(annotation)
                else:
                    for subcat in rules:  # võib vaadelda eraldi juhtu len(rules) == 1
                        new_annotation = Annotation(span, **annotation)
                        new_annotation['subcat'] = tuple(subcat)
                        span.add_annotation(new_annotation)
        return layer

    def rewrite(self, record):
        result = []
        for rec in record:
            
            rules = None
            if rec['partofspeech'] == 'V':
                # nii pole õige teha, aga see võimaldab jäljendada eelmist versiooni
                # kasutamata abileksikon_extrat
                root = rec['root'].split('+')[0]  # 'Avatakse-suletakse'
                rules = self.v_rules.get((root, rec['partofspeech']), None)
            elif rec['partofspeech'] == 'K':
                root = rec['root'].split('+')[0]
                rules = self.k_rules.get((root, rec['partofspeech'], rec['form']), None)
            if rules is not None:
                for subcat in rules:  # võib vaadelda eraldi juhtu len(rules) == 1
                    rec_copy = rec.copy()
                    rec_copy['subcat'] = tuple(subcat)
                    result.append(rec_copy)
            else:
                rec['subcat'] = None
                result.append(rec)
        return result

    def _load_subcat_info(self, subcat_rules_file):
        """ Loads subcategorization rules (for verbs and adpositions) from a
            text file.
            It is expected that the rules are given as pairs, where the first
            item is the root (of verb/adposition), followed on the next line by
            the subcategorization rule, in the following form:
               on the left side of '>' is the condition (POS-tag requirement for
               the lemma),
             and
               on the right side is the listing of subcategorization settings
               (hashtag items, e.g. names of morphological cases of nominals);
            If there are multiple subcategorization rules to be associated with
            a single lemma, different rules are separated by '&'.

            Example. An excerpt from the rules file:

            läbi
            _V_ >#Part &_K_ post >#gen |#nom |#el &_K_ pre >#gen
            läbista
            _V_ >#NGP-P
            lähedal
            _K_ post >#gen
            lähenda
            _V_ >#NGP-P #All

            returns a pair of dicts (v_rules, k_rules):

            v_rules = {
                ('läbi', 'V'): [['Part']],
                ('läbista', 'V'): [['NGP-P']],
                ('lähenda', 'V'): [['NGP-P', 'All']]
            }
            k_rules = {
                ('läbi', 'K', 'post'): [['el'], ['nom'], ['gen']],
                ('läbi', 'K', 'pre'): [['gen']],
                ('lähedal', 'K', 'post'): [['gen']]
            }

            If the part of speech is not 'K' or 'V', then the rules are ignored.
            .
            _Y_ >_Z_ Fst &_Z_ >Fst
            ,
            _Y_ >_Z_ Com &_Z_ >Com

        """
        rules = defaultdict(list)

        with open(subcat_rules_file, 'r', encoding='utf_8') as in_f:
            while True:
                root = next(in_f, None)
                if root is None:
                    break
                root = root.rstrip()

                rule_line = next(in_f).rstrip()
                parts = rule_line.split('&')
                for part in parts:
                    rules[root].append(part)

        v_rules = defaultdict(list)
        k_rules = defaultdict(list)
        for root, rulelist in rules.items():
            for rule in rulelist:
                pos, subcats = rule.split('>')
                pos = pos.strip()
                for subcat in subcats.split('|'):
                    subcat = subcat.strip()
                    if pos == '_V_':
                        v_rules[(root, 'V')].append(subcat)
                    elif pos == '_K_ post':
                        k_rules[(root, 'K', 'post')].append(subcat)
                    elif pos == '_K_ pre':
                        k_rules[(root, 'K', 'pre')].append(subcat)
        # [::-1] eelmise versiooniga ühildumiseks
        for k, v in v_rules.items():
            v_rules[k] = v[::-1]  # no effect
        for k, v in k_rules.items():
            k_rules[k] = v[::-1]
        
        for key, v in v_rules.items():
            v_rules[key] = [[subcat.lstrip('#') for subcat in u.split()] for u in v]
        for key, v in k_rules.items():
            k_rules[key] = [[subcat.lstrip('#') for subcat in u.split()] for u in v]

        return v_rules, k_rules
