import re

from estnltk_core import RelationLayer
from estnltk import Text
from estnltk.visualisation.span_visualiser.named_span_visualisation import DisplayNamedSpans


def _extract_html_content(html_output_str, remove_tags=['script', 'style']):
    # Extracts html body content, leaves out auxiliary content (such as <script>, <style>)
    assert len(remove_tags) > 0
    for tag_name in remove_tags:
        pat = re.compile(f'(<{tag_name}>.+?</{tag_name}>)', re.DOTALL)
        html_output_str = pat.sub('', html_output_str)
    return html_output_str

def test_html_output():
    text = Text('Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges: '+\
    '"Ma ei suutnud seda raamatut kohe kuidagi käest ära panna! Nii põnev oli see!"').tag_layer('words')
    coref_layer = RelationLayer('coreference', span_names=['mention', 'entity'], text_object=text)
    # Add relation based on a dictionary
    coref_layer.add_annotation( {'mention': (30, 32), 'entity': (0, 4)} )
    coref_layer.add_annotation( {'mention': (61, 63), 'entity': (0, 4)} )
    # Add relation by keyword arguments
    coref_layer.add_annotation( mention=(75, 88), entity=(42, 52) )
    coref_layer.add_annotation( mention=(133, 136), entity=(42, 52) )
    
    # Case 1: display just span names
    display_spans = DisplayNamedSpans()
    #print(display_spans(coref_layer))
    #print( _extract_html_content( display_spans.html_output(coref_layer) ) )
    assert _extract_html_content( display_spans.html_output(coref_layer) ) == \
        '<span style="background:#FFCC00;" span_info=Mari,Mari>Mari</span><sup style="font-size:75%">entity, entity</sup> kirjeldas õhinal, kuidas <span style="background:yellow;">ta</span><sup style="font-size:75%">mention</sup> väiksena <span style="background:#FFCC00;" span_info="Sipsikut","Sipsikut">"Sipsikut"</span><sup style="font-size:75%">entity, entity</sup> luges: "<span style="background:yellow;">Ma</span><sup style="font-size:75%">mention</sup> ei suutnud <span style="background:yellow;">seda raamatut</span><sup style="font-size:75%">mention</sup> kohe kuidagi käest ära panna! Nii põnev oli <span style="background:yellow;">see</span><sup style="font-size:75%">mention</sup>!"'
    
    # Case 2: display just span names with relation indexes
    display_spans2 = DisplayNamedSpans(add_relation_ids=True)
    #print(display_spans2(coref_layer))
    #print( _extract_html_content( display_spans2.html_output(coref_layer) ) )
    assert _extract_html_content( display_spans2.html_output(coref_layer) ) == \
        '<span style="background:#FFCC00;" span_info=Mari,Mari>Mari</span><sup style="font-size:75%">entity(0), entity(1)</sup> kirjeldas õhinal, kuidas <span style="background:yellow;">ta</span><sup style="font-size:75%">mention(0)</sup> väiksena <span style="background:#FFCC00;" span_info="Sipsikut","Sipsikut">"Sipsikut"</span><sup style="font-size:75%">entity(2), entity(3)</sup> luges: "<span style="background:yellow;">Ma</span><sup style="font-size:75%">mention(1)</sup> ei suutnud <span style="background:yellow;">seda raamatut</span><sup style="font-size:75%">mention(2)</sup> kohe kuidagi käest ära panna! Nii põnev oli <span style="background:yellow;">see</span><sup style="font-size:75%">mention(3)</sup>!"'
    


