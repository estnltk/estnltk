from base_collocation_net import BaseCollocationNet


class SubjectVerbCollocationNet(BaseCollocationNet):
    def __init__(self):
        super(SubjectVerbCollocationNet, self).__init__(collocation_type='subject_verb')

    def subjects_used_with_verb(self, word: str, number_of_words: int = 10):
        return super().rows_used_with(word, number_of_words)

    def verbs_used_with_subject(self, word: str, number_of_words: int = 10):
        return super().columns_used_with(word, number_of_words)

    def similar_subjects(self, word: str, number_of_words: int = 10):
        return super().similar_rows(word, number_of_words)

    def similar_subjects_for_several(self, words: list, num_of_words: int = 10):
        return super().similar_rows_for_list(words, num_of_words)

    def similar_verbs(self, word: str, number_of_words: int = 10):
        return super().similar_columns(word, number_of_words)

    def similar_verbs_for_several(self, words: list, num_of_words: int = 10):
        return super().similar_columns_for_list(words, num_of_words)

    def predict_verb_probabilities(self, subject: str, verbs: list = None, num_of_verbs: int = 10):
        return super().predict_column_probabilities(subject, verbs, num_of_verbs)

    def predict_subject_probabilities(self, verb: str, subject: list = None, num_of_subjects: int = 10):
        return super().predict_row_probabilities(verb, subject, num_of_subjects)

    def predict_verb_for_several_subjects(self, subject: list, num_of_verbs: int = 10):
        return super().predict_for_several_rows(subject, num_of_verbs)

    def predict_topic_for_several_subjects(self, subjects: list, num_of_topics: int = 10, num_of_verbs: int = 10):
        return super().predict_topic_for_several_rows(subjects, num_of_topics, num_of_verbs)
