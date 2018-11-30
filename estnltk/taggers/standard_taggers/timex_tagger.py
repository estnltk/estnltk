#
#   Temporal expression tagger identifies temporal expressions 
#  (timexes) in text and normalizes these expressions, providing 
#  corresponding calendrical dates,  times  and  durations. The 
#  normalizing format is based on TimeML's TIMEX3 standard.
#   This is a wrapper around Java-based temporal expression tagger, 
#  ported from the version 1.4.1.1:
#    https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/timex.py
#    ( with modifications )
# 

from typing import Union

import re
import os
import json
import os.path
import datetime

from collections import OrderedDict

from estnltk.text import Text, Layer, EnvelopingSpan

from estnltk.taggers import TaggerOld
from estnltk.taggers.morph_analysis.morf_common import _convert_morph_analysis_span_to_vm_dict
from estnltk.taggers.morph_analysis.morf_common import _is_empty_span, _get_word_text

from estnltk.java.javaprocess import JavaProcess
from estnltk.core import JAVARES_PATH


class TimexTagger(TaggerOld):
    description   = 'Detects temporal expressions (timexes) and normalizes '+\
                    'these expressions, providing corresponding calendrical '+\
                    'dates, times and durations. Uses a Java-based temporal '+\
                    'tagger (Ajavt) to perform the tagging.'
    layer_name    = 'timexes'
    attributes    = ('tid', 'type', 'value', 'temporal_function', 'anchor_time_id', \
                     'mod', 'quant', 'freq', 'begin_point', 'end_point' )
    depends_on    = ['words', 'sentences', 'morph_analysis']
    configuration = None


    def __init__(self, rules_file:str=None, \
                       pick_first_in_overlap:bool=True, \
                       mark_part_of_interval:bool=True, \
                       output_ordered_dicts:bool=True ):
        """Initializes Java-based temporal expression tagger.
        
        Parameters
        ----------
        rules_file: str (default: 'reeglid.xml')
             Initializes the temporal expression tagger with a custom rules file.
             The expected format of the rules file is described in  more  detail 
             here:
                 https://github.com/soras/Ajavt/blob/master/doc/writingRules.txt
        
        pick_first_in_overlap: boolean (default: True)
             If set, then in case of partially overlapping timexes the first timex
             will be preserved, and the following timex will be discarded. If not
             set, then all overlapping timexes will be preserved (Note: this likely
             creates conflicts with EstNLTK's data structures);
        
        mark_part_of_interval: boolean (default: True)
             If set, then the information about implicit intervals will also be 
             marked in the annotations. More specifically, all timexes will have an 
             additional attribute 'part_of_interval', and DATE and TIME expressions 
             that make up an interval (DURATION) will have their part_of_interval 
             filled in with a dictionary that contains attributes of the timex 
             tag of the corresponding interval.
             Otherwise (if mark_part_of_interval==False), the information about the 
             implicit intervals will be discarded;
        
        output_ordered_dicts: boolean (default: True)
             If set, then dictionaries in the timex attributes begin_point, end_point, 
             and part_of_interval will be converted into OrderedDict-s. Use this to 
             ensure fixed order of elements in the dictionaries (might be useful for
             nbval testing).
        """
        args = ['-pyvabamorf']
        use_rules_file = \
            os.path.join(JAVARES_PATH, 'reeglid.xml') if not rules_file else rules_file
        if not os.path.exists( use_rules_file ):
            raise Exception( \
                  '(!) Unable to find timex tagger rules file from the location:', \
                  use_rules_file )
        args.append('-r')
        args.append(use_rules_file)
        # Record configuration
        self.configuration = {'rules_file': use_rules_file, \
                              'pick_first_in_overlap': pick_first_in_overlap, \
                              'mark_part_of_interval': mark_part_of_interval, \
                              'output_ordered_dicts':output_ordered_dicts }
        # Start process
        self._java_process = \
            JavaProcess( 'Ajavt.jar', jar_path=JAVARES_PATH, args=args )


    def _find_creation_date(self, text: Text):
        ''' Looks for the document creation time in the metadata of the given 
            text object. If it is found (under key 'dct', 'document_creation_time', 
            or 'creation_time'), and it has a correct format (Python's 
            datetime.datetime obj, or string in the format 'YYYY-mm-ddTHH:MM'), 
            then returns the creation time string. Otherwise (there is no creation 
            time in the metadata) returns the current time (as string) and saves
            the current time in metadata;

            Parameters
            ----------
            text: estnltk.text.Text
                Analysable Text object which should have document creation time
                in the metadata, under the key 'dct', 'document_creation_time', 
                or 'creation_time';

            Returns
            -------
            str
                Document creation time string (in the format 
                'YYYY-mm-ddTHH:MM');
        '''
        creation_date_from_meta = None
        for dct_arg_name in ['dct', 'creation_date', 'document_creation_date', \
                                    'creation_time', 'document_creation_time']:
            for meta_key in text.meta.keys():
                if meta_key.lower() == dct_arg_name:
                   dct_candidate = text.meta[dct_arg_name]
                   # Get creation date according to the type of argument:
                   if isinstance(dct_candidate, datetime.datetime):
                      # Python's datetime object
                      return dct_candidate.strftime('%Y-%m-%dT%H:%M')
                   elif isinstance( dct_candidate, str ):
                      # A string following ISO date&time format
                      if re.match("[0-9X]{4}-[0-9X]{2}-[0-9X]{2}$", \
                                  dct_candidate):
                         return dct_candidate + "TXX:XX"
                      elif re.match("[0-9X]{4}-[0-9X]{2}-[0-9X]{2}T[0-9X]{2}:[0-9X]{2}$", \
                                    dct_candidate):
                         return dct_candidate
        # If document creation time is not given in metadata,
        # use the default creation time: execution time of the program
        # (also, record the newly created document creation time in 
        #  metadata)
        creation_date = datetime.datetime.now()
        text.meta['document_creation_time'] = \
             creation_date.strftime('%Y-%m-%dT%H:%M')
        return text.meta['document_creation_time']



    def _convert_timex_attributes(self, timex:dict, timex_span:EnvelopingSpan, \
                                        empty_timexes_dict:dict ):
        ''' Rewrites TIMEX attribute names and values from the XML format 
            (camelCase names such as 'temporalFunction', 'anchorTimeID') to
            Python's format, normalizes/corrects attribute values where necessary,
            and attaches as attributes of the timex_span (EnvelopingSpan);

            Parameters
            ----------
            timex : dict
                dictionary containing TIMEX attributes in the XML format;

            timex_span : EnvelopingSpan
                EnvelopingSpan of EstNLTK which is to be filled in with the 
                attributes from timex;
            
            empty_timexes_dict : dict
                dictionary containing TIMEX-es that have no textual content;
                (mappings from tid to TIMEX dict); This is used to fill in 
                beginPoint and endPoint attributes;
        '''
        for attrib in timex.keys():
            if attrib in ['_word_spans', '_word_span_ids']:
               continue
            if attrib == 'tid':
               timex_span.tid = timex[attrib]
            if attrib == 'type':
               timex_span.type = timex[attrib]
            if attrib == 'value':
               timex_span.value = timex[attrib]
            if attrib == 'temporalFunction':
               if timex[attrib] == 'true':
                  timex_span.temporal_function = True
               else:
                  timex_span.temporal_function = False
            if attrib == 'mod':
               timex_span.mod = timex[attrib]
            if attrib == 'anchorTimeID':
               timex_span.anchor_time_id = timex[attrib]
            if attrib == 'quant':
               timex_span.quant = timex[attrib]
            if attrib == 'freq':
               timex_span.freq = timex[attrib]
            if attrib == 'beginPoint':
               timex_span.begin_point = timex[attrib]
               if timex[attrib] in empty_timexes_dict:
                  timex_span.begin_point = empty_timexes_dict[timex[attrib]]
                  if isinstance(timex_span.begin_point, dict) and \
                     self.configuration['output_ordered_dicts']:
                      timex_span.begin_point = \
                           self._convert_timex_dict_to_ordered_dict( timex_span.begin_point )
            if attrib == 'endPoint':
               timex_span.end_point = timex[attrib]
               if timex[attrib] in empty_timexes_dict:
                  timex_span.end_point = empty_timexes_dict[timex[attrib]]
                  if isinstance(timex_span.end_point, dict) and \
                     self.configuration['output_ordered_dicts']:
                      timex_span.end_point = \
                           self._convert_timex_dict_to_ordered_dict( timex_span.end_point )
        if self.configuration['mark_part_of_interval']:
           # Determine whether this TIMEX is part of an interval, and
           # if so, then mark also TIMEX of the interval as an attribute
           timex_tid  = timex['tid'] if 'tid' in timex else None
           timex_type = timex['type'] if 'type' in timex else None
           if empty_timexes_dict and timex_type in ['DATE', 'TIME']:
              for empty_timex_id in empty_timexes_dict.keys():
                  empty_timex = empty_timexes_dict[empty_timex_id]
                  if 'beginPoint' in empty_timex.keys() and \
                     timex_tid == empty_timex['beginPoint']:
                     timex_span.part_of_interval = \
                                empty_timexes_dict[empty_timex_id]
                     if isinstance(timex_span.part_of_interval, dict) and \
                        self.configuration['output_ordered_dicts']:
                        timex_span.part_of_interval = \
                           self._convert_timex_dict_to_ordered_dict( timex_span.part_of_interval )
                     break
                  elif 'endPoint' in empty_timex.keys() and \
                        timex_tid == empty_timex['endPoint']:
                     timex_span.part_of_interval = \
                                empty_timexes_dict[empty_timex_id]
                     if isinstance(timex_span.part_of_interval, dict) and \
                        self.configuration['output_ordered_dicts']:
                        timex_span.part_of_interval = \
                           self._convert_timex_dict_to_ordered_dict( timex_span.part_of_interval )
                     break
        # If there is DATE and temporal_function==True and anchor_time_id
        # is not set, set it to 't0' (document creation time)
        if timex_span.type in ['DATE'] and timex_span.temporal_function:
           if 'anchorTimeID' not in timex.keys():
               timex_span.anchor_time_id = 't0'



    def _convert_timex_dict_to_ordered_dict( self, timex:dict ):
        ''' Converts timex dictionary into an OrderedDict, in which the keys 
            are ordered the same way as the TimexTagger.attributes are.
            In addition, rewrites TIMEX attribute names and values from the 
            camelCase format (e.g. 'temporalFunction', 'anchorTimeID') to
            Python's format, and normalizes boolean values ('true' -> True);

            Parameters
            ----------
            timex : dict
                dictionary containing TIMEX attributes in the XML format;

            Returns
            -------
            OrderedDict
                OrderedDict corresponding to the timex, in which the keys 
                are ordered the same way as in TimexTagger.attributes.
        '''
        ordered_timex_dict = OrderedDict()
        for attrib in self.attributes:
            # tid
            if attrib == 'tid' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            # type
            if attrib == 'type' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            # value
            if attrib == 'value' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            # temporal_function
            if attrib == 'temporal_function' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            elif attrib == 'temporal_function' and 'temporalFunction' in timex.keys():
               ordered_timex_dict[attrib] = timex['temporalFunction']
               if ordered_timex_dict[attrib] == 'true':
                  ordered_timex_dict[attrib] = True
               else:
                  ordered_timex_dict[attrib] = False
            # mod
            if attrib == 'mod' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            # anchor_time_id
            if attrib == 'anchor_time_id' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            elif attrib == 'anchor_time_id' and 'anchorTimeID' in timex.keys():
               ordered_timex_dict[attrib] = timex['anchorTimeID']
            # quant
            if attrib == 'quant' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            # freq
            if attrib == 'freq' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            # begin_point
            if attrib == 'begin_point' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            elif attrib == 'begin_point' and 'beginPoint' in timex.keys():
               ordered_timex_dict[attrib] = timex['beginPoint']
            # end_point
            if attrib == 'end_point' and attrib in timex.keys():
               ordered_timex_dict[attrib] = timex[attrib]
            elif attrib == 'end_point' and 'endPoint' in timex.keys():
               ordered_timex_dict[attrib] = timex['endPoint']
        return ordered_timex_dict



    def tag(self, text: Text, return_layer=False) -> Union['Text', Layer]:
        """Tags timexes layer.
        
        Parameters
        ----------
        text: estnltk.text.Text
            Text object that is to be analysed. It needs to have
            layers 'words', 'sentences', 'morph_analysis'.

        return_layer: boolean (default: False)
            If True, then the new layer is returned; otherwise 
            the new layer is attached to the Text object, and 
            the Text object is returned;

        Returns
        -------
        Text or Layer
            If return_layer==True, then returns the new layer, 
            otherwise attaches the new layer to the Text object 
            and returns the Text object;
        """
        # A) Find document creation time from the metadata, and
        #    convert morphologically analysed text into VM format:
        input_data = {
            'dct': self._find_creation_date(text),
            'sentences': []
        }
        morph_spans  = text['morph_analysis'].span_list
        word_spans   = text['words'].span_list
        assert len(morph_spans) == len(word_spans)
        word_span_id = 0
        for sentence in text['sentences'].span_list:
            #  Collect all words/morph_analyses inside the sentence
            #  Assume: len(word_spans) == len(morph_spans)
            sentence_morph_dicts = []
            sentence_words       = []
            while word_span_id < len(word_spans):
                # Get corresponding word span
                word_span  = word_spans[word_span_id]
                morph_span = None
                if sentence.start <= word_span.start and \
                    word_span.end <= sentence.end:
                    morphFound = False
                    # Get corresponding morph span
                    if word_span_id < len(morph_spans):
                        morph_span = morph_spans[word_span_id]
                        if word_span.start == morph_span.start and \
                           word_span.end == morph_span.end and \
                           len(morph_span) > 0 and \
                           (not _is_empty_span(morph_span[0])):
                            # Convert span to Vabamorf dict
                            word_morph_dict = \
                                    _convert_morph_analysis_span_to_vm_dict( \
                                        morph_span )
                            # Use normalized_form of the word (if available)
                            word_morph_dict['text'] = \
                                   _get_word_text( word_span )
                            sentence_morph_dicts.append( word_morph_dict )
                            morphFound = True
                    if not morphFound:
                        # No morph found: add an empty Vabamorf dict
                        empty_analysis_dict = { 'text' : word_span.text, \
                                                'analysis' : [] }
                        # Use normalized_form of the word (if available)
                        empty_analysis_dict['text'] = \
                                              _get_word_text( word_span )
                        sentence_morph_dicts.append( empty_analysis_dict )
                    sentence_words.append( word_span )
                if sentence.end <= word_span.start:
                    # Break the while (end of the sentence)
                    break
                word_span_id += 1
            # Record the current sentence in VM format
            input_data['sentences'].append( {'words': sentence_morph_dicts })
        # B) Analyse the text with the Java-based Timex Tagger
        #pprint(input_data)
        text_vm_json = json.dumps(input_data)
        result_vm_str  = \
            self._java_process.process_line(text_vm_json)
        result_vm_json = json.loads( result_vm_str )
        # Sanity check: 'sentences' and 'words' must be available in the 
        # output; 
        # the number of words in the output must match the number of words 
        # in the input;
        assert 'sentences' in result_vm_json, \
               "(!) Unexpected mismatch between TimexTagger's input and output. "+\
               "Probably there are problems with the Java subprocess."
        output_words = \
            [w for s in result_vm_json['sentences'] for w in s['words'] ]
        assert word_span_id == len(output_words), \
               "(!) Unexpected mismatch between TimexTagger's input and output. "+\
               "Probably there are problems with the Java subprocess. "
        #pprint(result_vm_json)
        #
        # C) Convert results from VM format (used by EstNLTK 1.4) to
        #    the format used by EstNLTK 1.6+
        #
        # C.1) Collect timexes and their locations (word spans)
        #
        timexes_dict = OrderedDict() # TIMEX-es with textual content
        empty_timexes_dict = {}      # TIMEX-es without textual content
        word_span_id = 0
        vm_word_id = 0
        vm_sent_id = 0
        while word_span_id < len(word_spans):
            if vm_sent_id >= len(result_vm_json['sentences']):
               break
            if vm_word_id >= len(result_vm_json['sentences'][vm_sent_id]['words']):
               vm_word_id = 0
               vm_sent_id += 1
               continue
            vm_sent = result_vm_json['sentences'][vm_sent_id]
            vm_word = vm_sent['words'][vm_word_id]
            word_span = word_spans[word_span_id]
            assert vm_word['text'] == _get_word_text( word_span )
            if 'timexes' in vm_word:
               for timex in vm_word['timexes']:
                   if 'tid' in timex:
                       tid = timex['tid'] # TIMEX id
                       if tid not in timexes_dict and \
                          tid not in empty_timexes_dict:
                          # First appearance of the timex
                          if 'type' in timex and 'value' in timex:
                             # Collect only timexes with type and value
                             if 'text' in timex and len(timex['text'])>0:
                                # 1) If the timex has textual content
                                timex['_word_spans'] = []
                                timex['_word_spans'].append( word_span )
                                timex['_word_span_ids'] = []
                                timex['_word_span_ids'].append( word_span_id )
                                timexes_dict[tid] = timex
                             else:
                                # 2) If the timex does not have text
                                empty_timexes_dict[tid] = timex
                       elif tid in timexes_dict:
                          # Next appearance of the timex:
                          # Collect only word span
                          if 'text' in timex and len(timex['text']) > 0:
                             timexes_dict[tid]['_word_spans'].append( word_span )
                             timexes_dict[tid]['_word_span_ids'].append( word_span_id )
            vm_word_id += 1
            word_span_id += 1
        #pprint(timexes_dict)
        #pprint(empty_timexes_dict)
        #
        # C.2) Create a new layer and populated with collected timexes
        #
        layer_attributes = self.attributes
        if self.configuration['mark_part_of_interval']:
           layer_attributes += ('part_of_interval', )
        layer = Layer(name=self.layer_name, 
                      enveloping ='words', 
                      attributes=layer_attributes, 
                      ambiguous=False)
        marked_timex_word_ids = set()
        for tid in timexes_dict.keys():
            timex = timexes_dict[tid]
            # Skip overlapping timexes
            if self.configuration['pick_first_in_overlap']:
                 skipTimex = False
                 for word_id in timex['_word_span_ids']:
                      if word_id in marked_timex_word_ids:
                         skipTimex = True
                         break
                 if skipTimex:
                      # Skip the current timex because it 
                      # partially overlaps with a previously
                      # annotated timex
                      continue
            timex_span = \
                 EnvelopingSpan(spans=timex['_word_spans'])
            # Convert timex attributes from camelCase to Python + 
            # perform some fixes
            self._convert_timex_attributes(timex, timex_span, \
                                           empty_timexes_dict )
            layer.add_span( timex_span )
            # Record location of the annotation (word_ids)
            for word_id in timex['_word_span_ids']:
                 marked_timex_word_ids.add( word_id )
        # Return results:
        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text
