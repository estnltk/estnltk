#
#  Converts Vabamorf's category names to Estonian
#
#  Purpose: only to increase human-readability & ease manual 
#  inspection.  Automatic  analysis should not be built upon 
#  this format.
# 

from estnltk import Annotation
from estnltk import Layer, Text
from estnltk.taggers import Tagger

from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation

# ==============================================================
#    Category name translations from:
#     https://filosoft.ee/html_morf_et/morfoutinfo.html 
#    and from:
#     https://github.com/estnltk/estnltk/blob/11873a7b3336609007ed208bb40fc73984140d80/estnltk/core.py#L36
# ==============================================================

VM_POSTAGS = {
    'A': 'omadussõna algvõrre',
    'C': 'omadussõna keskvõrre',
    'U': 'omadussõna ülivõrre',
    'D': 'määrsõna',
    'G': 'käändumatu omadussõna',
    'H': 'pärisnimi',
    'I': 'hüüdsõna',
    'J': 'sidesõna',
    'K': 'kaassõna',
    'N': 'põhiarvsõna',
    'O': 'järgarvsõna',
    'P': 'asesõna',
    'S': 'nimisõna',
    'V': 'tegusõna',
    'X': 'verbi juurde kuuluv sõna',
    'Y': 'lühend',
    'Z': 'lausemärk',
    # Exclusive in web corpora:
    'E': 'emotikon',
    'B': 'partikkel',
}

VM_NOM_CASES = {
    'ab': 'ilmaütlev (abessiiv)',
    'abl': 'alaltütlev (ablatiiv)',
    'ad': 'alalütlev (adessiiv)',
    'adt': 'lühike sisseütlev (aditiiv)',
    'all': 'alaleütlev (allatiiv)',
    'el': 'seestütlev (elatiiv)',
    'es': 'olev (essiiv)',
    'g': 'omastav (genitiiv)',
    'ill': 'sisseütlev (illatiiv)',
    'in': 'seesütlev (inessiiv)',
    'kom': 'kaasaütlev (komitatiiv)',
    'n': 'nimetav (nominatiiv)',
    'p': 'osastav (partitiiv)',
    'tm': 'rajav (terminatiiv)',
    'tr': 'saav (translatiiv)'
}

VM_NUMBER = {
    'sg': 'ainsus',
    'pl': 'mitmus'
}

VM_VERB_FORMS = {
    'b': 'kindel kõneviis olevik 3. isik ainsus aktiiv jaatav kõne',
    'd': 'kindel kõneviis olevik 2. isik ainsus aktiiv jaatav kõne',
    'da': 'infinitiiv jaatav kõne',
    'des': 'gerundium jaatav kõne',
    'ge': 'käskiv kõneviis olevik 2. isik mitmus aktiiv jaatav kõne',
    'gem': 'käskiv kõneviis olevik 1. isik mitmus aktiiv jaatav kõne',
    'gu': 'käskiv kõneviis olevik 3. isik aktiiv jaatav kõne',
    'ks': 'tingiv kõneviis olevik aktiiv jaatav kõne',
    'ksid': 'tingiv kõneviis olevik aktiiv jaatav kõne',
    'ksime': 'tingiv kõneviis olevik 1. isik mitmus aktiiv jaatav kõne',
    'ksin': 'tingiv kõneviis olevik 1. isik ainsus aktiiv jaatav kõne',
    'ksite': 'tingiv kõneviis olevik 2. isik mitmus aktiiv jaatav kõne',
    'ma': 'supiin aktiiv jaatav kõne sisseütlev',
    'maks': 'supiin aktiiv jaatav kõne saav',
    'mas': 'supiin aktiiv jaatav kõne seesütlev',
    'mast': 'supiin aktiiv jaatav kõne seestütlev',
    'mata': 'supiin aktiiv jaatav kõne ilmaütlev',
    'me': 'kindel kõneviis olevik 1. isik mitmus aktiiv jaatav kõne',
    'n': 'kindel kõneviis olevik 1. isik ainsus aktiiv jaatav kõne',
    'neg': 'eitav kõne',
    'neg ge': 'käskiv kõneviis olevik 2. isik mitmus aktiiv eitav kõne',
    'neg gem': 'käskiv kõneviis olevik 1. isik mitmus aktiiv eitav kõne',
    'neg gu': 'käskiv kõneviis olevik eitav kõne',
    'neg ks': 'tingiv kõneviis olevik aktiiv eitav kõne',
    'neg me': 'käskiv kõneviis olevik 1. isik mitmus aktiiv eitav kõne',
    'neg nud': 'kindel kõneviis lihtminevik aktiiv eitav kõne',
    'neg nuks': 'tingiv kõneviis minevik aktiiv eitav kõne',
    'neg o': 'käskiv kõneviis olevik aktiiv eitav kõne',
    'neg vat': 'kaudne kõneviis olevik aktiiv eitav kõne',
    'neg tud': 'kesksõna minevik passiiv eitav kõne',
    'nud': 'kesksõna minevik aktiiv jaatav kõne',
    'nuks': 'tingiv kõneviis minevik aktiiv jaatav kõne',
    'nuksid': 'tingiv kõneviis minevik aktiiv jaatav kõne',
    'nuksime': 'tingiv kõneviis minevik 1. isik mitmus aktiiv jaatav kõne',
    'nuksin': 'tingiv kõneviis minevik 1. isik ainsus aktiiv jaatav kõne',
    'nuksite': 'tingiv kõneviis minevik 2. isik mitmus aktiiv jaatav kõne',
    'nuvat': 'kaudne kõneviis minevik aktiiv jaatav kõne',
    'o': 'käskiv kõneviis olevik 2. isik ainsus aktiiv jaatav kõne',
    's': 'kindel kõneviis lihtminevik 3. isik ainsus aktiiv jaatav kõne',
    'sid': 'kindel kõneviis lihtminevik aktiiv jaatav kõne',
    'sime': 'kindel kõneviis lihtminevik 1. isik mitmus aktiiv jaatav kõne',
    'sin': 'kindel kõneviis lihtminevik 1. isik ainsus aktiiv jaatav kõne',
    'site': 'kindel kõneviis lihtminevik 2. isik mitmus aktiiv jaatav kõne',
    'ta': 'kindel kõneviis olevik passiiv eitav kõne',
    'tagu': 'käskiv kõneviis olevik passiiv jaatav kõne',
    'taks': 'tingiv kõneviis olevik passiiv jaatav kõne',
    'takse': 'kindel kõneviis olevik passiiv jaatav kõne',
    'tama': 'supiin passiiv jaatav kõne',
    'tav': 'kesksõna olevik passiiv jaatav kõne',
    'tavat': 'kaudne kõneviis olevik passiiv jaatav kõne',
    'te': 'kindel kõneviis olevik 2. isik mitmus aktiiv jaatav kõne',
    'ti': 'kindel kõneviis lihtminevik passiiv jaatav kõne',
    'tud': 'kesksõna minevik passiiv jaatav kõne',
    'tuks': 'tingiv kõneviis minevik passiiv jaatav kõne',
    'tuvat': 'kaudne kõneviis minevik passiiv jaatav kõne',
    'v': 'kesksõna olevik aktiiv jaatav kõne',
    'vad': 'kindel kõneviis olevik 3. isik mitmus aktiiv jaatav kõne',
    'vat': 'kaudne kõneviis olevik aktiiv jaatav kõne',
}


