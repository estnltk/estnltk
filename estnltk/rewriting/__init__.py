from .rewriting import Rewriter, RegexRewriter
__all__ = [Rewriter, RegexRewriter]

from estnltk.text import *
text = words_sentences('''
Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.
Seni vaid soome keelde tõlgitud teos ilmus äsja ka itaalia keeles
ning seda esitleti Rooma reisikirjanduse festivalil.
Tuntud reisikrijanduse festival valis tänavu peakülaliseks Eesti,
Ultima Thule ning Iidse-Põhjala ja Vahemere endisaegsed kultuurikontaktid j
ust seetõttu, et eelmisel nädalal avaldas kirjastus Gangemi "Hõbevalge"
itaalia keeles, vahendas "Aktuaalne kaamera".''')


import regex as re

class Rule:
    def match(self, span, **kwargs):
        #return falsy if no match
        #return context_dict if match
        return {}

    def rewrite(self, span, context):
        pass

class Ruleset:
    def __init__(self, rules):
        self.rules = rules

    def match_and_rewrite(self, span, **kwargs):
        for rule in self.rules:
            context = rule.match(span)
            if context:
                rule.rewrite(span, context)

class RegexRule(Rule):
    def __init__(self, source_attribute_name, target_layer, target_attribute_name, needle, target,
                 match_kwargs=None,
                 rewrite_kwargs=None
                 ):
        self.target_layer = None
        self.rewrite_kwargs = rewrite_kwargs
        self.match_kwargs = match_kwargs
        self.target = target
        self.needle = needle
        self.target_attribute_name = target_attribute_name
        self.source_attribute_name = source_attribute_name

    def match(self, span, **kwargs):
        return re.findall(self.needle, getattr(span, self.source_attribute_name), **self.match_kwargs)

rules = [
      ["…$",      "Ell"],
      ["\.\.\.$", "Ell"],
      ["\.\.$",   "Els"],
      ["\.$",     "Fst"],
      [",$",      "Com"],
      [":$",      "Col"],
      [";$",      "Scl"],
      ["(\?+)$",  "Int"],
      ["(\!+)$",  "Exc"],
      ["(---?)$", "Dsd"],
      ["(-)$",    "Dsh"],
      ["\($",     "Opr"],
      ["\)$",     "Cpr"],
      ['\\\\"$',  "Quo"],
      ["«$",      "Oqu"],
      ["»$",      "Cqu"],
      ["“$",      "Oqu"],
      ["”$",      "Cqu"],
      ["<$",      "Grt"],
      [">$",      "Sml"],
      ["\[$",     "Osq"],
      ["\]$",     "Csq"],
      ["/$",      "Sla"],
      ["\+$",     "crd"]
]

com_type = Layer(
    name = 'com_type',
    parent = 'morf_analysis',
    attributes = ['main'],
    ambiguous = True
)

text._add_layer(com_type)
def rewrite(source_layer, src_attrs, target_layer, target_attr, rules):
    assert target_layer.layer.parent == source_layer.layer.name
    for i in src_attrs:
        assert i in source_layer.layer.attributes, '{attr} is not an attribute of layer {layer}'.format(
            attr = i,
            layer = source_layer.layer.name
        )
    assert target_attr in target_layer.layer.attributes
    assert len(src_attrs) >= 1


    if len(src_attrs) == 1:
        # there is a single source attribute
        attr = src_attrs[0]
        for rule, target in rules:
            for item in source_layer:
                if isinstance(item, SpanList):
                    for itm in item.spans:
                        x = getattr(item, attr)
                        if re.findall(rule, x[0]):
                            itm.mark(target_layer.layer.name).__setattr__(target_attr, target)
                elif isinstance(itm, Span):
                    if re.findall(rule, x[0]):
                        item.mark(target_layer.layer.name).__setattr__(target_attr, target)


rewrite(source_layer=text.morf_analysis,
        src_attrs=['lemma'],
        target_layer = text.com_type,
        target_attr='main',
        rules=rules)

for i in text.com_type:
    print(i, i.parent.lemma, i.start, i.end)