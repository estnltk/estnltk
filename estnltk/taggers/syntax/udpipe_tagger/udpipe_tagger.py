from estnltk import ElementaryBaseSpan, Annotation, Layer
from estnltk.taggers import Tagger
from estnltk.converters.conll_exporter import sentence_to_conll
from ufal.udpipe import Model, Pipeline, ProcessingError


class UDPipeTagger(Tagger):
    """
    Input layers should be sentences and conll_morph, but there can also be some other layer with same attributes
    """
    conf_param = ['model', 'pipeline', 'error']

    def __init__(self,
                 model=None,
                 pipeline=None,
                 output_layer='udpipe',
                 input_layers=None,
                 output_attributes=None):

        if input_layers is None:
            input_layers = ['sentences', 'conll_morph']
        if output_attributes is None:
            output_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']
        if model is None:
            model = Model.load('resources/model_0.output')
        if pipeline is None:
            pipeline = Pipeline(model, 'conllu', Pipeline.NONE, Pipeline.DEFAULT, 'conllu')

        self.model = model
        self.pipeline = pipeline
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = output_attributes
        self.error = ProcessingError()

    def _make_layer(self, text, layers, status=None):
        conllu_string = sentence_to_conll(text.sentences[0], self.input_layers[1])
        layer = Layer(name=self.output_layer, text_object=text, attributes=self.output_attributes, ambiguous=True,
                      parent=self.input_layers[1].name)

        processed = self.pipeline.process(conllu_string, self.error).strip()
        if self.error.occurred():
            print("An error occurrred : %s" % self.error.message)
        start = 0
        for line in processed.split('\n'):
            line = line.split('\t')
            ID = line[0]
            form = line[1]
            lemma = line[2]
            upostag = line[3]
            xpostag = line[4]
            feats = line[5]
            head = line[6]
            deprel = line[7]
            deps = line[8]
            misc = line[9]

            span = ElementaryBaseSpan(start, start + len(form))
            attributes = {'id': ID, 'form': form, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag,
                          'feats': feats, 'head': head, 'deprel': deprel, 'deps': deps, 'misc': misc}
            annotation = Annotation(span, **attributes)
            layer.add_annotation(span, **annotation)
            start += len(form) + 1
        return layer

    def __doc__(self):
        print("Udpipe parser for syntactic analysis.")
