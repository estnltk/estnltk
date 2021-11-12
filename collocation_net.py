import pickle
import scipy
import os
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.neighbors import NearestNeighbors


class CollocationNetException(Exception):
    pass


class BaseCollocationNet:
    """
    CollocationNet class
    """

    def __init__(self, collocation_type: str = 'noun_adjective', read_data: bool = False):
        path = f"{os.path.dirname(os.path.abspath(__file__))}/data/{collocation_type}"
        if read_data:
            self.data = pd.read_csv(f"{path}/df.csv", index_col=0)
        self.row_dist = np.load(f"{path}/lda_row_distribution.npy")
        self.column_dist = np.load(f"{path}/lda_column_distribution.npy")
        self.rows = np.load(f"{path}/rows.npy", allow_pickle=True)
        self.columns = np.load(f"{path}/columns.npy", allow_pickle=True)
        self.topics = np.load(f"{path}/lda_topics.npy", allow_pickle=True)

        self.column_dist_probs = self.column_dist / self.column_dist.sum(axis=0)

    def row_index(self, word: str) -> int:
        for i, noun in enumerate(self.rows):
            if noun == word:
                return i
        raise CollocationNetException(f"Word '{word}' not in the dataset.")

    def column_index(self, word: str) -> int:
        for i, adj in enumerate(self.columns):
            if adj == word:
                return i
        raise CollocationNetException(f"Word '{word}' not in the dataset.")

    def rows_used_with(self, word: str, number_of_words: int = 10) -> list:
        word_index = self.column_index(word)

        column_topic = self.column_dist[:, word_index].argmax()
        row_topic = self.row_dist[:, column_topic].argsort()[::-1][:number_of_words]

        return self.rows[row_topic].tolist()

    def columns_used_with(self, word: str, number_of_words: int = 10) -> list:
        word_index = self.row_index(word)

        row_topic = self.row_dist[word_index].argmax()
        column_topic = self.column_dist[row_topic].argsort()[::-1][:number_of_words]

        return self.columns[column_topic].tolist()

    def similar_rows(self, word: str, number_of_words: int = 10) -> list:
        knn = NearestNeighbors(n_neighbors=number_of_words + 1).fit(self.row_dist)
        idx_of_word = self.row_index(word)

        neighbour_ids = knn.kneighbors(self.row_dist[idx_of_word].reshape(1, -1), return_distance=False)
        neighbours = self.rows[neighbour_ids]

        return list(neighbours[0])[1:]

    def similar_rows_for_list(self, words: list, num_of_words: int = 10) -> list:
        similar_for_each = {}

        for word in words:
            word_similar = self.similar_rows(word, self.rows.shape[0] - 1)
            similar_for_each[word] = word_similar

        common = []

        for i, row_words in enumerate(similar_for_each[words[0]]):
            if row_words in words:
                continue

            is_in_all = sum([1 for l in words[1:] if row_words in similar_for_each[l]])
            if is_in_all != len(words) - 1:
                continue

            c = [row_words, i]

            for l in words[1:]:
                c.append(similar_for_each[l].index(row_words))

            common.append(c)

        sorted_common = sorted(common, key= lambda x: sum(x[1:]))

        if len(sorted_common) == 0:
            return None

        similar_words = [sort[0] for sort in sorted_common]

        return similar_words[:num_of_words]

    def similar_columns(self, word: str, number_of_words: int = 10) -> list:
        column_vals = self.column_dist.T
        knn = NearestNeighbors(n_neighbors=number_of_words + 1).fit(column_vals)
        idx_of_word = self.column_index(word)

        neighbour_ids = knn.kneighbors(column_vals[idx_of_word].reshape(1, -1), return_distance=False)
        neighbours = self.columns[neighbour_ids]

        return list(neighbours[0])[1:]

    def similar_columns_for_list(self, words: list, num_of_words: int = 10) -> list:
        similar_for_each = {}

        for word in words:
            word_similar = self.similar_columns(word, self.columns.shape[0] - 1)
            similar_for_each[word] = word_similar

        common = []

        for i, column_word in enumerate(similar_for_each[words[0]]):
            if column_word in words:
                continue

            is_in_all = sum([1 for l in words[1:] if column_word in similar_for_each[l]])
            if is_in_all != len(words) - 1:
                continue

            c = [column_word, i]

            for l in words[1:]:
                c.append(similar_for_each[l].index(column_word))

            common.append(c)

        sorted_common = sorted(common, key= lambda x: sum(x[1:]))

        if len(sorted_common) == 0:
            return None

        similar_words = [sort[0] for sort in sorted_common]

        return similar_words[:num_of_words]

    def topic(self, word: str) -> int:
        """
        TODO
        .....
        :param word:
        :param with_info:
        :return:
        """
        for topic, words in enumerate(self.topics):
            if word in words:
                return list(words)

        raise CollocationNetException(f"Word '{word}' not in dataset")

    def characterisation(self, word: str, number_of_topics: int = 10, number_of_words: int = 10):
        """

        :param word:
        :param number_of_topics:
        :param number_of_words:
        :return:
        """
        word_index = self.row_index(word)

        topic_vector = self.row_dist[word_index]
        sorted_index = topic_vector.argsort()[::-1][:number_of_topics]
        columns_in_topics = pd.DataFrame(self.column_dist, columns=self.columns)
        final_list = list()

        for i in sorted_index:
            final_list.append((round(topic_vector[i], 3), columns_in_topics.loc[i].sort_values(ascending=False)[:number_of_words].index.tolist()))

        return final_list

    def predict_column_probabilities(self, row: str, columns: list = None, num_of_columns: int = 10) -> list:
        """
        :param row:
        :param columns:
        :param num_of_columns:
        :return:
        """
        row_index = self.row_index(row)
        row_topics = self.row_dist[row_index]

        avg_per_column = np.matmul(row_topics, self.column_dist_probs)

        if columns is None:
            top_column_ind = np.argpartition(avg_per_column, -num_of_columns)[-num_of_columns:]
            top_column_ind = top_column_ind[np.argsort(avg_per_column[top_column_ind])][::-1]
            top_probs = avg_per_column[top_column_ind]
            top_column_words = self.columns[top_column_ind]
            return list(zip(*(top_column_words, top_probs)))

        results = []

        for column_word in columns:
            column_idx = self.column_index(column_word)
            results.append((column_word, avg_per_column[column_idx]))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def predict_row_probabilities(self, column: str, rows: list = None, num_of_rows: int = 10) -> list:
        """
        :param column:
        :param rows:
        :param num_of_rows:
        :return:
        """
        column_index = self.column_index(column)
        column_topics = self.column_dist_probs.T[column_index]

        avg_per_row = np.matmul(column_topics, self.row_dist.T)

        if rows is None:
            top_row_ind = np.argpartition(avg_per_row, -num_of_rows)[-num_of_rows:]
            top_row_ind = top_row_ind[np.argsort(avg_per_row[top_row_ind])][::-1]
            top_probs = avg_per_row[top_row_ind]
            top_row_words = self.rows[top_row_ind]
            return list(zip(*(top_row_words, top_probs)))

        results = []

        for row_word in rows:
            row_idx = self.row_index(row_word)
            results.append((row_word, avg_per_row[row_idx]))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def predict_for_several_rows(self, words: list, num_of_columns: int = 10):
        avg_probs = defaultdict(int)

        for word in words:
            adj_probs = self.predict_column_probabilities(word, num_of_columns=self.columns.shape[0])
            for adj, prob in adj_probs:
                avg_probs[adj] += prob

        avg_probs = [(k, v / len(words)) for k, v in avg_probs.items()]

        return sorted(avg_probs, key=lambda x: x[1], reverse=True)[:num_of_columns]

    def predict_topic_for_several_rows(self, words: list, num_of_topics: int = 10, num_of_columns: int = 10):
        """
        When given a list of several words in rows, it predicts the most likely topic for them and returns
        the average probability of that topic and the top words describing that topic.
        :param words:
        :param num_of_topics:
        :param num_of_columns:
        :return:
        """
        avg_probs = defaultdict(int)

        for word in words:
            word_idx = self.row_index(word)
            topic_probs = self.row_dist[word_idx]
            for i, prob in enumerate(topic_probs):
                avg_probs[i] += prob

        avg_probs = [(k, v / len(words)) for k, v in avg_probs.items()]
        sorted_topics = sorted(avg_probs, key=lambda x: x[1], reverse=True)[:num_of_topics]
        predicted_topics = []

        for topic_id, topic_prob in sorted_topics:
            topic_columns = self.column_dist[topic_id]
            top_column_ind = np.argpartition(topic_columns, -num_of_columns)[-num_of_columns:]
            top_column_ind = top_column_ind[np.argsort(topic_columns[top_column_ind])][::-1]
            predicted_topics.append((list(self.columns[top_column_ind]), topic_prob))

        return predicted_topics

    def usable_phrase(self, row: str, column: str, number_of_topics: int = 10) -> str:
        """

        :param row: first word of the collocation, presented as rows in the data
        :param column: second word of the collocation, presented as columns in the data
        :param number_of_topics:
        :return:
        """
        word_index = self.row_index(row)

        topic_vector = self.row_dist[word_index]
        sorted_index = topic_vector.argsort()[::-1][:number_of_topics]
        column_words_in_topics = pd.DataFrame(self.column_dist, columns=self.columns)

        for i in sorted_index:
            adjs = column_words_in_topics.loc[i][column_words_in_topics.loc[i] > 10].sort_values(ascending=False).index.tolist()
            for a in adjs:
                if a == column:
                    return f"Fraas '{column} {row}' on koos kasutatav."

        return f"Fraas '{column} {row}' ei ole koos kasutatav."


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
