from abc import ABC, abstractmethod, abstractproperty
from typing import List

class Tagger(ABC):
    """
    Abstract base class for taggers.
    """

    @abstractproperty
    def description(self) -> str:
        pass

    @abstractproperty
    def layer_name(self) -> str:
        pass

    @abstractproperty
    def attributes(self) -> List:
        pass

    @abstractproperty
    def depends_on(self) -> List:
        pass

    @abstractproperty
    def configuration(self) -> dict:
        pass

    @abstractmethod
    def tag(self, text, return_layer=False, status={}):
        pass

    def parameters(self):
        record = {'name':self.__class__.__name__,
                  'layer':self.layer_name,
                  'attributes':self.attributes,
                  'depends_on':self.depends_on,
                  'configuration':self.configuration}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        table = pandas.DataFrame.from_records([self.parameters()], columns=['name', 'layer', 'attributes', 'depends_on', 'configuration'])
        table = table.to_html(index=False)
        return table + self.description
