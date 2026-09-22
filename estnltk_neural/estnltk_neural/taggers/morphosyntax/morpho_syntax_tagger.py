
from estnltk.taggers import Tagger
from estnltk import Layer
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger


class MorphoSyntaxTagger(Tagger):
    """
    Tagger that creates or uses existing uses vabamorf/'morph_analysis' layer, creates morph_extended layer, creates stanza_syntax layer
    and creates new morphosyntax layer that combines all three layers.
    User can define a tagger for creating vabamorf/morph_analysis layer or use an existing layer. 
    The morph_extended and stanza_syntax taggers have to be initialized and passed to MorphoSyntaxTagger.
    
    Returns morphosyntax layer with attributes:
    * {id} -- id from stanza layer;
    * {lemma} -- lemma from Vabamorf / "morph_analysis" layer;
    * {root_tokens} -- root_tokens from Vabamorf / "morph_analysis" layer;
    * {clitic} -- clitic from Vabamorf / "morph_analysis" layer;
    * {xpostag} -- partofspeech from Vabamorf / "morph_analysis" layer;
    * {feats} -- from from Vabamorf / "morph_analysis" layer;
    * {extended_feats} -- from from"morph_extended" layer;
    * {head} {deprel} -- from stanza layer;
    * {parent_span} {children} -- from stanza layer if "add_parent_and_children=True";
    * {stanza_pos} {stanza_feats} {stanza_lemma}  -- from stanza layer, required for transaction tables
    """

    conf_param = [ 'morph_analysis_tagger', 'morph_extended_tagger', 'stanza_tagger', 'output_layer',  'input_layers', 'morph_analysis_layer', 'words_layer']
    output_attributes = ['id', 'lemma', 'root_tokens', 'clitic', 'xpostag', 'feats', 'extended_feats', 'head', 'deprel', 'stanza_pos', 'stanza_feats', 'stanza_lemma', 'parent_span', 'children']
    input_layers = ('words', 'sentences')

    def __init__(self,
                morph_analysis_tagger=None,
                 morph_extended_tagger = None,
                 stanza_tagger = None,
                morph_analysis_layer = None,
                 output_layer:str="morphosyntax",
                 input_layers=input_layers,
                words_layer='words',
                ):
        """Initialize VabamorfWithBertTagger class.
        
        Parameters
        ----------
        output_layer: str (default: 'morphosyntax')
            Name of the layer where analysis results are stored.
        input_layers: List[str] (default: ['words', 'sentences'])
            Names of the input words and sentences layers.
        morph_analysis_tagger: Tagger (default: None)
            Tagger that is used to create the morph_analys layer if it doesn't exist.
            There is no need to pass the tagger if morph_analysis layer already exists. 
            If tagger is given, then a new morph_analsysi layer will be created.
        morph_extended_tagger: Tagger (default: None)
            Tagger that is used to create the morph_extended layer.
            This tagger needs to be defined by the used and passed into this tagger.
        stanza_tagger: Tagger (default: None)
            Tagger that is used to create the stanza_syntax layer.
            This tagger needs to be defined by the used and passed into this tagger.
        morph_analysis_layer: str (default: None)
            Name of the existing morph_analysis/Vabamorf layer that will be used 
            for morph_extended and stanza_syntax layers.
            If morph_analysis_tagger is None then morph_analysis_layer has to be 
            defined and exist in the layers. 
            In case morph_analysis_tagger is defined then this value will be 
            overwritten with the morph_analysis_tagger's output_layer.
        words_layer: str (default 'words')
            Name of the 'words' layer.
        """

        self.output_layer = output_layer
        self.input_layers=input_layers
        self.morph_analysis_layer = morph_analysis_layer
        self.words_layer= words_layer

        if not morph_extended_tagger or not stanza_tagger: 
            # TODO: if necessary layers have been created separately, maybe allow the usage of existing layers
            raise ValueError('(!) The morph_extended and stanza_syntax taggers have to be initialized and passed to MorphoSyntaxTagger.')

        if not morph_analysis_tagger and self.morph_analysis_layer: # use an existing layer 
            self.morph_analysis_layer = morph_analysis_layer
            self.morph_analysis_tagger = None
            self.input_layers += (self.morph_analysis_layer,)
        elif not morph_analysis_tagger and not self.morph_analysis_layer: # use an existing layer 
            raise ValueError('(!) Please provide either a morph_analysis tagger or layer name.')
        else:
            self.morph_analysis_tagger = morph_analysis_tagger
            self.morph_analysis_layer = self.morph_analysis_tagger.output_layer

        self.morph_extended_tagger = morph_extended_tagger
        self.stanza_tagger = stanza_tagger


    def _make_layer_template(self):
        layer = Layer(name=self.output_layer, text_object=None, 
                     attributes=self.output_attributes, parent=None, 
                     ambiguous=False)
        layer.layer.serialisation_module = syntax_v0.__version__
        return layer

    
    def _make_layer(self, text, layers, status=None):

        #   Vabamorf/morph_analysis
        if self.morph_analysis_tagger : # create new morph_analysis layer 
            morph_analysis_layer = self.morph_analysis_tagger.make_layer( text, layers, status )
            text.add_layer(morph_analysis_layer) # if not added then morph_to_syntax_morph_retagger.make_layer raises errors in MorphExtendedTagger
        elif not self.morph_analysis_tagger and self.morph_analysis_layer not in layers:
            raise ValueError(f'(!) Given morph_analysis layer "{self.morph_analysis_layer}" does not exist. Please provide either a morph_analysis tagger or valid layer name. Layers that exist:', layers.keys())
        else:
            morph_analysis_layer = layers[self.morph_analysis_layer]
        
        # layers should contain ideally 'tokens', 'sentences', 'words', 'compound_tokens'
        layers2 = layers.copy()
        layers2[self.input_layers[0]] = layers[self.input_layers[0]]  # words
        layers2[self.input_layers[1]] = layers[self.input_layers[1]]  # sentences
        layers2[self.morph_analysis_layer] = morph_analysis_layer

        

        #   morph_extended
        if self.morph_extended_tagger: # create morph_extended layer 
            morph_extended_layer = self.morph_extended_tagger.make_layer( text, layers2, status )
            layers2[self.morph_extended_tagger.output_layer] = morph_extended_layer

        #   stanza_syntax  
        if self.stanza_tagger: # create morph_extended layer 
            stanza_layer = self.stanza_tagger.make_layer( text, layers2, status )
            layers2[self.stanza_tagger.output_layer] = stanza_layer   

        assert len(morph_extended_layer) == len(stanza_layer)
        assert len(morph_extended_layer) == len(morph_analysis_layer)

        # combine annotations for output layer
        layer = self._make_layer_template()
        layer.text_object = text

        word_id = 0
        for analysis_span, extended_span, stanza_span in zip(morph_analysis_layer, morph_extended_layer, stanza_layer):
            word_span = text[self.words_layer][word_id]
            assert analysis_span.base_span == stanza_span.base_span
            assert analysis_span.base_span == extended_span.base_span
            assert word_span.base_span == stanza_span.base_span
            morph_ann = analysis_span.annotations[0]
            extended_ann = extended_span.annotations[0]
            syntax_ann = stanza_span.annotations[0]
            annotation_dict = {}
            annotation_dict['id'] = syntax_ann['id']
            annotation_dict['lemma'] = morph_ann['lemma']
            annotation_dict['root_tokens'] = morph_ann['root_tokens']
            annotation_dict['clitic'] = morph_ann['clitic']
            annotation_dict['xpostag'] = morph_ann['partofspeech']
            annotation_dict['feats'] = morph_ann['form']
            annotation_dict['extended_feats'] = extended_ann['form']
            annotation_dict['head'] = syntax_ann['head']
            annotation_dict['deprel'] = syntax_ann['deprel']
            annotation_dict['stanza_pos'] = syntax_ann['upostag']
            annotation_dict['stanza_feats'] = syntax_ann['feats']
            annotation_dict['stanza_lemma'] = syntax_ann['lemma']

            layer.add_annotation(analysis_span.base_span, annotation_dict)
            word_id += 1

        syntax_dependency_retagger = SyntaxDependencyRetagger(syntax_layer=self.output_layer)
        syntax_dependency_retagger.change_layer(text, {self.output_layer:layer})

        # clean up unnecessary layers
        if self.morph_analysis_tagger:
            text.pop_layer(self.morph_analysis_layer)
        
        assert len(layer) == len(stanza_layer)

        return layer


