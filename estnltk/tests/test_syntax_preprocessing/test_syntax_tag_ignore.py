""" Test detecting parts of text that should be ignored by the syntactic analyser;
"""

from estnltk.text import Text
from estnltk.taggers.syntax_preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger

def test_ignore_content_in_parenthesis():
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    test_texts = [ 
        { 'text': 'Eesti judokate võistlus jäi laupäeval lühikeseks , nii Joel Rothberg ( -66 kg ) kui ka Renee Villemson ( -73 kg ) võidurõõmu maitsta ei saanud .', \
          'expected_ignore_texts': ['( -66 kg )', '( -73 kg )'] }, \
        { 'text': 'Vladimir Grill ( M 66 kg ) , Joel Rothberg ( M 73 kg ) , Rasmus Toompere ( M 81 kg ) ja Sander Maripuu ( M 90 kg ).', \
          'expected_ignore_texts': ['( M 66 kg )', '( M 73 kg )', '( M 81 kg )', '( M 90 kg )'] }, \
        { 'text': 'B-grupi MM-il kaotas Eesti teisipäeval Kasahstanile 3 : 8 ( 0 : 1 , 1 : 1 , 2 : 5 ) .', \
          'expected_ignore_texts': ['( 0 : 1 , 1 : 1 , 2 : 5 )'] }, \
        { 'text': 'Meeste meistriliiga eilsed tulemused : Rivaal - Pärnu 1 : 3 ( 21 , -14 , -21 , -12 ) , Audentes - Volle 3 : 1 ( 15 , -25 , 17 , 22 ) .', \
          'expected_ignore_texts': ['( 21 , -14 , -21 , -12 )', '( 15 , -25 , 17 , 22 )'] }, \
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [sentence.enclosing_text for sentence in text['syntax_ignore'].spans]
        print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']


    