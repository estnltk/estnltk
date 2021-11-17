import regex as re

from estnltk.taggers import Retagger


class FiniteFormRetagger(Retagger):
    """ The fin attribute gets the value
            True, if the word is a finite verb,
            False, if word is a verb but not finite,
            None, if the word is not a verb.

        Finite forms are the ones that can act as (part of) a predicate,
        e.g in sentence "Mari läheb koju sööma.", 'läheb' is a finite form
        and can serve as a predicate by itself ("Mari läheb koju"),
        while "sööma" is infinite and needs to be combined with a verb
        in finite form ("Mari koju sööma" is not a correct sentence).

        The finiteness of a verb is decided based on its morphological information.
        The following morphological tags are used to define the finiteness of the form:
        * voice (personal/impersonal) tags - if marked with the following tags, the verb form is finite:
          ps1: personal, first person, e.g 'tahan', 'tahtsime', 'tahaksime'...
          ps2: personal, second person, e.g 'tahad', 'tahtke', 'tahaksite'...
          ps3: personal, third person, e.g 'tahab', 'tahtis', 'tahetagu'...
          impf imps: impersonal, imperfect tense, e.g 'taheti'
          pres imps: impersonal, present tense, e.g 'tahetakse'
        * mode (indicative - e.g 'tahan'/conditional - e.g. 'tahaksin'/...):
            - if the mode is marked, the verb is finite. Here, only quotative mode ('quot' - e.g 'tahetavat')
              is checked because other modes are always accompanied by the voice tags described above
        * polarity(negation - e.g 'ei'):
            - if verb is marked with the tag 'neg' ('pandud' in "Koera ei pandud ketti.")
              AND not with the tag 'aux neg' (auxiliaries like "ei"), it is marked as finite.

        Additional remarks:
        * Quotative mode is also accompanied by a voice tag 'ps' meaning 'personal' without specifying the person.
          This, however, wouldn't be suitable to use in the _morfFinV regex because the string 'ps' can be found inside
          other tags as well.
        * In addition to 'impf imps' and 'pres imps' there is also 'past imps' tag that should be considered a
          finite form. However, these forms ('tahetuvat', etc) occur extremely rarely (if at all) in the language.
        * In fact, 'aux neg' forms are a part of a predicate but in the interest of further analysis, it is not useful
          to mark them as finite verbs.
        * Currently, only "ei" is tagged as 'aux neg', but theoretically, there could be other words as well
          (like historical form "ep")

    """

    conf_param = ['check_output_consistency']

    _morfFinV = re.compile('(ps[123]|neg|quot|impf imps|pres imps)')

    def __init__(self):
        self.input_layers = ['morph_extended']
        self.output_layer = 'morph_extended'
        self.output_attributes = ['fin']
        self.check_output_consistency = False

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]
        if self.output_attributes[0] not in layer.attributes:
            layer.attributes = layer.attributes + self.output_attributes

        for span in layer:
            for annotation in span.annotations:
                if annotation['partofspeech'] == 'V':
                    annotation['fin'] = bool(self._morfFinV.search(annotation['form'])) \
                                        and annotation['form'] != 'aux neg'
                else:
                    annotation['fin'] = None
        return layer
