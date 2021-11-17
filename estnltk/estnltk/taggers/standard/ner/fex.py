from estnltk import Text, Layer
from estnltk.taggers import Tagger, Retagger
from collections import defaultdict
import codecs
from typing import MutableMapping
from itertools import product
import re


class BaseFeatureExtractor(object):
    """Base class for all feature extractors."""

    def __init__(self, *args, **kwargs):
        pass

    def prepare(self, docs):
        """ Called before feature extraction actually happens. Can be used to
        collect global statistics on the corpus. """
        pass

    def process(self, doc):
        for word in doc.words:
            self._process(word, doc)

    def _process(self, token, textobject):
        raise NotImplementedError("Not implemented!")


def get_lemma(morph_lemma):
    if len(morph_lemma) > 1:
        ridx = morph_lemma.rfind("=")
        if ridx == -1: ridx = morph_lemma.rfind("+")
        if ridx == -1: ridx = len(morph_lemma)
        if ridx > 0:
            morph_lemma = morph_lemma[:ridx]
        lemma = re.sub(r'(?<=[^\W_])_(?=[^\W_])', '', morph_lemma)
    else:
        lemma = morph_lemma
    return lemma.lower()


def get_pos(input):
    inputs = sorted(set(input))
    output = ""
    for inp in inputs:
        output += inp + "|"
    output = output[:-1]
    return "_" + output + "_"


def b(v):
    return 'y' if v else None


def is_prop(pos):
    return len(pos) == 1 and pos[0] == "H"


def get_word_parts(root_tokens):
    prefix = None
    postfix = None
    if len(root_tokens) > 1:
        prefix = root_tokens[0].lower()
        postfix = root_tokens[-1].lower()
    return prefix, postfix


def get_case(form):
    if len(form.split(" ")) > 1:
        return form.split(" ")[1]
    return None


def get_ending(ending):
    endings = sorted(set(ending))
    if len(endings) == 1:
        if endings in ([''], ['0']):
            return
    output = ""
    for end in endings:
        output += end + "|"
    output = output[:-1]
    return output


def get_shape(token):
    r = []
    for c in token:
        if c.isupper():
            r.append('U')
        elif c.islower():
            r.append('L')
        elif c.isdigit():
            r.append('D')
        elif c in ('.', ','):
            r.append('.')
        elif c in (';', ':', '?', '!'):
            r.append(';')
        elif c in ('+', '-', '*', '/', '=', '|', '_'):
            r.append('-')
        elif c in ('(', '{', '[', '<'):
            r.append('(')
        elif c in (')', '}', ']', '>'):
            r.append(')')
        else:
            r.append(c)
    return ''.join(r)


def degenerate(src):
    dst = u''
    for c in src:
        if not dst or dst[-1] != c:
            dst += c
    return dst


def get_2d(token):
    return len(token) == 2 and token.isdigit()


def get_4d(token):
    return len(token) == 4 and token.isdigit()


def get_dand(token, p):
    bd = False
    bdd = False
    for c in token:
        if c.isdigit():
            bd = True
        elif c == p:
            bdd = True
        else:
            return False
    return bd and bdd


def get_capperiod(token):
    return len(token) == 2 and token[0].isupper() and token[1] == '.'


def get_all_other(token):
    for c in token:
        if c.isalnum():
            return False
    return True


def contains_upper(token):
    b = False
    for c in token:
        b |= c.isupper()
    return b


def contains_lower(token):
    b = False
    for c in token:
        b |= c.islower()
    return b


def contains_alpha(token):
    b = False
    for c in token:
        b |= c.isalpha()
    return b


def contains_digit(token):
    b = False
    for c in token:
        b |= c.isdigit()
    return b


def contains_symbol(token):
    for c in token:
        if not c.isalnum():
            return True
    return False


def split_char(token, char):
    return token.split(char, 1) if token.find(char) > -1 else [None, None]


