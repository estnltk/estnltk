import pytest

from estnltk.converters.label_studio.labelling_configurations import PhraseTaggingConfiguration
from estnltk.converters.label_studio.labelling_configurations import PhraseClassificationConfiguration

def test_phrase_tagging_configuration():

    conf1 = PhraseTaggingConfiguration(['a', 'b', 'c'])
    expected_output_str1 = '''<View>
  <Labels name="phrase" toName="text" >
    <Label value="a" background="#1b9e77" />
    <Label value="b" background="#d95f02" />
    <Label value="c" background="#7570b3" />
  </Labels>
  <Text name="text" value="$text" granularity="word" />
</View>'''
    #print( str(conf1) )
    assert str(conf1) == expected_output_str1

    conf2 = PhraseTaggingConfiguration( list(range(11)), rand_seed=1 )
    expected_output_str2 = '''<View>
  <Labels name="phrase" toName="text" >
    <Label value="0" background="#44CB63" />
    <Label value="1" background="#204F89" />
    <Label value="2" background="#829868" />
    <Label value="3" background="#3C5FD7" />
    <Label value="4" background="#FDA9AA" />
    <Label value="5" background="#E623B1" />
    <Label value="6" background="#F1CA20" />
    <Label value="7" background="#C25CED" />
    <Label value="8" background="#6B7F32" />
    <Label value="9" background="#300E5D" />
    <Label value="10" background="#F9C859" />
  </Labels>
  <Text name="text" value="$text" granularity="word" />
</View>'''
    #print( str(conf2) )
    assert str(conf2) == expected_output_str2

    conf3 = PhraseTaggingConfiguration({'a': '#27E31D', 'b':'#E09C18'}, header='header text')
    conf3.hotkeys = {'a': 'a', 'b': 'b'}
    conf3.aliases = {'a': 'first', 'b': 'second'}
    expected_output_str3 = '''<View>
  <Header value="header text" />
  <Labels name="phrase" toName="text" >
    <Label value="a" background="#27E31D" hotkey="a" alias="first" />
    <Label value="b" background="#E09C18" hotkey="b" alias="second" />
  </Labels>
  <Text name="text" value="$text" granularity="word" />
</View>'''
    #print(str(conf3))
    assert str(conf3) == expected_output_str3



def test_phrase_classification_configuration():
    conf1 = PhraseClassificationConfiguration(['span'], {'True': 'Jah', 'False': 'Ei-Ei', 'na': 'Ei tea'}, 
                                              header='header text', header_placement='bottom')
    expected_output_str1 = '''<View>
  <Labels name="phrase" toName="text" >
    <Label value="span" background="green" />
  </Labels>
  <Text name="text" value="$text" />
  <Choices name="phrase_class" toName="text" >
    <Choice value="Jah" alias="True" />
    <Choice value="Ei-Ei" alias="False" />
    <Choice value="Ei tea" alias="na" />
  </Choices>
  <Header value="header text" />
</View>'''
    #print(str(conf1))
    assert str(conf1) == expected_output_str1

    conf2 = PhraseClassificationConfiguration(['span'], {'True': 'Jah', 'False': 'Ei-Ei', 'na': 'Ei tea'}, 
                                              header='header text', header_placement='top')
    expected_output_str2 = '''<View>
  <Header value="header text" />  <Labels name="phrase" toName="text" >
    <Label value="span" background="green" />
  </Labels>
  <Text name="text" value="$text" />
  <Choices name="phrase_class" toName="text" >
    <Choice value="Jah" alias="True" />
    <Choice value="Ei-Ei" alias="False" />
    <Choice value="Ei tea" alias="na" />
  </Choices>
</View>'''
    #print(str(conf2))
    assert str(conf2) == expected_output_str2

    conf3 = PhraseClassificationConfiguration(['span'], {'True': 'Jah', 'False': 'Ei-Ei', 'na': 'Ei tea'}, 
                                              header='header text', header_placement='middle')
    expected_output_str3 = '''<View>
  <Labels name="phrase" toName="text" >
    <Label value="span" background="green" />
  </Labels>
  <Text name="text" value="$text" />
  <Header value="header text" />
  <Choices name="phrase_class" toName="text" >
    <Choice value="Jah" alias="True" />
    <Choice value="Ei-Ei" alias="False" />
    <Choice value="Ei tea" alias="na" />
  </Choices>
</View>'''
    #print(str(conf3))
    assert str(conf3) == expected_output_str3

    conf4 = PhraseClassificationConfiguration(['span'], {'True': 'Jah', 'False': 'Ei-Ei', 'NA': 'Ei tea'})
    conf4.hotkeys = {'True': '+', 'False': '-', 'NA': '?'}
    expected_output_str4 = '''<View>
  <Labels name="phrase" toName="text" >
    <Label value="span" background="green" />
  </Labels>
  <Text name="text" value="$text" />
  <Choices name="phrase_class" toName="text" >
    <Choice value="Jah" alias="True" hotkey="+" />
    <Choice value="Ei-Ei" alias="False" hotkey="-" />
    <Choice value="Ei tea" alias="NA" hotkey="?" />
  </Choices>
</View>'''
    #print(str(conf4))
    assert str(conf4) == expected_output_str4

