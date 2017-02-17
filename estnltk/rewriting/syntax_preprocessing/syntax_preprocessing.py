from collections import defaultdict
import codecs
import os

import regex as re


class PunctuationTypeRewriter():
    ''' Adds 'punctuation_type' attribute to the analysis.
        If partofspeech is 'Z', then gets the punctuation type from the 
        _punctConversions.

        If partofspeech is not 'Z', then punctuation_type is None.
        
        _punctConversions is a tuple of tuples, where each inner tuple contains
        a pair of elements: first is the regexp pattern to match the root and 
        the second is the punctuation type.
    ''' 

    def rewrite(self, record):
        for rec in record:
            if rec['partofspeech'] == 'Z':
                rec['punctuation_type'] = self._get_punctuation_type(rec)
            else:
                rec['punctuation_type'] = None
        return record

    _punctConversions = (
                          ("…$",      "Ell"),
                          ("\.\.\.$", "Ell"),
                          ("\.\.$",   "Els"),
                          ("\.$",     "Fst"),
                          (",$",      "Com"),
                          (":$",      "Col"),
                          (";$",      "Scl"),
                          ("(\?+)$",  "Int"),
                          ("(\!+)$",  "Exc"),
                          ("(---?)$", "Dsd"),
                          ("(-)$",    "Dsh"),
                          ("\($",     "Opr"),
                          ("\)$",     "Cpr"),
                          ('\\\\"$',  "Quo"),
                          ("«$",      "Oqu"),
                          ("»$",      "Cqu"),
                          ("“$",      "Oqu"),
                          ("”$",      "Cqu"),
                          ("<$",      "Grt"),
                          (">$",      "Sml"),
                          ("\[$",     "Osq"),
                          ("\]$",     "Csq"),
                          ("/$",      "Sla"),
                          ("\+$",     "crd")
    )# double quotes are escaped by \


    def _get_punctuation_type(self, morph_extended):
        root = morph_extended['root']
        if root.rstrip('+0'):
            # eelmise versiooniga ühildumiseks
            # '0.0000000000000000000000000000000000000000000000000000000000'
            # '!+', '!++'
            # '(+'
            # '/+', '/++'
            root = root.rstrip('+0')
        for pattern, punct_type in self._punctConversions:
            if re.search(pattern, root):
                # kas match või search?     "//", ".-"
                # või hoopis pattern==morph_extended.root?
                # praegu on search, sest see klapib eelmise versiooniga
                return punct_type
            # mida teha kui matchi pole?
        if morph_extended['root'].endswith('+'):
            # eelmise versiooniga ühildumiseks
            return 'crd'