def contains_feature(feature, token):
    return feature in token.annotations[0] and getattr(token.annotations[0],feature) is not None


class NerMorphFeatureTagger(Tagger):
    """"Extracts features provided by the morphological analyser pyvabamorf. """
    conf_param = ['settings']

    def __init__(self, settings, input_layers = ('words','morph_analysis'), output_layer='ner_features',
                 output_attributes=("lem", "pos", "prop", "pref", "post", "case",
                                    "ending", "pun", "w", "w1", "shape", "shaped", "p1",
                                    "p2", "p3", "p4", "s1", "s2", "s3", "s4", "d2",
                                    "d4", "dndash", "dnslash", "dncomma", "dndot", "up", "iu", "au",
                                    "al", "ad", "ao", "aan", "cu", "cl", "ca", "cd",
                                    "cp", "cds", "cdt", "cs", "bdash", "adash",
                                    "bdot", "adot", "len", "fsnt", "lsnt", "gaz",
                                    "prew", "next", "iuoc", "pprop", "nprop", "pgaz",
                                    "ngaz", "F")):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(self.output_layer, ambiguous=True, attributes=self.output_attributes, text_object=None)

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = self._make_layer_template()
        layer.text_object = text
        morph_layer = self.input_layers[0]
        words = text[self.input_layers[1]]
        for token in words:
            morph = getattr(token, morph_layer)
            LEM = '_'.join(morph.root_tokens[0]) + ('+' + morph.ending[0] if morph.ending[0] else '')
            if not LEM:
                LEM = token.text
            layer.add_annotation(token, lem=get_lemma(LEM), pos=get_pos(morph.partofspeech),
                                 prop=b(is_prop(morph.partofspeech)),
                                 pref=get_word_parts(morph.root_tokens[0])[0],
                                 post=get_word_parts(morph.root_tokens[0])[1],
                                 case=get_case(morph.form[0]), ending=get_ending(morph.ending),
                                 pun=b(get_pos(morph.partofspeech)=="_Z_"), w=None, w1=None, shape=None, shaped=None, p1=None,
                                 p2=None, p3=None, p4=None, s1=None, s2=None, s3=None, s4=None, d2=None, d4=None,
                                 dndash=None,
                                 dnslash=None, dncomma=None, dndot=None, up=None, iu=None, au=None,
                                 al=None, ad=None, ao=None, aan=None, cu=None, cl=None, ca=None,
                                 cd=None, cp=None, cds=None, cdt=None, cs=None, bdash=None, adash=None,
                                 bdot=None, adot=None, len=None, fsnt=None, lsnt=None, gaz=None, prew=None,
                                 next=None, iuoc=None, pprop=None, nprop=None, pgaz=None, ngaz=None, F=None)

        return layer


