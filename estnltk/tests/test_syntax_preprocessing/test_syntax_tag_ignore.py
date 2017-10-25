""" Test detecting parts of text that should be ignored by the syntactic analyser;
"""

from estnltk.text import Text
from estnltk.taggers.syntax_preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger

def test_ignore_content_in_parenthesis():
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    test_texts = [ 
        # Pattern: parenthesis_1to3
        { 'text': 'Eesti judokate võistlus jäi laupäeval lühikeseks , nii Joel Rothberg ( -66 kg ) kui ka Renee Villemson ( -73 kg ) võidurõõmu maitsta ei saanud .', \
          'expected_ignore_texts': ['( -66 kg )', '( -73 kg )'] }, \
        { 'text': 'Vladimir Grill ( M 66 kg ) , Joel Rothberg ( M 73 kg ) , Rasmus Toompere ( M 81 kg ) ja Sander Maripuu ( M 90 kg ).', \
          'expected_ignore_texts': ['( M 66 kg )', '( M 73 kg )', '( M 81 kg )', '( M 90 kg )'] }, \
        { 'text': 'B-grupi MM-il kaotas Eesti teisipäeval Kasahstanile 3 : 8 ( 0 : 1 , 1 : 1 , 2 : 5 ) .', \
          'expected_ignore_texts': ['( 0 : 1 , 1 : 1 , 2 : 5 )'] }, \
        { 'text': 'Meeste meistriliiga eilsed tulemused : Rivaal - Pärnu 1 : 3 ( 21 , -14 , -21 , -12 ) , Audentes - Volle 3 : 1 ( 15 , -25 , 17 , 22 ) .', \
          'expected_ignore_texts': ['( 21 , -14 , -21 , -12 )', '( 15 , -25 , 17 , 22 )'] }, \
        { 'text': 'Suursoosikutele järgnevad AC Milan ( 7 : 1 ) , Manchester United ( 8 : 1 ) , Londoni Arsenal ja Müncheni Bayern ( 9 : 1 ) ning Torino Juventus ( 10 : 1 ) .', \
          'expected_ignore_texts': ['( 7 : 1 )', '( 8 : 1 )', '( 9 : 1 )', '( 10 : 1 )'] }, \
        # Pattern: parenthesis_title_words
        { 'text': 'Neidude 5 km klassikat võitis Lina Andersson ( Rootsi ) Pirjo Mannineni ( Soome ) ja Karin Holmbergi ( Rootsi ) ees .', \
          'expected_ignore_texts': ['( Rootsi )', '( Soome )', '( Rootsi )'] }, \
        # Pattern: parenthesis_ordinal_numbers
        { 'text': 'Naiste turniirid toimuvad Jakartas ja Budapestis ( 26. aprillini ) .', \
          'expected_ignore_texts': ['( 26. aprillini )'] }, \
        { 'text': '1930ndate algul avaldati romaani uus väljaanne ( 4. trükk ) KT XVI ande teise trüki kujul .', \
          'expected_ignore_texts': ['( 4. trükk )'] }, \
        # Pattern: brackets
        { 'text': 'Nurksulgudes tuuakse materjali viitekirje järjekorranumber kirjanduse loetelus ja leheküljed , nt [9: 5] või [9 lk 5], aga internetimaterjalil lihtsalt viitekirje, nt [7]', \
          'expected_ignore_texts': ['[9: 5]', '[9 lk 5]', '[7]'] }, \
        { 'text': 'Lepitav , harmooniat taaskinnitav finaal kutsub esile katarsise [Hegel1976:548-551].', \
          'expected_ignore_texts': ['[Hegel1976:548-551]'] }, \
        # Negative: do not extract <ignore> content inside email address
        { 'text': 'saada meil meie klubi esimehele xxxtonisxxx[at]gmail.com', \
          'expected_ignore_texts': [] }, \
        
    ]
    for test_text in test_texts:
        text = Text( test_text['text'] )
        # Perform analysis
        text.tag_layer(['words', 'sentences'])
        syntax_ignore_tagger.tag( text )
        # Collect results 
        ignored_texts = \
            [sentence.enclosing_text for sentence in text['syntax_ignore'].spans]
        #print(ignored_texts)
        # Check results
        assert ignored_texts == test_text['expected_ignore_texts']


    