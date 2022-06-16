from estnltk.collocation_net.base_collocation_net import BaseCollocationNet


class AdverbVerbCollocationNet(BaseCollocationNet):
    def __init__(self):
        super(AdverbVerbCollocationNet, self).__init__(collocation_type='adverb_verb')

    def adverbs_used_with_verb(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def verbs_used_with_adverb(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def similar_adverbs(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_adverbs_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_rows_for_list(words, number_of_words)

    def similar_verbs(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_averbs_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_columns_for_list(words, number_of_words)

    def predict_verb_probabilities(self, adverb: str, verbs: list = None, number_of_verbs: int = 10):
        return super().predict_column_probabilities(adverb, verbs, number_of_verbs)

    def predict_adverb_probabilities(self, verb: str, adverbs: list = None, number_of_adverbs: int = 10):
        return super().predict_row_probabilities(verb, adverbs, number_of_adverbs)

    def predict_verb_for_several_adverbs(self, adverbs: list, number_of_verbs: int = 10):
        return super().predict_for_several_rows(adverbs, number_of_verbs)

    def predict_topic_for_several_adverbs(self, adverbs: list, number_of_topics: int = 10, number_of_verbs: int = 10):
        return super().predict_topic_for_several_rows(adverbs, number_of_topics, number_of_verbs)

    def examples(self, adverb: str, verb: str, table_name="examples"):
        return super().examples(verb, adverb, table_name)
