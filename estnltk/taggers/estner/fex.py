from estnltk import Layer
from collections import defaultdict
import codecs
from functools import reduce
from estnltk.taggers import Tagger, Retagger
from typing import MutableMapping
from estnltk.text import Text
from itertools import product

class BaseFeatureExtractor(object):
    """Base class for all feature extractors."""

    def __init__(self, *args, **kwargs):
        pass

    def prepare(self, docs):
        ''' Called before feature extraction actually happens. Can be used to
        collect global statistics on the corpus. '''
        for doc in docs:
            doc.add_layer(Layer('ner_features', ambiguous=True, attributes=['value', 'name'], text_object=doc))

    def process(self, doc):
        doc.tag_layer()
        for word in doc.words:
            self._process(word, doc)

    def _process(self, token, textobject):
        raise NotImplementedError("Not implemented!")


def get_pos(input):
    return "_" + input[0] + "_"


def b(v):
    return 'y' if v else None


def is_prop(pos):
    return pos[0] == "H"


def get_word_parts(root_tokens):
    prefix = None
    postfix = None
    if len(root_tokens) > 1:
        prefix = root_tokens[0]
        postfix = root_tokens[1]
    return prefix, postfix


def get_case(form):
    if len(form) > 1:
        return form[1]
    return None


def get_ending(ending):
    if ending == '0':
        return None
    return ending


def get_shape(token):
    r = u''
    for c in token:
        if c.isupper():
            r += 'U'
        elif c.islower():
            r += 'L'
        elif c.isdigit():
            r += 'D'
        elif c in ('.', ','):
            r += '.'
        elif c in (';', ':', '?', '!'):
            r += ';'
        elif c in ('+', '-', '*', '/', '=', '|', '_'):
            r += '-'
        elif c in ('(', '{', '[', '<'):
            r += '('
        elif c in (')', '}', ']', '>'):
            r += ')'
        else:
            r += c
    return r


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
    return feature in token.name


class MorphFeatureExtractor(BaseFeatureExtractor):
    """Extracts features provided by the morphological analyser pyvabamorf. """

    def _process(self, token, textobject):
        add_annotation = textobject.ner_features.add_annotation
        add_annotation(token, value=token.lemma[0], name="lem")
        add_annotation(token, value=get_pos(token.partofspeech), name="pos")
        add_annotation(token, value=b(is_prop(token.partofspeech)), name="prop")
        add_annotation(token, value=get_word_parts(token.root_tokens[0])[0], name="pref")
        add_annotation(token, value=get_word_parts(token.root_tokens[0])[1], name="post")
        add_annotation(token, value=get_case(token.form[0]), name="case")
        add_annotation(token, value=get_ending(token.ending[0]), name="end")
        add_annotation(token, value=b(get_pos(token.partofspeech) == '_Z_'), name="pun")


class NerMorphFeatureTagger(Tagger):
    """MorphFeatureExtractor as tagger"""
    conf_param = ['settings']
    input_layers = []

    def __init__(self,settings,output_layer = 'ner_features', output_attributes = ("value", "name")):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = Layer(self.output_layer, ambiguous=True, attributes=self.output_attributes, text_object=text)
        text.tag_layer()
        for token in text.words:
            add_annotation = layer.add_annotation
            add_annotation(token, value=token.lemma[0], name="lem")
            add_annotation(token, value=get_pos(token.partofspeech), name="pos")
            add_annotation(token, value=b(is_prop(token.partofspeech)), name="prop")
            add_annotation(token, value=get_word_parts(token.root_tokens[0])[0], name="pref")
            add_annotation(token, value=get_word_parts(token.root_tokens[0])[1], name="post")
            add_annotation(token, value=get_case(token.form[0]), name="case")
            add_annotation(token, value=get_ending(token.ending[0]), name="end")
            add_annotation(token, value=b(get_pos(token.partofspeech) == '_Z_'), name="pun")
        return layer



