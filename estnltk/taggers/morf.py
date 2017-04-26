from estnltk.text import Span, Layer, Text
from estnltk.vabamorf.morf import Vabamorf

from estnltk.rewriting.postmorph.vabamorf_corrector import VabamorfCorrectionRewriter

class VabamorfTagger:
    def __init__(self, 
                 premorf_layer:str='normalized',
                 postmorph_rewriter=VabamorfCorrectionRewriter(),
                 **kwargs):
        self.kwargs = kwargs
        self.instance = Vabamorf.instance()

        self.premorf_layer = premorf_layer
        self.postmorph_rewriter = postmorph_rewriter

        # TODO: Think long and hard about the default parameters
        # TODO: See also https://github.com/estnltk/estnltk/issues/66
        """
        words: list of str or str
            Either a list of pretokenized words or a string. In case of a string, it will be splitted using
            default behaviour of string.split() function.
        disambiguate: boolean (default: True)
            Disambiguate the output and remove incosistent analysis.
        guess: boolean (default: True)
            Use guessing in case of unknown words
        propername: boolean (default: True)
            Perform additional analysis of proper names.
        compound: boolean (default: True)
            Add compound word markers to root forms.
        phonetic: boolean (default: False)
            Add phonetic information to root forms.

        Returns
        -------
        list of (list of dict)
            List of analysis for each word in input.
        """

    def _get_wordlist(self, text:Text):
        if self.premorf_layer is None:
            return text.words.text
        else:
            augmenting_layer = text.layers[self.premorf_layer]
            result = []
            substitutions = {(i.parent.start,i.parent.end):i for i in augmenting_layer.spans}

            for word in text.words:
                if (word.start, word.end) not in substitutions.keys():
                    result.append(word.text)
                else:
                    result.append(substitutions[(word.start, word.end)].normal)
            return result

            #selles punktis peab midagi otsustama.

    def tag(self, text: Text) -> Text:
        wordlist = self._get_wordlist(text)
        analysis_results = self.instance.analyze(words=wordlist, **self.kwargs)

        morph_attributes = ['form', 'root_tokens', 'clitic', 'partofspeech', 
                            'ending', 'root', 'lemma']

        attributes = morph_attributes
        if self.postmorph_rewriter:
            attributes = attributes + ['word_normal']
            morph = Layer(name='words',
              parent='words',
              ambiguous=True,
              attributes=attributes
              )
        else:
            morph = Layer(name='morf_analysis',
                          parent='words',
                          ambiguous=True,
                          attributes=morph_attributes
                          )

        for word, analyses in zip(text.words, analysis_results):
            for analysis in analyses['analysis']:
                span = morph.add_span(Span(parent=word))
                for attr in morph_attributes:
                    setattr(span, attr, analysis[attr])
                if self.postmorph_rewriter:
                    setattr(span, 'word_normal', analyses['text'])
        #print(morph.parent)
        if self.postmorph_rewriter:
            morph = morph.rewrite(source_attributes=attributes,
                                  target_attributes=morph_attributes, 
                                  rules=self.postmorph_rewriter,
                                  name='morf_analysis',
                                  ambiguous=True)
        #print(morph.parent)

        text['morf_analysis'] = morph

        return text
