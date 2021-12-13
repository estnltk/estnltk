import keyword
from typing import Union, List, Sequence
import pandas
import collections
import warnings
import pkgutil

from copy import deepcopy

from estnltk_core import BaseSpan, ElementaryBaseSpan, EnvelopingBaseSpan
from estnltk_core import Span, Annotation
from estnltk_core.layer import AmbiguousAttributeTupleList, AmbiguousAttributeList, AttributeList
from estnltk_core.layer.base_layer import BaseLayer


def check_if_estnltk_is_available():
    return pkgutil.find_loader("estnltk") is not None


class Layer(BaseLayer):
    """Layer extends BaseLayer with attribute resolving functionality and adds layer operations.
    
       Available layer operations:
       * Find descendant / ancestor layers of the given layer;
       * Count attribute values;
       * group spans or annotations of the layer, either by attributes or by another layer;
       * get rolling window over spans (generate n-grams);
       * visualise markup in text (only available with the full estnltk);
    """

    def ancestor_layers(self):
        if self.text_object is None:
            raise Exception('(!) Cannot find ancestor layers: the layer is detached from Text object.')
        from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies
        ancestors = find_layer_dependencies(self.text_object, self.name, reverse=False)
        return sorted(ancestors)

    def descendant_layers(self):
        if self.text_object is None:
            raise Exception('(!) Cannot find descendant layers: the layer is detached from Text object.')
        from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies
        descendants = find_layer_dependencies(self.text_object, self.name, reverse=True)
        return sorted(descendants)

    def count_values(self, attribute: str):
        """count attribute values, return frequency table"""
        if self.ambiguous:
            return collections.Counter(getattr(annotation, attribute)
                                       for span in self.spans for annotation in span.annotations)
        return collections.Counter(getattr(span, attribute) for span in self.spans)

    def groupby(self, by: Union[str, Sequence[str], 'Layer'], return_type: str = 'spans'):
        import estnltk_core.layer_operations.aggregators as layer_operations
        if isinstance(by, str):
            if by in self.attributes:
                # Group by a single attribute of this Layer
                return layer_operations.GroupBy(layer=self, by=[ by ], return_type=return_type)
            elif self.text_object is not None and by in self.text_object.layers:
                # Group by a Layer (using given layer name)
                return layer_operations.GroupBy(layer=self, by = self.text_object[by], return_type=return_type)
            raise ValueError(by)
        elif isinstance(by, Sequence) and all(isinstance(b, str) for b in by):
            # Group by multiple attributes of this Layer
            return layer_operations.GroupBy(layer=self, by=by, return_type=return_type)
        elif isinstance(by, Layer):
            # Group by a Layer
            return layer_operations.GroupBy(layer=self, by=by, return_type=return_type)
        raise ValueError(by)

    def rolling(self, window: int, min_periods: int = None, inside: str = None):
        import estnltk_core.layer_operations.aggregators as layer_operations
        return layer_operations.Rolling(self, window=window,  min_periods=min_periods, inside=inside)

    def resolve_attribute(self, item):
        if len(self) == 0:
            raise AttributeError(item, 'layer is empty')
        if self._span_list[0].base_span.level == 0:
            attribute_mapping = self.text_object.attribute_mapping_for_elementary_layers
        else:
            attribute_mapping = self.text_object.attribute_mapping_for_enveloping_layers
        if item not in attribute_mapping:
            raise AttributeError(item)

        target_layer = self.text_object[attribute_mapping[item]]
        if len(target_layer) == 0:
            return AttributeList([], item)
        result = [target_layer.get(span.base_span)[item] for span in self]

        target_level = target_layer[0].base_span.level
        self_level = self[0].base_span.level
        if target_level > self_level:
            raise AttributeError(item)
        if target_level == self_level and target_layer.ambiguous:
            return AmbiguousAttributeList(result, item)

        return AttributeList(result, item)

    def __getattr__(self, item):
        if item in self.__getattribute__('attributes'):
            return self.__getitem__(item)
        return self.resolve_attribute(item)

    def display(self, **kwargs):
        if check_if_estnltk_is_available():
            from estnltk.visualisation import DisplaySpans
            display_spans = DisplaySpans(**kwargs)
            display_spans(self)
        else:
            raise NotImplementedError("Layer display is not available in estnltk-core. Please use the full EstNLTK package for that.")


