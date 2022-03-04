from estnltk_core.taggers import Tagger, Retagger
from estnltk.default_resolver import make_resolver
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
    t.tag_layer('sentences', resolver=my_resolver)  # Use new resolver instead of the default one
    assert t.sentences.text == ['No', 'mida', 'teksti', ':)', 'Äge', '!']


def test_loading_and_applying_all_taggers_of_default_resolver():
    # Create a copy of the default pipeline
    my_resolver = make_resolver()
    # 1: Test that all taggers of the default resolver can be loaded 
    for layer_name in my_resolver.layers:
        # Test that the tagger can be loaded
        try:
            tagger = my_resolver.get_tagger(layer_name)
        except Exception as ex:
            raise Exception( 'Cannot load tagger for layer {!r}'.format(layer_name) ) from ex
        assert isinstance(tagger, Tagger)
        assert tagger.output_layer == layer_name
        # Test that retaggers can be loaded
        # (if no retaggers available, returns [])
        try:
            retaggers = my_resolver.get_retaggers(layer_name)
        except Exception as ex:
            raise Exception( 'Cannot load retaggers for layer {!r}'.format(layer_name) ) from ex
        assert isinstance(retaggers, list)
        assert all([isinstance(retagger, Retagger) for retagger in retaggers])
        assert all([retagger.output_layer == layer_name for retagger in retaggers])

    # 2: Test that all taggers of the default resolver can be applied
    test_text = Text('tere')
    for layer_name in my_resolver.layers:
        try:
            my_resolver.apply( test_text, layer_name )
        except Exception as ex:
            raise Exception( 'Cannot create layer {!r}'.format(layer_name) ) from ex
        # check that the layer has been created
        assert layer_name in test_text.layers
