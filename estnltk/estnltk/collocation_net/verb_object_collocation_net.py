from estnltk.collocation_net.base_collocation_net import BaseCollocationNet


class VerbObjectCollocationNet(BaseCollocationNet):
    def __init__(self):
        super(VerbObjectCollocationNet, self).__init__(collocation_type='verb_object', examples_file='object_verb')

    def verbs_used_with_object(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def objects_used_with_verb(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def similar_verbs(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_verbs_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_rows_for_list(words, number_of_words)

    def similar_objects(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_objects_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_columns_for_list(words, number_of_words)

    def predict_object_probabilities(self, verb: str, objects: list = None, number_of_objects: int = 10):
        return super().predict_column_probabilities(verb, objects, number_of_objects)

    def predict_verb_probabilities(self, obj: str, verbs: list = None, number_of_verbs: int = 10):
        return super().predict_row_probabilities(obj, verbs, number_of_verbs)

    def predict_object_for_several_verbs(self, verbs: list, number_of_objects: int = 10):
        return super().predict_for_several_rows(verbs, number_of_objects)

    def predict_topic_for_several_verbs(self, verbs: list, number_of_topics: int = 10, number_of_objects: int = 10):
        return super().predict_topic_for_several_rows(verbs, number_of_topics, number_of_objects)

    def examples(self, verb: str, object: str, table_name="examples"):
        return super().examples(verb, object, table_name)
