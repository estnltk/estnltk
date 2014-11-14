from itertools import izip
from estner import settings
import time
import operator
import codecs
import os
import re
from xml.dom import Node
from xml.dom import minidom
from string import Template

import pycrfsuite

from estner.featureextraction import FeatureExtractor
from estner import nlputil




class XmlTagger(object):
    PAT_EMAIL = re.compile(r'\b(?P<data>[\w\.-]+\s?@\s?[\w\.-]+)\b')
    PAT_SSN = re.compile(r'(?:\D|^)(?P<data>[1-6]\d{2}[0-1]\d[0-3][0-9]{5})(?:\D|$)')
    PAT_MOBILE = re.compile('(?:\W|^)(?P<data>(?:\+372)?(?:5|81|82)\d{6,7})(?:\W|^)')
    PAT_LANDLINE = [
        re.compile('(?:\W|^)(?P<data>(?:32|33|35|38|39|43|44|45|46|47|48|76|77|78|79)\d{5})(?:\W|^)'),  # landline
        re.compile('(?:\W|^)(?P<data>(?:6|7)\d{6})(?:\W|^)'), # landline harjumma, tallinn
        ]
    
    def __init__(self, model_file, do_anonymise, min_text_length):
        self.do_anonymise = do_anonymise
        self.min_text_length = min_text_length
        self.fex = FeatureExtractor(settings.FEATURE_EXTRACTORS, settings.TEMPLATES, settings.PATH)
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(model_file)
    
    def extract_entities(self, doc, text):
        nes = []
        nes.extend(self.extract_landline(text))
        nes.extend(self.extract_mobile(text))
        nes.extend(self.extract_ssn(text))
        nes.extend(self.extract_email(text))
        nes.extend(self.extract_person_names(doc))
        nes.sort(key=lambda x: x[1])
        
        if nes:
            nonoverlapping_nes = [nes[0]]
            for i in xrange(1, len(nes)):
                if nes[i][1] > nes[i-1][2]:
                    nonoverlapping_nes.append(nes[i])
            nes = nonoverlapping_nes
        
        return nes
    
    def extract_person_names(self, doc):
        self.fex.process([doc])
        for snt in doc.snts:
            xseq = [t.feature_list() for t in snt]
            ys = self.tagger.tag(xseq)
            for token, y in izip(snt, ys):
                token.predicted_label = y
        
        nes = []
        for snt in doc.snts:
            for i, t in enumerate(snt):
                if t.predicted_label != 'O':
                    if i > 0 and t.predicted_label[2:] == snt[i-1].predicted_label[2:]:
                        nes[-1][0] += " %s" % t.word
                        nes[-1][2] = t.end_pos
                    else:
                        nes.append([t.word, t.start_pos, t.end_pos, "name"])
        return nes
    
    def extract_landline(self, text):
        return self.extract_nes_reg_exp(text, XmlTagger.PAT_LANDLINE, "landline")
    
    def extract_mobile(self, text):
        return self.extract_nes_reg_exp(text, [XmlTagger.PAT_MOBILE], "mobile")
    
    def extract_ssn(self, text):
        return self.extract_nes_reg_exp(text, [XmlTagger.PAT_SSN], "ssn")
    
    def extract_email(self, text):
        return self.extract_nes_reg_exp(text, [XmlTagger.PAT_EMAIL], "email")
    
    def extract_nes_reg_exp(self, text, patterns, category):
        return [(m.group('data'), m.start('data'), m.end('data'), category) 
                for pat in patterns for m in pat.finditer(text)]
                
    def process_xml_document(self, xmldoc):
        root_node = xmldoc.documentElement
        self.nes = []
        self.traverse(root_node)
        return xmldoc, self.nes
    
    def process_text_node(self, node):
        text = node.nodeValue.strip()
        if len(text) < self.min_text_length:
            return
        doc = nlputil.lemmatise(text)
        nlputil.set_token_positions(doc.tokens, text)
        nes = self.extract_entities(doc, text)
        if self.do_anonymise:
            self.anonimise_text_node(node, text, nes, len(self.nes))
        else:
            self.annotate_text_node(node, text, nes, len(self.nes))
        self.nes.extend(nes)
    
    def anonimise_text_node(self, node, node_text, nes, id_offset):
        template = Template('${head} <ANONYM id="${iid}" type="${category}"/> ${tail}')
        iids = range(id_offset, id_offset + len(nes))
        for (word, start, end, category), iid in reversed(zip(nes, iids)):
            if len(word) > 2:
                node_text = template.substitute(head=node_text[:start], 
                                           iid=iid,
                                           category=category,
                                           tail=node_text[end:])
        node.replaceWholeText(node_text)
        
    def annotate_text_node(self, node, node_text, nes, id_offset):
        template = Template('${head} <ANONYM id="${iid}" type="${category}">${entity}</ANONYM> ${tail}')
        iids = range(id_offset, id_offset + len(nes))
        for (word, start, end, category), iid in reversed(zip(nes, iids)):
            if len(word) > 2:
                node_text = template.substitute(head=node_text[:start], 
                                           iid=iid,
                                           category=category,
                                           entity=word,
                                           tail=node_text[end:])
        node.replaceWholeText(node_text)
    
    def traverse(self, node):
        if node.nodeType == Node.ELEMENT_NODE: 
            for child in node.childNodes:
                self.traverse(child)
        elif node.nodeType == Node.TEXT_NODE:
            self.process_text_node(node)


def setup_settings(custom_settings_module_name):
    custom_settings = _get_modul_from_str(custom_settings_module_name)
    for prop, value in custom_settings.__dict__.iteritems():
        if not prop.startswith('__'):
            setattr(settings, prop, value)
    print "Settings:"
    for prop, value in settings.__dict__.iteritems():
        if not prop.startswith('__'):
            print "%s: %s" % (prop, value)
    print 'GAZETEER FILE: ', settings.GAZETEER_FILE


def traverse_xmlnode(node, process_text_node_callback):
    if node.nodeType == Node.ELEMENT_NODE: 
        for child in node.childNodes:
            traverse_xmlnode(child, process_text_node_callback)
    elif node.nodeType == Node.TEXT_NODE:
        process_text_node_callback(node.nodeValue)

def _get_modul_from_str(modulstr):
    m = __import__(modulstr, fromlist=['blah'])
    return m
