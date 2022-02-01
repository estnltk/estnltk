from typing import Sequence, Union
from collections import defaultdict
from estnltk_core.layer.base_layer import BaseLayer


class GroupBy:
    """Groups layer by attribute values of annotations or by an enveloping layer.
    
       The parameter return_type specifies, whether spans or annotations will be 
       grouped. 
       In case of grouping by attribute values, spans or annotations that have 
       the same attribute values will form a group. 
       In case of grouping by enveloping layer, spans or annotations that belong 
       to the same span in the enveloping layer will form a group. 
       """
    
    def __init__(self, layer: Union[BaseLayer, 'Layer'], 
                       by: Union[Sequence[str], Union[BaseLayer, 'Layer']], 
                       return_type: str):
        """Initiates GroupBy object, which groups layer's spans or annotations.
        
           The parameter `layer` is a layer which spans / annotations will 
           be grouped.
           
           The parameter `by` can be:
           *) name of an attribute of `layer`;
           *) list of attribute names of `layer`;
           *) name of a Layer enveloping around `layer`;
           *) Layer object which is enveloping around `layer`;
           Note: you can also use 'text' as an attribute name, 
           which groups spans / annotations by their surface 
           text strings.
           
           The parameter `return_type` specifies, whether "spans" or "annotations" 
           will be grouped.
        """
        self.layer = layer
        self.by = by
        self.return_type = return_type

        groups = defaultdict(list)
        group_by_layer = isinstance(by, BaseLayer)

        if return_type == 'annotations':
            if not group_by_layer:
                # group by attribute values
                for span in layer.spans:
                    for annotation in span.annotations:
                        key = tuple((annotation[k] if k != 'text' else annotation.text) for k in by)
                        groups[key].append(annotation)
            else:
                # group by indexes of the enveloping layer
                for span_id, enveloping_span in enumerate(by):
                    for env_sub_span in enveloping_span.spans:
                        span = layer.get( env_sub_span )
                        if span is not None:
                            for annotation in span.annotations:
                                groups[span_id].append( annotation )

        elif return_type == 'spans':
            if not group_by_layer:
                # group by attribute values
                for span in layer.spans:
                    keys = { tuple((annotation[a] if a != 'text' else annotation.text) \
                                    for a in by ) \
                                       for annotation in span.annotations }
                    for k in keys:
                        groups[k].append(span)
            else:
                # group by indexes of the enveloping layer
                for span_id, enveloping_span in enumerate(by):
                    for env_sub_span in enveloping_span.spans:
                        span = layer.get( env_sub_span )
                        if span is not None:
                            groups[span_id].append( span )
        else:
            raise ValueError("return_type must be 'spans' or 'annotations', got {!r}".format(return_type))

        self._groups = groups

    @property
    def groups(self):
        return self._groups

    @property
    def count(self):
        return {k: len(v) for k, v in self._groups.items()}

    def aggregate(self, func: callable, combiner: callable = None):
        if combiner is None:
            def combiner(spans):
                return spans

        return combiner({key: func(value) for key, value in self._groups.items()})

    def __iter__(self):
        yield from ((key, self._groups[key]) for key in sorted(self._groups))

    def __repr__(self):
        return '{self.__class__.__name__}(layer:{self.layer.name!r}, by={self.by}, return_type={self.return_type!r})'.format(self=self)

