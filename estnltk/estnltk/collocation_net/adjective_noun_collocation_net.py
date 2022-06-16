from estnltk.collocation_net.base_collocation_net import BaseCollocationNet


class AdjectiveNounCollocationNet(BaseCollocationNet):
    def __init__(self):
        super(AdjectiveNounCollocationNet, self).__init__(collocation_type='adjective_noun')

    def nouns_used_with_adjective(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def adjectives_used_with_noun(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def similar_nouns(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_nouns_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_columns_for_list(words, number_of_words)

    def similar_adjectives(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_adjectives_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_rows_for_list(words, number_of_words)

    def predict_adjective_probabilities(self, noun: str, adjectives: list = None, number_of_adjectives: int = 10):
        return super().predict_row_probabilities(noun, adjectives, number_of_adjectives)

    def predict_noun_probabilities(self, adjective: str, nouns: list = None, number_of_nouns: int = 10):
        return super().predict_column_probabilities(adjective, nouns, number_of_nouns)

    def predict_nouns_for_several_adjectives(self, adjectives: list, number_of_nouns: int = 10):
        return super().predict_for_several_rows(adjectives, number_of_nouns)

    def predict_topic_for_several_adjectives(self, adjectives: list, number_of_topics: int = 10, number_of_nouns: int = 10):
        return super().predict_topic_for_several_rows(adjectives, number_of_topics, number_of_nouns)

    def examples(self, adjective: str, noun: str, table_name="examples"):
        return super().examples(noun, adjective, table_name)
