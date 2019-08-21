import regex as re

from estnltk.taggers import TaggerOld, AnnotationRewriter
from estnltk.taggers import VabamorfTagger
from estnltk.rewriting import VerbExtensionSuffixRewriter


class VerbExtensionSuffixTagger(TaggerOld):
    description = 'Tags verb extension suffixes.'
    layer_name = 'verb_extension_suffix'
    attributes = VabamorfTagger.output_attributes + ('verb_extension_suffix',)
    depends_on = ['morph_analysis']
    configuration = {}

    def __init__(self):
        self.verb_extension_suffix_rewriter = VerbExtensionSuffixRewriter()

    def tag(self, text, return_layer=False):
        new_layer = text['morph_analysis']
        source_attributes = new_layer.attributes
        target_attributes = source_attributes + ('verb_extension_suffix',)
        new_layer = new_layer.rewrite(
            source_attributes = source_attributes,
            target_attributes = target_attributes,
            rules = self.verb_extension_suffix_rewriter,
            name = 'verb_extension_suffix',
            ambiguous = True
            )
        if return_layer:
            return new_layer
        text[self.layer_name] = new_layer


class VerbExtensionSuffixRetagger(AnnotationRewriter):
    """Tags verb extension suffixes.

    """
    _suffix_conversions = (("=[td]ud", "tud"),
                           ("=nud", "nud"),
                           ("=mine", "mine"),
                           ("=nu$", "nu"),
                           ("=nu[+]", "nu"),
                           ("=[td]u$", "tu"),
                           ("=[td]u[+]", "tu"),
                           ("=v$", "v"),
                           ("=[td]av", "tav"),
                           ("=mata", "mata"),
                           ("=ja", "ja")
                           )

    def rewrite(self, annotation):
        # 'verb_extension_suffix' on siin list (ikka eelmise versiooniga ühildumiseks)
        # 'Kirutud-virisetud'
        annotation['verb_extension_suffix'] = []
        if '=' in annotation['root']:
            for pattern, value in self._suffix_conversions:
                if re.search(pattern, annotation['root']):
                    if value not in annotation['verb_extension_suffix']:
                        annotation['verb_extension_suffix'].append(value)
        annotation['verb_extension_suffix'] = tuple(annotation['verb_extension_suffix'])

    def __init__(self, layer_name):
        super().__init__(layer_name=layer_name, output_attributes=['verb_extension_suffix'], function=self.rewrite,
                         check_output_consistency=False)
