from estnltk.taggers import Retagger


class RemoveAdpositionAnalysesRetagger(Retagger):
    """ Uses special logic for handling adposition (partofspeech 'K') analyses.

        Finds the last analyses of the word where the 'letter_case' is None,
        the 'subcat' is None and the 'verb_extension_suffix' is None, but the
        'form' is 'pre' or 'post'.

         *) If the word has only an analysis with the form 'post', removes that
            analysis.
         *) If the word has analyses with the form 'pre' and the form 'post',
            removes the analysis with the form 'pre'.

        The parameter allow_to_delete_all specifies whether it is allowed to
        delete all analyses of the word. If allow_to_delete_all==False, then
        one last analysis is not deleted, regardless whether it should
        be deleted considering the adposition-deletion rules;
        The original implementation corresponds to the settings
        allow_to_delete_all=True (and this is also the default value of the
        parameter).

        Returns the input list where the removals have been applied;

    """
    conf_param = ['check_output_consistency', 'allow_to_delete_all']

    def __init__(self, allow_to_delete_all=True):
        self.allow_to_delete_all = allow_to_delete_all
        self.input_layers = ['morph_extended']
        self.output_layer = 'morph_extended'
        self.output_attributes = []
        self.check_output_consistency = False

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]

        for span in layer:
            if not self.allow_to_delete_all and len(span.annotations) < 2:
                continue

            Kpre_index = None
            Kpost_index = None
            for i, annotation in enumerate(span.annotations):
                if annotation['partofspeech'] != 'K':
                    continue
                if annotation.get('letter_case') \
                   or annotation.get('subcat') \
                   or annotation.get('verb_extension_suffix'):
                    continue
                if annotation['form'] == 'pre':
                    Kpre_index = i
                elif annotation['form'] == 'post':
                    Kpost_index = i

            if Kpost_index is not None:
                if Kpre_index is None:
                    span.del_annotation(Kpost_index)
                else:
                    span.del_annotation(Kpre_index)

        return layer

    def rewrite(self, record):
        if not self.allow_to_delete_all and len(record) < 2:
            return record

        Kpre_index = None
        Kpost_index = None
        for i, rec in enumerate(record):
            if rec['partofspeech'] != 'K':
                continue
            if (rec.get('letter_case', None) or
                rec.get('subcat', None) or
                rec.get('verb_extension_suffix', None)):
                continue
            if rec['form'] == 'pre':
                Kpre_index = i
            elif rec['form'] == 'post':
                Kpost_index = i

        if Kpost_index is not None:
            if Kpre_index is None:
                del record[Kpost_index]
            else:
                del record[Kpre_index]
        return record

# Kaassõna (adposition, K) morf analüüsis partofspeech=='K' ja form==''.
# tmorftabel.txt põhjal tekib sellisest reast kaks analüüsi, kus
# partofspeech=='K', form=='pre'
# partofspeech=='K', form=='post'
# Vana kood eemaldas ainult viimase 'pre' või 'post' analüüsi.
# Ei leia näidet sõnast, millele vabamorf annaks mitmel real
# partofspeech=='K'.
# Kui disambiguate==False, siis võib esineda lisaks partofspeech=='K'
# muid ridu vabamorfi analüüsi väljundis
# Sõltuvalt algsest analüüsist on kolm võimalikku stsenaariumit:
# #####################################################################
#
#         A
#         1) vabamorf
#             partofspeech=='K' ja form==''
#         2) morph_to_syntax_morph
#             partofspeech=='K', form=='pre'
#             partofspeech=='K', form=='post'
#         3) remove_adposition_analyses
#             partofspeech=='K', form=='post'
#         4) letter_case / subcat
#             partofspeech=='K', form=='post', case=None
#         5) remove_adposition_analyses, kui allow_to_remove_all==False
#             partofspeech=='K', form=='post', case=None
#         #######################################################################
#         B
#         1) vabamorf
#             partofspeech=='V' ja form=='bla'
#             partofspeech=='K' ja form==''
#         2) morph_to_syntax_morph
#             partofspeech=='V' ja form=='bla'
#             partofspeech=='K', form=='pre'
#             partofspeech=='K', form=='post'
#         3) remove_adposition_analyses
#             partofspeech=='V' ja form=='bla'
#             partofspeech=='K', form=='post'
#         4) letter_case / subcat
#             partofspeech=='V' ja form=='bla', case=None
#             partofspeech=='K', form=='post', case=None
#         5) remove_adposition_analyses
#             partofspeech=='V' ja form=='bla', case=None
#         #######################################################################
#         C
#         1) vabamorf
#             partofspeech=='V' ja form=='bla'
#             partofspeech=='K' ja form==''
#         2) morph_to_syntax_morph
#             partofspeech=='V' ja form=='bla'
#             partofspeech=='K', form=='pre'
#             partofspeech=='K', form=='post'
#         3) remove_adposition_analyses
#             partofspeech=='V' ja form=='bla'
#             partofspeech=='K', form=='post'
#         4) letter_case / subcat
#             partofspeech=='V' ja form=='bla', case='cap'
#             partofspeech=='K', form=='post', case='cap'
#         5) remove_adposition_analyses
#             partofspeech=='V' ja form=='bla'
#             partofspeech=='K', form=='post', case='cap'
