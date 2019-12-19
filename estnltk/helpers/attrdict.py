from collections import Mapping


class AttrDict:
    """
    Base class for a Python dictionary where elements can be safely accessed as attributes

    The implementation has the same methods as an abstract container Mapping.
    The attribute access is implemented so that one can specify a set of attributes that cannot be defined.
    By default all methods of AttrDict class are protected.

    For a subclass, the set of protected attributes should be defined through a class variable methods.
    The set should contain all methods and variable methods for safety.
    The best way to define them is an idiom  methods = AttrDict.methods | {...}

    A safe way to add keys of one AttrDict to another is through update function.

    The class does not implement separate copy, deepcopy and pickling methods as it is an abstract base class.
    All subclasses should contain corresponding methods for safety and correctness.
    """
    __slots__ = ['mapping', '__dict__']
    methods = frozenset(['__doc__', '__hash__', '__module__', '__slots__',
                         '__setitem__', '__getitem__', '__delitem__',
                         '__iter__', '__len__', '__contains__', '__repr__',
                         'keys', 'items', 'values', 'get', 'update', 'methods']
                        + __slots__ + [method for method in dir(object) if callable(getattr(object, method, None))])

    def __init__(self, **attributes):
        super().__setattr__('mapping', attributes)
        super().__getattribute__('__dict__').update(
            (key, value) for key, value in attributes.items()
            if key not in super(AttrDict, self).__getattribute__('methods'))

    def __setattr__(self, key, value):
        if key in super().__getattribute__('methods'):
            raise AttributeError('attempt to set an attribute that shadows a method {!r}'.format(key))
        super().__setattr__(key, value)
        if key not in super().__getattribute__('__slots__'):
            super().__getattribute__('mapping')[key] = value

    def __delattr__(self, item):
        if item not in super().__getattribute__('__dict__'):
            raise AttributeError('{!r} object has no attribute {!r}'.format(type(self).__name__, item))
        super().__delattr__(item)
        del super().__getattribute__('mapping')[item]

    def __setitem__(self, key, value):
        if key not in super().__getattribute__('methods') and key not in super().__getattribute__('__slots__'):
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

    def update(self, other_dict):
        if isinstance(other_dict, AttrDict):
            super().__getattribute__('mapping').update(super(AttrDict, other_dict).__getattribute__('mapping'))
            super().__getattribute__('__dict__').update(super(AttrDict, other_dict).__getattribute__('__dict__'))
        elif isinstance(other_dict, Mapping):
            methods = super().__getattribute__('methods')
            super().__getattribute__('mapping').update(other_dict)
            super().__getattribute__('__dict__').update(
                (key, value) for key, value in other_dict.items() if key not in methods)
        else:
            raise TypeError("Argument 'other_dict' must be of type AttrDict or Mapping but not {!r}"
                            .format(type(other_dict)))
