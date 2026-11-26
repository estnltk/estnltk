from pathlib import Path

from estnltk.downloader import get_resource_paths
from estnltk_core import RelationLayer
from estnltk_core.taggers import RelationTagger

from estnltk.taggers.miscellaneous.verbal_multiword_expr.verbal_multiword_expr_core import (
    Token, find_matches, load_lexicon,
)


def _membership(layer):
    return {tuple(bounds): number for number, group in enumerate(layer)
            for bounds in group.base_span.flatten()}


def _participle_lemmas(form, lemma):
    from estnltk.vabamorf.morf import Vabamorf

    results = Vabamorf.instance().analyze([form, lemma], disambiguate=False, guess=False)
    return {a['lemma'].casefold() for result in results for a in result['analysis']
            if a['partofspeech'] == 'V' and a['form'] in {'nud', 'tud', 'v', 'tav'}}


class VerbalMultiWordExprPreTagger(RelationTagger):
    """Find potential verbal multiword expressions based on clauses and dependency syntactic annotations."""

    conf_param = ('include_nonfinite', 'include_compound_verbs', 'include_copula_heads',
                  'include_verbal_idioms', 'lexicon_path', 'max_components', '_entries', '_by_lemma')

    def __init__(self, syntax_layer='stanza_syntax', clauses_layer='clauses',
                 words_layer='words', sentences_layer='sentences',
                 output_layer='pre_verbal_multiword_expressions',
                 include_compound_verbs=False, include_nonfinite=False,
                 lexicon_path=None, max_components=5, include_copula_heads=True,
                 include_verbal_idioms=False):
        """Initialize VerbalMultiWordExprPreTagger.
        
        Parameters
        ----------
        syntax_layer: str (default: 'stanza_syntax')
            Name of the input dependency syntax layer.
        clauses_layer: str (default: 'clauses')
            Name of the input clauses layer.
        words_layer: str (default: 'words')
            Name of the input words layer.
        sentences_layer: str (default: 'sentences')
            Name of the input sentences layer.
        output_layer: str (default: 'pre_verbal_multiword_expressions')
            Name of the output layer.
        include_compound_verbs: boolean (default: False)
            If switched on, then adds particle verbs to the output layer 
            based the `compound:prt` deprels in the input syntax_layer. 
            The output layer will get additional attribute `'is_compound_verb'` 
            indicating whether the verbal multiword is a particle verb or not. 
        include_nonfinite: boolean (default: False)
            If switched on, then also finds verbal multiword expressions that 
            are anchored to infinite verbs. By default, verbal multiword 
            expressions are only anchored to finite verbs (central verbs of 
            clause), and inifinite verbs are excluded from being anchors. 
            Note that the attribute `'is_central_verb'` indicates whether the 
            detected multiword is anchored to a central verb (that is: no 
            verb occurs above the verb in its clause) or not.
        lexicon_path: str (default: None)
            Path to multiword expressions json format lexicon. 
            If not provided (default), then attempts to get the lexicon from 
            estnltk_resources. If that fails (the resource is missing and 
            downloading fails), then throws an exception.
        max_components: int (default: 5)
            The number of components (`f'comp_{i}'` named spans) in the output 
            layer. Defaults to 5. Change this value if you want to enable longer 
            multiword expressions, e.g. expressions that cover 6 or 7 words. 
        include_copula_heads: boolean (default: True)
            If switched on (default), then detects verbal multiwords also from 
            copula constructions where the dependency relations are reversed: 
            the copula verb 'olema' is governed by its complement (e.g. 'abiks' 
            governs 'olema' in the expression 'abiks olema'). 
        include_verbal_idioms: boolean (default: False)
            If switched on, then adds verbal idioms to the output layer 
            based the `compound:idiom` deprels in the input syntax_layer. 
            The output layer will get additional attribute `'is_verbal_idiom'` 
            indicating whether the verbal multiword is a verbal idiom or not. 
        """
        if type(max_components) is not int or max_components < 1:
            raise ValueError('max_components must be a positive integer.')
        self.input_layers = (words_layer, sentences_layer, clauses_layer, syntax_layer)
        self.output_layer = output_layer
        self.output_span_names = ('verb',) + tuple(f'comp_{i}' for i in range(1, max_components + 1))
        self.output_attributes = ('expression', 'is_inflected', 'is_central_verb')
        if include_compound_verbs:
            self.output_attributes += ('is_compound_verb',)
        if include_verbal_idioms:
            self.output_attributes += ('is_verbal_idiom',)
        self.include_nonfinite = include_nonfinite
        self.include_compound_verbs = include_compound_verbs
        self.include_copula_heads = include_copula_heads
        self.include_verbal_idioms = include_verbal_idioms
        self.max_components = max_components
        if lexicon_path is None:
            resource_path = get_resource_paths('verbal_multiword_expr_lexicon',
                                               only_latest=True, download_missing=True)
            if resource_path is None:
                raise FileNotFoundError('Verbal MWE lexicon is missing. Download '
                                        '"verbal_multiword_expr_lexicon" or set lexicon_path.')
            lexicon_path = Path(resource_path) / 'eki_verbal_mwe.json'
        self.lexicon_path = Path(lexicon_path)
        self._entries, self._by_lemma = load_lexicon(self.lexicon_path, max_components)

    def _make_layer_template(self):
        return RelationLayer(name=self.output_layer, span_names=self.output_span_names,
                             attributes=self.output_attributes, ambiguous=True)

    def _make_layer(self, text, layers, status=None):
        words, sentences, clauses, syntax = [layers[name] for name in self.input_layers]
        sentence_ids, clause_ids = _membership(sentences), _membership(clauses)
        tokens = []
        for word, span in zip(words, syntax):
            a = span.annotations[0]
            bounds = (word.start, word.end)
            tokens.append(Token(
                span=bounds, form=text.text[word.start:word.end], lemma=a['lemma'].casefold(),
                pos={a[key] for key in ('upostag', 'xpostag') if key in a}, features=a['feats'],
                sentence=sentence_ids[bounds], clause=clause_ids[bounds],
                identifier=a['id'], head=a['head'], deprel=a['deprel'],
            ))
        output = self._make_layer_template()
        output.text_object = text
        for match in find_matches(
            tokens, self._entries, self._by_lemma, _participle_lemmas,
            include_nonfinite=self.include_nonfinite,
            include_compound_verbs=self.include_compound_verbs,
            include_copula_heads=self.include_copula_heads,
            include_verbal_idioms=self.include_verbal_idioms,
        ):
            output.add_annotation(**match)
        return output
