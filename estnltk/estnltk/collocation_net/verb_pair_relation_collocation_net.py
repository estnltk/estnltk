from estnltk.collocation_net.base_collocation_net import BaseCollocationNet


class VerbPairRelationCollocationNet(BaseCollocationNet):
    def __init__(self, rel_type: str = "case_deprel"):
        """
        :param rel_type: Type of relation to use for the Collocation Net. Currently possible
        options are 'case_deprel', 'numbered_case' and 'case_only'.
        """
        super(VerbPairRelationCollocationNet, self).__init__(collocation_type=rel_type)

    def pairs_used_with_relation(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def relations_used_with_pair(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def similar_pairs(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_pairs_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_rows_for_list(words, number_of_words)

    def similar_relations(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_relations_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_columns_for_list(words, number_of_words)

    def predict_relation_probabilities(self, verb_pair: str, relations: list = None, number_of_relations: int = 10):
        return super().predict_column_probabilities(verb_pair, relations, number_of_relations)

    def predict_pair_probabilities(self, relation: str, pairs: list = None, number_of_pairs: int = 10):
        return super().predict_row_probabilities(relation, pairs, number_of_pairs)

    def predict_relations_for_several_pairs(self, pairs: list, number_of_relations: int = 10):
        return super().predict_for_several_rows(pairs, number_of_relations)

    def predict_topic_for_several_pairs(self, pairs: list, number_of_topics: int = 10, number_of_relations: int = 10):
        return super().predict_topic_for_several_rows(pairs, number_of_topics, number_of_relations)
