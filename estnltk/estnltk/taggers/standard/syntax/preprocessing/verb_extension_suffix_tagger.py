import regex as re

from estnltk_core.taggers.annotation_rewriter import AnnotationRewriter


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


def rewrite(annotation):
    # 'verb_extension_suffix' on siin list (ikka eelmise versiooniga ühildumiseks)
    # 'Kirutud-virisetud'
    annotation['verb_extension_suffix'] = []
    if '=' in annotation['root']:
        for pattern, value in _suffix_conversions:
            if re.search(pattern, annotation['root']):
                if value not in annotation['verb_extension_suffix']:
                    annotation['verb_extension_suffix'].append(value)
    annotation['verb_extension_suffix'] = tuple(annotation['verb_extension_suffix'])


class VerbExtensionSuffixRetagger(AnnotationRewriter):
    """Tags verb extension suffixes.

    """

    def __init__(self, layer_name):
        super().__init__(layer_name=layer_name, output_attributes=['verb_extension_suffix'], 
                         function=rewrite,
                         attr_change='ADD')