class NerLocalFeatureTagger(Retagger):
    """Generates features for a token based on its character makeup."""
    conf_param = ['settings']

    def __init__(self, settings, output_layer='ner_features', output_attributes=(), input_layers=['ner_features']):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        layer.attributes += tuple(self.output_attributes)
        morph_layer = self.input_layers[1]
        for token in text.ner_features:
            morph = getattr(token, morph_layer)
            LEM = '_'.join(morph.root_tokens[0]) + ('+' + morph.ending[0] if morph.ending[0] else '')
            if not LEM:
                LEM = token.text
            LEM = get_lemma(LEM)


            # Token.
            token.ner_features.w = token.text
            # Lowercased token.
            token.ner_features.w1 = token.text.lower()
            # Token shape.
            token.ner_features.shape = get_shape(token.text)
            # Token shape degenerated.
            token.ner_features.shaped = degenerate(get_shape(token.text))

            # Prefixes (length between one to four).
            token.ner_features.p1 = LEM[0] if len(LEM) >= 1 else None
            token.ner_features.p2 = LEM[:2] if len(LEM) >= 2 else None
            token.ner_features.p3 = LEM[:3] if len(LEM) >= 3 else None
            token.ner_features.p4 = LEM[:4] if len(LEM) >= 4 else None

            # Suffixes (length between one to four).
            token.ner_features.s1 = LEM[-1] if len(LEM) >= 1 else None
            token.ner_features.s2 = LEM[-2:] if len(LEM) >= 2 else None
            token.ner_features.s3 = LEM[-3:] if len(LEM) >= 3 else None
            token.ner_features.s4 = LEM[-4:] if len(LEM) >= 4 else None

            # Two digits
            token.ner_features.d2 = b(get_2d(token.text))
            # Four digits
            token.ner_features.d4 = b(get_4d(token.text))
            # Digits and '-'.
            token.ner_features.dndash = b(get_dand(token.text, '-'))
            # Digits and '/'.
            token.ner_features.dnslash = b(get_dand(token.text, '/'))
            # Digits and ','.
            token.ner_features.dncomma = b(get_dand(token.text, ','))
            # Digits and '.'.
            token.ner_features.dndot = b(get_dand(token.text, '.'))
            # A uppercase letter followed by '.'
            token.ner_features.up = b(get_capperiod(token.text))

            # An initial uppercase letter.
            token.ner_features.iu = b(token.text and token.text[0].isupper())
            # All uppercase letters.
            token.ner_features.au = b(token.text.isupper())
            # All lowercase letters.
            token.ner_features.al = b(token.text.islower())
            # All digit letters.
            token.ner_features.ad = b(token.text.isdigit())
            # All other (non-alphanumeric) letters.
            token.ner_features.ao = b(get_all_other(token.text))
            # Alphanumeric token.
            token.ner_features.aan = b(token.text.isalnum())

            # Contains an uppercase letter.
            token.ner_features.cu = b(contains_upper(token.text))
            # Contains a lowercase letter.
            token.ner_features.cl = b(contains_lower(token.text))
            # Contains a alphabet letter.
            token.ner_features.ca = b(contains_alpha(token.text))
            # Contains a digit.
            token.ner_features.cd = b(contains_digit(token.text))
            # Contains an apostrophe.
            token.ner_features.cp = b(token.text.find("'") > -1)
            # Contains a dash.
            token.ner_features.cds = b(token.text.find("-") > -1)
            # Contains a dot.
            token.ner_features.cdt = b(token.text.find(".") > -1)
            # Contains a symbol.
            token.ner_features.cs = b(contains_symbol(token.text))

            # Before, after dash
            token.ner_features.bdash = split_char(LEM, '-')[0]
            token.ner_features.adash = split_char(LEM, '-')[1]

            # Before, after dot
            token.ner_features.bdot = split_char(LEM, '.')[0]
            token.ner_features.adot = split_char(LEM, '.')[1]

            # Length
            token.ner_features.len = str(len(LEM))



class NerSentenceFeatureTagger(Retagger):
    """Generates features for the first and last tokens in a sentence."""
    conf_param = ['settings']

    def __init__(self, settings, output_layer='ner_features', output_attributes=(), input_layers=['ner_features']):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        layer.attributes += tuple(self.output_attributes)
        sentences = self.input_layers[3]
        for snt in getattr(text, sentences):
            snt[0].ner_features.fsnt = 'y'
            snt[-1].ner_features.lsnt = 'y' #never used



