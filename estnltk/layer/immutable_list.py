class ImmutableList:
    """Currently this looks like Python tuple.
    The intention is to add features in the feature."""
    def __init__(self, attr_list):
        self._list = list(attr_list)

    def __getitem__(self, item):
        return self._list[item]

    def __repr__(self):
        return repr(self._list)

    def __str__(self):
        return str(self._list)
