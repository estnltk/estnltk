from abc import ABC, abstractmethod, abstractproperty

class Tagger(ABC):
    """
    Abstract base class for taggers.
    """

    @abstractproperty
    def layer_name(self):
        return

    @abstractproperty
    def attributes(self):
        return ()

    @abstractproperty
    def depends_on(self):
        return ()

    @abstractproperty
    def parameters(self):
        return {}

    @abstractmethod
    def tag(self, text, return_layer=False, status={}):
        pass

    def configuration(self):
        record = {'name':self.__class__.__name__,
                  'layer':self.layer_name,
                  'attributes':self.attributes,
                  'depends_on': self.depends_on,
                  'parameters':self.parameters}
        return record

    def _repr_html_(self):
        import pandas
        pandas.set_option('display.max_colwidth', -1)
        df = pandas.DataFrame.from_records([self.configuration()], columns=['name', 'layer', 'attributes', 'depends_on', 'parameters'])
        return df.to_html(index=False)
