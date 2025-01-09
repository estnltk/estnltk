# GliLem: Vabamorf's lemmatization enhanced with a GLiNER model
# 
# Adapted from adorkin's GliLem demo files: 
# https://huggingface.co/spaces/adorkin/GliLem/blob/15ce1742d8f6bdb4fcce533d5b0fd904bf831c89/demo.py
# https://huggingface.co/spaces/adorkin/GliLem/blob/15ce1742d8f6bdb4fcce533d5b0fd904bf831c89/vabamorf_lemmatizer.py
#

from typing import Union, MutableMapping

from estnltk import Text, Layer

from estnltk_neural.taggers.neural_morph.glilem.rule_processor import RuleProcessor


def create_glilem_layer(text:str, gliner_model:'gliner.model.GLiNER', output_layer:str='glilem_tokens', 
                        lemmatizer:'Lemmatizer'=None, rule_processor:'RuleProcessor'=None,
                        add_missing_lemmas_from_vabamorf:bool=False):
    '''
    GliLem Lemmatizer's preprocessing, following the example:
    https://huggingface.co/spaces/adorkin/GliLem/blob/15ce1742d8f6bdb4fcce533d5b0fd904bf831c89/demo.py
    
    If add_missing_lemmas_from_vabamorf is set, then produces an ambiguous layer and adds 
    word's lemmas from Vabamorf in case GliLem's output did not contain any lemmas. 
    '''
    # Check inputs
    # Initialize missing components (if required)
    if lemmatizer is None:
        lemmatizer = Lemmatizer(
            disambiguate=False, use_context=False, proper_name=True, separate_punctuation=True
        )
    if rule_processor is None:
        rule_processor = RuleProcessor()
    # pre-process input with Vabamorf's lemmatizer
    lemmas, tokens, token_indexes = lemmatizer(text, return_tokens=True)
    # get unique lemmas while keeping the order of lemmas
    lemmas_uniq = []
    for word_lemmas in lemmas:
        lemmas_uniq.append([])
        for lemma in word_lemmas:
            if lemma not in lemmas_uniq[-1]:
                lemmas_uniq[-1].append( lemma )
    lemmas = lemmas_uniq
    assert len(lemmas) == len(tokens)
    assert len(lemmas) == len(token_indexes)
    # map spans to token indexes
    span_to_token_id = dict()
    for idx, token in enumerate(tokens):
        start, end = token_indexes[idx]
        span_to_token_id[f"{start}-{end}"] = idx
    labels = []
    labels_set = set()
    # produce a transofrmation rule for each lemma candidate
    # (!) keep only unique labels and strictly keep the order of labels (!)
    # ( otherwise, gliner's predictions will fluctuate )
    for token, lemma_list in zip(tokens, lemmas):
        for lemma in lemma_list:
            lemma_label = rule_processor.gen_lemma_rule(form=token, lemma=lemma, allow_copy=True)
            if lemma_label not in labels_set:
                labels.append(lemma_label)
            labels_set.add(lemma_label)
    # make predictions with GLiNER model
    predicted_entities = gliner_model.predict_entities(
        text=text, labels=labels, flat_ner=True, threshold=0.5
    )
    # create output layer
    glilem_layer = Layer(name=output_layer, text_object=None, 
                         attributes=('lemma', 'score', 'label', 
                         'vabamorf_overwritten', 'is_input_token'),
                         ambiguous=add_missing_lemmas_from_vabamorf)
    for entity in predicted_entities:
        cur_start = entity["start"]
        cur_end = entity["end"]
        cur_text = entity["text"]
        # Sanity check
        assert text[cur_start:cur_end] == cur_text
        new_lemma = None
        vabamorf_overwritten = False
        is_input_token = True
        if f"{cur_start}-{cur_end}" in span_to_token_id:
            # A) The token is inside the input tokens
            token_id = span_to_token_id[f"{cur_start}-{cur_end}"]
            token = tokens[token_id]
            if len(lemmas[token_id]) > 1:
                # if there are multiple lemma candidates, apply the highest scoring rule
                new_lemma = rule_processor.apply_lemma_rule(token, entity["label"])
                vabamorf_overwritten = True
            else:
                # otherwise, we trust the Vabamorf lemma
                new_lemma = lemmas[token_id][0]
        else:
            # B) The token is missing from input tokens
            new_lemma = rule_processor.apply_lemma_rule(cur_text, entity["label"])
            is_input_token = False
        glilem_layer.add_annotation( (cur_start, cur_end), 
                                      label=entity["label"], 
                                      score=entity["score"], 
                                      lemma=new_lemma,
                                      is_input_token=is_input_token,
                                      vabamorf_overwritten=vabamorf_overwritten )
    # add missing lemmas from Vabamorf (if requested)
    if add_missing_lemmas_from_vabamorf:
        for wid, span_lemmas in enumerate(lemmas):
            w_start, w_end = token_indexes[wid]
            if (w_start, w_end) not in glilem_layer._span_list:
                for vm_lemma in span_lemmas:
                    glilem_layer.add_annotation( (w_start, w_end), 
                                                  label=None, 
                                                  score=None, 
                                                  lemma=vm_lemma,
                                                  is_input_token=True,
                                                  vabamorf_overwritten=False )
    return glilem_layer


