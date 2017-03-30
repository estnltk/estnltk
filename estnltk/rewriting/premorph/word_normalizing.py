from .morph_analyzed_token import MorphAnalyzedToken


class WordNormalizingRewriter:
    def rewrite(self, record):
        token = MorphAnalyzedToken(record['text_copy'])
        if token is token.normal:
            return None
        record['normal'] = token.normal.text
        return record
