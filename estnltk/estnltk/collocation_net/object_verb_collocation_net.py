from estnltk.collocation_net.base_collocation_net import BaseCollocationNet


class ObjectVerbCollocationNet(BaseCollocationNet):
    def __init__(self):
        super(ObjectVerbCollocationNet, self).__init__(collocation_type='object_verb')

    def objects_used_with_verb(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def verbs_used_with_object(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def similar_objects(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_objects_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_rows_for_list(words, number_of_words)

    def similar_verbs(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_verbs_for_several(self, words: list, number_of_words: int = 10):
        return super().similar_columns_for_list(words, number_of_words)

    def predict_verb_probabilities(self, obj: str, verbs: list = None, number_of_verbs: int = 10):
        return super().predict_column_probabilities(obj, verbs, number_of_verbs)

    def predict_object_probabilities(self, verb: str, objects: list = None, number_of_objects: int = 10):
        return super().predict_row_probabilities(verb, objects, number_of_objects)

    def predict_verb_for_several_objects(self, obj: list, number_of_verbs: int = 10):
        return super().predict_for_several_rows(obj, number_of_verbs)

    def predict_topic_for_several_objects(self, objects: list, number_of_topics: int = 10, number_of_verbs: int = 10):
        return super().predict_topic_for_several_rows(objects, number_of_topics, number_of_verbs)

    def examples(self, object: str, verb: str, table_name="examples"):
        return super().examples(verb, object, table_name)