class LocalFeatureExtractor(BaseFeatureExtractor):
    """Generates features for a token based on its character makeup."""

    def _process(self, token, textobject):
        LEM = token.lemma[0]

        add_annotation = textobject.ner_features.add_annotation

        # Token.
        add_annotation(token, value=token.text, name="w")  # token
        # Lowercased token.
        add_annotation(token, value=token.text.lower(), name="wl")  # lowercased token
        # Token shape.
        add_annotation(token, value=get_shape(token.text), name="shape")
        # Token shape degenerated.
        add_annotation(token, value=degenerate(get_shape(token.text)), name="shaped")

        # Prefixes (length between one to four).
        add_annotation(token, value=LEM[0] if len(LEM) >= 1 else None,
                       name="p1")
        add_annotation(token, value=LEM[:2] if len(LEM) >= 2 else None,
                       name="p2")
        add_annotation(token, value=LEM[:3] if len(LEM) >= 3 else None,
                       name="p3")
        add_annotation(token, value=LEM[:4] if len(LEM) >= 4 else None,
                       name="p4")

        # Suffixes (length between one to four).
        add_annotation(token, value=LEM[-1] if len(LEM) >= 1 else None,
                       name="s1")
        add_annotation(token, value=LEM[-2:] if len(LEM) >= 2 else None,
                       name="s2")
        add_annotation(token, value=LEM[-3:] if len(LEM) >= 3 else None,
                       name="s3")
        add_annotation(token, value=LEM[-4:] if len(LEM) >= 4 else None,
                       name="s4")

        # Two digits
        add_annotation(token, value=b(get_2d(token.text)), name="2d")
        # Four digits
        add_annotation(token, value=b(get_4d(token.text)), name="4d")
        # Digits and '-'.
        add_annotation(token, value=b(get_dand(token.text, '-')), name="d&-")
        # Digits and '/'.
        add_annotation(token, value=b(get_dand(token.text, '/')), name="d&/")
        # Digits and ','.
        add_annotation(token, value=b(get_dand(token.text, ',')), name="d&,")
        # Digits and '.'.
        add_annotation(token, value=b(get_dand(token.text, '.')), name="d&.")
        # A uppercase letter followed by '.'
        add_annotation(token, value=b(get_capperiod(token.text)), name="up")

        # An initial uppercase letter.
        add_annotation(token, value=b(token.text and token.text[0].isupper()), name="iu")
        # All uppercase letters.
        add_annotation(token, value=b(token.text.isupper()), name="au")
        # All lowercase letters.
        add_annotation(token, value=b(token.text.islower()), name="al")
        # All digit letters.
        add_annotation(token, value=b(token.text.isdigit()), name="ad")
        # All other (non-alphanumeric) letters.
        add_annotation(token, value=b(get_all_other(token.text)), name="ao")
        # Alphanumeric token.
        add_annotation(token, value=b(token.text.isalnum()), name="aan")

        # Contains an uppercase letter.
        add_annotation(token, value=b(contains_upper(token.text)), name="cu")
        # Contains a lowercase letter.
        add_annotation(token, value=b(contains_lower(token.text)), name="cl")
        # Contains a alphabet letter.
        add_annotation(token, value=b(contains_alpha(token.text)), name="ca")
        # Contains a digit.
        add_annotation(token, value=b(contains_digit(token.text)), name="cd")
        # Contains an apostrophe.
        add_annotation(token, value=b(token.text.find("'") > -1), name="cp")
        # Contains a dash.
        add_annotation(token, value=b(token.text.find("-") > -1), name="cds")
        # Contains a dot.
        add_annotation(token, value=b(token.text.find(".") > -1), name="cdt")
        # Contains a symbol.
        add_annotation(token, value=b(contains_symbol(token.text)), name="cs")

        # Before, after dash
        add_annotation(token, value=split_char(LEM, '-')[0], name="bdash")
        add_annotation(token, value=split_char(LEM, '-')[1], name="adash")

        # Before, after dot
        add_annotation(token, value=split_char(LEM, '.')[0], name="bdot")
        add_annotation(token, value=split_char(LEM, '.')[1], name="adot")

        # Length
        add_annotation(token, value=str(len(LEM)), name="len")

