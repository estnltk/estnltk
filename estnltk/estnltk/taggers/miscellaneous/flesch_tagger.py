from estnltk.taggers import Retagger
from estnltk.vabamorf.morf import syllabify_word
from estnltk.taggers.miscellaneous import flesch


class SentenceFleschScoreRetagger(Retagger):
    """Adds Flesch reading ease score to sentences layer and the whole text."""
    
    def __init__(self,
                 sentences_layer='sentences',
                 score_attribute='flesch_score'):
        
        self.conf_param = []
        self.input_layers = [sentences_layer]
        self.output_layer = sentences_layer
        self.output_attributes = (score_attribute,)

    def _change_layer(self, text, layers, status):
        if 'sentences' not in text.layers:
            text.tag_layer(['sentences'])
        if 'morph_analysis' not in text.layers:
            text.tag_layer(['morph_analysis'])
        layer = text[self.output_layer]
        layer.attributes = layer.attributes + self.output_attributes
        
        total_sentences = len(text[self.output_layer])
        total_words     = len(text['words'])
        total_syllables = 0
        
        # tag individual scores for each sentence
        for sentence in text.sentences:
            sentence_syllables = 0
            
            for word in sentence:
                # skip non-words with Z as their part of speech
                if any(pos == 'Z' for pos in word.morph_analysis.partofspeech):
                    continue
                    
                total_words += 1
                sentence_syllables += len(syllabify_word(word.text))
            
            # tag the score of the sentence
            sentence.flesch_score = flesch.fres_score(
                total_sentences = 1, 
                total_words     = total_words,
                total_syllables = sentence_syllables)
            
            total_syllables += sentence_syllables
        
        # tag score for the whole text
        text_score = flesch.fres_score(
            total_sentences,
            total_words,
            total_syllables
        )

        layer.text_object.meta['whole_text_flesch_score'] = text_score
