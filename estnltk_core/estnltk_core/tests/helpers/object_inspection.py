
def inspect_class_members(obj: object):
    """
    Divides class members of an object into subclasses: properties, member functions etc

    Returns a dictionary of class members. Subclasses are built based on two properties:
    * access rights (private, protected, public)
    * member type (variable, property, method)
    """

    properties = []
    public_methods = []
    protected_methods = []
    private_methods = []
    public_variables = []
    protected_variables = []
    private_variables = []
    slots = obj.__slots__[:]
    # include slots of the parent class
    for cls in obj.__class__.__mro__:
        for slot in getattr( cls, "__slots__", [] ):
            if slot not in slots:
                slots.append( slot )
    # extract class members
    for attr in dir(obj):
        if attr in slots:
            pass
        elif isinstance(getattr(type(obj), attr, None), property):
            properties.append(attr)
        elif callable(getattr(obj, attr, None)):
            if attr[:2] == '__':
                private_methods.append(attr)
            elif attr[:1] == '_':
                protected_methods.append(attr)
            else:
                public_methods.append(attr)
        else:
            if attr[:2] == '__':
                private_variables.append(attr)
            elif attr[:1] == '_':
                protected_variables.append(attr)
            else:
                public_variables.append(attr)

    return {'properties': properties, 'private_methods': private_methods,
            'protected_methods': protected_methods, 'public_methods': public_methods,
            'private_variables': private_variables, 'protected_variables': protected_variables,
            'public_variables': public_variables, 'slots': slots}