import os
from estnltk.text import Layer
from estnltk.taggers import Tagger

from estnltk.neural_morph.new_neural_morph.general_utils import load_config_from_file
from estnltk.neural_morph.new_neural_morph.vabamorf_2_neural import neural_model_tags

# There are 4 different neural models that this tagger can be used with:
    
# Model 1
#   model_module = estnltk.neural_morph.new_neural_morph.seq2seq
#   config_filename = estnltk/neural_morph/new_neural_morph/seq2seq/emb_cat_sum/config.py

# Model 2
#   model_module = estnltk.neural_morph.new_neural_morph.seq2seq
#   config_filename = estnltk/neural_morph/new_neural_morph/seq2seq/emb_tag_sum/config.py
    
# Model 3
#   model_module = estnltk.neural_morph.new_neural_morph.softmax
#   config_filename = estnltk/neural_morph/new_neural_morph/softmax/emb_cat_sum/config.py

# Model 4
#   model_module = estnltk.neural_morph.new_neural_morph.softmax
#   config_filename = estnltk/neural_morph/new_neural_morph/softmax/emb_tag_sum/config.py

# out_dir directories (which contain trained models) are missing, but they should be located in the
# same folder as config.py files when the user downloads them.

def load_model(model_module, config_filename):
    config = load_config_from_file(config_filename)
    config_holder = model_module.ConfigHolder(config)
    model = model_module.Model(config_holder)
    model.build()
    model.restore_session(config.dir_model)
    return model


class NeuralMorphTagger(Tagger):
    """
    Performs neural morphological tagging. It takes vabamorf analyses
    as input to predict morphological tags with better accuracy than vabamorf, 
    but it uses a different tag set.
    """
    conf_param = ('model',)
    
    def __init__(self, model_module, config_filename, out_dir):
        os.environ['OUT_DIR'] = out_dir # This is used in estnltk/neural_morph/new_neural_morph/common_config.py
        self.model = load_model(model_module, config_filename)
        self.output_layer = 'new_neuro_morph'
        self.output_attributes = ('tag',)
        self.input_layers = ('morph_analysis',)

    def _make_layer(self, text, layers, status=None):
        preds = []
        
        for sentence in layers['sentences']:
            sentence_words = sentence['text']
            analyses = []
            
            for word in sentence:
                word_text = word.text
                pos_tags = word.morph_analysis['partofspeech']
                forms = word.morph_analysis['form']
                
                word_analyses = []
                for pos, form in zip(pos_tags, forms):
                    word_analyses.extend(neural_model_tags(word_text, pos, form))
                analyses.append(word_analyses)
                
            preds.extend(['|'.join(p) if isinstance(p, (list, tuple)) else p
                          for p in self.model.predict(sentence_words, analyses)])
        
        layer = Layer(name=self.output_layer, text_object=text, parent='morph_analysis', attributes=self.output_attributes)
        
        for span, pred in zip(layers['morph_analysis'], preds):
            layer.add_annotation(span, tag=pred)
            
        return layer
