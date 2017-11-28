from abc import ABC, abstractmethod, abstractproperty
from typing import List


class Tagger(ABC):
    """
    Abstract base class for taggers.
    """

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def layer_name(self) -> str:
        pass

    @property
    @abstractmethod
    def attributes(self) -> List:
        pass

    @property
    @abstractmethod
    def depends_on(self) -> List:
        pass

    @property
    @abstractmethod
    def configuration(self) -> dict:
        pass

    @abstractmethod
    def tag(self, text:'Text', return_layer:bool=False, status:dict={}):
        """
        return_layer: bool, default False
            If True, tagger returns a layer. 
            If False, tagger annotates the text object with the layer and
            returns None.
        status: dict, default {}
            This can be used to store metadata on layer creation.
        """
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
        table = pandas.DataFrame.from_records([self.parameters()], columns=['name', 'layer', 'attributes', 'depends_on'])
        table = table.to_html(index=False)
        if self.configuration:
            table2 = pandas.DataFrame.from_dict(self.configuration, orient='index')
            table2 = table2.to_html(header=False)
            return '\n'.join(('<h4>Tagger</h4>', self.description, table,
                              '<h4>Configuration</h4>', table2))
        else:
            return '\n'.join(('<h4>Tagger</h4>', self.description, table,
                              'No configuration parameters.'))