class NerLocalFeatureTagger(Retagger):
    """Tagger version of LocalFeatureExtractor"""
    conf_param = ['settings']


    def __init__(self, settings, output_layer='ner_features', output_attributes=(), input_layers = ['ner_features']):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        layer.attributes += tuple(self.output_attributes)
        for token in text.words:
            LEM = token.lemma[0]

            add_annotation = layer.add_annotation

            # Token.
            add_annotation(token, value=token.text, name="w")  # token
            # Lowercased token.
            add_annotation(token, value=token.text.lower(), name="wl")  # lowercased token
            # Token shape.
            add_annotation(token, value=get_shape(token.text), name="shape")
            # Token shape degenerated.
            add_annotation(token, value=degenerate(get_shape(token.text)), name="shaped")

            # Prefixes (length between one to four).
            add_annotation(token, value=LEM[0] if len(LEM) >= 1 else None,
                           name="p1")
            add_annotation(token, value=LEM[:2] if len(LEM) >= 2 else None,
                           name="p2")
            add_annotation(token, value=LEM[:3] if len(LEM) >= 3 else None,
                           name="p3")
            add_annotation(token, value=LEM[:4] if len(LEM) >= 4 else None,
                           name="p4")

            # Suffixes (length between one to four).
            add_annotation(token, value=LEM[-1] if len(LEM) >= 1 else None,
                           name="s1")
            add_annotation(token, value=LEM[-2:] if len(LEM) >= 2 else None,
                           name="s2")
            add_annotation(token, value=LEM[-3:] if len(LEM) >= 3 else None,
                           name="s3")
            add_annotation(token, value=LEM[-4:] if len(LEM) >= 4 else None,
                           name="s4")

            # Two digits
            add_annotation(token, value=b(get_2d(token.text)), name="2d")
            # Four digits
            add_annotation(token, value=b(get_4d(token.text)), name="4d")
            # Digits and '-'.
            add_annotation(token, value=b(get_dand(token.text, '-')), name="d&-")
            # Digits and '/'.
            add_annotation(token, value=b(get_dand(token.text, '/')), name="d&/")
            # Digits and ','.
            add_annotation(token, value=b(get_dand(token.text, ',')), name="d&,")
            # Digits and '.'.
            add_annotation(token, value=b(get_dand(token.text, '.')), name="d&.")
            # A uppercase letter followed by '.'
            add_annotation(token, value=b(get_capperiod(token.text)), name="up")

            # An initial uppercase letter.
            add_annotation(token, value=b(token.text and token.text[0].isupper()), name="iu")
            # All uppercase letters.
            add_annotation(token, value=b(token.text.isupper()), name="au")
            # All lowercase letters.
            add_annotation(token, value=b(token.text.islower()), name="al")
            # All digit letters.
            add_annotation(token, value=b(token.text.isdigit()), name="ad")
            # All other (non-alphanumeric) letters.
            add_annotation(token, value=b(get_all_other(token.text)), name="ao")
            # Alphanumeric token.
            add_annotation(token, value=b(token.text.isalnum()), name="aan")

            # Contains an uppercase letter.
            add_annotation(token, value=b(contains_upper(token.text)), name="cu")
            # Contains a lowercase letter.
            add_annotation(token, value=b(contains_lower(token.text)), name="cl")
            # Contains a alphabet letter.
            add_annotation(token, value=b(contains_alpha(token.text)), name="ca")
            # Contains a digit.
            add_annotation(token, value=b(contains_digit(token.text)), name="cd")
            # Contains an apostrophe.
            add_annotation(token, value=b(token.text.find("'") > -1), name="cp")
            # Contains a dash.
            add_annotation(token, value=b(token.text.find("-") > -1), name="cds")
            # Contains a dot.
            add_annotation(token, value=b(token.text.find(".") > -1), name="cdt")
            # Contains a symbol.
            add_annotation(token, value=b(contains_symbol(token.text)), name="cs")

            # Before, after dash
            add_annotation(token, value=split_char(LEM, '-')[0], name="bdash")
            add_annotation(token, value=split_char(LEM, '-')[1], name="adash")

            # Before, after dot
            add_annotation(token, value=split_char(LEM, '.')[0], name="bdot")
            add_annotation(token, value=split_char(LEM, '.')[1], name="adot")

            # Length
            add_annotation(token, value=str(len(LEM)), name="len")



