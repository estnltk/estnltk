from estnltk.text import Span, Layer, Text
from estnltk.taggers import Tagger
from estnltk.vabamorf.morf import Vabamorf

from estnltk.rewriting.postmorph.vabamorf_corrector import VabamorfCorrectionRewriter

class VabamorfTagger(Tagger):
    description = 'Tags morphological analysis on words.'
    layer_name = None
    attributes = ('lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech')
    depends_on = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis',
                 postmorph_rewriter=VabamorfCorrectionRewriter(),
                 **kwargs):
        self.kwargs = kwargs
        self.instance = Vabamorf.instance()

        self.layer_name = layer_name
        self.postmorph_rewriter = postmorph_rewriter

        self.configuration = {'postmorph_rewriter':self.postmorph_rewriter.__class__.__name__}
        self.configuration.update(self.kwargs)

        self.depends_on = ['words']

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
        result = []
        for word in text.words:
            if hasattr(word, 'normalized_form') and word.normalized_form != None:
                # If there is a normalized version of the word, add it
                # instead of word's text
                result.append(word.normalized_form)
            else:
                result.append(word.text)
        return result


    def tag(self, text: Text, return_layer=False) -> Text:
        wordlist = self._get_wordlist(text)
        analysis_results = self.instance.analyze(words=wordlist, **self.kwargs)

        morph_attributes = self.attributes

        attributes = morph_attributes
        if self.postmorph_rewriter:
            attributes = attributes + ('word_normal',)
            morph = Layer(name='words',
              parent='words',
              ambiguous=True,
              attributes=attributes
              )
        else:
            morph = Layer(name=self.layer_name,
                          parent='words',
                          ambiguous=True,
                          attributes=morph_attributes
                          )

        for word, analyses in zip(text.words, analysis_results):
            for analysis in analyses['analysis']:
                span = morph.add_span(Span(parent=word))
                for attr in morph_attributes:
                    if attr == 'root_tokens':
                        # make it hashable for Span.__hash__
                        setattr(span, attr, tuple(analysis[attr]))
                    else:
                        setattr(span, attr, analysis[attr])
                if self.postmorph_rewriter:
                    setattr(span, 'word_normal', analyses['text'])
        if self.postmorph_rewriter:
            morph = morph.rewrite(source_attributes=attributes,
                                  target_attributes=morph_attributes, 
                                  rules=self.postmorph_rewriter,
                                  name=self.layer_name,
                                  ambiguous=True)
        if return_layer:
            return morph
        text[self.layer_name] = morph
        return text
