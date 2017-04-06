from estnltk.rewriting.helpers.morph_analyzed_token import MorphAnalyzedToken


class WordNormalizingRewriter:
    def rewrite(self, record):
        token = MorphAnalyzedToken(record['text'])
        if token is token.normal:
            return None
        record['normal'] = token.normal.text
        return record