class NerGazetteerFeatureTagger(Retagger):
    """Generates features indicating whether the token is present in a precompiled
    list of organisations, geographical locations or person names. For instance,
    if a token t occurs both in the list of person names (PER) and organisations (ORG),
    assign t['gaz'] = ['PER', 'ORG']. With the parameter look_ahead, it is possible to
    compose multi-token phrases for dictionary lookup. When look_ahead=N, phrases
    (t[i], ..., t[i+N]) will be composed. If the phrase matches the dictionary, each
    token will be assigned the corresponding value.
    """
    conf_param = ['settings', 'look_ahead', 'data']

    def __init__(self, settings, look_ahead=3, output_layer='ner_features', output_attributes=(),
                 input_layers=['ner_features']):
        self.settings = settings
        self.look_ahead = look_ahead
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

        self.data = defaultdict(set)
        with codecs.open(settings.GAZETTEER_FILE, 'rb', encoding="utf8") as f:
            for ln in f:
                word, lbl = ln.strip().rsplit("\t", 1)
                self.data[word].add(lbl)

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        layer.attributes += tuple(self.output_attributes)
        tokens = list(layer)
        look_ahead = self.look_ahead
        morph_layer = self.input_layers[1]
        for i in range(len(tokens)):
            if tokens[i].ner_features.iu[0] is not None:  # Only capitalised strings
                for j in range(i + 1, i + 1 + look_ahead):
                    lemmas = []
                    for token in tokens[i:j]:
                        morph = getattr(token, morph_layer)
                        LEM = '_'.join(morph.root_tokens[0]) + (
                            '+' + morph.ending[0] if morph.ending[0] else '').lower()
                        if not LEM:
                            LEM = token.text
                        LEM = get_lemma(LEM)
                        lemmas.append(LEM)
                    phrase = " ".join(lemmas)
                    if phrase in self.data:
                        labels = self.data[phrase]
                        for tok in tokens[i:j]:
                            tok.ner_features.gaz = labels


class NerGlobalContextFeatureTagger(Retagger):
    """Tagger version of GlobalContextFeatureExtractor"""
    conf_param = ['settings']

    def __init__(self, settings, output_layer='ner_features', output_attributes=(), input_layers=['ner_features']):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):

        layer = layers[self.output_layer]
        layer.attributes += tuple(self.output_attributes)

        sentences = self.input_layers[3]
        morph_layer = self.input_layers[1]
        for snt in getattr(text, sentences):
            for i in range(1, len(snt)):
                snt[i].ner_features.prew = snt[i - 1].ner_features
            for i in range(len(snt) - 1):
                snt[i].ner_features.next = snt[i + 1].ner_features

        ui_lems = set()
        for i, token in enumerate(text.ner_features):
            morph = getattr(token, morph_layer)
            LEM = '_'.join(morph.root_tokens[0]) + ('+' + morph.ending[0] if morph.ending[0] else '')
            if not LEM:
                LEM = token.text
            if contains_feature('iu', token) and not contains_feature('fsnt', token):
                if layer[i - 1].text not in {u'\u201d', u'\u201e', u'\u201c'}:
                    ui_lems.add(get_lemma(LEM))
        sametoks_dict = defaultdict(list)
        sametoks_index_dict = defaultdict(list)
        for i, token in enumerate(layer):
            morph = getattr(token, morph_layer)
            LEM = '_'.join(morph.root_tokens[0]) + ('+' + morph.ending[0] if morph.ending[0] else '')
            if not LEM:
                LEM = token.text
            LEM = get_lemma(LEM)
            if LEM in ui_lems:
                sametoks_dict[LEM].append(token)
                sametoks_index_dict[LEM].append((token, i))

        for sametoks in sametoks_dict.values():
            for tok in sametoks:
                tok.ner_features.iuoc = 'y'

            if any(contains_feature('prew',t) and contains_feature('prop',t.prew[0]) for t in sametoks):
                for t in sametoks:
                    t.ner_features.pprop = 'y'


            if any(contains_feature('next',t) and contains_feature('prop',t.next[0]) for t in sametoks):
                for t in sametoks:
                    t.ner_features.nprop = 'y'
            pgaz_set = set()
            for t in sametoks:
                if contains_feature('prew',t) and contains_feature('gaz',t.prew[0]):
                    for gaz_set in t.prew[0].gaz:
                        for gaz in gaz_set:
                            pgaz_set.add(gaz)
            if pgaz_set:
                for t in sametoks:
                    t.ner_features.pgaz = pgaz_set

            ngaz_set = set()
            for t in sametoks:
                if contains_feature('next', t) and contains_feature('gaz', t.next[0]):
                    for gaz_set in t.next[0].gaz:
                        for gaz in gaz_set:
                            ngaz_set.add(gaz)
            if ngaz_set:
                for t in sametoks:
                    t.ner_features.ngaz = ngaz_set



