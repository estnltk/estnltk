#
#   Makes user-specified post-corrections to morphological analyses.
#  Basically, rewrites automatically produced morphological analyses 
#  with user-specified ones.
# 
import copy
import csv

from typing import MutableMapping, Sequence

from estnltk.text import Span, Layer, Text
from estnltk.layer.ambiguous_span import AmbiguousSpan

from estnltk.taggers import Retagger, TaggerOld

from estnltk.taggers.morph_analysis.morf_common import ESTNLTK_MORPH_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import VABAMORF_ATTRIBUTES
from estnltk.taggers.morph_analysis.morf_common import _get_word_text
from estnltk.taggers.morph_analysis.morf_common import _postprocess_root

from estnltk.taggers.morph_analysis.morf_common import VABAMORF_POSTAGS
from estnltk.taggers.morph_analysis.morf_common import VABAMORF_NOUN_FORMS
from estnltk.taggers.morph_analysis.morf_common import VABAMORF_VERB_FORMS



class UserDictTagger(Retagger):
    description   = "Makes user-specified post-corrections to morphological analyses. "+\
                    "This tagger can be applied after text has been morphologically analysed."
    output_layer  = 'morph_analysis'
    input_layers  = ['morph_analysis', 'words']
    depends_on    = input_layers
    attributes    = ESTNLTK_MORPH_ATTRIBUTES
    conf_param    = ['ignore_case', 'validate_vm_categories', 'autocorrect_root', '_dict']

    def __init__(self,
                 output_layer:str='morph_analysis', \
                 ignore_case:bool=False, \
                 validate_vm_categories:bool=True, \
                 autocorrect_root:bool=True ):
        """ Initialize UserDictTagger class.

        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the output layer.
        
        ignore_case: bool (default: False)
            If True, then case will be ignored when matching words in the text
            with words in the dictionary. Basically, all words added to the 
            dictionary will be converted to lowercase, and words in text will also 
            be converted to lowercase before the dictionary lookup;
        
        validate_vm_categories: bool (default: True)
            If True, then each analysis is checked for validity of partofspeech
            and form categories. Note that validation only checks if the respective 
            category values are valid category values for Vabamorf. But it does not
            check that the category values are also correctly combined (e.g. 
            partofspeech and form have been correctly combined);
        
        autocorrect_root: bool (default: True)
            If True, then dictionary entries for 'root_tokens' and 'lemma' will 
            be automatically generated and replaced, iff entries for 'root' and 
            'partofspeech' are given by the user. Note: this requires that when-
            ever 'root' has been specified by the user, 'partofspeech' must also 
            be specified (otherwise 'lemma' cannot be generated);

        """
        self.output_layer = output_layer
        self.ignore_case  = ignore_case
        self.validate_vm_categories = validate_vm_categories
        self.autocorrect_root       = autocorrect_root
        self._dict                  = {}



    def add_word(self, word, analysis_struct):
        """ Adds a word and its new morphological analysis to the user 
            dictionary.
            
            Note: if the user dictionary already contains entry for the word,
                  then the old entry will be overwritten with the new one;
                  
            Partial overwriting
            --------------------
            If  analysis_struct  is a dict, then its content will be used for 
            partial overwriting of the analysis in text: fields present in the 
            dict will be overwritten, and fields not present in the dict will 
            remain as they are.
            For instance, you can specify that only 'partofspeech' will be 
            changed, and other fields will remain as they are.
            The minimum requirement for the partial overwriting dict: it must 
            specify only one of the fields: 'root', 'ending', 'clitic', 'form', 
            'partofspeech';
            
            Complete overwriting
            --------------------
            If  analysis_struct  is a list, then its content will be used for 
            complete overwriting: word's analyses in the text will be completely
            replaced with the content of the list.
            Therefore, the list must contain at least one analysis dict (in case 
            of unambiguous word), or several dicts (in case of ambiguous word).
            Each dict must contain fields  'root', 'ending', 'clitic', 'form', 
            'partofspeech';
            
            Note: you should not specify manually 'root_tokens' and 'lemma', but 
            instead specify correct values for 'root', 'ending', and 'partofspeech', 
            and let the automagic to do the work (the flag 'autocorrect_root' must 
            be set for the automatic to happen!).
            
            Note: if validate_vm_categories is set, then partofspeech and form
            category names will be validated before accepting the entry (an 
            AssertionError will be thrown is validation fails).
            
        Parameters
        ----------
        word: str
            Word which entry is to be added to the user dictionary.
            If ignore_case is set, it will be converted to lowercase.
        
        analysis_struct: dict or list
            If analysis_struct is a dict, then it must contain at least one 
            of the keys 'root', 'ending', 'clitic', 'form', 'partofspeech',
            and the word's analyses in the text will be partially overwritten
            with the keys-values in the dict.
            If analysis_struct is a list (of dicts), then each of its dicts must 
            contain keys 'root', 'ending', 'clitic', 'form', 'partofspeech',
            and the word's analyses in the text will be completely overwritten
            with the dicts in the list.

        """
        assert isinstance(word, str)
        assert isinstance(analysis_struct, (dict, list))
        # Ignore case (if required)
        if self.ignore_case:
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
            if self.validate_vm_categories:
                self.validate_morph_record_for_vm_categories(analysis_struct)
            self._dict[word] = {}
            self._dict[word]['analysis'] = \
                [ copy.deepcopy(analysis_struct) ]
            # Autocorrect root analysis: 
            #    generate cleaned root, root_tokens & lemma
            if self.autocorrect_root:
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
                if self.validate_vm_categories:
                    self.validate_morph_record_for_vm_categories(record)
                # Autocorrect root analysis: 
                #    generate cleaned root, root_tokens & lemma
                if self.autocorrect_root:
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
        ''' Loads words with their morphological analyses from the given 
            csv file, and inserts to the user dictionary.
            
            Note: any words already having entries in the user dictionary 
                  will have their old entries overwritten with the new 
                  ones;
            
            By default, assumes that csv file is in tab-separated-values 
            format (dialect='excel-tab') and in the encoding 'utf-8'.
            You can change the encoding via parameter encoding. And you
            can also provide other custom parameters ( from the parameters 
            listed in: 
            https://docs.python.org/3/library/csv.html#csv-fmt-params )
            if your input csv file has some other format.
            
            It is required that the first line of the file is the header,
            and uses the heading names 'root', 'ending', 'clitic', 'form', 
            'partofspeech', 'text'. This is required to determine in which 
            order the data needs to be loaded from the file.
            Each line following the heading specifies a single analysis for
            a word. The word itself must be under the column 'text'.
            Note that there can also be multiple lines for a single word:
            these are considered as different analysis variants of an 
            ambiguous word.
            
            Note: after analyses have been collected from the file, they
            will be inserted to the dictionary via the method add_word().
            
        Parameters
        ----------
        filename: str
            Path to the csv file which contains entries. The first line of 
            the file must specify order of fields 'root', 'ending', 'clitic', 
            'form', 'partofspeech', 'text'. Each line following the heading 
            must specify a single analysis for a word. The word itself must 
            be under the column 'text'.
        
        encoding: str (Default: 'utf-8')
            Encoding of the csv file.
        
        dialect: str (Default: 'excel-tab')
            Parameter dialect to be passed to the function csv.reader().
            See https://docs.python.org/3/library/csv.html#csv.reader
            for details.

        fmtparams: 
            Optional keyword arguments to be passed to the function 
            csv.reader().
            See https://docs.python.org/3/library/csv.html#csv.reader
            for details.
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
                if self.ignore_case:
                    word_text = word_text.lower()
                # Add new analysis to the dict
                if word_text not in collected_analyses:
                    collected_analyses[word_text] = []
                collected_analyses[word_text].append(analysis_dict)
                #print(', '.join(row))
        # Rewrite all analyses into the user dict
        for word in collected_analyses.keys():
            self.add_word( word, collected_analyses[word] )



    def _make_layer(self, raw_text: str, layers: MutableMapping[str, Layer], status: dict = None) -> Layer:
        """Provides dictionary-based corrections on morphological
           analyses layer.
           More technically: rewrites the layer 'morph_analysis'
           by replacing existing analyses with analyses from the
           user dictionary. Dictionary lookup is made via word texts:
           word which text matches a word in dictionary will have
           its analyses overwritten. If ignore_case is switched on,
           then the lookup is also case-insensitive.

           Parameters
           ----------
           raw_text: str
              Text string corresponding to the text which annotation
              layers will be corrected;
           layers: MutableMapping[str, Layer]
              Mappings from name to Layer. The mapping must have
              layers 'morph_analysis' and 'words'. The layer
              'morph_analysis' will be rewritten;
           status: dict
              This can be used to store metadata on layer creation.

           Returns
           -------
           Layer
              Returns the corrected 'morph_analysis' layer;
        """
        # Take attributes from the input layer
        assert 'morph_analysis' in layers
        assert 'words' in layers
        current_attributes = layers['morph_analysis'].attributes
        # --------------------------------------------
        #   Rewrite spans according to the dict
        # --------------------------------------------
        morph_span_id = 0
        morph_spans = layers['morph_analysis'].spans
        word_spans  = layers['words'].spans
        assert len(morph_spans) == len(word_spans)
        while morph_span_id < len(morph_spans):
            # 0) Convert SpanList to list of Span-s
            morph_spanlist = \
                [span for span in morph_spans[morph_span_id].spans]

            # 1) Get corresponding word
            word_span = word_spans[morph_span_id]
            word_text = _get_word_text(word_span)
            # Check the dictionary
            if self.ignore_case:
                word_text = word_text.lower()

            new_morph_spans_added = False
            if word_text in self._dict:
                # 2) If the word is inside user dictionary

                # 2.1) Convert spans to records
                records = [span.to_record() for span in morph_spanlist]

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

                # 2.3) Create new AmbiguousSpan
                ambiguous_span = \
                    AmbiguousSpan(layer=morph_spans[morph_span_id].layer, \
                                  span=morph_spans[morph_span_id].span)

                # 2.4) Populate it with new records
                for rec in records:
                    # Carry over attributes
                    for attr in current_attributes:
                        if attr in ['start', 'end', 'text', 'word_normal']:
                            continue
                        attr_value = rec[attr] if attr in rec else None
                        if attr == 'root_tokens':
                            # make it hashable for Span.__hash__
                            rec[attr] = tuple(attr_value)
                        else:
                            rec[attr] = attr_value
                    # Add record as an annotation
                    ambiguous_span.add_annotation( **rec )

                # 2.5) Overwrite the old span
                morph_spans[morph_span_id] = ambiguous_span

            # 3) If the word was not inside user dictionary
            #       or a new analysis was not added,
            #    then we do not have to do anything: the old analysis
            #    span will be preserved in the layer
            if not new_morph_spans_added:
                pass

            # Advance in the old "morph_analysis" layer
            morph_span_id += 1


    def validate_morph_record_for_vm_categories(self, morph_dict):
        """Validates given dictionary containing single morphological 
        analysis for correctness of Vabamorf's categories. 
        Note that validation only checks if the respective category 
        values are valid category values for Vabamorf, e.g. checks that 
        partofspeech does not have illegal value 'W'. 
        But the validation does not check that the category values are 
        also correctly combined (e.g. partofspeech and form have been 
        correctly combined).
        Validation is made via assertions, so an AssertionError will 
        be thrown if one of the validations fails.
        
        Parameters
        ----------
        morph_dict: dict
            Dict object with morphological analyses of a word. Should 
            contain keys 'partofspeech' and 'form'.
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
                        "Proper values should be from the following: "+\
                             str( VABAMORF_NOUN_FORMS + VABAMORF_VERB_FORMS )