class MorphToSyntaxMorphRewriter():
    ''' Converts given analysis from Filosoft's mrf format to syntactic analyzer's
        format, using the morph-category conversion rules from conversion_rules.

        Morph-category conversion rules should be loaded via method
            load_fs_mrf_to_syntax_mrf_translation_rules( rulesFile ),
        usually from a file named 'tmorftrtabel.txt';

        Note that the resulting analysis list is likely longer than the
        original, because the conversion often requires that the
        original Filosoft's analysis is expanded into multiple analysis.
    '''

    def __init__(self, fs_to_synt_rules_file=None):
        if fs_to_synt_rules_file:
            assert os.path.exists(fs_to_synt_rules_file),\
                'Unable to find *fs_to_synt_rules_file* from location ' + fs_to_synt_rules_file
        else:
            fs_to_synt_rules_file = os.path.dirname(__file__)
            fs_to_synt_rules_file = os.path.join(fs_to_synt_rules_file,
                                                 'rules_files/tmorftrtabel.txt')
            assert os.path.exists(fs_to_synt_rules_file),\
                'Missing default *fs_to_synt_rules_file* ' + fs_to_synt_rules_file
        self.fs_to_synt_rules = \
            self.load_fs_mrf_to_syntax_mrf_translation_rules(fs_to_synt_rules_file)


    def rewrite(self, record):
        result = []
        for rec in record:
            pos = rec['partofspeech']
            form = rec['form']
            # 1) Convert punctuation
            if pos == 'Z':
                result.append(rec)
            else:
            # 2) Convert morphological analyses that have a form specified
                if form:
                    morph_key = (pos, form)
                else:
                    morph_key = (pos, '')
                if morph_key in self.fs_to_synt_rules:
                    rules = self.fs_to_synt_rules[morph_key]
                else:
                    # parem oleks tmorfttabel.txt täiendada ja võibolla siin hoopis viga visata
                    rules = [morph_key]
                for pos, form in rules:
                    rec['partofspeech'] = pos
                    rec['form'] = form
                    result.append(rec.copy())
        return result

    @staticmethod
    def _esc_que_mark(form):
        ''' Replaces a question mark in form (e.g. 'card ? digit' or 'ord ? roman')  
            with an escaped version of the question mark <?>
        '''
        return form.replace(' ?', ' <?>')

    @staticmethod
    def load_fs_mrf_to_syntax_mrf_translation_rules(fs_to_synt_rules_file):
        ''' Loads rules that can be used to convert from Filosoft's mrf format to
            syntactic analyzer's format. Returns a dict containing rules.
    
            Expects that each line in the input file contains a single rule, and that
            different parts of the rule are separated by @ symbols, e.g.
    
                1@_S_ ?@Substantiiv apellatiiv@_S_ com @Noun common@Nc@NCSX@kesk-
                32@_H_ ?@Substantiiv prooprium@_S_ prop @Noun proper@Np@NPCSX@Kesk-
                313@_A_@Adjektiiv positiiv@_A_ pos@Adjective positive@A-p@ASX@salkus
    
            Only the 2nd element and the 4th element are extracted from each line.
            Both are treated as a pair of strings. The 2nd element will be the key
            of the dict entry, and 4th element will be added to the value of the
            dict entry:
            {('S', '?'): [('S', 'com ')],
             ('H', '?'): [('S', 'prop ')],
             ('A', ''): [('A', 'pos')]
            }
    
            A list is used for storing values because one Filosoft's analysis could
            be mapped to multiple syntactic analyzer's analyses.
    
            Lines that have ¤ in the beginning of the line are skipped.
        '''
        rules = defaultdict(list)
        rules_pattern = re.compile('(¤?)[^@]*@(_(.)_\s*([^@]*)|####)@[^@]*@_(.)_\s*([^@]*)')
        with codecs.open(fs_to_synt_rules_file, mode='r', encoding='utf-8') as in_f:
            for line in in_f:
                m = rules_pattern.match(line)
                assert m is not None, ' Unexpected format of the line: ' + line
                if m.group(1): #line starts with '¤'
                    continue
                new_form = MorphToSyntaxMorphRewriter._esc_que_mark(m.group(6)).strip()
                if (m.group(5), new_form) not in rules[(m.group(3), m.group(4))]:
                    rules[(m.group(3), m.group(4))].append((m.group(5), new_form))
        for key, value in rules.items():
            # eelmise versiooniga ühildumiseks
            rules[key] = tuple(value[::-1])
        return rules


