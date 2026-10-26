
from estnltk.taggers import Tagger, Retagger
from estnltk import Layer
from collections import defaultdict
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger


class ElativeConstructionChecker(Retagger):
    """
    Tags spans that are part of elative constructions (like "lendurist abikaasa").
    This (re)tagger is for detecting cases where word in locative case is not a location: 
        "rabasin kapist kleiti" - "kapist" is in locative case and is a location, instances like this are correct 
        "rabasin siidist kleiti" - "siidist" is also in locative case but is not a location, 
            therefore "siidist" should be detected by this tagger and potential correction should be "kleiti"
    The words that should be detected are based on a dictionary give by a user. 
    The dictionary is expected to include of common words and potential matches to it that form the incorrect instance. 
        For example {"lendurist":["abikaasa", "isa"], "treenerist": ["isa", "ema", ..], ...}

    Returns/modifies morphosyntax_conflicts layer with attributes:
    * {id} -- id form stanza layer;
    * {lemma} -- lemma from Vabamorf / "morph_analysis" layer;
    * {root_tokens} -- root_tokens from Vabamorf / "morph_analysis" layer;
    * {clitic} -- clitic from Vabamorf / "morph_analysis" layer;
    * {xpostag} -- partofspeech from Vabamorf / "morph_analysis" layer;
    * {feats} -- form from Vabamorf / "morph_analysis" layer;
    * {extended_feats} -- form from"morph_extended" layer;
    * {head} {deprel} -- form stanza layer;
    * {parent_span} {children} -- form stanza layer if "add_parent_and_children=True";
    * {stanza_pos} {stanza_feats} {stanza_lemma} - from stanza layer; might be removed later on.

    This tagger works either as a tagger (A) or as a retagger (B), depending on 
       whether the flag <code>use_retag</code> is disabled or enabled. As a Tagger, 
       it creates a new morphological conflicts layer, while as a Retagger, it adds to  
       an existing morphological conflicts layer. 
       
       A) If <code>use_retag</code> is False, then the tagger works as a tagger and 
       a new layer (<code>output_layer</code>) can be created by calling tagger's 
       tag(...) or make_layer(...) methods. 
       
       B) If <code>use_retag</code> is True, then <code>output_layer</code> must be set 
       to an existing morphological conflicts layer (which will become an input layer) and which then 
       can be expanded by calling tagger's retag(...) or change_layer(...) methods. 
    
    """

    conf_param = [ 'output_layer',  "morphosyntax_layer", "input_layers", "use_retag", "elative_dict"]
    output_attributes = ['id', 'lemma', 'root_tokens', 'clitic', 'xpostag', 'feats', 'extended_feats', 'head', 'deprel', 'error_type', 'match_type', 'correction']

    def __init__(self,
                morphosyntax_layer = None,
                output_layer:str="morphosyntax_conflicts",
                input_layers=[],
                use_retag:bool = False,
                elative_dict: dict = {},
                ):
        """Initialize ElativeConstructionChecker class.
        
        Parameters
        ----------
        output_layer: str (default: 'morphosyntax')
            Name of the layer where analysis results are stored.
        input_layers: List[str] (default: ['words'])
            Names of the input words and sentences layers.
        morphosyntax_layer: str (default: None)
            Name of the existing morphosyntax layer where conflicts will be searched from.
        use_retag: bool (default False)
            if True then expands and existing conflicts layer 
            if False then creates new conflicts layer 
        """
        self.output_layer = output_layer
        self.input_layers=input_layers
        self.morphosyntax_layer = morphosyntax_layer
        self.use_retag = use_retag 
        self.elative_dict = elative_dict

        if self.use_retag:  
            self.input_layers.append( self.output_layer ) # if tagger.retag() is used


    def _make_layer_template(self):
        
        layer = Layer(name=self.output_layer, text_object=None, 
                     attributes=self.output_attributes, parent=self.morphosyntax_layer, 
                     ambiguous=True)
        layer.layer.serialisation_module = syntax_v0.__version__
        return layer 

    
    def _make_layer(self, text, layers, status=None):

        layer = self._make_layer_template()
        layer.text_object = text

        stokens = text[self.morphosyntax_layer].spans 
        results = self._find_semantic_pairs(stokens, self.elative_dict)
        for res in results:
            annotations = res[0].annotations[0]
            annotation_dict = {}
            for elem in annotations.keys():
                annotation_dict[elem] = annotations[elem]
            annotation_dict["error_type"] = "elative"
            annotation_dict["match_type"] = res[2]
            annotation_dict["correction"] = res[1]
            layer.add_annotation(res[0].base_span, annotation_dict)

        return layer


    def _change_layer(self, text, layers, status=None):

        assert self.output_layer in text.layers, f"Missing {self.output_layer} layer!"

        conflicts_layer = layers[self.output_layer]
        
        stokens = text[self.morphosyntax_layer].spans 
        results = self._find_semantic_pairs(stokens, self.elative_dict)
        for res in results:
            annotations = res[0].annotations[0]
            annotation_dict = {}
            for elem in annotations.keys():
                annotation_dict[elem] = annotations[elem]
            annotation_dict["error_type"] = "elative"
            annotation_dict["match_type"] = res[2]
            annotation_dict["correction"] = res[1]
            conflicts_layer.add_annotation(res[0].base_span, annotation_dict)


    def _find_semantic_pairs(self, tokens, obl_dict):

        """
        Checks the span accoring to the rules (obl_dict). 
        """
        children = defaultdict(list)
        siblings = defaultdict(list)

        for t in tokens:
            children[t["head"]].append(t)
            siblings[t["head"]].append(t)

        results = []
        linear_results = []

        
        def find_descendant_match(root, targets):
            stack = [root]
            while stack:
                node = stack.pop()
                if node.text in targets or node["lemma"] in targets:
                    return node
                stack.extend(children[node["id"]])
            return None

        
        def find_linear_match(obl, targets):
            """
            Cases:
                lendurist abikaasa
                lendurist vana abikaasa
                lendurist väga vana abikaasa
            Should work even if syntax tree is faulty
            
            Also potential matches:
            lendurist kalkunikasvataja
            lendurist vana kalkunikasvataja
            
            Returns:
                real_match, potential_match
            """

            #TODO: there should be a validator for potential matches (gpt or wordnet etc)

            # copilot recommendations
            allowed_between = {
                "amod",     # adjective modifier
                "advmod",   # väga
                "det",      # see, tema, üks ...
                "nummod"
            }

            potential_match = None
            
            i = obl["id"]
            while i < len(tokens):
                tok = tokens[i]
                # target
                if tok.text in targets or tok["lemma"] in targets:
                    return tok, potential_match
                # firts noun that is not in target list 
                if potential_match is None and tok["upostag"]=="S":
                    potential_match = tok
                # adjectives etc 
                if tok["upostag"] in {"A", "D", "P", "N"}: #{"ADJ", "ADV", "DET", "NUM"}:
                    i += 1
                    continue
                if tok["deprel"] in allowed_between:
                    i += 1
                    continue
                # no target match but found potential
                if potential_match is not None:
                    break
                # not adjective etc and not target 
                if tok["upostag"] not in {"A", "D", "P", "N"}:
                    break
                i += 1
            return None, potential_match

        
        for obl in tokens:
            if obl["deprel"] != "obl":
                continue

            targets = obl_dict.get(obl.text) or obl_dict.get(obl["lemma"])
            if not targets:
                continue

            # linear match based on word order in sentence: lendurist [ADJ*] abikaasa
            # in case synta xtree is faulty or to find potential matches 
            linear_match, potential_match = find_linear_match(obl, targets)

            move_next_match = None
            move_further_match = None
                
            # parse syntax tree
            for sib in siblings[obl["head"]]:

                # search only after obl 
                if sib["id"] <= obl["id"]:
                    continue

                # obl and match are direct children of the verb: case /\
                if sib.text in targets or sib["lemma"] in targets:
                    #results.append((obl, sib, "move_next"))
                    move_next_match = sib
                    break
                    
                # obl is verb's direct child but the target is not  
                # target has at least one parent before verb: case / ... \
                further_match = find_descendant_match(sib, targets)
                if further_match: # and match["deprel"] in ["obl", "nmod", "subj", "nsubj"]:
                    move_further_match = further_match
                    break

                    
            # linear_match is the same as move_next, keep latter 
            if linear_match is not None and move_next_match is not None and linear_match["id"]==move_next_match["id"]:
                results.append((obl, move_next_match, "move_next"))

            # linear_match is the same as move_further, keep latter
            elif linear_match is not None and move_further_match is not None and linear_match["id"]==move_further_match["id"]:
                results.append((obl, move_further_match, "move_further"))
                
            elif linear_match is not None:
                results.append((obl, linear_match, "linear_match"))

            elif move_next_match is not None:
                results.append((obl, move_next_match, "move_next"))

            elif move_further_match is not None:
                results.append((obl, move_further_match, "move_further"))
                
            elif potential_match is not None:
                results.append((obl, potential_match, "potential_match"))
        
        return results
        
        