class SentenceFeatureExtractor(BaseFeatureExtractor):
    """Generates features for the first and last tokens in a sentence."""

    def process(self, doc):
        for snt in doc.sentences:
            doc.ner_features.add_annotation(snt[0], value='y', name="fsnt")
            doc.ner_features.add_annotation(snt[-1], value='y', name="lsnt")

class NerSentenceFeatureTagger(Retagger):
    """Tagger version of SentenceFeatureExtractor"""
    conf_param = ['settings']

    def __init__(self, settings, output_layer='ner_features', output_attributes=(), input_layers=['ner_features']):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        layer.attributes += tuple(self.output_attributes)
        for snt in text.sentences:
            layer.add_annotation(snt[0], value='y', name="fsnt")
            layer.add_annotation(snt[-1], value='y', name="lsnt")


class GazetteerFeatureExtractor(BaseFeatureExtractor):
    """Generates features indicating whether the token is present in a precompiled
    list of organisations, geographical locations or person names. For instance,
    if a token t occurs both in the list of person names (PER) and organisations (ORG),
    assign t['gaz'] = ['PER', 'ORG']. With the parameter look_ahead, it is possible to
    compose multi-token phrases for dictionary lookup. When look_ahead=N, phrases
    (t[i], ..., t[i+N]) will be composed. If the phrase matches the dictionary, each
    token will be assigned the corresponding value.
    """

    def __init__(self, settings, look_ahead=3):
        """Loads a gazetteer file. Can take some time!

        Parameters
        -----------

        settings: dict
            Global configuration dictionary.
        look_ahead: int
            A number of tokens to check to compose phrases.

        """
        self.look_ahead = look_ahead
        self.data = defaultdict(set)
        with codecs.open(settings.GAZETTEER_FILE, 'rb', encoding="utf8") as f:
            for ln in f:
                word, lbl = ln.strip().rsplit("\t", 1)
                self.data[word].add(lbl)

    def process(self, doc):
        tokens = list(doc.ner_features)
        look_ahead = self.look_ahead
        for i in range(len(tokens)):
            if tokens[i].value[list(tokens[i].name).index('iu')] is not None:  # Only capitalised strings
                for j in range(i + 1, i + 1 + look_ahead):
                    phrase = " ".join(token.lemma[0] for token in tokens[i:j]).lower()
                    if phrase in self.data:
                        labels = self.data[phrase]
                        for tok in tokens[i:j]:
                            doc.ner_features.add_annotation(tok, value=labels, name="gaz")

class NerGazetteerFeatureTagger(Retagger):
    """Tagger version of GazetteerFeatureExtractor"""
    conf_param = ['settings', 'look_ahead','data']

    def __init__(self, settings, look_ahead=3, output_layer='ner_features', output_attributes=(), input_layers=['ner_features']):
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
        for i in range(len(tokens)):
            if tokens[i].value[list(tokens[i].name).index('iu')] is not None:  # Only capitalised strings
                for j in range(i + 1, i + 1 + look_ahead):
                    phrase = " ".join(token.lemma[0] for token in tokens[i:j]).lower()
                    if phrase in self.data:
                        labels = self.data[phrase]
                        for tok in tokens[i:j]:
                            layer.add_annotation(tok, value=labels, name="gaz")

