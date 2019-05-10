from typing import Mapping, Any, Tuple, Sequence


def value_mapper_unique(segment: Tuple[str, Sequence], attribute: str, value_mapping: Mapping[Any, str],
                        default_value: str, conflict_value: str) -> str:
    """A function for defining mappings that assign css-attributes for each span in a layer. 
    
    Keyword arguments:

    segment        -- text segment to be decorated
    attribute      -- the attribute of the span of that segment (e.g. "lemma")
    value_mapping  -- dictionary that maps the attribute value to the value of css attribute (e.g. {"kala":"red"})
    default_value  -- value to be returned if the attribute value is not in the value_mapping
    conflict_value -- value to be returned if the segment is inside the overlap of several spans 

    Returns the value for the css element.

    Important: Can be used only for decorating spans of non-ambigious layers. If a span has several annotations
    the mapper does not know how to map list of attribute values to appropriate css attribute value.

    Example
    -------

    Define a background colour based on the value of a part-of-speech tag

    bg_mapper = lambda s: value_mapper_unique(s,
                    attribute='partofspeech', value_mapping={'S': 'green', 'V': 'yellow', 'O': 'blue'},
                    default_value='gray', conflict_value='red')
    """

    if len(segment[1]) != 1:
        return conflict_value

    return value_mapping.get(getattr(segment[1][0], attribute), default_value)


def value_mapper_ambiguous(segment: Tuple[str, Sequence], attribute: str, value_mapping: Mapping[Any, Tuple[str, int]],
                           default_value: str, conflict_value: str) -> str:
    """A function for defining mappings that assign css-attributes for each span in a layer.

    Keyword arguments:
    segment        -- text segment to be decorated
    attribute      -- the attribute of the span of that segment (e.g. "lemma")
    value_mapping  -- dictionary that maps the attribute value to the value of css attribute and priority
                      (e.g. {"kala": ("red", 1)})
    default_value  -- value to be returned if the attribute value is not in the value_mapping
    conflict_value -- value to be returned if the segment is inside the overlap of several spans 

    Returns the value for the css element.

    Conflict resolving for ambiguous spans
    --------------------------------------

    If the span has several annotations then mapping is applied to all attribute values and the value with the highest
    priority is taken. By convention, all priorities are integers and the highest possible priority is 0.

    Example:
    --------

    Define a background colour based on the value of a part-of-speach tag   

    bg_mapper = lambda s: value_mapper_ambiguous(s,
                    attribute='partofspeech', value_mapping={'S': ('green', 1), 'V': ('yellow', 0), 'O': ('blue', 2)},
                    default_value='gray', conflict_value='red')
    """

    if len(segment[1]) != 1:
        return conflict_value

    # TODO: Update code to reflect documentation
    for attr in getattr(segment[1][0], attribute):
        if attr in value_mapping:
            return value_mapping.get(attr)
    return default_value

# There is a way to write function with signature (segment, attribute, value_mapping_func) but this hides only the
# structure of a segment and thus does not make sense
