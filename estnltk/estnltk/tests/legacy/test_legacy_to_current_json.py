import json
import os

from estnltk_core.common import CORE_PACKAGE_PATH
from estnltk.legacy.legacy_to_current_json import legacy_to_current_json

def test_legacy_to_current_json():
    input_json = '{"meta": {"year": 2017}, "text": "Ööbik laulab.", "layers": [{"spans": [{"normalized_form": null, "end": 5, "start": 0}, {"normalized_form": null, "end": 12, "start": 6}, {"normalized_form": null, "end": 13, "start": 12}], "parent": null, "_base": "words", "name": "words", "attributes": ["normalized_form"], "ambiguous": false, "enveloping": null}, {"spans": [[{"end": 5, "partofspeech": "S", "root_tokens": ["ööbik"], "root": "ööbik", "form": "sg n", "ending": "0", "_index_": 0, "start": 0, "lemma": "ööbik", "clitic": ""}], [{"end": 12, "partofspeech": "V", "root_tokens": ["laul"], "root": "laul", "form": "b", "ending": "b", "_index_": 1, "start": 6, "lemma": "laulma", "clitic": ""}], [{"end": 13, "partofspeech": "Z", "root_tokens": ["."], "root": ".", "form": "", "ending": "", "_index_": 2, "start": 12, "lemma": ".", "clitic": ""}]], "parent": "words", "_base": "words", "name": "morph_analysis", "attributes": ["lemma", "root", "root_tokens", "ending", "clitic", "form", "partofspeech"], "ambiguous": true, "enveloping": null}, {"spans": [{"_index_": [0, 1, 2]}], "parent": null, "_base": "sentences", "name": "sentences", "attributes": [], "ambiguous": false, "enveloping": "words"}]}'
    expected = '{"meta": {"year": 2017}, "text": "Ööbik laulab.", "layers": [{"meta": {}, "attributes": ["normalized_form"], "secondary_attributes": [], "parent": null, "ambiguous": false, "spans": [{"base_span": [0, 5], "annotations": [{"normalized_form": null}]}, {"base_span": [6, 12], "annotations": [{"normalized_form": null}]}, {"base_span": [12, 13], "annotations": [{"normalized_form": null}]}], "enveloping": null, "serialisation_module": null, "name": "words"}, {"meta": {}, "attributes": ["lemma", "root", "root_tokens", "ending", "clitic", "form", "partofspeech"], "secondary_attributes": [], "parent": "words", "ambiguous": true, "spans": [{"base_span": [0, 5], "annotations": [{"lemma": "ööbik", "ending": "0", "root_tokens": ["ööbik"], "form": "sg n", "partofspeech": "S", "root": "ööbik", "clitic": ""}]}, {"base_span": [6, 12], "annotations": [{"lemma": "laulma", "ending": "b", "root_tokens": ["laul"], "form": "b", "partofspeech": "V", "root": "laul", "clitic": ""}]}, {"base_span": [12, 13], "annotations": [{"lemma": ".", "ending": "", "root_tokens": ["."], "form": "", "partofspeech": "Z", "root": ".", "clitic": ""}]}], "enveloping": null, "serialisation_module": null, "name": "morph_analysis"}, {"meta": {}, "attributes": [], "secondary_attributes": [], "parent": null, "ambiguous": false, "spans": [{"base_span": [[0, 5], [6, 12], [12, 13]], "annotations": [{}]}], "enveloping": "words", "serialisation_module": null, "name": "sentences"}]}'
    legacy_test_input  = os.path.join(CORE_PACKAGE_PATH, 'tests', 'legacy', 'legacy_test_input.json')
    legacy_test_output = os.path.join(CORE_PACKAGE_PATH, 'tests', 'legacy', 'legacy_test_output.json')

    with open(legacy_test_input, 'w', encoding='utf-8') as in_file:
        in_file.write(input_json)

    legacy_to_current_json(input_file=legacy_test_input, output_file=legacy_test_output)

    with open(legacy_test_output, 'r', encoding='utf-8') as out_file:
        result = out_file.read()
        assert json.loads(result) == json.loads(expected)

    os.remove(legacy_test_input)
    os.remove(legacy_test_output)