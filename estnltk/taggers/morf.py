from estnltk.text import Text, Layer
from estnltk.vabamorf.morf import Vabamorf

from estnltk.rewriting.postmorph.vabamorf_corrector import NumericAnalysis

class VabamorfTagger:
    def __init__(self, premorf_layer: str = None, **kwargs):
        self.kwargs = kwargs
        self.instance = Vabamorf.instance()

        self.premorf_layer = premorf_layer
        
        self.numeric_analysis = NumericAnalysis()

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

        morf_attributes = ['form', 'root_tokens', 'clitic', 'partofspeech', 'ending', 'root', 'lemma']

        dep = Layer(name='morf_analysis',
                    parent='words',
                    ambiguous=True,
                    attributes=morf_attributes
                    )
        text._add_layer(dep)

        for word, analysises in zip(text.words, analysis_results):
            
            if not word.text.isalpha():
                nm = self.numeric_analysis.analyze_number(word.text)
                if nm:
                    analysises['analysis'] = nm

            for analysis in analysises['analysis']:
                m = word.mark('morf_analysis')

                for attr in morf_attributes:
                    setattr(m, attr, analysis[attr])

        return text