class GlobalContextFeatureExtractor(BaseFeatureExtractor):
    def process(self, doc):

        for i in range(1, len(doc.ner_features)):
            doc.ner_features.add_annotation(doc.ner_features[i], value=doc.ner_features[i - 1], name="prew")
        for i in range(len(doc.ner_features) - 1):
            doc.ner_features.add_annotation(doc.ner_features[i], value=doc.ner_features[i + 1], name="next")

        ui_lems = set()
        for i, token in enumerate(doc.ner_features):
            if contains_feature('iu', token) and not contains_feature('fsnt', token):
                if doc.ner_features[i - 1].text not in {u'\u201d', u'\u201e', u'\u201c'}:
                    ui_lems.add(token.lemma[0])

        sametoks_dict = defaultdict(list)
        for token in doc.ner_features:
            if token.lemma[0] in ui_lems:
                sametoks_dict[token.lemma[0]].append(token)

        for sametoks in sametoks_dict.values():
            for tok in sametoks:
                doc.ner_features.add_annotation(tok, value='y', name="iuoc")

            if any('prew' in t.name and 'prop' in t.value[list(t.name).index('prew')].name for t in sametoks):
                for t in sametoks:
                    doc.ner_features.add_annotation(t, value='y', name="pprop")

            if any('next' in t.name and 'prop' in t.value[list(t.name).index('next')].name for t in sametoks):
                for t in sametoks:
                    doc.ner_features.add_annotation(t, value='y', name="nprop")
            # t.value[list(t.name).index('next')].value[list(t.value[list(t.name).index('next')].name).index("gaz")]
            pgaz_set = reduce(set.union, [
                t.value[list(t.name).index('prew')].value[list(t.value[list(t.name).index('prew')].name).index("gaz")]
                for t in sametoks if 'prew' in t.name and 'gaz' in t.value[list(t.name).index('prew')].name], set([]))
            if pgaz_set:
                for t in sametoks:
                    doc.ner_features.add_annotation(t, value=pgaz_set, name="pgaz")

            ngaz_set = reduce(set.union, [
                t.value[list(t.name).index('next')].value[list(t.value[list(t.name).index('next')].name).index("gaz")]
                for t in sametoks if 'next' in t.name and 'gaz' in t.value[list(t.name).index('next')].name], set([]))
            if ngaz_set:
                for t in sametoks:
                    doc.ner_features.add_annotation(t, value=ngaz_set, name="ngaz")

    def __process(self, doc):
        sametoks_dict = defaultdict(list)
        for t in doc.ner_features:
            if "prop" in t.name:
                sametoks_dict[t.lemma[0]].append(t)

        def check_feature(sametoks, fname, fvalue, test_fun):
            for tok in sametoks:
                if test_fun(tok):
                    for t in sametoks:
                        doc.ner_features.add_annotation(t, value=fvalue, name=fname)
                    break

        for t in doc.tokens:
            if t.lemma[0] in sametoks_dict:
                sametoks = sametoks_dict[t.lemma[0]]
                # Capitalized in other occurrences
                check_feature(sametoks, 'iuoc', "y", lambda tok: tok and "iu" in tok)
                # Prew proper in other occurrences
                check_feature(sametoks, 'pprop', "y", lambda tok: tok.prew and 'prop' in t.value[list(t.name).index('prew')].name)
                # Next proper in other occurrences
                check_feature(sametoks, 'nprop', "y", lambda tok: tok.next and 'prop' in t.value[list(t.name).index('next')].name)
                # Prew in gazeteer in other occurrences
                check_feature(sametoks, 'pgaz', "y", lambda tok: tok.prew and 'gaz' in t.value[list(t.name).index('prew')].name)
                # Next in gazeteer in other occurrences
                # Prew lemma in other occurrences
                check_feature(sametoks, 'plem', "y", lambda tok: tok.prew and 'prop' in t.value[list(t.name).index('prew')].name)
                # Next lemma in other occurrences

                del sametoks_dict[t.lemma[0]]