class PronounTypeRewriter():
    ''' Adds 'pronoun_type' attribute to the analysis.
        Converts pronouns from Filosoft's mrf to syntactic analyzer's mrf format.
        
        If partofspeech is 'P', then gets the pronoun_type from the
        _pronConversions;
        If 'partofspeech' is not 'P', then pronoun_type is None.
        
        _pronConversions is a tuple of tuples, where each inner tuple contains a 
        pair of elements: first is the regexp pattern to match the
        <root>+<ending><clitic> and the second is the pronoun_type (a tuple of 
        strings).
    '''

    # ma, sa, ta ei lähe kunagi mängu, sest ma -> mina, sa -> sina, ta-> tema
    # pronoun type on tuple, et säiliks järjekord, muidu võiks vist olla set.
    _pronConversions = ( ("emb\+.*",             ("det",)),
                         ("enda\+.*",            ("pos", "refl")),
                         ("enese\+.*",           ("pos", "refl")),
                         ("eikeegi.*",           ("indef",)),
                         ("eimiski.*",           ("indef",)),
                         ("emb-kumb.*",          ("det",)),
                         ("esimene.*",           ("dem",)),
                         ("iga\+.*",             ("det",)),
                         ("iga_sugune.*",        ("indef",)),
                         ("iga_.ks\+.*",         ("det",)),
                         ("ise\+.*",             ("pos", "det", "refl")),
                         ("ise_enese.*",         ("refl",)),
                         ("ise_sugune.*",        ("dem",)),
                         ("keegi.*",             ("indef",)),
                         ("kes.*",               ("inter rel",)),
                         ("kumb\+.*",            ("rel",)),
                         ("kumbki.*",            ("det",)),
                         ("kõik.*",              ("det",)),
                         ("k.ik.*",              ("det",)),
                         ("meie_sugune.*",       ("dem",)),
                         ("meie_taoline.*",      ("dem",)),
                         ("mihuke\+.*",          ("inter rel",)),
                         ("mihukene\+.*",        ("inter rel",)),
                         ("mille_taoline.*",     ("dem",)),
                         ("milli=?ne.*",         ("rel",)),
                         ("mina\+.*",            ("pers ps1",)),
                         (" ma\+.*",             ("pers ps1",)),
                         ("mina=?kene\+.*",      ("dem",)),
                         ("mina=?ke\+.*",        ("dem",)),
                         ("mingi\+.*",           ("indef",)),
                         ("mingi_sugune.*",      ("indef",)),
                         ("minu_sugune.*",       ("dem",)),
                         ("minu_taoline.*",      ("dem",)),
                         ("miski.*",             ("indef",)),
                         ("mis\+.*",             ("inter rel",)),
                         ("mis_sugune.*",        ("inter rel",)),
                         ("miski\+.*",           ("inter rel",)),
                         ("miski_sugune.*",      ("inter rel",)),
                         ("misu=?ke(ne)?\+.*",   ("dem",)),
                         ("mitme_sugune.*",      ("indef",)),
                         ("mitme_taoline.*",     ("indef",)),
                         ("mitmendik\+.*",       ("inter rel",)),
                         ("mitmes\+.*",          ("inter rel", "indef")),
                         ("mi=?tu.*",            ("indef",)),
                         ("miuke(ne)?\+.*",      ("inter rel",)),
                         ("muist\+.*",           ("indef",)),
                         ("muu.*",               ("indef",)),
                         ("m.lema.*",            ("det",)),
                         ("m.ne_sugune\+.*",     ("indef",)),
                         ("m.ni\+.*",            ("indef",)),
                         ("m.ningane\+.*",       ("indef",)),
                         ("m.ningas.*",          ("indef",)),
                         ("m.herdune\+.*",       ("indef", "rel")),
                         ("määntne\+.*",         ("dem",)),
                         ("na_sugune.*",         ("dem",)),
                         ("nende_sugune.*",      ("dem",)),
                         ("nende_taoline.*",     ("dem",)),
                         ("nihuke(ne)?\+.*",     ("dem",)),
                         ("nii_mi=?tu\+.*",      ("indef", "inter rel")),
                         ("nii_sugune.*",        ("dem",)),
                         ("niisama_sugune.*",    ("dem",)),
                         ("nii?su=?ke(ne)?\+.*", ("dem",)),
                         ("niuke(ne)?\+.*",      ("dem",)),
                         ("oma\+.*",             ("pos", "det", "refl")),
                         ("oma_enese\+.*",       ("pos",)),
                         ("oma_sugune\+.*",      ("dem",)),
                         ("oma_taoline\+.*",     ("dem",)),
                         ("palju.*",             ("indef",)),
                         ("sama\+.*",            ("dem",)),
                         ("sama_sugune\+.*",     ("dem",)),
                         ("sama_taoline\+.*",    ("dem",)),
                         ("samune\+.*",          ("dem",)),
                         ("see\+.*",             ("dem",)),
                         ("see_sama\+.*",        ("dem",)),
                         ("see_sam[au]ne\+.*",   ("dem",)),
                         ("see_sinane\+.*",      ("dem",)),
                         ("see_sugune\+.*",      ("dem",)),
                         ("selle_taoline\+.*",   ("dem",)),
                         ("selli=?ne\+.*",       ("dem",)),
                         ("setu\+.*",            ("indef",)),
                         ("setmes\+.*",          ("indef",)),
                         ("sihuke\+.*",          ("dem",)),
                         ("sina\+.*",            ("pers ps2",)),
                         (" sa\+.*",             ("pers ps2",)),
                         ("sinu_sugune\+.*",     ("dem",)),
                         ("sinu_taoline\+.*",    ("dem",)),
                         ("siuke(ne)?\+.*",      ("dem",)),
                         ("säherdune\+.*",       ("dem",)),
                         ("s.herdune\+.*",       ("dem",)),
                         ("säärane\+.*",         ("dem",)),
                         ("s..rane\+.*",         ("dem",)),
                         ("taoline\+.*",         ("dem",)),
                         ("teie_sugune\+.*",     ("dem",)),
                         ("teie_taoline\+.*",    ("dem",)),
                         ("teine\+.*",           ("dem",)),
                         ("teine_teise\+.*",     ("rec",)),
                         ("teist?_sugune\+.*",   ("dem",)),
                         ("tema\+.*",            ("pers ps3",)),
                         (" ta\+.*",             ("pers ps3",)),
                         ("temake(ne)?\+.*",     ("pers ps3",)),
                         ("tema_sugune\+.*",     ("dem",)),
                         ("tema_taoline\+.*",    ("dem",)),
                         ("too\+.*",             ("dem",)),
                         ("too_sama\+.*",        ("dem",)),
                         ("üks.*",               ("dem", "indef")),
                         (".ks.*",               ("dem", "indef")),
                         ("ükski.*",             ("dem", "indef")),
                         (".kski.*",             ("dem", "indef")),
                         ("üks_teise.*",         ("rec", "indef")),
                         (".ks_teise.*",         ("rec",))
    )
    
    def rewrite(self, record):
        for rec in record:
            rec['pronoun_type'] = None
            if rec['partofspeech'] == 'P':  # only consider lines containing pronoun analyses
                if rec['form'] == '':
                    # eelmise versiooni jäljendamiseks
                    # miskipärast tahetakse igale asesõnale singulari või pluuralit
                    # 'muist' on ainus P juur, millel form on tühi 
                    continue
                root_ec = ''.join((rec['root'], '+', rec['ending'], rec['clitic']))
                for pattern, pron_type in self._pronConversions:
                    if re.search(pattern, root_ec):
                        # kas search või match? "enese" vs "iseenese"
                        rec['pronoun_type'] = pron_type
                        break
        return record