class VabamorfEstCatConverter(Tagger):
    """Converts Vabamorf's morphological analysis category names to Estonian (for educational purposes).
       Purpose: only to increase human-readability & ease manual inspection.
       Automatic analysis should not be built upon this format.
    """
    output_attributes = ('normaliseeritud_sõne', 'algvorm', 'lõpp', 'sõnaliik', 'vormi_nimetus', 'kliitik')
    conf_param = []
    input_layers = ['morph_analysis']
    output_layer = 'morph_analysis_est'
    
    def __init__(self,
                 output_layer='morph_analysis_est',
                 input_morph_analysis_layer='morph_analysis'):
        """Initialize VabamorfEstCatNames class.
        
        Parameters
        ----------
        output_layer: str (default: 'morph_analysis_est')
            Name of the output layer which will contain analyses with 
            Estonian categories.
        input_morph_analysis_layer: str (default: 'morph_analysis')
            Name of the morph_analysis layer that will be converted. 
        """
        self.input_layers = [input_morph_analysis_layer]
        self.output_layer = output_layer

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     parent=self.input_layers[0],
                     text_object=None,
                     ambiguous=True,
                     attributes=self.output_attributes)

    def _make_layer(self, text: Text, layers, status: dict):
        """Converts 'morph_analysis' layer of given Text object 
           to Estonian category names.

           Parameters
           ----------
           text: estnltk.text.Text
              Input Text object.

           layers: MutableMapping[str, Layer]
              Layers of the text. Contains mappings from the
              name of the layer to the Layer object. Must contain
              morph_analysis;

           status: dict
              This can be used to store metadata on layer tagging.
        """
        original_morph_layer = layers[self.input_layers[0]]
        translated_morph_layer = self._make_layer_template()
        translated_morph_layer.text_object = text
        for morph_span in original_morph_layer:
            if not _is_empty_annotation( morph_span.annotations[0] ):
                # Convert existing annotations
                for annotation in morph_span.annotations:
                    record = {}
                    record['normaliseeritud_sõne'] = annotation['normalized_text']
                    record['algvorm'] = annotation['lemma']
                    record['lõpp'] = annotation['ending']
                    record['sõnaliik'] = VM_POSTAGS.get(annotation['partofspeech'], '??')
                    record['vormi_nimetus'] = '??'
                    if annotation['partofspeech'] == 'V':
                        record['vormi_nimetus'] = VM_VERB_FORMS.get(annotation['form'], '??')
                    elif 'sg ' in annotation['form'] or 'pl ' in annotation['form']:
                        number, case = annotation['form'].split()
                        record['vormi_nimetus'] = VM_NUMBER.get(number, '??')+' '+VM_NOM_CASES.get(case, '??')
                    elif 'adt' == annotation['form']:
                        record['vormi_nimetus'] = VM_NOM_CASES.get(annotation['form'], '??')
                    elif annotation['form'] == '':
                        record['vormi_nimetus'] = ''
                    record['kliitik'] = annotation['clitic']
                    translated_morph_layer.add_annotation(morph_span.base_span, **record)
            else:
                # Convert an empty annotation
                record = { a:None for a in self.output_attributes }
                translated_morph_layer.add_annotation(morph_span.base_span, **record)
        assert len(translated_morph_layer) == len(original_morph_layer)
        return translated_morph_layer

