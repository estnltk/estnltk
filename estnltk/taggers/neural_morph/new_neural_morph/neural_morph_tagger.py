import os

from estnltk.text import Layer
from estnltk.taggers import Tagger
from estnltk.taggers.neural_morph.new_neural_morph.models import seq2seq, softmax
from estnltk.taggers.neural_morph.new_neural_morph.models.general_utils import load_config_from_file
from estnltk.taggers.neural_morph.new_neural_morph.models.vabamorf_2_neural import neural_model_tags
from estnltk.taggers.neural_morph.new_neural_morph.models.neural_2_vabamorf import vabamorf_tags

MODEL_FILES = {"data":["analysis.txt",
                       "chars.txt",
                       "embeddings.npz",
                       "singletons.txt",
                       "tags.txt",
                       "words.txt"],

              "results":["model.weights.data-00000-of-00001",
                         "model.weights.index",
                         "model.weights.meta"]}

def check_model_files(model_dir):
    if (os.path.exists(model_dir)):
        for folder in MODEL_FILES:
            for file in MODEL_FILES[folder]:
                if not os.path.exists(os.path.join(model_dir, folder, file)):
                    raise FileNotFoundError("TODO: Instructions for downloading model files")

def SoftmaxEmbTagSumTagger():
    return load_tagger(os.path.join(os.path.dirname(softmax.__file__), "emb_tag_sum", "config.py"))

def SoftmaxEmbCatSumTagger():
    return load_tagger(os.path.join(os.path.dirname(softmax.__file__), "emb_cat_sum", "config.py"))

def Seq2SeqEmbTagSumTagger():
    return load_tagger(os.path.join(os.path.dirname(seq2seq.__file__), "emb_tag_sum", "config.py"))    
    
def Seq2SeqEmbCatSumTagger():
    return load_tagger(os.path.join(os.path.dirname(seq2seq.__file__), "emb_cat_sum", "config.py"))

def load_tagger(neural_model_config):
    if "softmax" in neural_model_config:
        model_module = softmax
    else:
        model_module = seq2seq
        
    config = load_config_from_file(neural_model_config)
    check_model_files(config.out_dir)
    
    config_holder = model_module.ConfigHolder(config)
    model = model_module.Model(config_holder)
    model.build()
    model.restore_session(config.dir_model)
    
    return NeuralMorphTagger(model)

class NeuralMorphTagger(Tagger):
    """
    Performs neural morphological tagging. It takes vabamorf analyses as input to predict
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
    
    def __init__(self, model):
        self.model = model
        self.output_layer = 'neural_morph_analysis'
        self.output_attributes = ('morphtag', 'pos', 'form')
        self.input_layers = ('morph_analysis',)

    def _make_layer(self, text, layers, status=None):
        layer = Layer(name=self.output_layer, 
                      text_object=text, 
                      parent='words', 
                      ambiguous=False, 
                      attributes=self.output_attributes)
        
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
                
            tags = self.model.predict(sentence_words, analyses)
        
            for word, tag in zip(sentence.words, tags):
                vm_pos, vm_form = vabamorf_tags(tag)
                layer.add_annotation(word, morphtag=tag, pos=vm_pos, form=vm_form)
            
        return layer
    
    def reset(self):
        self.model.reset()