class RemoveDuplicateAnalysesRewriter():
    ''' Removes duplicate analyses. 
        The analyses are duplicate if the 'root', 'ending', 'clitic', 
        'partofspeech' and 'form' attributes are equal.
        
        Returns the input list where the removals have been applied.
    '''     

    def rewrite(self, record):
        seen_analyses = set()
        to_delete = []
        for i, rec in enumerate(record):
            analysis = (rec['root'], rec['ending'], rec['clitic'], rec['partofspeech'], rec['form'])
            if analysis in seen_analyses:
                to_delete.append(i)
            else:
                seen_analyses.add(analysis)
        for i in sorted(to_delete, reverse=True):
            del record[i]

        return record


class RemoveAdpositionAnalysesRewriter():
    ''' Uses special logic for handling adposition (partofspeech 'K') analyses.

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
    '''
    def __init__(self, allow_to_delete_all=True):
        self.allow_to_delete_all = allow_to_delete_all

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
        #######################################################################
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
        return record


class LetterCaseRewriter():
    ''' The 'letter_case' attribute gets the value
            'cap' if the word has capital beginning
            None otherwise
    '''
    
    def rewrite(self, record):
        if record and record[0]['word_text'][0].isupper():
            cap = 'cap'
        else:
            cap = None
        for rec in record:
            rec['letter_case'] = cap
        return record


class FiniteFormRewriter():
    ''' The fin attribute gets the value
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
 
    '''

    _morfFinV = re.compile('(ps[123]|neg|quot|impf imps|pres imps)')

    def rewrite(self, record):
        for rec in record:
            if rec['partofspeech'] == 'V':
                rec['fin'] = bool(self._morfFinV.search(rec['form'])) and rec['form'] != 'aux neg'
            else:
                rec['fin'] = None
        return record


