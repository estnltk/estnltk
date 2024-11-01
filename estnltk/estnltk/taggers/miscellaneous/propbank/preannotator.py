#
# Pre-annotates Estonian PropBank semantic roles based on a (manually-crafted) lexicon mapping 
# morph/syntactic features to their respective arguments.
#

import re
import json
import os, os.path

import warnings

from estnltk import Text
from estnltk_core import RelationLayer
from estnltk_core.taggers import RelationTagger

from estnltk.downloader import get_resource_paths

from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger


# Mapping cases from UD lowercase to morph_analysis
ud_to_vm_case_mapping = {
    'nom': 'n', 
    'gen': 'g',
    'par': 'p',
    'ill': 'ill',
    'ine': 'in',
    'ela': 'el',
    'all': 'all', 
    'ade': 'ad',
    'abl': 'abl',
    'tra': 'tr',
    'ter': 'ter',
    'ess': 'es',
    'abe': 'ab',
    'com': 'kom',
    # aditiiv
    'add': 'add'
}

# Mapping cases from UD lowercase to morph_extended
ud_to_morph_ext_case_mapping = {
    'nom': 'nom', 
    'gen': 'gen',
    'par': 'part',
    'ill': 'ill',
    'ine': 'in',
    'ela': 'el',
    'all': 'all', 
    'ade': 'ad',
    'abl': 'abl',
    'tra': 'tr',
    'ter': 'term',
    'ess': 'es',
    'abe': 'abes',
    'com': 'kom',
    # aditiiv
    'add': 'adit'
}


