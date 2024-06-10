import os
import importlib
from importlib.util import find_spec

from estnltk import Layer
from estnltk.taggers import Retagger
from estnltk.downloader import get_resource_paths

from estnltk_neural.taggers.neural_morph.new_neural_morph.general_utils import load_config_from_file
from estnltk_neural.taggers.neural_morph.new_neural_morph.general_utils import override_config_paths_from_model_dir
from estnltk_neural.taggers.neural_morph.new_neural_morph.vabamorf_2_neural import neural_model_tags
from estnltk_neural.taggers.neural_morph.new_neural_morph.neural_2_vabamorf import vabamorf_tags

def is_tensorflow_available():
    '''Checks if tensorflow package has been installed.'''
    return find_spec('tensorflow') is not None


MODEL_FILES = {"data": ["analysis.txt",
                        "chars.txt",
                        "embeddings.npz",
                        "singletons.txt",
                        "tags.txt",
                        "words.txt"],

               "results": ["model.weights.data-00000-of-00001",
                           "model.weights.index",
                           "model.weights.meta"]}


def check_model_files(model_dir):
    check_failed = False
    if os.path.exists(model_dir):
        for folder in MODEL_FILES:
            for file in MODEL_FILES[folder]:
                if not os.path.exists(os.path.join(model_dir, folder, file)):
                    check_failed = True
    else:
        check_failed = True
    if check_failed:
        msg = "Could not load location of NeuralMorphTagger's model. "+\
              "For model autodownload and autoinitialization, do not use "+\
              "NeuralMorphTagger class directly, but use classes "+\
              "SoftmaxEmbTagSumTagger, SoftmaxEmbCatSumTagger, "+\
              "Seq2SeqEmbTagSumTagger or Seq2SeqEmbCatSumTagger. "+\
              "For manual pre-downloading of the models, use estnltk.download(MODEL_NAME) "+\
              "where MODEL_NAME is one of the following: 'softmaxembcatsumtagger', "+\
              "'softmaxembtagsumtagger', 'seq2seqembcatsumtagger' or "+\
              "'seq2seqembtagsumtagger'."
        raise FileNotFoundError( msg )


class NeuralMorphTagger(Retagger):
    """
    Performs neural morphological tagging. It takes Vabamorf's analyses as an input to 
    predict morphological tags (partofspeech and form) with better accuracy than Vabamorf. 
    The tagger also employs a special morphological tagset that extends Vabamorf's tags 
    towards UD's morphological features.
    
    Do not use this class directly. Use the following classes to get taggers with
    different types of neural models:
    
    SoftmaxEmbTagSumTagger()
    SoftmaxEmbCatSumTagger()
    Seq2SeqEmbTagSumTagger()
    Seq2SeqEmbCatSumTagger()
    
    This tagger works either as a tagger (A) or as a retagger (B), depending on 
    whether the input morph_analysis layer is different from the output layer or 
    not. 
    
    A) If output_layer != input_morph_analysis_layer, then the tagger works as a tagger 
    and a new morph layer can be created by calling tagger's tag(...) or make_layer(...) 
    methods. 
    For example:
    
        text = Text("See on lause.")
        text.tag_layer('morph_analysis')
        
        tagger = SoftmaxEmbCatSumTagger()
        tagger.tag(text)
        
        print(text.neural_morph_analysis['morphtag'])
        
    Output:
    
        ['POS=P|NUMBER=sg|CASE=nom', 
         'POS=V|VERB_TYPE=main|MOOD=indic|TENSE=pres|PERSON=ps3|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=af', 
         'POS=S|NOUN_TYPE=com|NUMBER=sg|CASE=nom', 
         'POS=Z|PUNCT_TYPE=Fst']
    
    B) If output_layer == input_morph_analysis_layer, then the tagger works as a retagger 
    and disambiguates existing morph_analysis layer. 
    For example:
    
        text = Text("See on lause.")
        text.tag_layer('morph_analysis')
        
        tagger = SoftmaxEmbCatSumTagger(output_layer='morph_analysis')
        tagger.retag(text)
        
        print([(a.text, a.lemma, a.partofspeech, a.form) for word in text['morph_analysis'] for a in word.annotations])
    
    Output:
    
        [('See', 'see', 'P', 'sg n'), ('on', 'olema', 'V', 'b'), ('lause', 'lause', 'S', 'sg n'), ('.', '.', 'Z', '')]
    
    """
    conf_param = ('model',)

    def __init__(self, output_layer='neural_morph_analysis', input_words_layer='words',
                       input_sentences_layer='sentences', input_morph_analysis_layer='morph_analysis', 
                       module_name=None, module_package=None, model_module=None, model=None, 
                       model_dir=None, bypass_tensorflow_check=False):
        if not is_tensorflow_available():
            if not bypass_tensorflow_check:
                raise ModuleNotFoundError("(!) Tensorflow not installed. "+\
                                          "You'll need tensorflow <= 1.15.5 for running this tagger.")
        if module_name is not None and module_package is not None:
            model_module = importlib.import_module('.' + module_name, module_package)
        if model_module is not None:
            module_path = os.path.dirname(model_module.__file__)
            config = load_config_from_file(os.path.join(module_path, "config.py"))
            if module_name is None:
                module_name = (model_module.__name__).split('.')[-1]
            else:
                assert (model_module.__name__).endswith(module_name)
            
            # Try to overwrite file paths in the configuration based on 
            # the given model directory. If model_dir is None, do nothing
            config = override_config_paths_from_model_dir(config, model_dir)

            check_model_files(config.out_dir)

            config_holder = model_module.ConfigHolder(config)
            self.model = model_module.Model(config_holder)
            self.model.build()
            self.model.restore_session(config.dir_model)
        else:
            self.model = model  # For unit testing

        self.output_layer = output_layer
        self.output_attributes = ('morphtag', 'pos', 'form')
        self.input_layers = (input_morph_analysis_layer, 
                             input_sentences_layer, 
                             input_words_layer)

    def _make_layer(self, text, layers, status=None):
        sentences_layer = self.input_layers[1]
        words_layer = self.input_layers[2]
        morph_layer = self.input_layers[0]
        layer = Layer(name=self.output_layer,
                      text_object=text,
                      parent=words_layer,
                      ambiguous=False,
                      attributes=self.output_attributes)
        morphtags = []

        global_word_id = 0
        for sentence in layers[sentences_layer]:
            sentence_words = sentence.text
            analyses = []

            for word_base_span in sentence.base_span:
                morph_word = layers[morph_layer][global_word_id]
                assert word_base_span == morph_word.base_span
                word_text = morph_word.text
                pos_tags = morph_word['partofspeech']
                forms = morph_word['form']
                word_analyses = []
                for pos, form in zip(pos_tags, forms):
                    word_analyses.extend(neural_model_tags(word_text, pos, form))
                analyses.append(word_analyses)
                global_word_id += 1

            morphtags.extend(self.model.predict(sentence_words, analyses))

        for word, tag in zip(layers[words_layer], morphtags):
            vm_pos, vm_form = vabamorf_tags(tag)
            layer.add_annotation(word, morphtag=tag, pos=vm_pos, form=vm_form)

        return layer

    def _change_layer(self, text, layers, status=None):
        # Validate inputs
        if self.output_layer != self.input_layers[0]:
            raise Exception( ('(!) Mismatching output_layer and input_morph_analysis_layer {!r} != {!r}. '+\
                             'Cannot use as a retagger.').format(self.output_layer, self.input_layers[0]) )
        morph_layer = layers[self.output_layer]
        for attr in ['partofspeech', 'form']:
            if attr not in morph_layer.attributes:
                raise Exception( ('(!) Missing attribute {!r} in input_morph_analysis_layer {!r}.'+\
                                  '').format(attr, morph_layer.name) )
        # Create disambiguation layer
        disamb_layer = self._make_layer(text, layers, status)
        # Disambiguate input_morph_analysis_layer
        assert len(morph_layer) == len(disamb_layer)
        for original_word, disamb_word in zip(morph_layer, disamb_layer):
            disamb_pos  = disamb_word.annotations[0]['pos']
            disamb_form = disamb_word.annotations[0]['form']
            # Filter annotations of the original morph layer: keep only those
            # annotations that are matching with the disambiguated annotation
            # (note: there can be multiple suitable annotations due to lemma 
            #  ambiguities)
            keep_annotations = []
            for annotation in original_word.annotations:
                if annotation['partofspeech'] == disamb_pos and annotation['form'] == disamb_form:
                    keep_annotations.append(annotation)
            if len(keep_annotations) > 0:
                # Only disambiguate if there is at least one annotation left
                # (can't leave a word without any annotations)
                original_word.clear_annotations()
                for annotation in keep_annotations:
                    original_word.add_annotation( annotation )

    def reset(self):
        self.model.reset()


