class ImmutableList:
    """Read-only list of (attribute) values.
       Currently this looks like Python tuple.
       The intention is to add features in the future."""
    def __init__(self, attr_list):
        self._list = list(attr_list)

    def __eq__(self, other):
        if isinstance(other, ImmutableList):
            return self._list == other._list
        return False

    def __len__(self):
        return len(self._list)

    def __getitem__(self, item):
        return self._list[item]

    def __repr__(self):
        return repr(self._list)

    def __str__(self):
        return str(self._list)