class Lemmatizer:
    '''
    GliLem Lemmatizer, adapted from:
    https://huggingface.co/spaces/adorkin/GliLem/blob/15ce1742d8f6bdb4fcce533d5b0fd904bf831c89/vabamorf_lemmatizer.py
    '''

    def __init__(
        self,
        disambiguate: bool = False,
        use_context: bool = False,
        proper_name: bool = True,
        guess: bool = False,
        separate_punctuation: bool = False,
    ):
        from estnltk.taggers import (
            VabamorfTagger,
            WhiteSpaceTokensTagger,
            PretokenizedTextCompoundTokensTagger,
            TokensTagger,
        )
        self.disambiguate = disambiguate
        self.use_context = use_context
        self.proper_name = proper_name
        self.guess = guess
        # TODO: make input layer names customizable
        # TODO: switching off compound and guess is rather restrictive
        # TODO: add possibility to used a customized VabamorfTagger 
        # for preprocessing
        self.tagger = VabamorfTagger(
            output_layer='_gilem_preproccessing_morph',
            compound=False,
            disambiguate=self.disambiguate,
            guess=self.guess,
            slang_lex=False,
            phonetic=False,
            use_postanalysis=True,
            use_reorderer=True,
            propername=self.proper_name,
            predisambiguate=self.use_context,
            postdisambiguate=self.use_context,
        )
        self.separate_punctuation = separate_punctuation
        if self.separate_punctuation:
            self.tokens_tagger = TokensTagger()
        else:
            self.tokens_tagger = WhiteSpaceTokensTagger()
        self.compound_token_tagger = PretokenizedTextCompoundTokensTagger()

    def __call__(self, text: Union[str, Text], return_tokens: bool = False, layers: MutableMapping[str, Layer]=None) -> list[list[str]]:
        if isinstance(text, str):
            # Process input as string. Use tokenization from GliLem's demo
            text = Text(text)
            self.tokens_tagger.tag(text)
            self.compound_token_tagger.tag(text)
            text.tag_layer(self.tagger.input_layers)
            self.tagger.tag(text)
            if return_tokens:
                words = []
                lemmas = []
                indexes = []
                for span in text[self.tagger.output_layer]:
                    words.append( span.annotations[0]['normalized_text'] ) 
                    lemmas.append( [a['lemma'] for a in span.annotations] ) 
                    indexes.append( (span.start, span.end) ) 
                return lemmas, words, indexes
            return list(text[self.tagger.output_layer].lemma)
        elif isinstance(text, Text):
            # Process input that has already been tokenized by Estnltk
            # Rely on Estnltk's tokenization
            missing_layers = []
            for layer in self.tagger.input_layers:
                if layers is None or (layer not in layers):
                    missing_layers.append(layer)
            if missing_layers:
                raise ValueError(f'(!) Missing input layer(s): {missing_layers!r}')
            preprocessed_layer = self.tagger.make_layer(text, layers=layers)
            if return_tokens:
                words = []
                lemmas = []
                indexes = []
                for span in preprocessed_layer:
                    words.append( span.annotations[0]['normalized_text'] ) 
                    lemmas.append( [a['lemma'] for a in span.annotations] )
                    indexes.append( (span.start, span.end) )
                return lemmas, words, indexes
            return list(preprocessed_layer.lemma)


