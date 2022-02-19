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

import re
import os
import json
import os.path
import datetime

from collections import OrderedDict

from estnltk import Text, Layer
from estnltk import EnvelopingSpan

from estnltk.taggers import Tagger
from estnltk.taggers.standard.morph_analysis.morf_common import _convert_morph_analysis_span_to_vm_dict
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation, _get_word_text

from estnltk.java.javaprocess import JavaProcess
from estnltk.common import JAVARES_PATH


class CoreTimexTagger( Tagger ):
    """Detects and normalizes temporal expressions (timexes).
       Normalization involves providing calendrical dates, times 
       and durations corresponding to the expressions.
       Uses a Java-based temporal tagger (Ajavt) to perform the 
       tagging.
       
       Note: CoreTimexTagger requires different tokenization than
       provided by EstNLTK's default pipeline.
       Therefore, using this class directly is not recommended .
       Instead, use TimexTagger, which provides timex tagging with
       the necessary preprocessing.
    """
    output_layer = 'timexes'
    output_attributes = ('tid', 'type', 'value', 'temporal_function', 'anchor_time_id', \
                         'mod', 'quant', 'freq', 'begin_point', 'end_point' )
    input_layers = ['words', 'sentences', 'morph_analysis']
    conf_param = [ 'rules_file', 'pick_first_in_overlap', 
                   'mark_part_of_interval', 'output_ordered_dicts', 
                   'use_normalized_word_form',
                   # Names of the specific input layers
                   '_input_words_layer', '_input_sentences_layer',
                   '_input_morph_analysis_layer',
                   # Internal process
                   '_java_process'
                  ]

    def __init__(self, 
                       output_layer:str='timexes',
                       input_words_layer:str='words',
                       input_sentences_layer:str='sentences',
                       input_morph_analysis_layer:str='morph_analysis',
                       rules_file:str=None, \
                       pick_first_in_overlap:bool=True, \
                       mark_part_of_interval:bool=True, \
                       output_ordered_dicts:bool=True, \
                       use_normalized_word_form:bool=True ):
        """Initializes Java-based temporal expression tagger.
        
        Parameters
        ----------
        output_layer: str (default: 'timexes')
            Name for the timexes layer;
        
        input_words_layer: str (default: 'words')
            Name of the input words layer;
        
        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        
        input_morph_analysis_layer: str (default: 'morph_analysis')
            Name of the input morph_analysis layer;
        
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
             
        use_normalized_word_form: boolean (default: True)
             If set, then normalized word forms will be passed to temporal expression 
             tagger's input: the word.text will always be overwritten by (the first 
             value of) word.normalized_form (if word.normalized_form is not None). 
             Otherwise, timex tagger uses only the surface word forms (word.text),
             and no attention is paid on word normalizations;
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self._input_morph_analysis_layer = input_morph_analysis_layer
        self.input_layers = [input_words_layer, input_sentences_layer, input_morph_analysis_layer]
        # Set configuration
        self.pick_first_in_overlap = pick_first_in_overlap
        self.mark_part_of_interval = mark_part_of_interval
        self.output_ordered_dicts  = output_ordered_dicts
        if self.mark_part_of_interval:
           self.output_attributes += ('part_of_interval', )
        self.use_normalized_word_form = use_normalized_word_form
        # Fetch & check rules file 
        use_rules_file = \
            os.path.join(JAVARES_PATH, 'reeglid.xml') if not rules_file else rules_file
        if not os.path.exists( use_rules_file ):
            raise Exception( \
                  '(!) Unable to find timex tagger rules file from the location:', \
                  use_rules_file )
        self.rules_file = use_rules_file
        # Start process
        args = ['-pyvabamorf']
        args.append('-r')
        args.append(use_rules_file)
        self._java_process = \
            JavaProcess( 'Ajavt.jar', jar_path=JAVARES_PATH, check_java=True, lazy_initialize=True, args=args )



    def __enter__(self):
        # Initialize java process (only if we are inside the with context manager)
        if self._java_process and self._java_process._process is None:
            self._java_process.initialize_java_subprocess()
        return self


    def __exit__(self, *args):
        """ Terminates Java process. """
        if self._java_process._process is not None: # if the process was initialized
            # The proper way to terminate the process:
            # 1) Send out the terminate signal
            self._java_process._process.terminate()
            # 2) Interact with the process. Read data from stdout and stderr, 
            #    until end-of-file is reached. Wait for process to terminate.
            self._java_process._process.communicate()
            # 3) Assert that the process terminated
            assert self._java_process._process.poll() is not None
        return False


    def close(self):
        if self._java_process._process is not None: # if the process was initialized
            if self._java_process._process.poll() is None:
                self.__exit__()


    def _find_creation_date(self, text: Text):
        ''' Looks for the document creation time in the metadata of the given 
            text object. If it is found ( under key 'dct', 'creation_time' or
            'document_creation_time' ),  and it has a correct format (Python's 
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
        for dct_arg_name in [ 'dct', 'creation_time', 'document_creation_time' ]:
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

    def _convert_timex_attributes(self, timex: dict, empty_timexes_dict: dict):
        """Rewrites TIMEX attribute names and values from the XML format
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

        Returns: dict
            attributes from timex for span annotation

        """
        attributes = {k: timex.get(k) for k in ['tid', 'type', 'value', 'mod', 'quant', 'freq']}
        attributes['temporal_function'] = (timex.get('temporalFunction') == 'true')
        attributes['anchor_time_id'] = timex.get('anchorTimeID')

        if 'beginPoint' in timex:
           attributes['begin_point'] = timex['beginPoint']
           if timex['beginPoint'] in empty_timexes_dict:
              attributes['begin_point'] = empty_timexes_dict[timex['beginPoint']]
              if isinstance(attributes['begin_point'], dict) and \
                 self.output_ordered_dicts:
                  attributes['begin_point'] = \
                       self._convert_timex_dict_to_ordered_dict(attributes['begin_point'])

        if 'endPoint' in timex:
            attributes['end_point'] = timex['endPoint']
            if timex['endPoint'] in empty_timexes_dict:
                attributes['end_point'] = empty_timexes_dict[timex['endPoint']]
                if isinstance(attributes['end_point'], dict) and \
                   self.output_ordered_dicts:
                    attributes['end_point'] = \
                       self._convert_timex_dict_to_ordered_dict(attributes['end_point'])

        if self.mark_part_of_interval:
            # Determine whether this TIMEX is part of an interval, and
            # if so, then mark also TIMEX of the interval as an attribute
            timex_tid = timex['tid'] if 'tid' in timex else None
            timex_type = timex['type'] if 'type' in timex else None
            if empty_timexes_dict and timex_type in ['DATE', 'TIME']:
                for empty_timex_id in empty_timexes_dict.keys():
                    empty_timex = empty_timexes_dict[empty_timex_id]
                    if 'beginPoint' in empty_timex.keys() and \
                        timex_tid == empty_timex['beginPoint']:
                        attributes['part_of_interval'] = \
                                   empty_timexes_dict[empty_timex_id]
                        if isinstance(attributes['part_of_interval'], dict) and \
                           self.output_ordered_dicts:
                           attributes['part_of_interval'] = \
                              self._convert_timex_dict_to_ordered_dict(attributes['part_of_interval'])

                        break
                    elif 'endPoint' in empty_timex.keys() and \
                           timex_tid == empty_timex['endPoint']:
                        attributes['part_of_interval'] = empty_timexes_dict[empty_timex_id]
                        if isinstance(attributes['part_of_interval'], dict) and \
                           self.output_ordered_dicts:
                           attributes['part_of_interval'] = \
                              self._convert_timex_dict_to_ordered_dict(attributes['part_of_interval'])
                        break
        # If there is DATE and temporal_function==True and anchor_time_id
        # is not set, set it to 't0' (document creation time)
        if attributes['type']=='DATE' and attributes['temporal_function']:
            if 'anchorTimeID' not in timex:
                attributes['anchor_time_id'] = 't0'

        return attributes



    def _convert_timex_dict_to_ordered_dict( self, timex:dict ):
        ''' Converts timex dictionary into an OrderedDict, in which the keys 
            are ordered the same way as the TimexTagger.output_attributes are.
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
                are ordered the same way as in TimexTagger.output_attributes.
        '''
        ordered_timex_dict = OrderedDict()
        for attrib in self.output_attributes:
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

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer, 
                     text_object=None,
                     enveloping=self._input_words_layer, 
                     attributes=self.output_attributes, 
                     ambiguous=False)

    def _make_layer(self, text, layers, status: dict):
        """Creates timexes layer.
        
        Parameters
        ----------
        text: Text
           Text in which timexes will be annotated;
        
        layers: MutableMapping[str, Layer]
           Layers of the text.  Contains mappings  from the 
           name of the layer to the Layer object. Must contain
           the words, sentences and morph_analysis layers.
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        # A) Find document creation time from the metadata, and
        #    convert morphologically analysed text into VM format:
        input_data = {
            'dct': self._find_creation_date(text),
            'sentences': []
        }
        morph_spans  = layers[ self._input_morph_analysis_layer ]
        word_spans   = layers[ self._input_words_layer ]
        assert len(morph_spans) == len(word_spans)
        word_span_id = 0
        for sentence in layers[ self._input_sentences_layer ]:
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
                        if word_span.base_span == morph_span.base_span \
                           and len(morph_span.annotations) > 0 \
                           and not _is_empty_annotation(morph_span.annotations[0]):
                            # Convert span to Vabamorf dict
                            word_morph_dict = \
                                    _convert_morph_analysis_span_to_vm_dict(
                                        morph_span )
                            if self.use_normalized_word_form:
                                # Use normalized_form of the word (if available)
                                word_morph_dict['text'] = \
                                       _get_word_text( word_span )
                            sentence_morph_dicts.append( word_morph_dict )
                            morphFound = True
                    if not morphFound:
                        # No morph found: add an empty Vabamorf dict
                        empty_analysis_dict = { 'text' : word_span.text,
                                                'analysis' : [] }
                        if self.use_normalized_word_form:
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
            if self.use_normalized_word_form:
                assert vm_word['text'] == _get_word_text( word_span )
            else:
                assert vm_word['text'] == word_span.text
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
        layer = self._make_layer_template()
        layer.text_object = text
        marked_timex_word_ids = set()
        for tid in timexes_dict.keys():
            timex = timexes_dict[tid]
            # Skip overlapping timexes
            if self.pick_first_in_overlap:
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
            # Convert timex attributes from camelCase to Python +
            # perform some fixes
            attributes = self._convert_timex_attributes(timex, empty_timexes_dict)
            layer.add_annotation(timex['_word_spans'], **attributes)
            # Record location of the annotation (word_ids)
            for word_id in timex['_word_span_ids']:
                 marked_timex_word_ids.add( word_id )
        # Return results:
        return layer


