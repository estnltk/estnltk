from base_collocation_net import BaseCollocationNet


class NounAdjectiveCollocationNet(BaseCollocationNet):
    def nouns_used_with_adjective(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def adjectives_used_with_noun(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def similar_nouns(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_nouns_for_several(self, words: list, num_of_words: int = 10):
        return super().similar_rows_for_list(words, num_of_words)

    def similar_adjectives(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_adjectives_for_several(self, words: list, num_of_words: int = 10):
        return super().similar_columns_for_list(words, num_of_words)

    def predict_adjective_probabilities(self, noun: str, adjectives: list = None, num_of_adjectives: int = 10):
        return super().predict_column_probabilities(noun, adjectives, num_of_adjectives)

    def predict_noun_probabilities(self, adjective: str, nouns: list = None, num_of_nouns: int = 10):
        return super().predict_row_probabilities(adjective, nouns, num_of_nouns)

    def predict_adjectives_for_several_nouns(self, nouns: list, num_of_adjectives: int = 10):
        return super().predict_for_several_rows(nouns, num_of_adjectives)

    def predict_topic_for_several_nouns(self, nouns: list, num_of_topics: int = 10, num_of_adjectives: int = 10):
        return super().predict_topic_for_several_rows(nouns, num_of_topics, num_of_adjectives)
