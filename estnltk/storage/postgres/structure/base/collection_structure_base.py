class CollectionStructureBase:
    def __init__(self, collection):
        self.collection = collection

        self._structure = None
        self._modified = True
        self.load()

    def __bool__(self):
        return bool(self.structure)

    def __iter__(self):
        yield from self.structure

    def __contains__(self, item):
        return item in self.structure

    def __getitem__(self, item):
        return self.structure[item]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.structure == other.structure
        return False

    @property
    def structure(self):
        if self._modified:
            self._structure = self.load()
            self._modified = False
        return self._structure

    def create_table(self):
        raise NotImplementedError

    def insert(self, layer, layer_type: str, meta: dict = None, loader: str = None):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError
