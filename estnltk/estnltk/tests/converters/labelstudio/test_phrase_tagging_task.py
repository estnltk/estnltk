import pytest

from estnltk import Text

from estnltk.common import abs_path
from estnltk.taggers.system.rule_taggers.extraction_rules.ruleset import Ruleset
from estnltk.taggers.system.rule_taggers.extraction_rules.static_extraction_rule import StaticExtractionRule
from estnltk.taggers.system.rule_taggers.taggers.substring_tagger import SubstringTagger

from estnltk.converters import layer_to_dict
from estnltk.converters.label_studio.labelling_configurations import PhraseTaggingConfiguration
from estnltk.converters.label_studio.labelling_tasks.phrase_tagging_task import PhraseTaggingTask

def test_data_export_for_phrase_tagging_task():
    # Create input data
    rules = Ruleset([
        StaticExtractionRule('kass', {'label': 'kass'}),
        StaticExtractionRule('koer', {'label': 'koer'})
    ])
    tagger = SubstringTagger(rules, output_attributes=['label'], ignore_case=True)
    text = Text('Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei tohi olla ilusam kui vana')
    tagger(text)
    
    # Case 1
    conf1 = PhraseTaggingConfiguration(['Koer', 'kass'])
    task1 = PhraseTaggingTask(conf1, input_layer=tagger.output_layer, 
                                     output_layer=tagger.output_layer, 
                                     labelling_function=lambda x: x.text)
    #print(task1.interface_file)
    #print(task1.export_data(text, indent=2, ensure_ascii=False))
    assert task1.interface_file == '''<View>
  <Labels name="terms" toName="text" >
    <Label value="Koer" background="green" />
    <Label value="kass" background="blue" />
  </Labels>
  <Text name="text" value="$text" granularity="word" />
</View>'''
    assert task1.export_data(text, indent=2, ensure_ascii=False) == '''[
  {
    "data": {
      "text": "Koer tuletas omanikule meelde, et uus kass, mille peremees v\u00f5tab, ei tohi olla ilusam kui vana"
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
            "from_name": "terms",
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
            "from_name": "terms",
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
    conf2 = PhraseTaggingConfiguration(['koer', 'kass'])
    task2 = PhraseTaggingTask(conf2, input_layer=tagger.output_layer, 
                                     output_layer=tagger.output_layer, label_attribute='label')
    #print(task2.export_data(text, indent=2))
    assert task2.export_data(text, indent=2, ensure_ascii=False) == '''[
  {
    "data": {
      "text": "Koer tuletas omanikule meelde, et uus kass, mille peremees v\u00f5tab, ei tohi olla ilusam kui vana"
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
            "from_name": "terms",
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
            "from_name": "terms",
            "to_name": "text",
            "type": "labels"
          }
        ]
      }
    ]
  }
]'''
    assert task2.exported_labels == {'koer', 'kass'}



def test_data_import_from_phrase_tagging_task():
    # Case 1
    rules = Ruleset([
        StaticExtractionRule('kass', {'label': 'kass'}),
        StaticExtractionRule('koer', {'label': 'koer'})
    ])
    tagger = SubstringTagger(rules, output_attributes=['label'], ignore_case=True)
    text = Text('Koer tuletas omanikule meelde, et uus kass, mille peremees võtab, ei tohi olla ilusam kui vana')
    tagger(text)
    conf1 = PhraseTaggingConfiguration(['koer', 'kass'])
    task1 = PhraseTaggingTask(conf1, input_layer=tagger.output_layer, 
                                     output_layer=tagger.output_layer, label_attribute='label')
    input_str = task1.export_data(text, indent=2)
    imported_texts = task1.import_data(input_str)
    assert len(imported_texts) == 1
    assert layer_to_dict( imported_texts[0][tagger.output_layer] ) == \
        {'ambiguous': True,
         'attributes': ('label', 'lead_time', 'created_at', 'updated_at'),
         'enveloping': None,
         'meta': {},
         'name': 'terms',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'created_at': None,
                                     'label': 'koer',
                                     'lead_time': None,
                                     'updated_at': None}],
                    'base_span': (0, 4)},
                   {'annotations': [{'created_at': None,
                                     'label': 'kass',
                                     'lead_time': None,
                                     'updated_at': None}],
                    'base_span': (38, 42)}]}
    #from pprint import pprint
    #pprint(layer_to_dict(imported_texts[0][tagger.output_layer]))
    
    # Case 2 & 3
    with open(abs_path('tests/converters/labelstudio/imports/phrase_tagging_input_json_1.json'), 'r') as in_file:
        content = in_file.read()
    #from pprint import pprint
    #pprint( layer_to_dict( task1.import_data(content)[0]['terms'] ) )
    expected_imported_layer_dict = \
        {'ambiguous': True,
         'attributes': ('label', 'lead_time', 'created_at', 'updated_at'),
         'enveloping': None,
         'meta': {},
         'name': 'terms',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'created_at': '2024-04-26T13:02:59.317338Z',
                                     'label': 'Koer',
                                     'lead_time': 19.383000000000003,
                                     'updated_at': '2024-04-29T10:59:32.561256Z'}],
                    'base_span': (0, 4)},
                   {'annotations': [{'created_at': '2024-04-26T13:02:59.317338Z',
                                     'label': 'kass',
                                     'lead_time': 19.383000000000003,
                                     'updated_at': '2024-04-29T10:59:32.561256Z'}],
                    'base_span': (38, 42)},
                   {'annotations': [{'created_at': '2024-04-26T13:02:59.317338Z',
                                     'label': 'Koer',
                                     'lead_time': 19.383000000000003,
                                     'updated_at': '2024-04-29T10:59:32.561256Z'}],
                    'base_span': (50, 58)},
                   {'annotations': [{'created_at': '2024-04-26T13:02:59.317338Z',
                                     'label': 'kass',
                                     'lead_time': 19.383000000000003,
                                     'updated_at': '2024-04-29T10:59:32.561256Z'}],
                    'base_span': (90, 94)}]}
    assert layer_to_dict( task1.import_data(content)[0]['terms'] ) == expected_imported_layer_dict
    with open(abs_path('tests/converters/labelstudio/imports/phrase_tagging_input_json_min_1.json'), 'r') as in_file:
        content = in_file.read()
    assert layer_to_dict( task1.import_data(content, input_type='json-min')[0]['terms'] ) == expected_imported_layer_dict

