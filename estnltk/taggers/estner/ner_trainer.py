from estnltk.taggers.estner.fex import FeatureExtractor
from estnltk.taggers.estner import CrfsuiteTrainer
from estnltk.taggers.estner.refac.ner import ModelStorageUtil

class NerTrainer(object):
    """The class for training NER models. Uses crfsuite implementation."""

    def __init__(self, nersettings, morph_layer_input=('morph_analysis',)):
        """Initialize a new NerTrainer.

        Parameters
        ----------
        nersettings: module
            NER settings module.
        """
        self.settings = nersettings
        self.fex = FeatureExtractor(nersettings,morph_layer_input)
        self.trainer = CrfsuiteTrainer(algorithm=nersettings.CRFSUITE_ALGORITHM,
                                       c2=nersettings.CRFSUITE_C2)

    def train(self, text, labels, model_dir):
        """ Train a NER model using given documents.

        Each word in the documents must have a "label" attribute, which
        denote the named entities in the documents.

        Parameters
        ----------
        text: EstNLTK Text object
            The text used for training the CRF model.
        labels: list of lists
            List of correct labels for each sentence and word
            The list has to be of the same size as the sentences layer of the text
            and the list corresponding to the sentence has to be of the same size as the number of spans in that sentence.
        model_dir: str
            A directory where the model will be saved.
        """
        modelUtil = ModelStorageUtil(model_dir)
        modelUtil.makedir()
        modelUtil.copy_settings(self.settings)

        self.fex.process([text])

        self.trainer.train(text, labels, modelUtil.model_filename)