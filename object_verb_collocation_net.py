from base_collocation_net import BaseCollocationNet


class VerbObjectCollocationNet(BaseCollocationNet):
    def __init__(self):
        super(VerbObjectCollocationNet, self).__init__(collocation_type='object_verb')

    def objects_used_with_verb(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def verbs_used_with_object(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def similar_objects(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_objects_for_several(self, words: list, num_of_words: int = 10):
        return super().similar_rows_for_list(words, num_of_words)

    def similar_verbs(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_verbs_for_several(self, words: list, num_of_words: int = 10):
        return super().similar_columns_for_list(words, num_of_words)

    def predict_verb_probabilities(self, object: str, verbs: list = None, num_of_verbs: int = 10):
        return super().predict_column_probabilities(object, verbs, num_of_verbs)

    def predict_object_probabilities(self, verb: str, object: list = None, num_of_objects: int = 10):
        return super().predict_row_probabilities(verb, object, num_of_objects)

    def predict_verb_for_several_objects(self, object: list, num_of_verbs: int = 10):
        return super().predict_for_several_rows(object, num_of_verbs)

    def predict_topic_for_several_objects(self, objects: list, num_of_topics: int = 10, num_of_verbs: int = 10):
        return super().predict_topic_for_several_rows(objects, num_of_topics, num_of_verbs)
