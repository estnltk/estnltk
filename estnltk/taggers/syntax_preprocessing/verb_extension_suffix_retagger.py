import regex as re


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
            rec['verb_extension_suffix'] = tuple(rec['verb_extension_suffix'])
        return record
