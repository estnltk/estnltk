from nltk.tokenize.api import StringTokenizer
from estnltk.text import Text, Layer

class SentenceTokenizer( StringTokenizer ):
    sentence_tokenizer = None

    def __init__(self):
        # use NLTK-s sentence tokenizer for Estonian, in case it is not downloaded, try to download it first
        import nltk.data
        try:
            self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
        except LookupError:
            import nltk.downloader
            nltk.downloader.download('punkt')
        finally:
            if self.sentence_tokenizer is None:
                self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')


    def tag(self, text: Text) -> Text:
        # Apply sentence tokenization paragraph by paragraph
        if 'paragraphs' not in text.layers:
            raise Exception('(!) Missing "paragraphs" layer!'+\
                            ' Paragraph tokenization should be performed before sentence tokenization!')
        sentence_spans = []
        for paragraph in text['paragraphs']:
            spans = self.sentence_tokenizer.span_tokenize(paragraph.text)
            paragraph_start = paragraph.start
            # Recalculate indices of the spans based on the paragraph beginning
            spans = [ (paragraph_start+start, paragraph_start+end) for start, end in spans ]
            sentence_spans.extend( spans )
        # Create a new layer
        sentences = Layer(name='sentences').from_records([{
                                            'start': start,
                                              'end': end
                                                          } for start, end in sentence_spans], rewriting=True)
        text['sentences'] = sentences
        return text