class PropBankPreannotator(RelationTagger):
    """Pre-annotates Estonian PropBank semantic roles based on lexicon mapping morph/syntactic features to arguments."""

    conf_param = ['_lexicon', '_output_display_order',
                  'output_flat_layer',
                  'skip_compound_prt', 
                  'discard_frames_wo_args', 
                  'discard_overlapped_frames', 
                  'add_verb_class',
                  'add_arg_descriptions', 
                  'add_arg_feats',
                  'debug_output']

    def __init__(self,
                 propbank_lexicon: str=None, 
                 output_layer: str='pre_semantic_roles',
                 input_syntax_layer: str='stanza_syntax', 
                 output_flat_layer: bool=False, 
                 discard_frames_wo_args: bool=False, 
                 discard_overlapped_frames: bool=False, 
                 add_verb_class: bool=False,
                 add_arg_descriptions: bool=False,
                 add_arg_feats: bool=False,
                 skip_compound_prt: bool=True, 
                 debug_output: bool=False 
                ):
        '''
        Initializes PropBankPreannotator.

        Parameters
        ----------
        propbank_lexicon: str
            Path to lexicon with mappings from morph/syntactic features to frames and arguments. 
            If not provided, then attempts to download the lexicon automatically from ESTNLTK's 
            resources. 
        output_layer: str
            Name of the output layer.
            Default: 'pre_semantic_roles'
        input_syntax_layer: str
            Name of the input syntax layer. Must be a CONLLU format layer with fields 'deprel', 
            'head' and 'id' conveying dependency syntactic relations among words. 
            If the layer is missing 'children' and 'parent_span' attributes, these will be 
            automatically added via SyntaxDependencyRetagger.
            Default: 'stanza_syntax'
        output_flat_layer: bool 
            Whether the output_layer will be formatted as a flat layer. By default, the output 
            layer is not a flat layer, but an enveloping layer around the input_syntax_layer.
            Default: False
        discard_frames_wo_args: bool
            Whether frames without arguments will be included in the output_layer. 
            Default: False
        discard_overlapped_frames: bool
            Whether frames that are entirely overlapped by a bigger frame should be removed 
            from the output_layer. 
            Note: this is a heuristic and not entirely unharmful. Removing overlapped frames 
            can reduce redundant frames roughly 9 %pt, but with a cost of decreasing correct 
            frame detection accuracy 0.3 %pt (based on measurements on EDT-UD corpus). 
            Default: False
        add_verb_class: bool
            Whether the output_layer has extra attribute 'verb_class' conveying the verb class 
            from the lexicon.
            Default: False
        add_arg_descriptions: bool
            Whether the output_layer contains extra attributes with argument descriptions, 
            named as 'arg0_desc', 'arg1_desc', ... , 'arg5_desc'.
            Default: False
        add_arg_feats:bool
            Whether information about arguments' morph/syntactic features will be added to 
            the output layer, named as  'arg0_feats', 'arg1_feats', ... , 'argm_loc_feats'. 
            These are the features that were used in the frame extraction. 
            Default: False
        skip_compound_prt:bool
            Whether verbs that have a child with 'compound:prt' deprel will be discarded 
            from the output. 
            Default: True
        debug_output: str
            Whether debug information about frame detection will be printed. 
            Default: False
        '''
        # Load lexicon mapping morph/syntactic features to arguments
        self._lexicon = {}
        
        if propbank_lexicon is None:
            # Try to get the resources path for PropBankPreannotator. Attempt to download resources, if missing
            propbank_lexicon = get_resource_paths("propbankpreannotator", only_latest=True, download_missing=True)
            propbank_lexicon = os.path.join(propbank_lexicon, 'propbank_frames.jl') if propbank_lexicon is not None else None
        if propbank_lexicon is None:
            raise Exception('Resources of PropBankPreannotator are missing. '+\
                            'Please use estnltk.download("propbankpreannotator") to download the resources.')
        assert isinstance(propbank_lexicon, str)
        assert os.path.exists(propbank_lexicon), \
            f'(!) Illegal path for propbank_lexicon: {propbank_lexicon}'
        
        with open(propbank_lexicon, 'r', encoding='utf-8') as in_f:
            for entry in in_f:
                #
                # Example entry:
                #
                #  {"sense_id": "eitama_1", 
                #   "lemma": "eitama", 
                #   "class": "KÕNEAKT", 
                #   "description": "", 
                #   "complete": true, 
                #   "arguments": [{"name": "Arg0", "description": "eitaja", "variants": [{"feats": ["deprel=nsubj"]}]}, 
                #                 {"name": "Arg1", "description": "seda", "variants": [{"feats": ["deprel=obj"]}]}]}
                #
                entry = entry.strip()
                if entry.startswith('#'):
                    # Skip comment lines
                    continue
                entry_dict = json.loads(entry)
                lemma = entry_dict['lemma']
                if lemma not in self._lexicon:
                    self._lexicon[lemma] = []
                # TODO: optimize data representation format
                self._lexicon[lemma].append( entry_dict )
        self.output_span_names = ['verb', 'arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'arg5', \
                                  'argm_mnr', 'argm_tmp', 'argm_loc']
        self.output_attributes = ['sense_id']
        self.output_flat_layer = output_flat_layer
        self.output_layer = output_layer
        self.input_layers = [input_syntax_layer]
        self.skip_compound_prt = skip_compound_prt
        self.discard_frames_wo_args = discard_frames_wo_args
        self.discard_overlapped_frames = discard_overlapped_frames
        self.add_verb_class = add_verb_class
        self.add_arg_descriptions = add_arg_descriptions
        self.add_arg_feats = add_arg_feats
        if self.add_verb_class:
            self.output_attributes += ('verb_class',)
        if self.add_arg_descriptions:
            self.output_attributes += ('arg0_desc', 'arg1_desc', 'arg2_desc', 'arg3_desc', 'arg4_desc', 'arg5_desc')
        if self.add_arg_feats:
            self.output_attributes += ('arg0_feats', 'arg1_feats', 'arg2_feats', 'arg3_feats', 'arg4_feats', 'arg5_feats', 
                                       'argm_mnr_feats', 'argm_tmp_feats', 'argm_loc_feats')
        # Set/fix display order
        self._output_display_order = ['verb', 'sense_id']
        if self.add_verb_class:
            self._output_display_order += ['verb_class']
        for arg_name in ['arg0', 'arg1', 'arg2', 'arg3', 'arg4', 'arg5', 'argm_mnr', 'argm_tmp', 'argm_loc']:
            if self.add_arg_descriptions and arg_name[-1].isnumeric():
                self._output_display_order.append(f'{arg_name}_desc')
            self._output_display_order.append(arg_name)
            if self.add_arg_feats:
                self._output_display_order.append(f'{arg_name}_feats')
        self.debug_output = debug_output

    @staticmethod
    def _group_matches_feats(group, feats):
        '''
        Calculates matches between listed features and a group of spans. 
        Returns a dictionary mapping from feats.keys() to corresponding matching 
        spans. 
        Note that currently, each feature will be assigned a single matching 
        span, not more. 
        The output dictionary also includes features which have no matches -- 
        in that case, the value of the feature will be None. 
        '''
        assert isinstance(feats, list) and len(feats) > 0
        assert isinstance(group, tuple) and len(group) > 0
        # Collect matches/mistmatches from all feats
        # Example feats:
        #  "feats": [
        #    "deprel=obl",
        #    "case=Gen",
        #    "casemarker=kohta"
        #  ]
        feats_matches = {}
        for feat_str in feats:
            assert '=' in feat_str
            fname, fval = feat_str.split('=')
            
            if fname == 'deprel':
                # deprel: check only the first member of the group
                # (direct child) for match
                span_deprel = (group[0]).annotations[0]['deprel']
                if span_deprel.lower() == fval.lower():
                    feats_matches[feat_str] = group[0]
            
            elif fname == 'case':
                # Find children with the appropriate case. 
                # Note: this is not necessarily a direct child, 
                # look all children in the group
                for span in group:
                    span_postag = span.annotations[0]['xpostag']
                    span_feats = span.annotations[0]['feats']
                    if span_feats is not None:
                        # Check for UD Case match
                        if 'Case' in span_feats.keys() and \
                           span_feats['Case'] is not None and \
                           span_postag != 'V' and \
                           (span_feats['Case']).lower() == fval.lower():
                            feats_matches[feat_str] = span
                            break
                        # Check for morph_analysis case match
                        ma_case = ud_to_vm_case_mapping.get(fval.lower(), '<missing>')
                        if ma_case in span_feats.keys() and \
                            span_postag != 'V':
                            feats_matches[feat_str] = span
                            break
                        # Check for morph_extended case match
                        me_case = ud_to_morph_ext_case_mapping.get(fval.lower(), '<missing>')
                        if me_case in span_feats.keys() and \
                            span_postag != 'V':
                            feats_matches[feat_str] = span
                            break

            elif fname == 'casemarker':
                # Find children with the appropriate casemarker. 
                # Note: this is not necessarily a direct child, 
                # look all children in the group
                for span in group:
                    span_postag = span.annotations[0]['xpostag']
                    span_lemma = span.annotations[0]['lemma']
                    if span_lemma == fval:
                        feats_matches[feat_str] = span
            
            if feat_str not in feats_matches:
                # no match found
                feats_matches[feat_str] = None
            
        return feats_matches

    @staticmethod
    def get_children(span):
        '''
        Finds direct and specific indirect children of the span. 
        
        Indirect (children of children) are included only if:
        * children have labels ['fixed', 'flat', 'appos'];
        * child is part of pre-position/post-position phrase
        (has 'case' as deprel of one of its child);
        
        Retruns a list of child groups, where each child group 
        is a tuple containing one or more child spans (the first 
        is always the direct child, and the following are indirect 
        children/grand* children).
        '''
        assert span.layer is not None and \
               'children' in span.layer.attributes
        checked = set()
        spans_to_check = list(span.annotations[0]['children'])
        group_ids = [i for i in range(len(spans_to_check))]
        groups = [() for i in range(len(spans_to_check))]
        while spans_to_check:
            c_span = spans_to_check.pop(-1)
            group_id = group_ids.pop(-1)
            if c_span.base_span not in checked:
                collect_children = False
                c_deprel = c_span.annotations[0]['deprel'] or ''
                c_xpostag = c_span.annotations[0]['xpostag'] or ''
                if c_deprel in ['fixed', 'flat', 'appos']:
                    # collect fixed/flat/appos phrases
                    collect_children = True
                #
                # Skip 'conj' children, because they can easily lead 
                # to sub-clauses, and add children of sub-clause verbs,
                # not the current verb.
                #
                #elif c_deprel == 'conj' and c_xpostag != 'V':
                #    # collect conjunctions (excl verb conjunctions)
                #    collect_children = True
                else:
                    # collect pre-position/post-position phrases
                    for child in c_span.annotations[0]['children']:
                        cc_deprel = child.annotations[0]['deprel'] or ''
                        if cc_deprel == 'case':
                            collect_children = True
                            break
                if collect_children:
                    for child in c_span.annotations[0]['children']:
                        spans_to_check.append(child)
                        group_ids.append(group_id)
            checked.add(c_span.base_span)
            # Update group
            groups[group_id] += (c_span, )
        return groups

    @staticmethod
    def _find_mergeable_matches(found_matches):
        '''
        Groups partial matches by common features and checks 
        mergeability of groups. 
        Partial matches will be merged into a group if they 
        collectively match all the features, despite that 
        individually they mismatch one feature or another.
        Returns the merge group that collectively matches all 
        the features, or [] if no such group is found.        
        '''
        # 1) Group matches with the same feats
        groups = {}
        for (feats_matches_bool, feats_matches) in found_matches:
            feats = feats_matches.keys()
            key = '&&&'.join(sorted(feats))
            if key not in groups:
                groups[key] = []
            groups[key].append((feats_matches_bool, feats_matches))
        # 2) Check mergeability of groups
        for group in groups.keys():
            # There should be a match for every feature, 
            # although not necessarily on the same span
            number_of_feats = group.count('&&&') + 1
            group_matches = []
            for i in range( number_of_feats ):
                for (feats_matches_bool, feats_matches) in groups[group]:
                    if feats_matches_bool[i]:
                        # Record match
                        group_matches.append( (feats_matches_bool, feats_matches) )
                        # We got one matching span,
                        # no need to look further
                        break
            # Check if all distinct features got matches
            if number_of_feats == len(group_matches):
                return group_matches
        return []

    @staticmethod
    def _frame_overlap_status(frame_info_a, frame_info_b):
        '''Detects frame overlap status between frames a and b. 
          
           Returns string indicating the status:
           * 'B-in-A' -- B is fully contained within A
                         (and A is bigger than B);
           * 'A-in-B' -- A is fully contained within B
                         (and B is bigger than A);
           * 'A==B' -- A equals B;
           * '' -- undetermined status (could be a partial 
                   overlap or no overlap); 
        '''
        # Extract frame A info
        frame_a_base_span = frame_info_a[1]
        frame_a_args = {}
        for arg_info in frame_info_a[-1]:
            arg_name = arg_info[0]
            arg_spans = [s.base_span for s in arg_info[2]]
            frame_a_args[arg_name] = arg_spans
        # Extract frame B info
        frame_b_base_span = frame_info_b[1]
        frame_b_args = {}
        for arg_info in frame_info_b[-1]:
            arg_name = arg_info[0]
            arg_spans = [s.base_span for s in arg_info[2]]
            frame_b_args[arg_name] = arg_spans
        if frame_a_base_span == frame_b_base_span:
            # Check whether all B spans are within A spans or 
            #       all B spans are within A spans 
            b_within_a = []
            for (arg, spans_b) in frame_b_args.items():
                if arg in frame_a_args and \
                   all([span_b in frame_a_args[arg] for span_b in spans_b]):
                    b_within_a.append( arg )
            a_within_b = []
            for (arg, spans_a) in frame_a_args.items():
                if arg in frame_b_args and \
                   all([span_a in frame_b_args[arg] for span_a in spans_a]):
                    a_within_b.append( arg )
            if len(b_within_a) == len(frame_b_args.keys()) and \
               len(b_within_a) < len(frame_a_args.keys()):
                # B is contained within A
                return 'B-in-A'
            elif len(a_within_b) == len(frame_a_args.keys()) and \
                 len(a_within_b) < len(frame_b_args.keys()):
                # A is contained within B
                return 'A-in-B'
            elif len(a_within_b) == len(b_within_a) and \
                 len(a_within_b) == len(frame_a_args.keys()) and \
                 len(frame_a_args.keys()) == len(frame_b_args.keys()):
                # A equals B
                return 'A==B'
        return ''


    def _extract_frames(self, sentence_syntax):
        '''
        Extracts frames from the given sentence_syntax. 
        The input sentence_syntax should be a list of word spans 
        from an UD syntax_layer. 
        
        Returns a list of frame_info structures, each structure is in 
        the form:
            frame_info = [frame_name, verb_base_span, frame_args]
        where frame_args is a list of frame_arg-s in the format:
            frame_arg = (arg_name, description, arg_spans)
        
        If self.add_verb_class == True, then frame_info comes in the 
        form: [frame_name, verb_base_span, verb_class, frame_args].
        Otherwise, verb_class will be excluded from frame_info.
        
        If self.add_arg_feats == True, then each frame_arg also contains 
        information about matching features, which will be appended at 
        the end of the tuple, e.g. frame_arg = (arg_name, description, 
        arg_spans, arg_feats). Otherwise, the feature information will 
        be excluded. 
        '''
        detected_frames = []
        for syntax_word in sentence_syntax:
            lemma = syntax_word.annotations[0]['lemma']
            xpostag = syntax_word.annotations[0]['xpostag']
            if lemma in self._lexicon and 'V' in xpostag:
                found_matches = dict()
                proceed = True
                if self.skip_compound_prt:
                    # Check for phrasal verb particles: if this is a phrasal verb, then 
                    # exclude it from the tagging 
                    direct_children = list(syntax_word.annotations[0]['children'])
                    for child in direct_children:
                        if child.annotations[0]['deprel'] == "compound:prt":
                            proceed = False
                            break
                if proceed:
                    
                    '''
                    sent_str = ' '.join([sw.text for sw in sentence_syntax])
                    print(f'Detected frame triggering lemma {lemma!r} in {sent_str!r} ...')
                    cg = 1
                    for child_group in PropBankPreannotator.get_children(syntax_word):
                        items = []
                        for child in child_group:
                            span_id = child.annotations[0]['id']
                            span_text = child.text
                            span_deprel = child.annotations[0]['deprel']
                            span_head = child.annotations[0]['head']
                            items.append( f'{span_id}|{span_text!r}|{span_deprel}|{span_head}')
                        print( 'child_group:',cg, items )
                        cg += 1
                    print()
                    '''                    

                    # Collect all matches with direct and specific indirect children
                    for child_group in PropBankPreannotator.get_children(syntax_word):
                        # Find matching frames and matching argument(s)
                        for frame in self._lexicon[lemma]:
                            for arg in frame["arguments"]:
                                for var_dict in arg["variants"]:
                                    # Check matches with all listed features
                                    feats_matches = \
                                        PropBankPreannotator._group_matches_feats(child_group, var_dict['feats'])
                                    feats_matches_bool = \
                                       [v is not None for v in list(feats_matches.values())]
                                    if any( feats_matches_bool ):
                                        # If any of the features matches, record a match
                                        if frame["sense_id"] not in found_matches:
                                            found_matches[frame["sense_id"]] = {}
                                        if arg["name"] not in found_matches[frame["sense_id"]]:
                                            found_matches[frame["sense_id"]][arg["name"]] = []
                                        found_matches[frame["sense_id"]][arg["name"]].append( \
                                            (feats_matches_bool, feats_matches) \
                                        )
                    
                    # Filter matches: 
                    # 1) prioritize full matches
                    # 2) try to merge partial matches
                    # 3) remove incomplete partial matches
                    for frame in found_matches.keys():
                        args_to_remove = []
                        for arg_name in found_matches[frame]:
                            # Get full matches
                            full_matches = \
                                [m for m in found_matches[frame][arg_name] if all(m[0])]
                            if full_matches:
                                found_matches[frame][arg_name] = full_matches
                            else:
                                # Try to find mergeable matches
                                # Note, the method can return [], 
                                # which nullifies found match
                                mergeable_matches = \
                                    PropBankPreannotator._find_mergeable_matches( \
                                        found_matches[frame][arg_name] )
                                found_matches[frame][arg_name] = mergeable_matches
                            if len(found_matches[frame][arg_name]) == 0:
                                # If nothing was found, remove the arg altogether
                                args_to_remove.append(arg_name)
                        if args_to_remove:
                            for arg_name in args_to_remove:
                                del found_matches[frame][arg_name]
                    if self.discard_frames_wo_args:
                        # Remove frames without args if requested
                        for frame in list(found_matches.keys()):
                            if len(found_matches[frame].keys()) == 0:
                                del found_matches[frame]

                    if len(found_matches.keys()) > 0:
                        collected_frame_infos = []
                        for frame_name in found_matches.keys():
                            frame_info = [frame_name, syntax_word.base_span]
                            if self.add_verb_class:
                                # Add verb class
                                for lexicon_frame in self._lexicon[lemma]:
                                    if lexicon_frame["sense_id"] == frame_name:
                                        frame_info += [ lexicon_frame.get("class", None) ]
                                        break
                                assert len(frame_info) == 3
                            frame_info += [[]]
                            for arg_name in found_matches[frame_name]:
                                arg_spans = []
                                arg_feats = []
                                for (feats_matches_bool, feats_matches) in found_matches[frame_name][arg_name]:
                                    for feat_str, span in feats_matches.items():
                                        if span is None:
                                            continue
                                        arg_spans.append(span)
                                        arg_feats.append(feat_str)
                                if arg_spans:
                                    arg_spans = sorted(arg_spans, key=lambda x: x.base_span)
                                    # Remove duplicates (otherwise enveloping span rises an error)
                                    new_arg_spans = []
                                    for arg_span in arg_spans:
                                        if arg_span not in new_arg_spans:
                                            new_arg_spans.append(arg_span)
                                    arg_spans = new_arg_spans
                                    # Collect arg info
                                    arg_info = [arg_name.lower(), arg_spans]
                                    # Add argument description 
                                    description = ''
                                    for frame in self._lexicon[lemma]:
                                        if frame["sense_id"] == frame_name:
                                            for arg in frame["arguments"]:
                                                if arg_name == arg["name"]:
                                                   description = arg.get("description",'')
                                                   break
                                    arg_info = [arg_name.lower(), description, arg_spans]
                                    if self.add_arg_feats:
                                        arg_info.append(arg_feats)
                                    # Add argument to frame
                                    frame_info[-1].append( tuple(arg_info) )
                            collected_frame_infos.append(frame_info)
                        if self.discard_overlapped_frames:
                            if len(collected_frame_infos) > 1:
                                # Detect frames that are entirely overlapped by a bigger frame
                                to_remove = set()
                                for fid_a, frame_a in enumerate(collected_frame_infos):
                                    for fid_b, frame_b in enumerate(collected_frame_infos):
                                        if fid_a != fid_b:
                                            overlap_status = \
                                                PropBankPreannotator._frame_overlap_status(frame_a, frame_b)
                                            if overlap_status == 'B-in-A':
                                                to_remove.add(fid_b)
                                            elif overlap_status == 'A-in-B':
                                                to_remove.add(fid_a)
                                # Remove detected frames
                                if len(to_remove) > 0:
                                    for i in sorted(list(to_remove), reverse=True):
                                        del collected_frame_infos[i]
                        detected_frames.extend(collected_frame_infos)
                        
                    if self.debug_output and len(found_matches.keys()) > 0:
                        # 
                        #    Output debugging information
                        # 
                        starts = [syntax_word.start]
                        ends   = [syntax_word.end]
                        span_to_annotations = dict()
                        display = True
                        for frame in found_matches.keys():
                            for arg_name in found_matches[frame]:
                                for (feats_matches_bool, feats_matches) in found_matches[frame][arg_name]:
                                    for feat_str, span in feats_matches.items():
                                        if span is None:
                                            continue
                                        if span.base_span not in span_to_annotations:
                                            span_to_annotations[span.base_span] = []
                                        starts.append(span.start)
                                        ends.append(span.end)
                                        #if 'casemarker' in feat_str:
                                        #    display = True
                                        span_to_annotations[span.base_span].append( f'{frame} -> {arg_name} -> feat: {feat_str}' )
                        if display:
                            sent_str = ' '.join([sw.text for sw in sentence_syntax])
                            starts = sorted(starts)
                            ends = sorted(ends)
                            for sw2 in sentence_syntax:
                                if starts[0] <= sw2.start and sw2.end <= ends[-1]:
                                    sw_lemma = sw2.annotations[0]['lemma']
                                    sw_postag = sw2.annotations[0]['xpostag']
                                    sw_deprel = sw2.annotations[0]['deprel']
                                    sw_feats = sw2.annotations[0]['feats']
                                    sw_id = sw2.annotations[0]['id']
                                    sw_head = sw2.annotations[0]['head']
                                    local_matches = []
                                    if sw2.base_span in span_to_annotations:
                                        local_matches = span_to_annotations[sw2.base_span]
                                    elif (sw2.start, sw2.end) == (syntax_word.start, syntax_word.end):
                                        local_matches = list(found_matches.keys())
                                    print('   -> ', [sw_id, sw2.text, sw_deprel, sw_head]+local_matches)
                            print()
        return detected_frames

    def _add_frames_to_layer(self, layer, extracted_frames, check_arg_spans:bool=True):
        '''
        Adds extracted frames to the given layer based on the current configuration of the tagger.
        
        If check_arg_spans is True (default), then argument spans are checked for meeting the 
        text bounds, and if any of the spans falls out of the text bounds (probably due to the 
        incorrect assignment of 'parent_span' and 'children' attributes in the input syntax layer), 
        then a warning will be raised. 
        '''
        text = layer.text_object.text
        if not self.output_flat_layer:
            # Create enveloping annotations
            for frame_info in extracted_frames:
                frame_name = frame_info[0]
                base_span = frame_info[1]
                args = frame_info[-1]
                #print(frame_name, base_span)
                annotation_dict = {'verb':[base_span], 'sense_id':frame_name}
                if self.add_verb_class:
                    annotation_dict['verb_class'] = frame_info[2]
                for arg_info in args:
                    arg_name = arg_info[0]
                    desc     = arg_info[1]
                    spans    = arg_info[2]
                    #print(arg_name, desc, spans)
                    spans_str = [s.text for s in spans]
                    annotation_dict[arg_name] = [s.base_span for s in spans]
                    if self.add_arg_descriptions:
                        annotation_dict[f'{arg_name}_desc'] = desc
                    if self.add_arg_feats:
                        annotation_dict[f'{arg_name}_feats'] = arg_info[3]
                    if check_arg_spans:
                        # Check argument spans are inside text boundaries. 
                        # Warn if not (possibly due to wrong parent_span/children)
                        for base_span in annotation_dict[arg_name]:
                            start = base_span.start
                            end = base_span.end
                            if len(text) <= start or len(text) < end:
                                warnings.warn( \
                                    f'(!) Frame {frame_name!r} arg {arg_name!r} matched '+\
                                    f'span {base_span!r} outside text bounds ({len(text)}). '+\
                                    "Please check that 'parent_span' and 'children' attributes "+\
                                    "point to spans correctly.")
                layer.add_annotation( annotation_dict )
        else:
            # Create flat annotations
            for frame_info in extracted_frames:
                frame_name = frame_info[0]
                base_span = frame_info[1]
                args = frame_info[-1]
                #print(frame_name, base_span)
                annotation_dict = {'verb':base_span, 'sense_id':frame_name}
                if self.add_verb_class:
                    annotation_dict['verb_class'] = frame_info[2]
                for arg_info in args:
                    arg_name = arg_info[0]
                    desc     = arg_info[1]
                    spans    = arg_info[2]
                    start = spans[0].start
                    end   = spans[-1].end
                    deprels = [s.annotations[0]['deprel'] for s in spans]
                    spans_str = [s.text for s in spans]
                    #print(arg_name, desc, spans_str)
                    if 'xcomp' in deprels or 'ccomp' in deprels:
                        # If we have clausal complements, then limit 
                        # the phrase only to the first complement
                        annotation_dict[arg_name] = (spans[0].start, spans[0].end)
                    else:
                        annotation_dict[arg_name] = (start, end)
                    if self.add_arg_descriptions:
                        annotation_dict[f'{arg_name}_desc'] = desc
                    if self.add_arg_feats:
                        annotation_dict[f'{arg_name}_feats'] = arg_info[3]
                    if check_arg_spans:
                        # Check argument spans are inside text boundaries. 
                        # Warn if not (possibly due to wrong parent_span/children)
                        (a_start, a_end) = annotation_dict[arg_name]
                        if len(text) <= a_start or len(text) < a_end:
                            warnings.warn( \
                                f'(!) Frame {frame_name!r} arg {arg_name!r} matched '+\
                                f'span {annotation_dict[arg_name]!r} outside text bounds ({len(text)}). '+\
                                "Please check that 'parent_span' and 'children' attributes "+\
                                "point to spans correctly." )
                layer.add_annotation( annotation_dict )
        #print()

    def _make_layer_template(self):
        return RelationLayer(name=self.output_layer, 
                             span_names=self.output_span_names,
                             attributes=self.output_attributes,
                             display_order=self._output_display_order,
                             enveloping=self.input_layers[0] if not self.output_flat_layer else None,
                             ambiguous=True,
                             text_object=None)

    def _make_layer(self, text, layers, status=None):
        layer = self._make_layer_template()
        layer.text_object = text
        syntax_layer = layers[self.input_layers[0]]
        for attr in ['id', 'lemma', 'xpostag', 'feats', 'deprel', 'head']:
            assert attr in syntax_layer.attributes, \
                f'(!) syntax_layer {syntax_layer.name!r} is missing required attribute {attr!r}'
        # Add 'children' & 'parent_span' attributes, if needed
        if 'children' not in syntax_layer.attributes or \
           'parent_span' not in syntax_layer.attributes:
            dep_retagger = \
                SyntaxDependencyRetagger(syntax_layer=syntax_layer.name)
            dep_retagger.retag(text)
        i = 0
        sentence_syntax = []
        while i < len(syntax_layer):
            syntax_word = syntax_layer[i]
            if str(syntax_word.annotations[0]['id']) == '1':
                if sentence_syntax:
                    # process the collected sentence
                    frames = self._extract_frames(sentence_syntax)
                    if frames:
                        # Add frame annotations
                        self._add_frames_to_layer(layer, frames)
                    # start a new sentence 
                    sentence_syntax = []
            sentence_syntax.append(syntax_word)
            i += 1
        # Finish the last sentence
        if sentence_syntax:
            # process the collected sentence
            frames = self._extract_frames(sentence_syntax)
            if frames:
                # Add frame annotations
                self._add_frames_to_layer(layer, frames)
        return layer

