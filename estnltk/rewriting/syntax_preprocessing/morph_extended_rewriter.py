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
