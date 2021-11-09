from typing import Sequence, Union
from collections import defaultdict
from estnltk_core.layer.layer import Layer, SpanList


class GroupBy:
    """Groups layer by attribute values of annotations or by an enveloping layer.
    
       The parameter return_type specifies, whether spans or annotations will be 
       grouped. 
       In case of grouping by attribute values, spans or annotations that have 
       the same attribute values will form a group. 
       In case of grouping by enveloping layer, spans or annotations that belong 
       to the same span in the enveloping layer will form a group. 
       """
    
    def __init__(self, layer: Layer, by: Union[Sequence[str], Layer], return_type: str):
        self.layer = layer
        self.by = by
        self.return_type = return_type

        groups = defaultdict(list)
        group_by_layer = isinstance(by, Layer)

        if return_type == 'annotations':
            if not group_by_layer:
                # group by attribute values
                for span in layer.spans:
                    for annotation in span.annotations:
                        key = tuple(getattr(annotation, k) for k in by)
                        groups[key].append(annotation)
            else:
                # group by indexes of the enveloping layer
                for span_id, enveloping_span in enumerate(by):
                    span_list = SpanList()
                    for env_sub_span in enveloping_span.spans:
                        span = layer.get( env_sub_span )
                        if span is not None:
                            for annotation in span.annotations:
                                groups[span_id].append( annotation )

        elif return_type == 'spans':
            if not group_by_layer:
                # group by attribute values
                for span in layer.spans:
                    keys = {tuple(getattr(annotation, a) for a in by) for annotation in span.annotations}
                    for k in keys:
                        groups[k].append(span)
            else:
                # group by indexes of the enveloping layer
                for span_id, enveloping_span in enumerate(by):
                    span_list = SpanList()
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


def group_by_layer(layer: Layer, by: Layer):
    """Groups layer's spans by an enveloping layer.
    
    :param layer: Layer
        Layer which spans will be grouped;
    :param by: Layer
        Layer that envelopes the groupable layer.
    :return:
        iterator of SpanList
    """
    for enveloping_span in by:
        span_list = SpanList()
        for span in enveloping_span.spans:
            sp = layer.get(span)
            if sp is not None:
                span_list.add_span(sp)
        yield span_list
