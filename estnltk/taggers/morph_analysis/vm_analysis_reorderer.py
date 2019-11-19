import csv
import os, os.path

from estnltk import Annotation
from estnltk.text import Layer, Text
from estnltk.taggers import Retagger

from estnltk.taggers.morph_analysis.morf_common import NORMALIZED_TEXT
from estnltk.taggers.morph_analysis.morf import VabamorfTagger


# Default dict of analysis reorderings 
DEFAULT_REORDERING_DICT = os.path.join(os.path.dirname(__file__),
                          'reorderings/et_edt-ud-train_sorted_analyses_full.csv')

class MorphAnalysisReorderer(Retagger):
    """ Retagger for reordering ambiguous morphological analyses.
        Use this tagger as a post-corrector after VabamorfTagger or 
        VabamorfCorpusTagger.

        Analyses will be reordered based on the reordering information
        read from an input CSV file.
        
        By default, the reordering information is loaded from the 
        file:
          'reorderings/et_edt-ud-train_sorted_analyses_full.csv'
        It contains reorderings of Vabamorf's analyses based on 
        frequency counts obtained from the training part of the 
        Estonian Dependency Treebank:
           https://github.com/UniversalDependencies/UD_Estonian-EDT
        Evaluation on the dev and test parts of the corpus showed 
        that after applying these reorderings, approx. +20% more 
        ambiguous words will have the correct analysis as their 
        first one (the increase from ~50% --> ~70%).
    """
    
    output_attributes = VabamorfTagger.output_attributes
    conf_param = [ # reorderings file
                   'reorderings_file',
                   # internal stuff
                   '_word_to_ordering',
                   '_word_to_ordering_header',
                   '_word_to_ordering_header_minimum',
                 ]

    def __init__(self, output_layer:str='morph_analysis',
                       word_to_ordering_csv_file:str=DEFAULT_REORDERING_DICT ):
        """ Initialize MorphAnalysisReorderer class.

        Parameters
        ----------
        output_layer: str (default: 'morph_analysis')
            Name of the morphological analysis layer that is to be changed;
            
        word_to_ordering_csv_file: str (default: DEFAULT_REORDERING_DICT)
            Path to the CSV file containing word reorderings. 
            By default, assumes that csv file is in tab-separated-values 
            format (dialect='excel-tab') and in the encoding 'utf-8'.
            The first line must be a header specifying (at minimum)
            the following attributes:
             * 'text'           -- word surface form;
             * 'lemma'          -- 'lemma' attribute from 'morph_analysis';
             * 'partofspeech'   -- 'partofspeech' attribute from 'morph_analysis';
             * 'form'           -- 'form' attribute from 'morph_analysis';
             * 'prob' or 'freq' -- probability or frequency of the analysis;
            Each line following the header specifies a single analysis for
            a word. Naturally, a word having multiple analyses should be 
            described on multiple successive lines.
            Important: we assume that word's analyses in the CSV file are 
            already in the correct order -- from most probable to least 
            probable.
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self.input_layers = [self.output_layer]
        assert os.path.isfile( word_to_ordering_csv_file ), \
            '(!) Invalid input CSV file location: {!r}'.format( word_to_ordering_csv_file )
        self.reorderings_file = word_to_ordering_csv_file
        self._word_to_ordering, self._word_to_ordering_header = \
             self._load_reorderings( word_to_ordering_csv_file )
        self._word_to_ordering_header_minimum = \
            [ i for i in self._word_to_ordering_header if i not in ['freq', 'prob', 'text']]



    def _load_reorderings( self, input_csv_file, encoding='utf-8', \
                                dialect='excel-tab', **fmtparams ):
        ''' Loads keywords with their corresponding reordered morphological 
            analyses from the given csv file.
            Keywords are either surface word forms or abstract patterns 
            representing words.
            Returns two items:
               1) a mapping from keywords to analyses lists;
               2) a list containing attribute names used in analyses;
               
            By default, assumes that csv file is in tab-separated-values 
            format (dialect='excel-tab') and in the encoding 'utf-8'.
            You can change the encoding via parameter encoding. And you
            can also provide other custom parameters ( from the parameters 
            listed in: 
            https://docs.python.org/3/library/csv.html#csv-fmt-params )
            if your input csv file has some other format.
            
            The first line must be a header specifying (at minimum)
            the following attributes:
             * 'text'           -- word surface form;
             * 'lemma'          -- 'lemma' attribute from 'morph_analysis';
             * 'partofspeech'   -- 'partofspeech' attribute from 'morph_analysis';
             * 'form'           -- 'form' attribute from 'morph_analysis';
             * 'prob' or 'freq' -- probability or frequency of the analysis;
            Other attributes from the 'morph_analysis' layer can also be 
            used.
            The header is required to determine in which order the data 
            needs to be loaded from the file.
            Each line following the header specifies a single analysis for
            a word. Naturally, a word having multiple analyses should be 
            described on multiple successive lines.
            Important: we assume that analyses in CSV file are already in 
            the correct order -- from most probable to least probable.
            The surface word form (or an abstract pattern representing
            the word) must be under the column 'text'.
            
        Parameters
        ----------
        filename: str
            Path to the CSV file which contains entries. The first line of 
            the file must specify (at minimum) the order of fields 'text', 
            'lemma', 'partofspeech', 'form' and 'prob' or 'freq'. Each 
            line following the heading must specify a single analysis for 
            a word. The word itself must be under the column 'text'.
        
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
        
        def _is_float_convertable( value_str ):
            '''Detects if value_str is a numeric string that can be converted to float.
               The idea borrows from: https://stackoverflow.com/a/38329481
            '''
            return value_str.replace('.','',1).isdecimal()
        
        word_to_reorderings = {}
        header = []
        with open(input_csv_file, 'r', newline='', encoding=encoding) as csvfile:
            fle_reader = csv.reader(csvfile, dialect=dialect, **fmtparams)
            header = next(fle_reader)
            # Validate that header specifies the minimum set of required attribute names
            missing = []
            for attr in ('text','lemma','partofspeech','form'):
                if attr not in header:
                    missing.append(attr)
            # At least count attribute -- 'prob' or 'freq' -- must be present
            if 'prob' not in header and 'freq' not in header:
                missing.append('prob')
            assert not missing, \
                '(!) CSV file header misses the following key(s): '+str(missing)
            # Validate redundant attributes
            redundant = []
            for attr in header:
                if attr not in ['text', 'freq', 'prob']:
                    if attr not in VabamorfTagger.output_attributes:
                        redundant.append( attr )
            assert not redundant, \
                '(!) CSV file header contains unexpected "morph_analysis" attributes: '+str(redundant)
            # Parse CSV file
            # Collect and aggregate analyses
            for row in fle_reader:
                assert len(row) == len(header), '(!) Unexpected number of elements in a row: {!r}'.format(row)
                items = ()
                word_text = None
                for kid, key in enumerate(header):
                    attr  = header[kid]
                    value = row[kid]
                    # Convert numerics to floats
                    if attr == 'prob':
                        assert _is_float_convertable(value), \
                            '(!) Expected numeric for {!r}, but got: {!r} in row {!r}'.format(attr,value,row)
                        value = float(value)
                    elif attr == 'freq':
                        assert _is_float_convertable(value), \
                            '(!) Expected numeric for {!r}, but got: {!r} in row {!r}'.format(attr,value,row)
                        value = float(value)
                    items += ( value, )
                    if attr == 'text':
                        word_text = value
                assert word_text is not None
                if word_text not in word_to_reorderings:
                    word_to_reorderings[word_text] = []
                word_to_reorderings[word_text].append( items )
        return word_to_reorderings, header


    def _reorder_analyses( self, current_annotations, reordering, add_probs=False ):
        ''' Reorders current_annotations based on the list of ordered annotations (reordering).
            By default, returns reordered list of Annotations objects.
            
            List reordering contains tuples of values (reduced annotations), and these tuples 
            only contain values for attributes specified in self._word_to_ordering_header.
            
            The list current_annotations contains fully specified morphologial annotations
            from the layer 'morph_analysis'.
            
            If add_probs == True, then returns a list of tuples, where each tuple contains:
                ( Annotation, probability_or_frequency )
        '''
        reordered_annotations = []
        matched_current_annotations = set()
        freq_or_prob_id = -1
        if add_probs:
            # Find id of the freq/prob attribute (if both exists, prefer 'prob')
            for attr_id, attr in enumerate(self._word_to_ordering_header):
                if attr == 'freq' and freq_or_prob_id == -1:
                    freq_or_prob_id = attr_id
                elif attr == 'prob':
                    freq_or_prob_id = attr_id
            assert freq_or_prob_id > -1, \
                "(!) Unable to find 'prob' or 'freq' from {!r}".format(self._word_to_ordering_header)
        # Find current annotations matching to the reordered annotations 
        for orderly_annotation in reordering:
            assert len(orderly_annotation) == len(self._word_to_ordering_header), \
                '(!) Mismatch between reordering\'s attributes {!r} and values {!r}'.format( self._word_to_ordering_header,\
                                                                                             orderly_annotation )
            for cid, cur_annotation in enumerate(current_annotations):
                matching_attrs = []
                for attr_id, attr in enumerate(self._word_to_ordering_header):
                    if attr not in self._word_to_ordering_header_minimum:
                        # Skip uncomparable attributes 'text', 'freq', 'prob'
                        continue
                    if cur_annotation[attr] == orderly_annotation[attr_id]:
                        matching_attrs.append( attr )
                if len(matching_attrs) == len(self._word_to_ordering_header_minimum):
                    if add_probs:
                        # Add probability or frequency
                        prob_or_freq = orderly_annotation[freq_or_prob_id]
                        assert isinstance(prob_or_freq, float)
                        # Make a tuple: ( annotation, prob_or_freq )
                        cur_annotation = (cur_annotation, prob_or_freq)
                    reordered_annotations.append( cur_annotation )
                    matched_current_annotations.add( cid )
                    break
        # Add remaining (mismatching) annotations
        for cid, cur_annotation in enumerate(current_annotations):
            if cid not in matched_current_annotations:
                if add_probs:
                    # Make a tuple: ( annotation, prob_or_freq )
                    cur_annotation = (cur_annotation, 0.0)
                reordered_annotations.append( cur_annotation )
        assert len(current_annotations) == len(reordered_annotations)
        return reordered_annotations


    def _change_layer(self, text, layers, status: dict):
        """Reorders ambiguous analyses on the morph_analysis layer.
        
        Parameters
        ----------
        text: Text
           Text object that will be retagged;
          
        layers: MutableMapping[str, Layer]
           Layers of the text. Contains mappings from the 
           name of the layer to the Layer object. Must 
           contain morph_analysis layer;
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        morph_analysis = layers[ self.output_layer ]
        for morph_word in morph_analysis:
            if len(morph_word.annotations) == 1:
                # We have only one annotation: on we go, to the next word!
                continue
            # We have an ambiguous analysis
            # 1) Group annotations by their NORMALIZED_TEXT
            annotations_by_norm_text = {}
            for anno in morph_word.annotations:
                norm_text = anno[NORMALIZED_TEXT]
                if norm_text is None:
                    # Fall back to the surface text
                    norm_text = morph_word.text
                if norm_text not in annotations_by_norm_text:
                    annotations_by_norm_text[norm_text] = []
                annotations_by_norm_text[norm_text].append( anno )
            # 2) Try to find orderings for each of the keywords
            resortable_annotations = []
            reordering_was_applied = False
            for keyword in annotations_by_norm_text.keys():
                if keyword in self._word_to_ordering:
                    reordering = self._word_to_ordering[keyword]
                    reordered_annotations = \
                        self._reorder_analyses(annotations_by_norm_text[keyword], reordering, add_probs=True)
                    resortable_annotations.extend( reordered_annotations )
                    reordering_was_applied = True
                elif keyword.lower() in self._word_to_ordering:
                    reordering = self._word_to_ordering[keyword.lower()]
                    reordered_annotations = \
                        self._reorder_analyses(annotations_by_norm_text[keyword], reordering, add_probs=True)
                    resortable_annotations.extend( reordered_annotations )
                    reordering_was_applied = True
                else:
                    # No match: simply add all annotations with probability/frequency 0.0
                    for anno in annotations_by_norm_text[keyword]:
                        resortable_annotations.append( (anno, 0.0) )
            # 3) If at least one keyword got a reordering, then reorder all analyses
            if reordering_was_applied:
                assert len(resortable_annotations) == len(morph_word.annotations)
                # Re-sort annotations by their probability or frequency
                resortable_annotations=sorted(resortable_annotations,key=lambda x:x[1],reverse=True)
                # Updated word's annotations according to the reordering
                morph_word.clear_annotations()
                for (annotation, prob_or_freq) in resortable_annotations:
                    morph_word.add_annotation( annotation )

