from typing import Any
from typing import List

import networkx as nx

from estnltk import Span
from estnltk import BaseSpan

from estnltk.taggers.standard.syntax.phrase_extraction.syntax_tree import SyntaxTree
from estnltk.taggers.standard.syntax.syntax_error_count_tagger import by_sentences

import pandas as pd 

def filter_nodes_by_attributes(tree: SyntaxTree, attribute: str, value: Any) -> List[int]:
    """Returns list of nodes in the syntax tree that have the desired attribute value"""
    return [node for node, data in tree.nodes.items() if attribute in data and data[attribute] == value]


def filter_spans_by_attributes(tree: SyntaxTree, attribute: str, value: Any) -> List[Span]:
    """Returns list of spans in the syntax tree that have the desired attribute value"""
    return [data['span'] for node, data in tree.nodes.items() if attribute in data and data[attribute] == value]


def extract_base_spans_of_subtree(tree: SyntaxTree, root: int) -> List[BaseSpan]:
    """Returns base-spans of the entire subtree from left to right in the text."""
    nodes = tree.graph.nodes
    return [nodes[idx]['span'].base_span for idx in sorted(nx.dfs_postorder_nodes(tree.graph, root))]
    
    
def get_graph_edge_difference(stanza_syntax_layer, without_entity_layer, ignore_layer, ignored_tokens):
    big_table = []

    for span in without_entity_layer.spans:  
        old_span = stanza_syntax_layer.get(span)  
        big_table.append((span.text, old_span.id, old_span.deprel, old_span.head, span.id, span.deprel, span.head))
    
    if not ignored_tokens:
        ignored_tokens = [word for span in ignore_layer for word in span.words]
    for span in ignored_tokens:
        old_span = stanza_syntax_layer.get(span) 
        big_table.append((span.text, old_span.id, old_span.deprel, old_span.head, "-", "-", "-"))

    bigdf = pd.DataFrame(big_table, columns=["text", "long_id", "long_deprel", "long_head", "short_id", "short_deprel", "short_head"])
    mapped_heads = []

    for row in bigdf.iterrows():
        if row[1]["short_head"] != "-":
            if row[1]["short_head"]==0:
                mapped_heads.append(0)
            else:
                try:
                    mapped_heads.append(bigdf["long_id"][list((bigdf['short_id'] == row[1]["short_head"])).index(True)])
                except Exception as e:
                    mapped_heads.append("-")
        else:
            mapped_heads.append("-")
    bigdf["mapped_head"] = mapped_heads
    bigdf = bigdf.sort_values("long_id", axis=0, ascending=True)
    bigdf2 = bigdf.drop(["short_id", "short_head"], axis = 1)

    samad = []
    head_samad = []
    deprelid_samad = []

    for row in bigdf2.iterrows():
        if row[1].short_deprel!= "-":
            samad.append(0 if row[1].long_head == row[1].mapped_head and row[1].long_deprel == row[1].short_deprel else 1)    
            head_samad.append(0 if row[1].long_head == row[1].mapped_head else 1)
            deprelid_samad.append(0 if row[1].long_deprel == row[1].short_deprel else 1)

    las = round(samad.count(0)*100/len(samad),1) if len(samad)!=0 else None
    uas = round(head_samad.count(0)*100/len(head_samad),1) if len(head_samad)!=0 else None
    la = round(deprelid_samad.count(0)*100/len(deprelid_samad),1) if len(deprelid_samad)!=0 else None
  
    return las, uas, la
    
    

def get_las_score(layer_orig, layer_short):
    lases = []
    for spans, deprels, LASes, UASes, LAs in by_sentences(layer_orig, layer_short):
        if spans is not None:
            # Labelled Attachment Score (LAS)
            # Unlabelled Attachment Score (UAS)  round(UASes.count(0)*100/len(UASes),1)
            # Label Accuracy (LA)  round(LAs.count(0)*100/len(LAs),1)
            
            return  round(LASes.count(0)*100/len(LASes),1),  round(UASes.count(0)*100/len(UASes),1),  round(LAs.count(0)*100/len(LAs),1)  
        return None, None, None 