def apply_templates(toks, templates, text_layers=["morph_analysis", "words", "sentences"]):
    """
    Generate features for an item sequence by applying feature templates.
    A feature template consists of a tuple of (name, offset) pairs,
    where name and offset specify a field name and offset from which
    the template extracts a feature value. Generated features are stored
    in the 'F' field of each item in the sequence.

    Parameters
    ----------
    toks: list of tokens
        A list of processed toknes.

    templates: list of template tuples (str, int)
        A feature template consists of a tuple of (name, offset) pairs,
        where name and offset specify a field name and offset from which
        the template extracts a feature value.
    """
    token_lists = []
    for template in templates:
        name = '|'.join(['%s[%d]' % (f, o) for f, o in template])
        index = 0
        sentences_layer = text_layers[2]
        for snt in getattr(toks, sentences_layer):
            for t in range(len(snt)):
                values_list = []
                for field, offset in template:
                    p = t + offset
                    if p < 0 or p >= len(snt):
                        values_list = []
                        break
                    if field in snt[p].ner_features.annotations[0]:
                        value = getattr(snt[p].ner_features,field)
                        values_list.append(value if isinstance(value, (set, list)) else [value])
                if len(template) == len(values_list):
                    for values in product(*values_list):
                        if len(token_lists)==t+index:
                            token_lists.append([])
                        if None not in values[0] and len(values)==1 or None not in values[0] and None not in values[1]:
                            joinable=[]
                            if isinstance(values[0][0],set):
                                for value in values[0]:
                                    for instance in value:
                                        joinable.append(instance)
                                if len(values) > 1:
                                    for value in values[1]:
                                        for instance in value:
                                            joinable.append(instance)
                            else:
                                joinable = values[0]
                                if len(values)==2:
                                    joinable = list(joinable)
                                    joinable.append(values[1][0])
                            if name == 'ending[0]':
                                name = 'end[0]'
                            token_lists[t+index].append('%s=%s' % (name, '|'.join(joinable)))
            index+= len(snt)

    for t in range(len(toks.ner_features)):
        toks.ner_features[t].F = token_lists[t]


class FeatureExtractor(object):
    """Feature extractor is used for decorating tokens of the documents
    with features specified in configuration files.
    """

    def __init__(self, settings, morph_layer_inputs):
        """Initialize the feature extractor.

        Parameters
        ----------
        settings: estnltk.ner.settings.Settings
            The settings and configuration of the NER system.
        """
        self.settings = settings
        self.fex_list = []

        first_fex = settings.FEATURE_EXTRACTORS[0]
        fex_class = FeatureExtractor._get_class(first_fex)
        fex_obj = fex_class(settings, morph_layer_inputs)
        self.fex_list.append(fex_obj)
        for fex_name in settings.FEATURE_EXTRACTORS[1:]:
            fex_class = FeatureExtractor._get_class(fex_name)
            input_layers = ["ner_features"]
            input_layers.extend(morph_layer_inputs)
            fex_obj = fex_class(settings, input_layers=input_layers)
            self.fex_list.append(fex_obj)

        self.morph_layer_inputs = morph_layer_inputs

    def prepare(self, docs):
        # init extractors
        for fex in [self.fex_list[0]]:
            fex.prepare(docs)

    def process(self, docs):
        # extract features
        for fex in self.fex_list:
            for doc in docs:
                try:
                    fex.process(doc)
                except:
                    try:
                        fex.tag(doc)
                    except:
                        fex.retag(doc)
        # apply the feature templates.
        for doc in docs:
            apply_templates(doc, self.settings.TEMPLATES, self.morph_layer_inputs)

    @staticmethod
    def _get_class(kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)

        return m
