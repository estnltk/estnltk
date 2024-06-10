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

def test_html_output_empty_layer():
    text = Text('Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges.')
    coref_layer = RelationLayer('coreference', span_names=['mention', 'entity'], text_object=text)
    display_spans = DisplayNamedSpans()
    #print( _extract_html_content( display_spans.html_output(coref_layer) ) )
    assert _extract_html_content( display_spans.html_output(coref_layer) ) == \
        'Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges.'

def test_html_output():
    text = Text('Mari kirjeldas õhinal, kuidas ta väiksena "Sipsikut" luges: '+\
    '"Ma ei suutnud seda raamatut kohe kuidagi käest ära panna! Nii põnev oli see!"')
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
        '<ruby><span style="background:#FFCC00;" span_info=Mari,Mari>Mari</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">entity, entity</rt><rp></sup></rp></ruby> kirjeldas õhinal, kuidas <ruby><span style="background:yellow;">ta</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention</rt><rp></sup></rp></ruby> väiksena <ruby><span style="background:#FFCC00;" span_info="Sipsikut","Sipsikut">"Sipsikut"</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">entity, entity</rt><rp></sup></rp></ruby> luges: "<ruby><span style="background:yellow;">Ma</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention</rt><rp></sup></rp></ruby> ei suutnud <ruby><span style="background:yellow;">seda raamatut</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention</rt><rp></sup></rp></ruby> kohe kuidagi käest ära panna! Nii põnev oli <ruby><span style="background:yellow;">see</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention</rt><rp></sup></rp></ruby>!"'
    
    # Case 2: display just span names with relation indexes
    display_spans2 = DisplayNamedSpans(add_relation_ids=True)
    #print(display_spans2(coref_layer))
    #print( _extract_html_content( display_spans2.html_output(coref_layer) ) )
    assert _extract_html_content( display_spans2.html_output(coref_layer) ) == \
        '<ruby><span style="background:#FFCC00;" span_info=Mari,Mari>Mari</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">entity(0), entity(1)</rt><rp></sup></rp></ruby> kirjeldas õhinal, kuidas <ruby><span style="background:yellow;">ta</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention(0)</rt><rp></sup></rp></ruby> väiksena <ruby><span style="background:#FFCC00;" span_info="Sipsikut","Sipsikut">"Sipsikut"</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">entity(2), entity(3)</rt><rp></sup></rp></ruby> luges: "<ruby><span style="background:yellow;">Ma</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention(1)</rt><rp></sup></rp></ruby> ei suutnud <ruby><span style="background:yellow;">seda raamatut</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention(2)</rt><rp></sup></rp></ruby> kohe kuidagi käest ära panna! Nii põnev oli <ruby><span style="background:yellow;">see</span><rp><sup style="font-size:75%"></rp><rt style="font-size:75%">mention(3)</rt><rp></sup></rp></ruby>!"'
    


