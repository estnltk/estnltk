import pytest

from estnltk import Text

from estnltk.common import abs_path
from estnltk.taggers.system.rule_taggers.extraction_rules.ruleset import Ruleset
from estnltk.taggers.system.rule_taggers.extraction_rules.static_extraction_rule import StaticExtractionRule
from estnltk.taggers.system.rule_taggers.taggers.substring_tagger import SubstringTagger

from estnltk.converters import layer_to_dict, text_to_dict
from estnltk.converters.label_studio.labelling_configurations import PhraseClassificationConfiguration
from estnltk.converters.label_studio.labelling_tasks import PhraseClassificationTask


def test_data_export_for_phrase_classification_task():
    # Create input data
    rules = Ruleset([
        StaticExtractionRule('kass', {'label': 'kass'}),
        StaticExtractionRule('koer', {'label': 'koer'})
    ])
    tagger = SubstringTagger(rules, output_attributes=['label'], ignore_case=True)
    text = Text('Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei tohi olla ilusam kui vana')
    tagger(text)
    
    # Case 1
    conf1 = PhraseClassificationConfiguration(phrase_labels=['koer', 'kass'], class_labels={'True': 'Jah', 'False': 'Ei'})
    task1 = PhraseClassificationTask(conf1, input_layer=tagger.output_layer, 
                                            output_layer=tagger.output_layer, labelling_function=lambda x: x.text)
    #print(task1.interface_file)
    #print(task1.export_data(text, indent=2, ensure_ascii=False))
    assert task1.interface_file == '''<View>
  <Labels name="phrase" toName="text" >
    <Label value="koer" background="green" />
    <Label value="kass" background="blue" />
  </Labels>
  <Text name="text" value="$text" />
  <Choices name="phrase_class" toName="text" >
    <Choice value="Jah" alias="True" />
    <Choice value="Ei" alias="False" />
  </Choices>
</View>'''
    exported_data_json_str = \
'''[
  {
    "data": {
      "text": "Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei tohi olla ilusam kui vana"
    },
    "annotations": [
      {
        "result": [
          {
            "value": {
              "start": 0,
              "end": 4,
              "labels": [
                "Koer"
              ]
            },
            "from_name": "phrase",
            "to_name": "text",
            "type": "labels"
          },
          {
            "value": {
              "start": 38,
              "end": 42,
              "labels": [
                "kass"
              ]
            },
            "from_name": "phrase",
            "to_name": "text",
            "type": "labels"
          }
        ]
      }
    ]
  }
]'''
    with pytest.warns(UserWarning, match='Unexpected label classes occurred during the export.+'):
        assert task1.export_data(text, indent=2, ensure_ascii=False) == '''[
  {
    "data": {
      "text": "Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei tohi olla ilusam kui vana"
    },
    "annotations": [
      {
        "result": [
          {
            "value": {
              "start": 0,
              "end": 4,
              "labels": [
                "Koer"
              ]
            },
            "from_name": "phrase",
            "to_name": "text",
            "type": "labels"
          },
          {
            "value": {
              "start": 38,
              "end": 42,
              "labels": [
                "kass"
              ]
            },
            "from_name": "phrase",
            "to_name": "text",
            "type": "labels"
          }
        ]
      }
    ]
  }
]'''
    assert task1.exported_labels == {'Koer', 'kass'}

    # Case 2
    conf2 = PhraseClassificationConfiguration(phrase_labels=['koer', 'kass'], class_labels={'True': 'Jah', 'False': 'Ei'})
    task2 = PhraseClassificationTask(conf2, input_layer=tagger.output_layer, 
                                            output_layer=tagger.output_layer, label_attribute='label')
    assert task2.export_data(text, indent=2, ensure_ascii=False) == '''[
  {
    "data": {
      "text": "Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei tohi olla ilusam kui vana"
    },
    "annotations": [
      {
        "result": [
          {
            "value": {
              "start": 0,
              "end": 4,
              "labels": [
                "koer"
              ]
            },
            "from_name": "phrase",
            "to_name": "text",
            "type": "labels"
          },
          {
            "value": {
              "start": 38,
              "end": 42,
              "labels": [
                "kass"
              ]
            },
            "from_name": "phrase",
            "to_name": "text",
            "type": "labels"
          }
        ]
      }
    ]
  }
]'''


def test_data_import_from_phrase_classification_task():
    # Create input data
    rules = Ruleset([
        StaticExtractionRule('kass', {'label': 'kass'}),
        StaticExtractionRule('koer', {'label': 'koer'})
    ])
    tagger = SubstringTagger(rules, output_attributes=['label'], ignore_case=True)
    text = Text('Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei tohi olla ilusam kui vana')
    tagger(text)
    
    # Case 1
    conf1 = PhraseClassificationConfiguration(phrase_labels=['koer', 'kass'], class_labels={'True': 'Jah', 'False': 'Ei'})
    task1 = PhraseClassificationTask(conf1, input_layer=tagger.output_layer, 
                                            output_layer=tagger.output_layer, label_attribute='label')
    exported_data_str = task1.export_data(text, indent=2)
    imported_texts = task1.import_data(exported_data_str)
    assert len(imported_texts) == 1
    #from pprint import pprint
    #pprint(layer_to_dict(imported_texts[0][tagger.output_layer]))
    assert layer_to_dict( imported_texts[0][tagger.output_layer] ) == \
        {'ambiguous': True,
         'attributes': ('label',),
         'enveloping': None,
         'meta': {},
         'name': 'terms',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'label': 'koer'}], 'base_span': (0, 4)},
                   {'annotations': [{'label': 'kass'}], 'base_span': (38, 42)}]}
    
    # Cases 2 & 3
    with open(abs_path('tests/converters/labelstudio/imports/phrase_classification_input_json_1.json'), 'r', encoding='utf-8') as in_file:
        content = in_file.read()
    #from pprint import pprint
    #pprint( text_to_dict( task1.import_data(content)[0] ) )
    assert text_to_dict( task1.import_data(content)[0] ) == \
        {'layers': [{'ambiguous': True,
                     'attributes': ('label',),
                     'enveloping': None,
                     'meta': {},
                     'name': 'terms',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'label': 'koer'}],
                                'base_span': (0, 4)},
                               {'annotations': [{'label': 'kass'}],
                                'base_span': (38, 42)}]}],
         'meta': {'class_label': ['No'],
                  'created_at': '2024-05-17T10:08:53.339812Z',
                  'lead_time': 8.304,
                  'updated_at': '2024-05-17T10:09:04.135250Z'},
         'relation_layers': [],
         'text': 'Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei '
                 'tohi olla ilusam kui vana'}

    with open(abs_path('tests/converters/labelstudio/imports/phrase_classification_input_json_min_1.json'), 'r', encoding='utf-8') as in_file:
        content = in_file.read()
    #from pprint import pprint
    #pprint( text_to_dict( task1.import_data(content, input_type='json-min')[0] ) )
    assert text_to_dict( task1.import_data(content, input_type='json-min')[0] ) == \
         {'layers': [{'ambiguous': True,
                     'attributes': ('label',),
                     'enveloping': None,
                     'meta': {},
                     'name': 'terms',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'label': 'koer'}],
                                'base_span': (0, 4)},
                               {'annotations': [{'label': 'kass'}],
                                'base_span': (38, 42)}]}],
         'meta': {'class_label': 'No',
                  'created_at': '2024-05-17T10:08:53.339812Z',
                  'lead_time': 8.304,
                  'updated_at': '2024-05-17T10:09:04.135250Z'},
         'relation_layers': [],
         'text': 'Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei '
                 'tohi olla ilusam kui vana'}