class NerGlobalContextFeatureTagger(Retagger):
    """Tagger version of SentenceFeatureExtractor"""
    conf_param = ['settings']

    def __init__(self, settings, output_layer='ner_features', output_attributes=(), input_layers=['ner_features']):
        self.settings = settings
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_layers = input_layers

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = layers[self.output_layer]
        layer.attributes += tuple(self.output_attributes)

        add_annotation = layer.add_annotation

        for i in range(1, len(layer)):
            add_annotation(layer[i], value=layer[i - 1], name="prew")
        for i in range(len(layer) - 1):
            add_annotation(layer[i], value=layer[i + 1], name="next")

        ui_lems = set()
        for i, token in enumerate(layer):
            if contains_feature('iu', token) and not contains_feature('fsnt', token):
                if layer[i - 1].text not in {u'\u201d', u'\u201e', u'\u201c'}:
                    ui_lems.add(token.lemma[0])

        sametoks_dict = defaultdict(list)
        for token in layer:
            if token.lemma[0] in ui_lems:
                sametoks_dict[token.lemma[0]].append(token)

        for sametoks in sametoks_dict.values():
            for tok in sametoks:
                add_annotation(tok, value='y', name="iuoc")

            if any('prew' in t.name and 'prop' in t.value[list(t.name).index('prew')].name for t in sametoks):
                for t in sametoks:
                    add_annotation(t, value='y', name="pprop")

            if any('next' in t.name and 'prop' in t.value[list(t.name).index('next')].name for t in sametoks):
                for t in sametoks:
                    add_annotation(t, value='y', name="nprop")
            # t.value[list(t.name).index('next')].value[list(t.value[list(t.name).index('next')].name).index("gaz")]
            pgaz_set = reduce(set.union, [
                t.value[list(t.name).index('prew')].value[list(t.value[list(t.name).index('prew')].name).index("gaz")]
                for t in sametoks if 'prew' in t.name and 'gaz' in t.value[list(t.name).index('prew')].name], set([]))
            if pgaz_set:
                for t in sametoks:
                    add_annotation(t, value=pgaz_set, name="pgaz")

            ngaz_set = reduce(set.union, [
                t.value[list(t.name).index('next')].value[list(t.value[list(t.name).index('next')].name).index("gaz")]
                for t in sametoks if 'next' in t.name and 'gaz' in t.value[list(t.name).index('next')].name], set([]))
            if ngaz_set:
                for t in sametoks:
                    add_annotation(t, value=ngaz_set, name="ngaz")

        sametoks_dict = defaultdict(list)
        for t in layer:
            if "prop" in t.name:
                sametoks_dict[t.lemma[0]].append(t)

        def check_feature(sametoks, fname, fvalue, test_fun):
            for tok in sametoks:
                if test_fun(tok):
                    for t in sametoks:
                        add_annotation(t, value=fvalue, name=fname)
                    break

        for t in text.tokens:
            if t.lemma[0] in sametoks_dict:
                sametoks = sametoks_dict[t.lemma[0]]
                # Capitalized in other occurrences
                check_feature(sametoks, 'iuoc', "y", lambda tok: tok and "iu" in tok)
                # Prew proper in other occurrences
                check_feature(sametoks, 'pprop', "y",
                              lambda tok: tok.prew and 'prop' in t.value[list(t.name).index('prew')].name)
                # Next proper in other occurrences
                check_feature(sametoks, 'nprop', "y",
                              lambda tok: tok.next and 'prop' in t.value[list(t.name).index('next')].name)
                # Prew in gazeteer in other occurrences
                check_feature(sametoks, 'pgaz', "y",
                              lambda tok: tok.prew and 'gaz' in t.value[list(t.name).index('prew')].name)
                # Next in gazeteer in other occurrences
                # Prew lemma in other occurrences
                check_feature(sametoks, 'plem', "y",
                              lambda tok: tok.prew and 'prop' in t.value[list(t.name).index('prew')].name)
                # Next lemma in other occurrences

                del sametoks_dict[t.lemma[0]]



def apply_templates(toks, templates):
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
    for template in templates:
        name = '|'.join(['%s[%d]' % (f, o) for f, o in template])
        for t in range(len(toks)):
            values_list = []
            for field, offset in template:
                p = t + offset
                if p < 0 or p >= len(toks):
                    values_list = []
                    break
                if field in toks[p].name:
                    value = toks[p].value[list(toks[p].name).index(field)]
                    values_list.append(value if isinstance(value, (set, list)) else [value])
            if len(template) == len(values_list):
                f_values = []
                for values in product(*values_list):
                    if None not in values:
                        f_values.append('%s=%s' % (name, '|'.join(values)))
                toks.add_annotation(toks[t], value=f_values, name='F')


class FeatureExtractor(object):
    """Feature extractor is used for decorating tokens of the documents
    with features specified in configuration files.
    """

    def __init__(self, settings):
        """Initialize the feature extractor.

        Parameters
        ----------
        settings: estnltk.estner.settings.Settings
            The settings and configuration of the NER system.
        """
        self.settings = settings
        self.fex_list = []
        for fex_name in settings.FEATURE_EXTRACTORS:
            fex_class = FeatureExtractor._get_class(fex_name)
            fex_obj = fex_class(settings)
            self.fex_list.append(fex_obj)

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
            apply_templates(doc.ner_features, self.settings.TEMPLATES)

    @staticmethod
    def _get_class(kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
