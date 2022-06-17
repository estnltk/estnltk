import os
import sqlite3
import pkgutil
import pandas as pd
import numpy as np
from typing import List
import matplotlib.pyplot as plt
from collections import defaultdict
from estnltk import get_resource_paths

class BaseCollocationNet:
    """
    BaseCollocationNet class, serves as a base for CollocationNets
    with different collocation types.
    """

    def __init__(self, collocation_type: str = 'noun_adjective', base_path: str = None, examples_file: str = None):
        if base_path is None:
            base_path = get_resource_paths("collocation_net", only_latest=True, download_missing=True)
            if base_path is None:
                raise Exception("CollocationNet's resources have not been downloaded. "+\
                                "Use estnltk.download('collocation_net') to get the missing resources.")
        if examples_file is None:
            examples_file = collocation_type
        self.examples_path = f"{base_path}/examples/{examples_file}.db"
        path = f"{base_path}/data/{collocation_type}"
        self.path = path
        self.row_dist = np.load(f"{path}/lda_row_distribution.npy")
        self.column_dist = np.load(f"{path}/lda_column_distribution.npy")
        self.rows = np.load(f"{path}/rows.npy", allow_pickle=True)
        self.columns = np.load(f"{path}/columns.npy", allow_pickle=True)
        self.topics = np.load(f"{path}/lda_topics.npy", allow_pickle=True)

        self.column_dist_probs = self.column_dist / self.column_dist.sum(axis=0)

    def is_package_installed(self, module: str) -> bool:
        """
        Checks if the package sklearn has been installed.
        This package is required for the similar words functions.
        """
        return pkgutil.find_loader(module) is not None

    def row_index(self, word: str) -> int:
        """
        Returns the index of the word in a row. Words in the dataset rows were
        used as documents when training the LDA model.
        """
        for i, noun in enumerate(self.rows):
            if noun == word:
                return i
        raise ValueError(f"Word '{word}' not in the dataset.")

    def column_index(self, word: str) -> int:
        """
        Returns the index of the word in a column.
        """
        for i, adj in enumerate(self.columns):
            if adj == word:
                return i
        raise ValueError(f"Word '{word}' not in the dataset.")

    def rows_used_with(self, word: str, number_of_words: int = 10) -> list:
        """
        Returns a list of words most likely to form a collocation with the
        given word.
        """
        word_index = self.column_index(word)

        column_topic = self.column_dist[:, word_index].argmax()
        row_topic = self.row_dist[:, column_topic].argsort()[::-1][:number_of_words]

        return self.rows[row_topic].tolist()

    def columns_used_with(self, word: str, number_of_words: int = 10) -> List[str]:
        """
        Returns a list of words most likely to form a collocation with the
        given word.
        """
        word_index = self.row_index(word)

        row_topic = self.row_dist[word_index].argmax()
        column_topic = self.column_dist[row_topic].argsort()[::-1][:number_of_words]

        return self.columns[column_topic].tolist()

    def similar_rows(self, word: str, number_of_words: int = 10) -> List[str]:
        """
        Finds the most similar words to the given word using KNN based on
        the word distribution obtained from the LDA model.
        """
        if not self.is_package_installed("sklearn"):
            raise ModuleNotFoundError('Missing sklearn module that is ' + \
                                      'required for the functions finding similar words. Please install the ' + \
                                      'module via conda or pip, e.g.\n pip install -U scikit-learn')

        from sklearn.neighbors import NearestNeighbors

        knn = NearestNeighbors(n_neighbors=number_of_words + 1).fit(self.row_dist)
        idx_of_word = self.row_index(word)

        neighbour_ids = knn.kneighbors(self.row_dist[idx_of_word].reshape(1, -1), return_distance=False)
        neighbours = self.rows[neighbour_ids]

        return list(neighbours[0])[1:]

    def similar_rows_for_list(self, words: list, number_of_words: int = 10) -> List[str]:
        """
        Finds the most similar words in common for a list of given words using KNN
        based on the word distribution obtained with the LDA model.
        """
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

        return similar_words[:number_of_words]

    def similar_columns(self, word: str, number_of_words: int = 10) -> List[str]:
        """
        Finds the most similar words to the given word using KNN based on
        the word distribution obtained from the LDA model.
        """
        if not self.is_package_installed("sklearn"):
            raise ModuleNotFoundError('Missing sklearn module that is ' + \
                                      'required for the functions finding similar words. Please install the ' + \
                                      'module via conda or pip, e.g.\n pip install -U scikit-learn')

        from sklearn.neighbors import NearestNeighbors

        column_vals = self.column_dist.T
        knn = NearestNeighbors(n_neighbors=number_of_words + 1).fit(column_vals)
        idx_of_word = self.column_index(word)

        neighbour_ids = knn.kneighbors(column_vals[idx_of_word].reshape(1, -1), return_distance=False)
        neighbours = self.columns[neighbour_ids]

        return list(neighbours[0])[1:]

    def similar_columns_for_list(self, words: list, number_of_words: int = 10) -> List[str]:
        """
        Finds the most similar words in common for a list of given words using KNN
        based on the word distribution obtained with the LDA model.
        """
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

        return similar_words[:number_of_words]

    def topic(self, word: str) -> List[str]:
        """
        Returns the topic to which the word was assigned to. The topic
        returned shows all words assigned to this topic. Each word in
        the dataset was assigned to the topic with the highest probability.
        """
        for topic, words in enumerate(self.topics):
            if word in words:
                return list(words)

        raise ValueError(f"Word '{word}' not in dataset")

    def topic_words(self, word: str, number_of_words: int = 100):
        """
        Shows a Word Cloud of the top words that influenced belonging to the
        top cluster for the given word.
        :param word: Word for which we want to find words it forms collocations with
        :param number_of_words: Number of words to include in the Word Cloud, default 100
        """

        if not self.is_package_installed("wordcloud"):
            raise ModuleNotFoundError('Missing Wordcloud module that is ' + \
                                      'required for this function. Please install the ' + \
                                      'module via conda or pip, e.g.\n pip install wordcloud')

        from wordcloud import WordCloud

        topic_idx = None

        for topic, words in enumerate(self.topics):
            if word in words.tolist():
                topic_idx = topic
                break

        if topic_idx is None:
            raise ValueError(f"Word '{word}' not in dataset")

        dist = self.column_dist[topic_idx]
        words = self.columns

        wordcloud = WordCloud(background_color="white", color_func=lambda *args, **kwargs: "black",
                              max_words=number_of_words).generate_from_frequencies({v: d for v, d in zip(*(words, dist))})

        plt.imshow(wordcloud)

    def characterisation(self, word: str, number_of_topics: int = 10, number_of_words: int = 10) -> List[tuple]:
        """
        Returns the top clusters for the given word, showing the probability that the
        word belonged to said cluster for each of them. In addition to the probability,
        top words describing the cluster will be shown. For example if noun-adjective
        collocations are used, the given word could be a noun and then the words in clusters
        will be adjectives.
        """
        word_index = self.row_index(word)

        topic_vector = self.row_dist[word_index]
        sorted_index = topic_vector.argsort()[::-1][:number_of_topics]
        columns_in_topics = pd.DataFrame(self.column_dist, columns=self.columns)
        final_list = list()

        for i in sorted_index:
            final_list.append((round(topic_vector[i], 3), columns_in_topics.loc[i].sort_values(ascending=False)[:number_of_words].index.tolist()))

        return final_list

    def predict_column_probabilities(self, row: str, columns: list = None, number_of_columns: int = 10) -> List[tuple]:
        """
        When given a list of words the first word can form a collocation with, probabilities will
        be calculated for each collocation and the result will be an ordered list of tuples where
        each tuple is a word and its probability from most to least likely to form a collocation
        with the word corresponding to 'row'. If no list of words (columns) is provided, the top
        pairings will be found from the dataset.

        For example if we set row = 'kohv' and columns = ['tugev', 'kange'], the result will be
        [('kange', prob), ('tugev', prob)] meaning 'kange kohv' is a more likely collocation. In
        each tuple, prob will be a float from 0-1.
        """
        row_index = self.row_index(row)
        row_topics = self.row_dist[row_index]

        avg_per_column = np.matmul(row_topics, self.column_dist_probs)

        if columns is None:
            top_column_ind = np.argpartition(avg_per_column, -number_of_columns)[-number_of_columns:]
            top_column_ind = top_column_ind[np.argsort(avg_per_column[top_column_ind])][::-1]
            top_probs = avg_per_column[top_column_ind]
            top_column_words = self.columns[top_column_ind]
            return list(zip(*(top_column_words, top_probs)))

        results = []

        for column_word in columns:
            column_idx = self.column_index(column_word)
            results.append((column_word, avg_per_column[column_idx]))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def predict_row_probabilities(self, column: str, rows: list = None, number_of_rows: int = 10) -> List[tuple]:
        """
        When given a list of words the first word can form a collocation with, probabilities will
        be calculated for each collocation and the result will be an ordered list of tuples where
        each tuple is a word and its probability from most to least likely to form a collocation
        with the word corresponding to 'column'. If no list of words (rows) is provided, the top
        pairings will be found from the dataset.
        """
        column_index = self.column_index(column)
        column_topics = self.column_dist_probs.T[column_index]

        avg_per_row = np.matmul(column_topics, self.row_dist.T)

        if rows is None:
            top_row_ind = np.argpartition(avg_per_row, -number_of_rows)[-number_of_rows:]
            top_row_ind = top_row_ind[np.argsort(avg_per_row[top_row_ind])][::-1]
            top_probs = avg_per_row[top_row_ind]
            top_row_words = self.rows[top_row_ind]
            return list(zip(*(top_row_words, top_probs)))

        results = []

        for row_word in rows:
            row_idx = self.row_index(row_word)
            results.append((row_word, avg_per_row[row_idx]))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def predict_for_several_rows(self, words: list, number_of_columns: int = 10) -> List[tuple]:
        """
        Uses the function predict_column_probabilities to find most probable collocates with
        each given word. To predict which words are most likely to describe the entire list
        of words given, an average of probabilities is found. The result returned is an ordered
        list of tuples where each tuple contains the word that could form a collocation with
        each given word and its average probability.
        """
        avg_probs = defaultdict(int)

        for word in words:
            adj_probs = self.predict_column_probabilities(word, number_of_columns=self.columns.shape[0])
            for adj, prob in adj_probs:
                avg_probs[adj] += prob

        avg_probs = [(k, v / len(words)) for k, v in avg_probs.items()]

        return sorted(avg_probs, key=lambda x: x[1], reverse=True)[:number_of_columns]

    def predict_topic_for_several_rows(self, words: list, number_of_topics: int = 10, number_of_columns: int = 10) -> List[tuple]:
        """
        When given a list of several words in rows, it predicts the most likely topic for them and returns
        the average probability of that topic and the top words describing that topic.
        """
        avg_probs = defaultdict(int)

        for word in words:
            word_idx = self.row_index(word)
            topic_probs = self.row_dist[word_idx]
            for i, prob in enumerate(topic_probs):
                avg_probs[i] += prob

        avg_probs = [(k, v / len(words)) for k, v in avg_probs.items()]
        sorted_topics = sorted(avg_probs, key=lambda x: x[1], reverse=True)[:number_of_topics]
        predicted_topics = []

        for topic_id, topic_prob in sorted_topics:
            topic_columns = self.column_dist[topic_id]
            top_column_ind = np.argpartition(topic_columns, -number_of_columns)[-number_of_columns:]
            top_column_ind = top_column_ind[np.argsort(topic_columns[top_column_ind])][::-1]
            predicted_topics.append((list(self.columns[top_column_ind]), topic_prob))

        return predicted_topics

    def usable_phrase(self, row: str, column: str, number_of_topics: int = 10) -> bool:
        """
        Predicts whether the two words given are likely to form a collocation.
        """
        word_index = self.row_index(row)

        topic_vector = self.row_dist[word_index]
        sorted_index = topic_vector.argsort()[::-1][:number_of_topics]
        column_words_in_topics = pd.DataFrame(self.column_dist, columns=self.columns)

        for i in sorted_index:
            adjs = column_words_in_topics.loc[i][column_words_in_topics.loc[i] > 10].sort_values(ascending=False).index.tolist()
            for a in adjs:
                if a == column:
                    return True

        return False

    def examples(self, row: str, column: str, table_name: str) -> List[str]:
        conn = sqlite3.connect(self.examples_path)
        cur = conn.cursor()
        cur.execute(f"SELECT example1, example2, example3 FROM {table_name} WHERE word1 = '{row}' AND word2 = '{column}';")
        examples = cur.fetchone()
        final_sentences = []

        for sent in examples:
            if sent is not None:
                final_sentences.append(sent)

        return final_sentences
