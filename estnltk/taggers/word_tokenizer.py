from math import inf
from estnltk.taggers.legacy_tokenizers import EstWordTokenizer
from estnltk.text import Layer


class WordTokenizer:
    Tokenizer = EstWordTokenizer()

    def tag(self, text: 'Text') -> 'Text':        
        spans = self.Tokenizer.span_tokenize(text.text)
        words = Layer(name='words').from_records([{
                                                   'start': start,
                                                   'end': end
                                                  } for start, end in spans], rewriting=True)
        if 'tokenization_hints' in text.layers:
            hints = text.tokenization_hints.to_record()
            # word_spans = words.to_record() ei tööta kahjuks
            word_spans = [{'start': w.start, 'end': w.end} for w in words]
            records = self._merge_overwrite(hints, word_spans)
            words = Layer(name='words').from_records(records, rewriting=True)

        text['words'] = words

        return text

    def _spans_in_next_gap(self, spans, start, end):
        """To fill the next gap efficiently, remembers the index of the last word used."""
        if start >= end:
            return
        for i in range(self._last_word, len(spans)):
            span = spans[i]
            if span['start'] >= end:
                break
            elif span['end'] > start:
                yield {'start': max(span['start'], start), 'end': min(span['end'], end)}
        self._last_word = max(i - 1, self._last_word)
    
    def _merge_overwrite(self, hints, spans):
        self._last_word = 0
        result = []
        start = 0
        for hint in hints:
            result.extend(self._spans_in_next_gap(spans, start, hint['start']))
            result.append(hint)
            start = hint['end']
        result.extend(self._spans_in_next_gap(spans, start, inf))
        return result
