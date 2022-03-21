from typing import Sequence, Union, Set, List, Union, Any, Mapping
from typing import Dict

import networkx as nx

from estnltk_core.base_text import BaseText
from estnltk.default_resolver import DEFAULT_RESOLVER

class Text( BaseText ):
    """Central component of EstNLTK. Encapsulates the raw text and allows applying text analysers (taggers).
    Text analysis results (annotations) are also stored in the Text object, and can be accessed and explored 
    as layers.

    Text 101
    =========
    You can create new Text object simply by passing analysable text to the constructor:

        from estnltk import Text
        my_text=Text('Tere, maailm!')

    Now, you can use `tag_layer` method to add linguistic analyses to the text:

        # add morphological analysis to the text
        my_text.tag_layer('morph_analysis')

    Type `Text.layer_resolver` to get more information about layers that can be tagged. 

    Added layer can be accessed via indexing (square brackets):

        my_text['morph_analysis']

    or as an attribute:

        my_text.morph_analysis

    This returns the whole layer, but if you need to access analyses of specific
    words, you can either iterate over the layer:

        for word in my_text['morph_analysis']:
            # do something with the word's analyses
            ...

    Or you can use index to access analyses of specific word:

        # morph analysis (span) of the first word
        my_text['morph_analysis'][0]

    Note that both index access and iteration over the layer gives you spans
    (locations) of annotations in the text. To access corresponding annotation
    values, you can either use index access:

        # get 'partofspeech' values from morph analysis of the first word
        my_text['morph_analysis'][0]['partofspeech']

    Or used attribute `.annotations` to get all annotations as a list:

        # get all morph analysis annotations of the first word
        my_text['morph_analysis'][0].annotations

    In both cases, a list is returned, because annotations can be ambiguous, 
    so list holds multiple alternative interpretations.

    Metadata
    =========
    It is possible to add meta-information about text as a whole by specifying text.meta,
    which is a dictionary of type MutableMapping[str, Any]. However, we strongly advise to
    use the following value types:
        str
        int
        float
        DateTime
    as database serialisation does not work for other types.
    See [estnltk.storage.postgres] for further documentation.
    
    More tools
    ===========
    `Text.layer_resolver` contains taggers of the default NLP pipeline. More taggers can 
    be found in `estnltk.taggers`:
    
        import estnltk.taggers
        # List names of taggers that can be imported
        dir( estnltk.taggers )
        
    How to use manually a tagger imported from `estnltk.taggers` ?
    
    1) Initialize the tagger, e.g.

        from estnltk.taggers import VabamorfTagger
        tagger = VabamorfTagger()
    
    2) Create input layers required by the tagger, e.g.
    
        new_text = Text(...)
        new_text.tag_layer( tagger.input_layers )
    
    3) Tag layer with the tagger:
    
        tagger.tag( new_text )
    
    Note that some of the taggers are retaggers, which means that 
    instead of creating a layer they modify an existing layer. 
    In that case, you should use `tagger.retag( new_text )` instead.
    ---
    """
    
    # All methods for BaseText/Text object
    # methods: Set[str]
    methods = {
        '_repr_html_',
        'add_layer',
        'analyse',
        'layer_attributes',
        'pop_layer',
        'diff',
        'layers',
        'sorted_layers',
        'tag_layer',
        'topological_sort',
    } | {method for method in dir(object) if callable(getattr(object, method, None))}

    # presorted_layers: Tuple[str, ...]
    presorted_layers = (
        'paragraphs',
        'sentences',
        'tokens',
        'compound_tokens',
        'words',
        'morph_analysis',
        'morph_extended'
    )
    """
    Presorted layers used for visualization purposes (BaseText._repr_html_).
    """
    
    # layer resolver that is used for computing layers
    layer_resolver = DEFAULT_RESOLVER
    """
    LayerResolver that is used for computing layers. 
    Defaults to DEFAULT_RESOLVER from estnltk.default_resolver.
    
    Note 1: if you mess up the resolver accidentially, you can 
    restart it via make_resolver() function:
    
       from estnltk.default_resolver import make_resolver
       # Reset default resolver
       Text.layer_resolver = make_resolver()
    
    Note 2: if you want to use Python's multiprocessing, you 
    should make a separate LayerResolver for each process/job, 
    otherwise you'll likely run into errors. tag_layer method 
    can take resolver as a parameter.
    """

    def tag_layer(self, layer_names: Union[str, Sequence[str]]=None, resolver=None) -> 'Text':
        """
        Tags given layers along with their prerequisite layers.
        Returns this Text object with added layers.

        Type `Text.layer_resolver` to get more information about layers that can be 
        tagged by default. 

        If you don't pass any parameters, defaults to tagging 'sentences' and
        'morph_analysis' layers along with their prerequisite layers (segmentation
        layers).

        Note: if you want to use Python's multiprocessing, you should make a separate
        LayerResolver for each process/job, and pass it as a `resolver` parameter while
        tagging a text. You can use `make_resolver` from `estnltk.default_resolver` to
        create new resolver instances.

        Parameters
        ----------
        layer_names: Union[str, Sequence[str]] (default: None)
            Names of the layers to be tagged. If not specified, tags
            `resolver.default_layers`. And if `resolver` is not specified,
            uses `Text.layer_resolver.default_layers` instead.
            Note that you can only tag layers that are available in the
            resolver, i.e. layers listed by resolver's `layers` attribute.
        resolver: LayerResolver (default: None)
            Resolver to be used for tagging the layers. If not specified,
            then uses `Text.layer_resolver` which is equivalent to
            DEFAULT_RESOLVER from estnltk.default_resolver.

        Returns
        ----------
        Text
            This Text object with added layers.
        """
        if resolver is None:
            resolver = self.layer_resolver
        if isinstance(layer_names, str):
            layer_names = [layer_names]
        if layer_names is None:
            layer_names = resolver.default_layers
        for layer_name in layer_names:
            resolver.apply(self, layer_name)
        return self

    def analyse(self, t: str, resolver=None) -> 'Text':
        """
        Analyses text by adding NLP layers corresponding to the given level `t`.
        **Important**: this method is deprecated, please use Text.tag_layer instead!
        
        How to replace Text.analyse functionality with Text.tag_layer?
        
        * text.analyse('segmentation') is same as text.tag_layer('paragraphs'); 
          text.pop_layer('tokens');
        
        * text.analyse('morphology') is same as text.tag_layer('morph_analysis'); 
          text.pop_layer('tokens');
        
        * text.analyse('syntax_preprocessing') is same as text.tag_layer(['sentences','morph_extended']);
          text.pop_layer('tokens');
        
        * text.analyse('all') is same as text.tag_layer(['paragraphs','morph_extended']);
        """
        raise Exception("(!) Text.analyse method is deprecated. Please use Text.tag_layer instead.\n\n"+\
            "How to replace Text.analyse function with Text.tag_layer? \n"+\
            "1) text.analyse('segmentation') is same as text.tag_layer('paragraphs');"+\
            "text.pop_layer('tokens');\n"+\
            "2) text.analyse('morphology') is same as text.tag_layer('morph_analysis');"+\
            "text.pop_layer('tokens');\n"+\
            "3) text.analyse('syntax_preprocessing') is same as text.tag_layer(['sentences','morph_extended']);"+\
            "text.pop_layer('tokens');\n"+\
            "4) text.analyse('all') is same as text.tag_layer(['paragraphs','morph_extended']);\n\n"+\
            "Also, you can use Text.layer_resolver to explore which layers can be tagged.")

    @property
    def layer_attributes(self) -> Dict[str, List[str]]:
        """
        Returns a mapping from all attributes to layer names hosting them.
        """
        result = dict()

        # Collect attributes from standard layers
        for name, layer in self._layers.items():
            for attrib in layer.attributes:
                if attrib not in result:
                    result[attrib] = []
                result[attrib].append(name)

        return result

    # attribute_mapping_for_elementary_layers: Mapping[str, str]
    attribute_mapping_for_elementary_layers = {
        'lemma': 'morph_analysis',
        'root': 'morph_analysis',
        'root_tokens': 'morph_analysis',
        'ending': 'morph_analysis',
        'clitic': 'morph_analysis',
        'form': 'morph_analysis',
        'partofspeech': 'morph_analysis'
    }

    attribute_mapping_for_enveloping_layers = attribute_mapping_for_elementary_layers

    def __delattr__(self, item):
        raise TypeError("'{}' object does not support attribute deletion, use pop_layer(...) function instead".format( self.__class__.__name__ ))

    def __getattr__(self, item):
        # Resolve slots
        if item in self.__class__.__slots__:
            return self.__getattribute__(item)

        # Resolve all function calls
        if item in self.__class__.methods:
            return self.__getattribute__(item)

        # Resolve layers
        if item in self.layers:
            return self.__getitem__(item)

        # Resolve attributes that uniquely determine a layer, e.g. BaseText/Text.lemmas ==> BaseText/Text.morph_layer.lemmas
        attributes = self.__getattribute__('layer_attributes')

        if len( attributes.get(item, []) ) == 1:
            return getattr(self._layers[attributes[item][0]], item)

        # Nothing else to resolve
        raise AttributeError("'{}' object has no layer {!r}".format( self.__class__.__name__, item ))
    

