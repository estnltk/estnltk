import importlib
import os

from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk_neural.taggers.neural_morph.new_neural_morph.general_utils import load_config_from_file
from estnltk_neural.taggers.neural_morph.new_neural_morph.vabamorf_2_neural import neural_model_tags
from estnltk_neural.taggers.neural_morph.new_neural_morph.neural_2_vabamorf import vabamorf_tags

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
    if (os.path.exists(model_dir)):
        for folder in MODEL_FILES:
            for file in MODEL_FILES[folder]:
                if not os.path.exists(os.path.join(model_dir, folder, file)):
                    raise FileNotFoundError("TODO: Instructions for downloading model files")


class NeuralMorphTagger(Tagger):
    """Performs neural morphological tagging. It takes vabamorf analyses as input to predict
    morphological tags with better accuracy than vabamorf, but uses a different tag set.
    
    Do not use this class directly. Use the following methods to get taggers with
    different types of neural models:
        
    SoftmaxEmbTagSumTagger()
    SoftmaxEmbCatSumTagger()
    Seq2SeqEmbTagSumTagger()
    Seq2SeqEmbCatSumTagger()
    
    For example:
    
        text = Text("See on lause.")
        text.tag_layer(['morph_analysis'])
        
        tagger = SoftmaxEmbTagSumTagger()
        tagger.tag(text)
        
        print(text.neural_morph_analysis['morphtag'])
        
    Output:
        
        ['POS=P|NUMBER=sg|CASE=nom', 
         'POS=V|VERB_TYPE=main|MOOD=indic|TENSE=pres|PERSON=ps3|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=af', 
         'POS=S|NOUN_TYPE=com|NUMBER=sg|CASE=nom', 
         'POS=Z|PUNCT_TYPE=Fst']

    """
    conf_param = ('model',)

    def __init__(self, output_layer='neural_morph_analysis', module_name=None, module_package=None,
                 model_module=None, model=None):
        if module_name is not None and module_package is not None:
            model_module = importlib.import_module('.' + module_name, module_package)
        if model_module is not None:
            module_path = os.path.dirname(model_module.__file__)
            config = load_config_from_file(os.path.join(module_path, "config.py"))
            check_model_files(config.out_dir)

            config_holder = model_module.ConfigHolder(config)
            self.model = model_module.Model(config_holder)
            self.model.build()
            self.model.restore_session(config.dir_model)
        else:
            self.model = model  # For unit testing

        self.output_layer = output_layer
        self.output_attributes = ('morphtag', 'pos', 'form')
        self.input_layers = ('morph_analysis', 'sentences', 'words')

    def _make_layer(self, text, layers, status=None):
        layer = Layer(name=self.output_layer,
                      text_object=text,
                      parent='words',
                      ambiguous=False,
                      attributes=self.output_attributes)
        morphtags = []

        for sentence in layers['sentences']:
            sentence_words = sentence.text
            analyses = []

            for word in sentence:
                word_text = word.text
                pos_tags = word.morph_analysis['partofspeech']
                forms = word.morph_analysis['form']

                word_analyses = []
                for pos, form in zip(pos_tags, forms):
                    word_analyses.extend(neural_model_tags(word_text, pos, form))
                analyses.append(word_analyses)

            morphtags.extend(self.model.predict(sentence_words, analyses))

        for word, tag in zip(layers['words'], morphtags):
            vm_pos, vm_form = vabamorf_tags(tag)
            layer.add_annotation(word, morphtag=tag, pos=vm_pos, form=vm_form)

        return layer

    def reset(self):
        self.model.reset()


class SoftmaxEmbTagSumTagger(NeuralMorphTagger):
    """SoftmaxEmbTagSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='softmax_emb_tag_sum',
                         module_package='estnltk.taggers.neural_morph.new_neural_morph')


class SoftmaxEmbCatSumTagger(NeuralMorphTagger):
    """SoftmaxEmbCatSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='softmax_emb_cat_sum',
                         module_package='estnltk.taggers.neural_morph.new_neural_morph')


class Seq2SeqEmbTagSumTagger(NeuralMorphTagger):
    """Seq2SeqEmbTagSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='seq2seq_emb_tag_sum',
                         module_package='estnltk.taggers.neural_morph.new_neural_morph')


class Seq2SeqEmbCatSumTagger(NeuralMorphTagger):
    """Seq2SeqEmbCatSumTagger

    """
    def __init__(self, output_layer: str = 'neural_morph_analysis'):
        super().__init__(output_layer=output_layer, module_name='seq2seq_emb_cat_sum',
                         module_package='estnltk.taggers.neural_morph.new_neural_morph')
