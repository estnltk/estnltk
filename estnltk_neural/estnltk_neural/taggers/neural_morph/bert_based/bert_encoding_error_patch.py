
## The code in collect_and_add_missing_spans() is added to BertMorphTagger's _make_layer function to resolve issues with tokenizing texts that contain special symbols ("�").

## This code alone is not currently working and is not importable, since it might require modifications depending on the tagger.
## It is intended as an example solution.

from estnltk import Span, Layer, Text


def collect_and_add_missing_spans(morph_layer:Layer, sent_chunk:str, layers:MutableMapping[str, Layer], words_layer:str, split_pos_form:bool):
	# collecting spans with encoding problems
	probably_missing_spans = []
	if "�" in sent_chunk:
		#print("� is in the sentence. Collecting all the spans where that symbol appears.")
		for sp ,span in enumerate(layers[words_layer]):
			if "�" in span.text:
				probably_missing_spans.append((span.base_span.start, span.base_span.end))
	#print(probably_missing_spans)

	# this is for spans with encoding problem: add the spans with None attributes
	for span in probably_missing_spans:
		if split_pos_form:
			annotation2 = {
							'bert_tokens': None,
							'form': "",
							'partofspeech': "",
							'probability': None
			}
		else:
			annotation2 = {
				'bert_tokens': None,
				'morph_label': "",
				'probability': None
			}
		morph_layer.add_annotation(span, **annotation2)

	return morph_layer  #, probably_missing_spans






