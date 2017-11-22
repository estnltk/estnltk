from estnltk.taggers import Tagger
from estnltk.layer import Layer
from estnltk.layer_operations import resolve_conflicts
from collections import defaultdict


class PhraseListTagger(Tagger):
    """
    Tags phrases on a given layer. Creates an enveloping layer.
    """
    description = 'Tags event sequences.'
    layer_name = None
    attributes = None
    depends_on = None
    configuration = None

    def __init__(self,
                 layer_name:str,
                 input_layer:str,
                 input_attribute:str,
                 phrase_list,
                 attributes=None,
                 decorator=None,
                 consistency_checker=None,
                 conflict_resolving_strategy='MAX',
                 ):
        """Initialize a new EventSequenceTagger instance.

        Parameters
        ----------
        layer_name: str
            The name of the new layer.
        input_layer: str
            The name of the input layer.
        input_attribute: str
            The name of the input layer attribute.
        phrase_list: list of tuples
            input layer attribute value tuples to annotate
        conflict_resolving_strategy: 'ALL', 'MAX', 'MIN' (default: 'MAX')
            Strategy to choose between overlapping events.
        """

        if conflict_resolving_strategy not in ['ALL', 'MIN', 'MAX']:
            raise ValueError("Unknown conflict_resolving_strategy '%s'." % conflict_resolving_strategy)
        self._conflict_resolving_strategy = conflict_resolving_strategy
        self.layer_name = layer_name
        self._input_layer = input_layer
        self._input_attribute = input_attribute
        self.attributes = ()
        if attributes:
            self.attributes = attributes
        def default_decorator(text, span, phrase):
            return {}
        self._decorator = default_decorator
        if decorator:
            self._decorator = decorator
        def default_consistency_checker(text, span, phrase):
            return True
        self._consistency_checker = default_consistency_checker
        if consistency_checker:
            self._consistency_checker = consistency_checker
        
        self.depends_on = [input_layer]
        self.configuration = {}
        self.configuration['input_layer'] = input_layer
        self.configuration['layer_name'] = layer_name
        self.configuration['input_attribute'] = input_attribute
        self.configuration['phrase_list'] = str(len(phrase_list)) + ' phrases'
        self.configuration['attributes'] = attributes
        self.configuration['decorator'] = str(decorator)
        self.configuration['consistency_checker'] = str(consistency_checker)
        self.configuration['conflict_resolving_strategy'] = conflict_resolving_strategy
        
        self.heads = defaultdict(list)
        for phrase in phrase_list:
            self.heads[phrase[0]].append(phrase[1:])


    def tag(self, text, return_layer=False):
        input_layer = text[self._input_layer]
        layer = Layer(
                      name=self.layer_name,
                      attributes = self.attributes,
                      enveloping=self._input_layer,
                      ambiguous=False)
        heads = self.heads
        value_list = getattr(input_layer, self._input_attribute)
        if input_layer.ambiguous:
            for i, values in enumerate(value_list):
                for value in set(values):
                    if value in heads:
                        for tail in heads[value]:
                            if i + len(tail) < len(value_list):
                                match = True
                                for a, b in zip(tail, value_list[i+1:i+len(tail)+1]):
                                    if a not in b:
                                        match = False
                                        break
                                if match:
                                    span = input_layer.spans[i:i+len(tail)+1]
                                    phrase = (value,)+tail
                                    if self._consistency_checker(text, span, phrase):
                                        rec = self._decorator(text, span, phrase)
                                        for attr in self.attributes:
                                            setattr(span, attr, rec[attr])
                                        layer.add_span(span)
        else:
            for i, value in enumerate(value_list):
                if value in heads:
                    for tail in heads[value]:
                        if i + len(tail) < len(value_list):
                            match = True
                            for a, b in zip(tail, value_list[i+1:i+len(tail)+1]):
                                if a != b:
                                    match = False
                                    break
                            if match:
                                span = input_layer.spans[i:i+len(tail)+1]
                                phrase = (value,)+tail
                                if self._consistency_checker(text, span, phrase):
                                    rec = self._decorator(text, span, phrase)
                                    for attr in self.attributes:
                                        setattr(span, attr, rec[attr])
                                    layer.add_span(span)

        resolve_conflicts(layer, conflict_resolving_strategy=self._conflict_resolving_strategy)

        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text
