from nltk import RegexpTokenizer

from estnltk.text import Layer, SpanList, Text


class ParagraphTokenizer:

    def __init__(self, regex = '\n\n'):
        self.paragraph_tokenizer = RegexpTokenizer(regex, gaps=True, discard_empty=True)

    def tag(self, text: Text) -> Text:
        paragraph_spans = list(self.paragraph_tokenizer.span_tokenize(text.text))
        paragraph_lists = [[] for i in paragraph_spans]

        layer = Layer(name='paragraphs', enveloping = 'sentences', ambiguous=False)

        #Seda saaks teha algoritmiliselt kiiremini.
        for sentence in text.sentences:
            mid = sentence.start + ( sentence.end - sentence.start)//2
            for (s,e), lst in zip(paragraph_spans, paragraph_lists):
                if s <= mid <= e:
                    lst.append(sentence)
                    break
            else:
                raise AssertionError('Iga lause peab olema mõnes lõigus.')

        for i in paragraph_lists:
            spl = SpanList()
            spl.spans = i

            layer.add_span(spl)
        text._add_layer(layer)
        return text


