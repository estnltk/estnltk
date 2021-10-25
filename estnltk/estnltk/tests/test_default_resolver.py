from estnltk.resolve_layer_dag import make_resolver
from estnltk import Text

def test_simple_resolver_update():
    # Example: Modifying the pipeline -- replacing an existing tagger
    my_resolver = make_resolver()  # Create a copy of the default pipeline

    # Create a new sentence tokenizer that does not split sentences by emoticons
    from estnltk.taggers import SentenceTokenizer
    new_sentence_tokenizer = SentenceTokenizer(use_emoticons_as_endings=False)

    # Replace the sentence tokenizer on the pipeline with the new one
    my_resolver.update( new_sentence_tokenizer )

    # Test out the new tokenizer
    t = Text('No mida teksti :) Äge!')
    t.analyse('segmentation', resolver=my_resolver)  # Use new resolver instead of the default one
    assert t.sentences.text == ['No', 'mida', 'teksti', ':)', 'Äge', '!']
