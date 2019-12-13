class AttrDict:
    """
    Base class for Python dictionary where elements can be safely accessed as attributes


    __getitem__,
    __iter__,
    __len__
    __contains__,

    keys,
    items,
    values,
    get,

    __eq__,
    __ne__
    __repr__

    TODO: Explain rules
    """
    __slots__ = ['mapping', '__dict__']
    methods = frozenset(['methods'])

    def __init__(self, **attributes):
        super().__setattr__('mapping', attributes)
        super().__getattribute__('__dict__').update(
            (key, value) for key, value in attributes.items()
            if key not in super(AttrDict, self).__getattribute__('methods'))

    def __setattr__(self, key, value):
        if key in super().__getattribute__('methods'):
            raise AttributeError('attempt to set an attribute that shadows a method {!r}'.format(key))
        super().__setattr__(key, value)
        super().__getattribute__('mapping')[key] = value

    def __delattr__(self, item):
        if item not in super().__getattribute__('__dict__'):
            raise AttributeError('{!r} object has no attribute {!r}'.format(type(self).__name__, item))
        super().__delattr__(item)
        del super().__getattribute__('mapping')[item]

    def __setitem__(self, key, value):
        if key not in super().__getattribute__('methods'):
            super().__setattr__(key, value)
        super().__getattribute__('mapping')[key] = value

    def __delitem__(self, key):
        if key not in super().__getattribute__('mapping'):
            raise KeyError('{!r} object does not have a key {!r}'.format(type(self).__name__, key))
        if key not in super().__getattribute__('methods'):
            super().__delattr__(key)
        del super().__getattribute__('mapping')[key]

    def __getitem__(self, key):
        if key not in super().__getattribute__('mapping'):
            raise KeyError('{!r} object does not have a key {!r}'.format(type(self).__name__, key))
        return super().__getattribute__('mapping')[key]

    def __iter__(self):
        return iter(super().__getattribute__('mapping'))

    def __len__(self):
        return len(super().__getattribute__('mapping'))

    def __contains__(self, item):
        return super().__getattribute__('mapping').__contains__(item)

    def __eq__(self, other):
        return super().__getattribute__('mapping').__eq__(other)

    def __ne__(self, other):
        return super().__getattribute__('mapping').__ne__(other)

    def __repr__(self):
        return "{type}({args})".format(
            type=type(self).__name__,
            args=", ".join("{}={!r}".format(key, value)
                           for key, value in super(AttrDict, self).__getattribute__('mapping').items()))

    def keys(self):
        return super().__getattribute__('mapping').keys()

    def items(self):
        return super().__getattribute__('mapping').items()

    def values(self):
        return super().__getattribute__('mapping').values()

    def get(self, key, default=None):
        return super().__getattribute__('mapping').get(key, default)
