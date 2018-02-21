#
#   Makes user-specified post-corrections to morphological analyses.
#  Basically, rewrites automatic morphological analyses with user-
#  specified ones.
# 
#  ( work in progress )

import regex as re
import copy
import csv

from estnltk.text import Span, Layer, Text
from estnltk.taggers import Tagger

from estnltk.taggers.morph.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.morph.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morph.morf_common import _get_word_text
from estnltk.taggers.morph.morf_common import _postprocess_root

from estnltk.taggers.morph.morf_common import VABAMORF_POSTAGS
from estnltk.taggers.morph.morf_common import VABAMORF_NOUN_FORMS
from estnltk.taggers.morph.morf_common import VABAMORF_VERB_FORMS



class UserDictTagger(Tagger):
    description   = "Makes user-specified post-corrections to morphological analyses. "+\
                    "This tagger can be applied after text has been morphologically analysed."
    layer_name    = None
    attributes    = ESTNLTK_MORPH_ATTRIBUTES
    depends_on    = None
    configuration = None

    def __init__(self,
                 layer_name='morph_analysis', \
                 ignore_case:bool=False, \
                 validate_vm_categories:bool=True, \
                 autocorrect_root:bool=True ):
        """
        """
        self.layer_name    = layer_name
        self.configuration = {'ignore_case':ignore_case,\
                              'validate_vm_categories': validate_vm_categories,\
                              'autocorrect_root': autocorrect_root }
        self.depends_on    = ['morph_analysis', 'words']
        self._dict         = {}



    def add(self, word, analysis_struct):
        """
            Note: if the user dictionary already contains morphological analysis 
                  for the current word, then it will be overwritten;
        """
        assert isinstance(word, str)
        assert isinstance(analysis_struct, (dict, list))
        # Ignore case (if required)
        if self.configuration['ignore_case']:
            word = word.lower()
        if isinstance(analysis_struct, dict):
            # validate attributes & attribute names
            assert len(analysis_struct.keys()) > 0
            has_any_attrib = \
                any([ attr in analysis_struct for attr in VABAMORF_ATTRIBUTES ])
            assert has_any_attrib, \
                    '(!) Entry '+str(analysis_struct)+' should contain at least one key '+\
                   'from the following: '+str(VABAMORF_ATTRIBUTES)
            # validate category names
            if self.configuration['validate_vm_categories']:
                self.validate_morph_record_for_vm_categories(analysis_struct)
            self._dict[word] = {}
            self._dict[word]['analysis'] = \
                [ copy.deepcopy(analysis_struct) ]
            # Autocorrect root analysis: 
            #    generate cleaned root, root_tokens & lemma
            if self.configuration['autocorrect_root']:
                if 'root' in self._dict[word]['analysis'][0]:
                    assert 'partofspeech' in self._dict[word]['analysis'][0], \
                        "(!) Please provide 'partofspeech' value in "+str(self._dict[word]['analysis'][0])+\
                        " to enable autocorrection of root / lemma."
                    postag = self._dict[word]['analysis'][0]['partofspeech']
                    root   = self._dict[word]['analysis'][0]['root']
                    root, root_tokens, lemma = _postprocess_root( root, postag )
                    self._dict[word]['analysis'][0]['lemma'] = lemma
                    self._dict[word]['analysis'][0]['root_tokens'] = root_tokens
                    self._dict[word]['analysis'][0]['root']  = root
            # Merge analyses: overwrite analysis fields that
            # are present in the dict, but preserve all other
            # fields
            self._dict[word]['merge'] = True
        elif isinstance(analysis_struct, list):
            assert len(analysis_struct) > 0
            # validate that all records are complete and well-formed
            for record in analysis_struct:
                assert isinstance(record, dict)
                # Check that the record has all VM attributes
                # ( a minimum set of attributes )
                missing = []
                for attr in VABAMORF_ATTRIBUTES:
                    if attr not in record:
                        missing.append(attr)
                assert not missing, \
                    '(!) Entry '+str(record)+' misses the following keys: '+str(missing)
                # Validate category names
                if self.configuration['validate_vm_categories']:
                    self.validate_morph_record_for_vm_categories(record)
                # Autocorrect root analysis: 
                #    generate cleaned root, root_tokens & lemma
                if self.configuration['autocorrect_root']:
                    if 'root' in record:
                        assert 'partofspeech' in record, \
                            "(!) Please provide 'partofspeech' value in "+str(record)+\
                            " to enable autocorrection of root / lemma."
                        postag = record['partofspeech']
                        root   = record['root']
                        root, root_tokens, lemma = _postprocess_root( root, postag )
                        record['lemma']       = lemma
                        record['root_tokens'] = root_tokens
                        record['root']        = root
            self._dict[word] = {}
            self._dict[word]['analysis'] = \
                copy.deepcopy(analysis_struct)
            # Overwrite analyses: delete all existing analyses,
            # and add new analyses from the dict
            self._dict[word]['merge'] = False



    def add_words_from_csv_file(self, filename, encoding='utf-8', \
                                dialect='excel-tab', **fmtparams):
        '''
            Note: any words that are already in the user dictionary will be overwritten;
        '''
        collected_analyses = {}
        with open(filename, 'r', newline='', encoding=encoding) as csvfile:
            fle_reader = csv.reader(csvfile, dialect=dialect, **fmtparams)
            header = next(fle_reader)
            # Validate that header specifies all the required attribute names
            missing = []
            for attr in VABAMORF_ATTRIBUTES + ('text',):
                if attr not in header:
                    missing.append(attr)
            assert not missing, \
                '(!) CSV file header misses the following key(s): '+str(missing)
            # Parse csv file
            # Collect and aggregate analyses
            for row in fle_reader:
                assert len(row) == len(header)
                analysis_dict = {}
                word_text = None
                for kid, key in enumerate(header):
                    if key != 'text':
                        analysis_dict[key] = row[kid]
                    else:
                        word_text = row[kid]
                assert word_text, \
                    "'(!) Key 'text' not specified in line: "+str(row)
                # Ignore case (if required)
                if self.configuration['ignore_case']:
                    word_text = word_text.lower()
                # Add new analysis to the dict
                if word_text not in collected_analyses:
                    collected_analyses[word_text] = []
                collected_analyses[word_text].append(analysis_dict)
                #print(', '.join(row))
        # Rewrite all analyses into the user dict
        for word in collected_analyses.keys():
            self.add( word, collected_analyses[word] )



    def tag(self, text: Text, return_layer=False) -> Text:
        """
        """
        # Take attributes from the input layer
        current_attributes = text[self.layer_name].attributes
        # Create a new layer
        new_morph_layer = Layer(name=self.layer_name,
                            parent=text[self.layer_name].parent,
                            ambiguous=True,
                            attributes=current_attributes
        )

        # --------------------------------------------
        #   Rewrite spans according to the dict
        # --------------------------------------------
        morph_span_id = 0
        morph_spans   = text[self.layer_name].spans
        word_spans    = text['words'].spans
        assert len(morph_spans) == len(word_spans)
        while morph_span_id < len(morph_spans):
            # 0) Convert SpanList to list of Span-s
            morph_spanlist = \
                [span for span in morph_spans[morph_span_id].spans]

            # 1) Get corresponding word
            word_span = word_spans[morph_span_id]
            word_text = _get_word_text( word_span )
            # Check the dictionary
            if self.configuration['ignore_case']:
                word_text = word_text.lower()
            
            new_morph_spans_added = False
            if word_text in self._dict:
                # 2) If the word is inside user dictionary

                # 2.1) Convert spans to records
                records = [ span.to_record() for span in morph_spanlist ]
                
                # 2.2) Process records:
                if self._dict[word_text]['merge']:
                    # 2.2.1) Merge existing records with new ones
                    new_analysis = self._dict[word_text]['analysis'][0]
                    for rec in records:
                        # Overwrite keys in dict, keep all other 
                        # keys-values as they were before
                        for key in new_analysis:
                            rec[key] = new_analysis[key]
                else: 
                    # 2.2.2) Overwrite existing records with new ones
                    # NB! This assumes that records in the dict are 
                    #     in the valid format;
                    records = self._dict[word_text]['analysis']
                
                # 2.3) Convert records back to spans
                record_added = False
                for rec in records:
                    new_morph_span = Span(parent=word_span)
                    # Carry over attributes
                    for attr in rec.keys():
                        if attr in ['start', 'end', 'text', 'word_normal']:
                            continue
                        if attr not in current_attributes:
                            continue
                        if attr == 'root_tokens':
                            # make it hashable for Span.__hash__
                            setattr(new_morph_span, attr, tuple(rec[attr]))
                        else:
                            setattr(new_morph_span, attr, rec[attr])
                    # Record the new span
                    new_morph_layer.add_span( new_morph_span )
                    new_morph_spans_added = True

            # 3) If the word was not inside user dictionary
            #       or a new analysis was not added, 
            #    then add the old morph analysis
            if not new_morph_spans_added:
                for old_morph_span in morph_spanlist:
                    new_morph_layer.add_span( old_morph_span )

            # Advance in the old "morph_analysis" layer
            morph_span_id += 1

        # --------------------------------------------
        #   Return layer or Text
        # --------------------------------------------
        # Return layer
        if return_layer:
            return new_morph_layer
        # Overwrite the old layer
        delattr(text, self.layer_name)
        text[self.layer_name] = new_morph_layer
        return text



    def validate_morph_record_for_vm_categories(self, morph_dict):
        """
        """
        assert isinstance(morph_dict, dict)
        for key, val in morph_dict.items():
            if key == 'partofspeech':
                assert val in VABAMORF_POSTAGS, \
                    "(!) Unexpected 'partofspeech':'"+str(val)+"'. "+\
                    "Proper value should be one of the following: "+str(VABAMORF_POSTAGS)
            if key == 'form':
                if len(val) > 0:
                    vals = val.split()
                    for v in vals:
                        assert v in VABAMORF_NOUN_FORMS or v in VABAMORF_VERB_FORMS, \
                        "(!) Unexpected 'form':'"+str(val)+"'. "+\
                        "Proper values should be from the following: "+str(VABAMORF_NOUN_FORMS+VABAMORF_VERB_FORMS)

