
from estnltk.taggers import Tagger
from estnltk import Layer
from estnltk.converters.serialisation_modules import syntax_v0

class BasicConsistencyChecker(Tagger):
    """
    Tags spans that contain conflicts between morph and syntax attributes.
    
    Returns morphosyntax layer with attributes:
    * {id} -- id form stanza layer;
    * {lemma} -- lemma from Vabamorf / "morph_analysis" layer;
    * {root_tokens} -- root_tokens from Vabamorf / "morph_analysis" layer;
    * {clitic} -- clitic from Vabamorf / "morph_analysis" layer;
    * {xpostag} -- partofspeech from Vabamorf / "morph_analysis" layer;
    * {feats} -- form from Vabamorf / "morph_analysis" layer;
    * {extended_feats} -- form from"morph_extended" layer;
    * {head} {deprel} -- form stanza layer;
    * {parent_span} {children} -- form stanza layer if "add_parent_and_children=True";
    * {error_type} -- type of error to differentiate between errors found by different taggers 
    * {stanza_pos} {stanza_feats} {stanza_lemma} - from stanza layer; might be removed later on.
    """

    conf_param = [ 'output_layer',  "morphosyntax_layer", "input_layers"]
    output_attributes = ['id', 'lemma', 'root_tokens', 'clitic', 'xpostag', 'feats', 'extended_feats', 'head', 'deprel',  'error_type'] # 'parent_span', 'children', , 'stanza_pos', 'stanza_feats', 'stanza_lemma'
    input_layers = ("words",)

    def __init__(self,
                morphosyntax_layer = None,
                 output_layer:str="morphosyntax_conflicts",
                 input_layers=input_layers,
                ):
        """Initialize VabamorfWithBertTagger class.
        
        Parameters
        ----------
        output_layer: str (default: 'morphosyntax')
            Name of the layer where analysis results are stored.
        input_layers: List[str] (default: ['words'])
            Names of the input words and sentences layers.
        morphosyntax_layer: str (default: None)
            Name of the existing morphosyntax layer where conflicts will be searched from.
        """
        self.output_layer = output_layer
        self.input_layers=input_layers
        self.morphosyntax_layer = morphosyntax_layer


    def _make_layer_template(self):
        return Layer(name=self.output_layer, text_object=None, 
                     attributes=self.output_attributes, parent=self.morphosyntax_layer, 
                     ambiguous=True)

    
    def _make_layer(self, text, layers, status=None):

        layer = self._make_layer_template()
        layer.text_object = text

        for sp in layers[self.morphosyntax_layer]:
            correct = self._check_consistency(sp)
            if not correct:
                annotations = sp.annotations[0]
                annotation_dict = {}
                for elem in annotations.keys():
                    annotation_dict[elem] = annotations[elem]
                annotation_dict["error_type"] = "basic"
                layer.add_annotation(sp.base_span, annotation_dict)

        return layer


    def _check_consistency(self, span):

        """
        Checks the span accoring to the rules. 
        Rules should be added in this function for now.
        """
        annotations = span.annotations[0]
        #feats = annotations["extended_feats"].split(",") # uuema versiooni jaoks
        feats = annotations["feats"].keys() # vanem versioon 
        deprel = annotations["deprel"]

        # when nsubj is not in nominative/partitive case
        if deprel == 'nsubj' and 'nom' not in feats and 'part' not in feats:
            return False

        # when nsubj:cop is not in nominative/partitive case
        if deprel ==  'nsubj:cop' and 'nom' not in feats and 'part' not in feats:
            return False

        # when obj is not in nominative/genitive/partitive case
        if deprel == 'obj' and 'nom' not in feats and 'part' not in feats and 'gen' not in feats:
            return False 

        # when advcl has case marking
        if deprel == 'advcl' and len(feats) != 0:
            return False

        # when advmod has case marking
        if deprel == 'advmod'  and len(feats) != 0:
            return False

        # when xcomp has case marking
        if deprel == 'xcomp' and  len(feats) != 0:
            return False

        # when obl is in nominative case
        if deprel == 'obl' and 'nom' in feats:
            return False
        
        return True
