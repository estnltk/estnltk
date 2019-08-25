import os

from estnltk.text import Layer
from estnltk.taggers import Tagger
from estnltk.neural_morph.new_neural_morph.general_utils import load_config_from_file
from estnltk.neural_morph.new_neural_morph.vabamorf_2_neural import neural_model_tags
from estnltk.neural_morph.new_neural_morph import softmax
from estnltk.neural_morph.new_neural_morph import seq2seq

model_files = {"data":["analysis.txt",
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
        for folder in model_files:
            for file in model_files[folder]:
                if not os.path.exists(os.path.join(model_dir, folder, file)):
                    raise FileNotFoundError("TODO: Instructions for downloading model files")

def softmax_emb_tag_sum():
    return load_tagger(softmax, "emb_tag_sum")

def softmax_emb_cat_sum():
    return load_tagger(softmax, "emb_cat_sum")

def seq2seq_emb_tag_sum():
    return load_tagger(seq2seq, "emb_tag_sum")    
    
def seq2seq_emb_cat_sum():
    return load_tagger(seq2seq, "emb_cat_sum")

def load_tagger(model_module, dir_name):
    model_path = os.path.join(os.path.dirname(model_module.__file__), dir_name)
    config_filename = os.path.join(model_path, "config.py")
    model_dir = os.path.join(model_path, "output")
    check_model_files(model_dir)
    os.environ['OUT_DIR'] = model_dir
    return NeuralMorphTagger(load_model(model_module, config_filename))

def load_model(model_module, config_filename):
    config = load_config_from_file(config_filename)
    config_holder = model_module.ConfigHolder(config)
    model = model_module.Model(config_holder)
    model.build()
    model.restore_session(config.dir_model)
    return model

class NeuralMorphTagger(Tagger):
    """
    Performs neural morphological tagging. It takes vabamorf analyses as input to predict
    morphological tags with better accuracy than vabamorf, but uses a different tag set.
    
    Do not use this class directly. Use the following methods to get taggers with
    different types of neural models:
        
    softmax_emb_tag_sum()
    softmax_emb_cat_sum()
    seq2seq_emb_tag_sum()
    seq2seq_emb_cat_sum()
    
    For example:
    
        text = Text("See on lause.")
        text.tag_layer(['morph_analysis'])
        
        tagger = softmax_emb_tag_sum()
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
        self.output_attributes = ('morphtag',)
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
                layer.add_annotation(word, morphtag=tag)
            
        return layer