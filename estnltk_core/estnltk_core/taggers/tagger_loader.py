from typing import Sequence, Union, Dict, Any

import importlib, importlib.util

from estnltk_core.taggers.tagger import Tagger
from estnltk_core.taggers.retagger import Retagger

class TaggerClassNotFound(Exception):
    pass

DEFAULT_DESCRIPTION = 'No description provided.'

class TaggerLoader:
    """TaggerLoader describes tagger's input layers, output layer and importing path, and allows to load the tagger on demand.
       
       Usage example
       --------------
       >>> from estnltk_core.taggers.tagger_loader import TaggerLoader
       >>> tl = TaggerLoader('morph_analysis', ['words', 'sentences', 'compound_tokens'], 
       ...                   'estnltk.taggers.standard.morph_analysis.morf.VabamorfTagger')
       >>> vm_tagger = tl.tagger
       >>> vm_tagger
       VabamorfTagger(('words', 'sentences', 'compound_tokens')->morph_analysis)
       
       Note: TaggerLoader does not validate that declared inputs and output match with the actual inputs and 
       output of the tagger after it has been loaded. This validation should be done by users of the class. 
    """
    __slots__ = ['output_layer', 'input_layers', 'import_path', 'output_attributes', 'description',
                 '_parameters', '_tagger', '_tagger_class_name', '_tagger_module_path']

    def __init__(self, output_layer:str, input_layers:Sequence[str], import_path:str, 
                       parameters:Dict[str, Any]={}, output_attributes:Sequence[str]=None, 
                       description:str=DEFAULT_DESCRIPTION):
        """Initializes TaggerLoader, which can be used to load given Tagger/Retagger on demand.
        
        Parameters
        ----------
        output_layer:str
            name of the layer produced (or modified) by the tagger, once it has been imported.
        input_layers:Sequence[str]
            names of layers required by this tagger as an input.
        import_path:str
            full import path of the Tagger/Retagger.
        parameters:Dict[str, Any]
            dictionary with constructor parameters to be passed to the tagger upon initialization.
            optional, defaults to {}.
        output_attributes: Sequence[str]
            attributes of the layer produced by the tagger.
            optional, defaults to None.
        description:str
            description of the tagger / layer. 
            optional, defaults to "No description provided."
        """
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.import_path = import_path
        self.output_attributes = output_attributes
        self.description = description
        self._parameters = parameters
        if '.' in import_path:
            path_tokens = import_path.split('.')
            self._tagger_class_name = path_tokens[-1]
            self._tagger_module_path = '.'.join( path_tokens[:-1] )
        else:
            raise ValueError('Unexpected import_path {!r}: should be a full path to the Tagger/Retagger class.'.format(import_path))
        self._tagger = None

    def __copy__(self):
        raise NotImplementedError('__copy__ method not implemented in ' + self.__class__.__name__)

    def __deepcopy__(self, memo={}):
        raise NotImplementedError('__deepcopy__ method not implemented in ' + self.__class__.__name__)

    def _load_tagger(self):
        assert not isinstance(self._tagger, (Tagger, Retagger)), \
            '(!) Tagger {} is already loaded'.format(self._tagger_class_name)
        module = None
        tagger_class = None
        tagger = None
        # First, try to load the module
        try:
            module_spec = importlib.util.find_spec( self._tagger_module_path )
            if module_spec:
                module = importlib.import_module( self._tagger_module_path )
        except ModuleNotFoundError as module_err:
            raise ModuleNotFoundError( ("(!) Unable to load {!r}. "+\
                                            "Please check that the module path {!r} is correct.").format( self._tagger_class_name, 
                                                                                                          self._tagger_module_path )) from module_err
        except:
            raise
        # Second, try to load the class from the module
        if module is not None:
            try:
                tagger_class = getattr(module, self._tagger_class_name )
            except AttributeError as attr_err:
                raise TaggerClassNotFound( ("(!) Unable to load {!r} from the module {!r}. "+\
                                            "Please check that the Tagger's name and path are correct.").format( self._tagger_class_name, 
                                                                                                                 self._tagger_module_path )) from attr_err
            except:
                raise
        # Finally, create the instance of the class
        if tagger_class is not None:
            tagger = tagger_class( **self._parameters )
        else:
            raise TaggerClassNotFound( ('(!) Unable to load Tagger class from {!r}. '+\
                                        'Please check that the import path is correct.').format( self.import_path ))
        return tagger

    def is_loaded(self):
        return self._tagger is not None

    @property
    def tagger(self):
        if not self.is_loaded():
            # initialize tagger
            self._tagger = self._load_tagger()
        return self._tagger

    def __str__(self):
        return self.__class__.__name__ + '(' + self._tagger_class_name + ': ' + str(self.input_layers) + '->' + self.output_layer + ')'

    def parameters(self):
        """Returns a dictionary with loader's parameters. 
        Used in TaggerRegistry for listing information about the Tagger. 
        """
        record = {'name': self._tagger_class_name,
                  'layer': self.output_layer,
                  'attributes': self.output_attributes,
                  'depends_on': self.input_layers,
                  'is_loaded': self.is_loaded(),
                  'description': self.description
                  }
        return record


class TaggerLoaded(TaggerLoader):
    """TaggerLoaded is a TaggerLoader that has a fully loaded Tagger or Retagger.
    The purpose of this class is to skip the tagger importing and loading inside 
    the TaggerLoader. 
    
    Usage example
    --------------
    >>> from estnltk_core.taggers.tagger_loader import TaggerLoaded
    >>> from estnltk.taggers import VabamorfTagger
    >>> tl = TaggerLoaded( VabamorfTagger() )
    >>> vm_tagger = tl.tagger
    >>> vm_tagger
    VabamorfTagger(('words', 'sentences', 'compound_tokens')->morph_analysis)
    """

    def __init__(self, tagger, description:str=None):
        """Initializes TaggerLoaded with the given tagger instance.
        
        Parameters
        ----------
        tagger
            A tagger instance; should be from a subclass of Tagger or Retagger.
        description:str
            description of the tagger / layer. 
            optional, defaults to the first line in Tagger's docstring.
        """
        if not isinstance( tagger, (Tagger, Retagger) ):
            raise TypeError( '(!) Expected an instance of Tagger or Retagger, but got {}'.format( type(tagger) ) )
        self._tagger = tagger
        self.output_layer = tagger.output_layer
        self.input_layers = tagger.input_layers
        self.output_attributes = tagger.output_attributes
        self._parameters = {}
        self._tagger_class_name = tagger.__class__.__name__
        self._tagger_module_path = tagger.__class__.__module__
        self.import_path = self._tagger_module_path + '.' + self._tagger_class_name
        self.description = description
        if description is None and tagger.__doc__ is not None:
            description = tagger.__doc__.strip().split('\n', 1)[0]

