from estnltk import Text
from estnltk.taggers import ParagraphTokenizer

def test_apply_paragraph_tokenizer_on_empty_text():
    # Applying paragraph tokenizer on empty text should not produce any errors
    text = Text( '' )
    text.tag_layer(['words', 'sentences', 'paragraphs'])
    assert len(text.words) == 0
    assert len(text.sentences) == 0
    assert len(text.paragraphs) == 0