class VerbExtensionSuffixRewriter():
    ''' 
        Marks nouns and adjectives that are derived from verbs.
    
        VerbExtensionSuffixRewriter looks at the ending separated by '=' from the root
        and based on this, adds the suffix information. If the morphological analyser
        has not separated the ending with '=', no suffix information is added.
    
        The suffixes that are considered here:
            - tud/dud (kaevatud/löödud)
            - nud (leidnud)
            - mine (leidmine)
            - nu (kukkunu)
            - tu/du (joostu, pandu)
            - v (laulev)
            - tav/dav (joostav/lauldav)
            - mata (kaevamata)
            - ja (kaevaja)
    
        *It seems that to lexicalised derivations ('surnud', 'õpetaja', 'löömine', 
        'söödav', etc - the words that are frequently used in the derived form), 
        morphological analyser does not add the '='. 
    '''

    _suffix_conversions = ( ("=[td]ud",   "tud"),
                            ("=nud",      "nud"),
                            ("=mine",     "mine"),
                            ("=nu$",       "nu"),
                            ("=nu[+]",       "nu"),
                            ("=[td]u$",    "tu"),
                            ("=[td]u[+]",    "tu"),
                            ("=v$",       "v"),
                            ("=[td]av",   "tav"),
                            ("=mata",     "mata"),
                            ("=ja",       "ja")
    )

    # Note: in double forms like 'vihatud-armastatud', both components should actually get the same analysis
    # (the same POS-tag - S, A, or V and corresponding attributes like ending, morph analysis, etc)
    # which is not the case now ("viha=tu+d-armasta" the first part is currently analysed as a noun, the second
    # as a verb). 
    
#     def rewrite(self, record):
#         for rec in record:
#             rec['verb_extension_suffix'] = None
#             if '=' in rec['root']:
#                 for pattern, value in self._suffix_conversions:
#                     if re.search(pattern, rec['root']):
#                         rec['verb_extension_suffix'] = value
#                         break
#         return record
    def rewrite(self, record):
        # 'verb_extension_suffix' on siin list (ikka eelmise versiooniga ühildumiseks)
        # 'Kirutud-virisetud'
        for rec in record:
            rec['verb_extension_suffix'] = []
            if '=' in rec['root']:
                for pattern, value in self._suffix_conversions:
                    if re.search(pattern, rec['root']):
                        if value not in rec['verb_extension_suffix']:
                            rec['verb_extension_suffix'].append(value)
        return record


