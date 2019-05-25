from estnltk.text import Text
from estnltk.taggers.morph_analysis.vm_corpus_tagger import VabamorfCorpusTagger


def test_vm_corpus_tagger_input_structures():
    import pytest
    #
    #  Tests the vm_corpus_tagger works on different input structures
    #
    vm_corpus_tagger = VabamorfCorpusTagger()
    #
    #   TestCase X : an empty list
    #
    docsy = []
    vm_corpus_tagger.tag( docsy )
    #
    #   TestCase Y : a Text as input gives AssertionError
    #        ( a collection of Text-s is required )
    #
    # Giving Text as an input gives AssertionError: 
    #   a list of Texts is expected
    text = Text('Tahtis kulda. Aga sai kasside kulla.')
    with pytest.raises(AssertionError) as e1:
        vm_corpus_tagger.tag( text )
    #
    #   TestCase Z : if some of the required 
    #       layers are missing raises Exception
    #
    text = Text('Tahtis kulda. Aga sai kasside kulla.')
    with pytest.raises(Exception) as ex1:
        vm_corpus_tagger.tag( [text] )


# TODO: add more tests
