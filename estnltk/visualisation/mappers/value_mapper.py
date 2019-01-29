# tüüpida ja dokumenteerida

def value_mapper_discrete(segment, attribute, value_mapping, default_value, conflict_value) -> str:
    """Function for applying mappings. Arguments are: segment - the same segment that is passed to the visualisers;
    attribute - the attribute of the span of that segment (e.g. "lemma"); value_mapping - dictionary that maps the
    attribute values to the values given to css (e.g. {"kala":"red"}); default_value - value to be returned if
    the attribute value is not in value_mapping; conflict_value - value to be returned if there is an overlapping
    span. Returns the value for the css element."""
    """Does not work for spans with ambigious annotations"""
    if len(segment[1]) != 1:
        return conflict_value

    return value_mapping.get(getattr(segment[1][0],attribute), default_value)

def value_mapper_ambigious(segment, attribute, value_mapping, default_value, conflict_value) -> str:
    """Function for applying mappings to ambigious annotations. Arguments are: segment - the same segment that is
     passed to the visualisers; attribute - the attribute of the span of that segment (e.g. "lemma");
     value_mapping - dictionary that maps the attribute values to the values given to css (e.g. {"kala":"red"}). Note
     that the last elements take priority over first elements if the annotation contains more than one value that is in
     the dictionary and ordered dictionary should be used in that case; default_value - value to be returned if
     the attribute value is not in value_mapping; conflict_value - value to be returned if there is an overlapping
     span. Returns the value for the css element."""
    if len(segment[1]) != 1:
        return conflict_value

    for attr in getattr(segment[1][0],attribute):
        if attr in value_mapping:
            value = value_mapping.get(attr)
    return value or default_value