class SubcatRewriter():
    ''' Adds subcategorization information (hashtags) to verbs and adpositions.
    
        Subcategorization describes the necessary arguments that are required by the word.
        
        In verbs, this is related to both valency and transitivity.
        
        Transitivity is a property of verbs that defines whether they take a direct object:
         e.g 'vaatama' takes a direct object ("Ma vaatan filmi".)
             'suhtlema' does not take a direct object (but it takes other syntactic arguments - "Jüri suhtleb Mariga." 
        SubcatRewriter adds a tag #Intr to intransitive verbs (verbs that cannot take a direct object)
        
        Valency is the number of syntactic arguments required by the predicate:
         e.g 'andma' requires three:
            "Jüri annab Marile raamatu." is a correct sentence, arguments Jüri, Mari and raamat are all necessary
            "Jüri annab.", "Jüri annab Marile.", "Jüri annab raamatu." are missing some arguments and feel incomplete
         e.g 'jooksma' requires one:
            "Jüri jookseb." is a correct sentence. 
            "Jüri jookseb Tartus maratoni." is correct as well, but the location and distance are not
            necessary in the sentence and are therefore not arguments
        SubcatRewriter specifies the cases/types of verbs' syntactic arguments:
            #Part, #NGP-P, #Part-P direct object (can be nominative, genitive, partitive, a clause or construction)
            #Ill illative ("Eestlased emigreerusid **Kanadasse**.")
            #In inessive ("Vanaema kahtleb **müüja jutus**.")
            #El elative ("Tibu koorus **munast**.")
            #All allative ("Aasta läheneb **lõpule**.")
            #Ad adessive ("Järeldused põhinevad **eeldustel**.")
            #Abl ablative ("Õpilane küsib **õpetajalt** küsimuse.")
            #Tr translative ("Elevant külmub **kringliks**.")
            #Ter terminative ("Laps ei küündi **kraanikausini**.")
            #Es essive ("Jüri käitus **tõelise metslasena**.")
            #Kom comitative ("Võistleja leppis **tulemusega**.")
            #InfP infinite verb form ("Laps ei viitsi **õppda**.")
            
        For adpositions (laua **peal**, eilsest **saadik**, **mööda** põldu), subcategorization denotes
        the case of the noun phrase that it appears with: in the previous examples, postposition 'peal'
        needs a noun phrase in genitive form, 'saadik' needs a noun phrase in elative form and  preposition
        'mööda' needs a noun phrase in partitive case.
        The tags used for adpositions:
            #gen genitive (**laua** peal)
            #part partitive (mööda **põldu**)
            #nom nominative (**päev** otsa)
            #el (**eilsest** saadik)
            #all (tänu **emale**)
            #term (kuni **õhtuni**)
            #abes (ilma **hariduseta**)
        
        
        Argument subcat_rules must be a dict containing subcategorization information,
        loaded via method load_subcat_info();

        Performs word lemma lookups in subcat_rules, and in case of a match, checks 
        word part-of-speech conditions. If the POS conditions match, adds subcategorization
        information either to a single analysis line, or to multiple analysis lines 
        (depending on the exact conditions in the rule);

        Returns the input list where verb/adposition analyses have been augmented 
        with available subcategorization information;
    '''
    def __init__(self, subcat_rules_file=None):
        if subcat_rules_file:
            assert os.path.exists(subcat_rules_file),\
                'Unable to find *subcat_rules_file* from location ' + subcat_rules_file
        else:
            subcat_rules_file = os.path.dirname(__file__)
            subcat_rules_file = os.path.join(subcat_rules_file,
                                             'rules_files/abileksikon06utf.lx')
            assert os.path.exists(subcat_rules_file),\
                'Missing default *subcat_rules_file* ' + subcat_rules_file
        self.v_rules, self.k_rules = self._load_subcat_info(subcat_rules_file)

    def rewrite(self, record):
        result = []
        for rec in record:
            
            rules = None
            if rec['partofspeech'] == 'V':
                # nii pole õige teha, aga see võimaldab jäljendada eelmist versiooni
                # kasutamata abileksikon_extrat
                root = rec['root'].split('+')[0] # 'Avatakse-suletakse'
                rules = self.v_rules.get((root, rec['partofspeech']), None)
            elif rec['partofspeech'] == 'K':
                root = rec['root'].split('+')[0]
                rules = self.k_rules.get((root, rec['partofspeech'], rec['form']), None)
            if rules is not None:
                for subcat in rules: # võib vaadelda eraldi juhtu len(rules) == 1
                    rec_copy = rec.copy()
                    rec_copy['subcat'] = subcat
                    result.append(rec_copy)
            else:
                rec['subcat'] = None
                result.append(rec)

        return result

    def _load_subcat_info(self, subcat_rules_file):
        ''' Loads subcategorization rules (for verbs and adpositions) from a text 
            file. 
            It is expected that the rules are given as pairs, where the first item is 
            the lemma (of verb/adposition), followed on the next line by the 
            subcategorization rule, in the following form: 
               on the left side of '>' is the condition (POS-tag requirement for the 
               lemma), 
             and 
               on the right side is the listing of subcategorization settings (hashtag 
               items, e.g. names of morphological cases of nominals);
            If there are multiple subcategorization rules to be associated with a
            single lemma, different rules are separated by '&'.
    
            Example, an excerpt from the rules file:
              läbi
              _V_ >#Part &_K_ post >#gen |#nom |#el &_K_ pre >#gen 
              läbista
              _V_ >#NGP-P 
              läbistu
              _V_ >#Intr 
    
            Returns a dict of root to a-list-of-subcatrules mappings.
        '''
        rules = defaultdict(list)
        nonSpacePattern = re.compile('^\S+$')
        posTagPattern   = re.compile('_._')
        def read_lexicon(file, rules):
            in_f = codecs.open(file, mode='r', encoding='utf-8')
            root = None
            subcatRules = None
            for line in in_f:
                # seda võib kirjutada lihtsamaks, kui võib eeldada, et faili formaat on range
                line = line.rstrip()
                if posTagPattern.search(line) and root:
                    subcatRules = line
                    parts = subcatRules.split('&')#[::-1]#76 tekst 
                    for part in parts:
                        part = part.strip()
                        rules[root].append(part)
                    root = None
                    subcatRules = None
                elif nonSpacePattern.match(line):
                    root = line
            in_f.close()
            return rules

        rules = read_lexicon(subcat_rules_file, rules)
        #print( len(rules.keys()) )   # 4484

        v_rules = defaultdict(list)
        k_rules = defaultdict(list)
        for root, rulelist in rules.items():
            for rule in rulelist:
                pos, subcats = rule.split('>')
                pos = pos.strip()
                #if pos == '_V_':
                #    v_rules[(root, 'V')] = []
                if pos == '_K_ post':
                    if (root, 'K', 'post') in k_rules:
                        continue
                if pos == '_K_ pre':
                    if (root, 'K', 'pre') in k_rules:
                        continue
                    #k_rules[(root, 'K', 'pre')] = []
                for subcat in subcats.split('|'):
                    subcat = subcat.strip()
                    if pos == '_V_':
                        if all([subcat not in s for s in v_rules[(root, 'V')]]):
                        # ei tea, kas see if teeb mõistlikku asja, aga igatahes aitab ühilduda eelmise versiooniga
                            v_rules[(root, 'V')].append(subcat)
                    elif pos == '_K_ post':
                        if all([subcat not in s for s in k_rules[(root, 'K', 'post')]]):
                            k_rules[(root, 'K', 'post')].append(subcat)
                    elif pos == '_K_ pre':
                        if all([subcat not in s for s in k_rules[(root, 'K', 'pre')]]):
                            k_rules[(root, 'K', 'pre')].append(subcat)
        # [::-1] eelmise versiooniga ühildumiseks
        for k, v in v_rules.items():
            v_rules[k] = v[::-1]
        for k, v in k_rules.items():
            k_rules[k] = v[::-1]
        
        for key in v_rules:
            for i, subcat in enumerate(v_rules[key]):
                v_rules[key][i] = [s.strip(' #') for s in subcat.split()]
        for key in k_rules:
            for i, subcat in enumerate(k_rules[key]):
                k_rules[key][i] = [s.strip(' #') for s in subcat.split()]

        return v_rules, k_rules


