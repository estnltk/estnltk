import keyword
import warnings
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
from estnltk_core.layer_operations.layer_dependencies import find_layer_dependencies
from estnltk_core.layer_operations.aggregators import GroupBy
from estnltk_core.layer_operations.aggregators import Rolling

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

    def __setattr__(self, key, value):
        if key == 'attributes':
            # check attributes: add userwarnings in case of 
            # problematic attribute names
            attributes = value
            if isinstance(attributes, (list, tuple)) and all([isinstance(attr,str) for attr in attributes]):
                # Warn if user wants to use non-identifiers as argument names
                nonidentifiers = [attr for attr in attributes if not attr.isidentifier()]
                if nonidentifiers:
                    warnings.warn(('Attribute names {!r} are not valid Python identifiers. '+\
                                   'This can hinder setting and accessing attribute values.'+\
                                   '').format(nonidentifiers))
                # Warn if user wants to use 'text', 'start', 'end' as attribute names
                overlapping_props = [attr for attr in attributes if attr in ['text', 'start', 'end']]
                if overlapping_props:
                    warnings.warn(('Attribute names {!r} overlap with Span/Annotation property names. '+\
                                   'This can hinder setting and accessing attribute values.'+\
                                   '').format(overlapping_props))
        super().__setattr__(key, value)

    def ancestor_layers(self) -> List[str]:
        """Finds all layers that given layer depends on (ancestor layers).
           Returns names of ancestor layers in alphabetical order.
        """
        if self.text_object is None:
            raise Exception('(!) Cannot find ancestor layers: the layer is detached from Text object.')
        ancestors = find_layer_dependencies(self.text_object, self.name, reverse=False)
        return sorted(ancestors)

    def descendant_layers(self) -> List[str]:
        """Finds all layers that are depending on the given layer (descendant layers).
           Returns names of descendant layers in alphabetical order.
        """
        if self.text_object is None:
            raise Exception('(!) Cannot find descendant layers: the layer is detached from Text object.')
        descendants = find_layer_dependencies(self.text_object, self.name, reverse=True)
        return sorted(descendants)

    def count_values(self, attribute: str) -> collections.Counter:
        """Counts attribute values and returns frequency table (collections.Counter). 
           Note: you can also use 'text' as the attribute name to count corresponding 
           surface text strings.
        """
        if self.ambiguous:
            return collections.Counter(annotation[attribute] if attribute != 'text' else annotation.text \
                                                  for span in self.spans for annotation in span.annotations)
        return collections.Counter( span.annotations[0][attribute] if attribute != 'text' else span.text \
                                                                      for span in self.spans)

    def groupby(self, by: Union[str, Sequence[str], 'Layer'], return_type: str = 'spans') -> GroupBy:
        """Groups layer by attribute values of annotations or by an enveloping layer.

           Parameters
           -----------
           by: Union[str, Sequence[str], 'Layer']
                specifies basis for grouping, which can be either
                matching attribute values or containment in an
                enveloping span. More specifically, the parameter
                `by` can be::
                1) name of an attribute of this layer,
                2) list of attribute names of this layer,
                3) name of a Layer enveloping around this layer, or
                4) Layer object which is a layer enveloping around this layer.
                Note: you can also use 'text' as an attribute name; in that
                case, spans / annotations are grouped by their surface text
                strings.

           return_type: str (default: 'spans')
                specifies layer's units which will be grouped.
                Possible values: "spans" or "annotations".

           Returns
           --------
           estnltk_core.layer_operations.GroupBy
                estnltk_core.layer_operations.GroupBy object.
        """
        if isinstance(by, str):
            if by in self.attributes:
                # Group by a single attribute of this Layer
                return GroupBy(layer=self, by=[ by ], return_type=return_type)
            elif self.text_object is not None and by in self.text_object.layers:
                # Group by a Layer (using given layer name)
                return GroupBy(layer=self, by = self.text_object[by], return_type=return_type)
            raise ValueError(by)
        elif isinstance(by, Sequence) and all(isinstance(b, str) for b in by):
            # Group by multiple attributes of this Layer
            return GroupBy(layer=self, by=by, return_type=return_type)
        elif isinstance(by, Layer):
            # Group by a Layer
            return GroupBy(layer=self, by=by, return_type=return_type)
        raise ValueError( ('Unexpected grouping parameter by={!r}. The parameter '+\
                           'should be either an enveloping Layer (layer name or object) '+\
                           'or attribute(s) of this layer (a single attribute name '+\
                           'or a list of names).').format(by) )

    def rolling(self, window: int, min_periods: int = None, inside: str = None) -> Rolling:
        """Creates an iterable object yielding span sequences from a window rolling over the layer.

           Parameters
           -----------
           window
                length of the window (in spans);
           min_periods
                the minimal length of the window for borderline cases;
                allows to shrink the window to meet this minimal length. If not specified,
                then `min_periods == window`, which means that the shrinking is not allowed,
                and contexts smaller than the `window` will be discarded.
                Note: `0 < min_periods <= window` must hold;
           inside
                an enveloping layer to be used for constraining the rolling window.
                The rolling window is applied on each span of the enveloping layer separately,
                thus ensuring that the window does not exceed boundaries of enveloping spans.
                For instance, if you create a rolling window over 'words', you can specify
                inside='sentences', ensuring that the generated word N-grams do not exceed
                sentence boundaries;

           Returns
           --------
           estnltk_core.layer_operations.Rolling
                estnltk_core.layer_operations.Rolling object.
        """
        return Rolling(self, window=window, min_periods=min_periods, inside=inside)

    def resolve_attribute(self, item) -> Union[AmbiguousAttributeList, AttributeList]:
        """Resolves and returns values of foreign attribute `item`.
           
           Values of the attribute will be sought from a foreign layer, 
           which must either: 
           a) share the same base spans with this layer (be a parent or a child), or 
           b) share the same base spans with smaller span level, which means that 
              this layer should envelop around the foreign layer.
           
           Note: this method relies on a mapping from attribute names to 
           foreign layer names (`attribute_mapping_for_elementary_layers`), 
           which is defined estnltk's `Text` object. If this layer is attached 
           to estnltk-core's `BaseText` instead, then the method always raises 
           AttributeError.
        """
        if len(self) == 0:
            raise AttributeError(item, 'layer is empty')
        attribute_mapping = {}
        if self.text_object is not None:
            if hasattr(self.text_object, 'attribute_mapping_for_elementary_layers'):
                # Attribute mapping for elementary layers is only 
                # defined in Text object, it is missing in BaseText
                if self.span_level == 0:
                    attribute_mapping = self.text_object.attribute_mapping_for_elementary_layers
                else:
                    attribute_mapping = self.text_object.attribute_mapping_for_enveloping_layers
            else:
                raise AttributeError(item, "Foreign attribute resolving is only available "+\
                                           "if the layer is attached to estnltk.text.Text object.")
        else:
            raise AttributeError(item, \
                "Unable to resolve foreign attribute: the layer is not attached to Text object." )
        if item not in attribute_mapping:
            raise AttributeError(item, \
                  "Attribute not defined in attribute_mapping_for_elementary_layers.")

        target_layer = self.text_object[attribute_mapping[item]]
        if len(target_layer) == 0:
            return AttributeList([], item)
        result = [target_layer.get(span.base_span) for span in self]

        target_level = target_layer.span_level
        self_level = self.span_level
        if target_level > self_level:
            raise AttributeError(item, \
                  ("Unable to resolve foreign attribute: target layer {!r} has higher "+\
                   "span level than this layer.").format( target_layer.name ) )
        if target_level == self_level and target_layer.ambiguous:
            assert all([isinstance(s, Span) for s in result])
            return AmbiguousAttributeList(result, item)
        assert all([isinstance(l, BaseLayer) for l in result])
        return AttributeList(result, item, index_type='layers')

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


