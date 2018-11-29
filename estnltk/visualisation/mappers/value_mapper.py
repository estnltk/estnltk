def value_mapper_discrete(segment, attribute, value_mapping, default_value, conflict_value):
    if segment[2].length() != 1:
        return conflict_value

    return value_mapping.get(segment[2][0].get_attr(attribute), default_value)