class MorphExtendedRewriter():
    ''' Combines the rewrite methods of 
        PunctuationTypeRewriter
        MorphToSyntaxMorphRewriter
        PronounTypeRewriter
        RemoveDuplicateAnalysesRewriter
        RemoveAdpositionAnalysesRewriter
        LetterCaseRewriter
        FiniteFormRewriter
        VerbExtensionSuffixRewriter
        SubcatRewriter
    ''' 
    
    def __init__(self, punctuation_type_rewriter, morph_to_syntax_morph_rewriter, 
                 pronoun_type_rewriter,
                 remove_duplicate_analyses_rewriter,
                 remove_adposition_analyses_rewriter,
                 letter_case_rewriter, finite_form_rewriter,
                 verb_extension_suffix_rewriter, subcat_rewriter):
        self.punctuation_type_rewriter = punctuation_type_rewriter
        self.morph_to_syntax_morph_rewriter = morph_to_syntax_morph_rewriter
        self.pronoun_type_rewriter = pronoun_type_rewriter
        self.remove_duplicate_analyses_rewriter = remove_duplicate_analyses_rewriter
        self.remove_adposition_analyses_rewriter=remove_adposition_analyses_rewriter
        self.letter_case_rewriter = letter_case_rewriter
        self.finite_form_rewriter = finite_form_rewriter
        self.verb_extension_suffix_rewriter = verb_extension_suffix_rewriter
        self.subcat_rewriter = subcat_rewriter

    def rewrite(self, record):
        record = self.punctuation_type_rewriter.rewrite(record)
        record = self.morph_to_syntax_morph_rewriter.rewrite(record)
        record = self.pronoun_type_rewriter.rewrite(record)
        record = self.remove_duplicate_analyses_rewriter.rewrite(record)
        record = self.remove_adposition_analyses_rewriter.rewrite(record)
        record = self.letter_case_rewriter.rewrite(record)
        record = self.finite_form_rewriter.rewrite(record)
        record = self.verb_extension_suffix_rewriter.rewrite(record)
        record = self.subcat_rewriter.rewrite(record)

        record = self.remove_adposition_analyses_rewriter.rewrite(record)

        return record