class SoftmaxEmbTagSumTagger(NeuralMorphTagger):
    """SoftmaxEmbTagSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis', input_words_layer: str = 'words',
                       input_sentences_layer: str ='sentences', input_morph_analysis_layer: str ='morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='softmax_emb_tag_sum',
                         module_package='estnltk_neural.taggers.neural_morph.new_neural_morph',
                         model_dir=get_resource_paths("softmaxembtagsumtagger", only_latest=True, download_missing=True),
                         input_words_layer=input_words_layer, 
                         input_sentences_layer=input_sentences_layer,
                         input_morph_analysis_layer=input_morph_analysis_layer)


class SoftmaxEmbCatSumTagger(NeuralMorphTagger):
    """SoftmaxEmbCatSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis', input_words_layer: str = 'words',
                       input_sentences_layer: str ='sentences', input_morph_analysis_layer: str ='morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='softmax_emb_cat_sum',
                         module_package='estnltk_neural.taggers.neural_morph.new_neural_morph',
                         model_dir=get_resource_paths("softmaxembcatsumtagger", only_latest=True, download_missing=True),
                         input_words_layer=input_words_layer, 
                         input_sentences_layer=input_sentences_layer,
                         input_morph_analysis_layer=input_morph_analysis_layer)


class Seq2SeqEmbTagSumTagger(NeuralMorphTagger):
    """Seq2SeqEmbTagSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis', input_words_layer: str = 'words',
                       input_sentences_layer: str ='sentences', input_morph_analysis_layer: str ='morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='seq2seq_emb_tag_sum',
                         module_package='estnltk_neural.taggers.neural_morph.new_neural_morph',
                         model_dir=get_resource_paths("seq2seqembtagsumtagger", only_latest=True, download_missing=True),
                         input_words_layer=input_words_layer, 
                         input_sentences_layer=input_sentences_layer,
                         input_morph_analysis_layer=input_morph_analysis_layer)


class Seq2SeqEmbCatSumTagger(NeuralMorphTagger):
    """Seq2SeqEmbCatSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis', input_words_layer: str = 'words',
                       input_sentences_layer: str ='sentences', input_morph_analysis_layer: str ='morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='seq2seq_emb_cat_sum',
                         module_package='estnltk_neural.taggers.neural_morph.new_neural_morph',
                         model_dir=get_resource_paths("seq2seqembcatsumtagger", only_latest=True, download_missing=True),
                         input_words_layer=input_words_layer, 
                         input_sentences_layer=input_sentences_layer,
                         input_morph_analysis_layer=input_morph_analysis_layer)
