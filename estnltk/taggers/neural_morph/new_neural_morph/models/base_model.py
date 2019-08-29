from multiprocessing import Queue, Process

import tensorflow as tf

from . import rnn_util
from .common_data_utils import minibatches, create_numpy_embeddings_matrix


class BaseModel(object):
    """Generic class for models."""

    def __init__(self, config):
        """Defines self.config and self.logger

        Args:
            config: (Config instance) class with hyper parameters,
                vocab and embeddings

        """
        self.config = config
        self.logger = config.logger
        self.sess = None
        self.saver = None

    def add_placeholders(self):
        """Define placeholders = entries to computational graph"""
        self.training_phase = tf.placeholder(tf.bool, shape=[], name="training_phase")
        # shape = (batch size, max length of sentence in batch)
        self.word_ids = tf.placeholder(tf.int32, shape=[None, None], name="word_ids")
        # shape = (batch_size, max_length of sentence)
        self.word_lengths = tf.placeholder(tf.int32, shape=[None, None], name="word_lengths")
        # length of sentences in a batch
        self.sequence_lengths = tf.placeholder(tf.int32, shape=[None], name="sequence_lengths")
        # shape = (batch size, max length of sentence, max length of word)
        self.char_ids = tf.placeholder(tf.int32, shape=[None, None, None], name="char_ids")

        # Placeholders for full-tag analyses
        # shape = (batch size, max length of sentence, max analyses per word)
        self.analysis_ids = tf.placeholder(tf.int32, shape=[None, None, None], name="analysis_ids")
        self.analysis_lengths = tf.placeholder(tf.int32, shape=[None, None], name="analysis_lengths")

        # Placeholders for category-level analyses
        if self.config.analysis_embeddings == "category":
            for category in self.config.vocab_analysis:
                plh = tf.placeholder(tf.int32,
                                     shape=[None, None, None],
                                     name="category_analyses_{}".format(self.escape_category(category)))
                self.setattr("category_analyses", plh, category)
                plh = tf.placeholder(tf.int32,
                                     shape=[None, None],
                                     name="category_analysis_lengths_{}".format(self.escape_category(category)))
                self.setattr("category_analysis_lengths", plh, category)

        # dynamic learning rate
        self.lr = tf.placeholder(dtype=tf.float32, shape=[], name="lr")

    def escape_category(self, category):
        return category.replace('[', '_').replace(']', '_').replace("$", "_").replace("+", "_").replace("^", "_")

    def getattr(self, name, category):
        return getattr(self, "{}_{}".format(name, self.escape_category(category)))

    def setattr(self, name, value, category):
        setattr(self, "{}_{}".format(name, self.escape_category(category)), value)

    def reinitialize_weights(self, scope_name):
        """Reinitializes the weights of a given layer"""
        variables = tf.contrib.framework.get_variables(scope_name)
        init = tf.variables_initializer(variables)
        self.sess.run(init)

    def add_encoder_op(self):
        with tf.variable_scope("bi-lstm"):
            if self.config.use_encoder_lstm_batch_norm is True:
                # Batch normalised bi-directional lstm with recurrent dropout
                keep_prob = 1.0 - (1.0 - self.config.encoder_lstm_recurrent_dropout) * tf.cast(self.training_phase,
                                                                                               tf.float32)
                cell_fw_list = [
                    rnn_util.StatefulLayerNormBasicLSTMCell(self.config.hidden_size_lstm, dropout_keep_prob=keep_prob)
                    for _ in range(self.config.lstm_layers_num)]
                cell_bw_list = [
                    rnn_util.StatefulLayerNormBasicLSTMCell(self.config.hidden_size_lstm, dropout_keep_prob=keep_prob)
                    for _ in range(self.config.lstm_layers_num)]
            else:
                cell_fw_list = [rnn_util.StatefulLSTMCell(self.config.hidden_size_lstm)
                                for _ in range(self.config.lstm_layers_num)]
                cell_bw_list = [rnn_util.StatefulLSTMCell(self.config.hidden_size_lstm)
                                for _ in range(self.config.lstm_layers_num)]

            if self.config.encoder_lstm_state_dropout < 1 or \
                            self.config.encoder_lstm_output_dropout < 1 or \
                            self.config.encoder_lstm_input_dropout < 1 or \
                            self.config.encoder_lstm_use_recurrent_drouout is True:
                state_keep_prob = 1.0 - (1.0 - self.config.encoder_lstm_state_dropout) * tf.cast(self.training_phase,
                                                                                                 tf.float32)
                input_keep_prob = 1.0 - (1.0 - self.config.encoder_lstm_input_dropout) * tf.cast(self.training_phase,
                                                                                                 tf.float32)
                output_keep_prob = 1.0 - (1.0 - self.config.encoder_lstm_output_dropout) * tf.cast(self.training_phase,
                                                                                                   tf.float32)
                cell_fw_list = [tf.contrib.rnn.DropoutWrapper(cell,
                                                              state_keep_prob=state_keep_prob,
                                                              input_keep_prob=input_keep_prob,
                                                              output_keep_prob=output_keep_prob,
                                                              variational_recurrent=self.config.encoder_lstm_use_recurrent_drouout)
                                for cell in cell_fw_list]
                cell_bw_list = [tf.contrib.rnn.DropoutWrapper(cell,
                                                              state_keep_prob=state_keep_prob,
                                                              input_keep_prob=input_keep_prob,
                                                              output_keep_prob=output_keep_prob,
                                                              variational_recurrent=self.config.encoder_lstm_use_recurrent_drouout)
                                for cell in cell_bw_list]

            output_h, output_c = rnn_util.stack_bidirectional_dynamic_rnn(cell_fw_list, cell_bw_list,
                                                                          inputs=self.word_embeddings,
                                                                          sequence_length=self.sequence_lengths,
                                                                          dtype=tf.float32)

            if self.config.encoder_lstm_dropout_output < 1:
                output_h = tf.layers.dropout(output_h, rate=1. - self.config.encoder_lstm_dropout_output,
                                             training=self.training_phase)
                output_c = tf.layers.dropout(output_c, rate=1. - self.config.encoder_lstm_dropout_output,
                                             training=self.training_phase)

        self.encoder_output = (output_h, output_c)

    def add_word_embeddings_op(self):
        assert self.config.use_word_embeddings or self.config.use_char_embeddings is True
        word_embeddings, char_embeddings, analysis_embeddings = None, None, None

        with tf.variable_scope("words"):
            if self.config.use_word_embeddings is True:
                if self.config.embeddings is None:
                    self.logger.info("WARNING: randomly initializing word vectors")
                    _word_embeddings = tf.get_variable(
                        name="_word_embeddings",
                        dtype=tf.float32,
                        shape=[self.config.nwords, self.config.dim_word])
                else:
                    _word_embeddings = tf.Variable(
                        self.config.embeddings,
                        name="_word_embeddings",
                        dtype=tf.float32,
                        trainable=self.config.train_embeddings)
                word_embeddings = tf.nn.embedding_lookup(_word_embeddings, self.word_ids, name="word_embeddings")

        with tf.variable_scope("chars"):
            if self.config.use_char_embeddings:
                # get char embeddings matrix
                _char_embeddings = tf.get_variable(
                    name="_char_embeddings",
                    dtype=tf.float32,
                    shape=[self.config.nchars, self.config.dim_char])
                char_embeddings = tf.nn.embedding_lookup(_char_embeddings, self.char_ids, name="char_embeddings")

                # Unfold batch into a list of words
                batch_size, max_sentence_len, max_word_len, _ = tf.unstack(tf.shape(char_embeddings))
                # shape = [words, max-word-length, char-embedding-size]
                char_embeddings = tf.reshape(char_embeddings, shape=[batch_size * max_sentence_len,
                                                                     max_word_len,
                                                                     self.config.dim_char])
                # shape = [words, max-word-length]
                word_lengths = tf.reshape(self.word_lengths, shape=[batch_size * max_sentence_len])

                # bi-lstm on chars
                cell_fw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char, state_is_tuple=True)
                cell_bw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char, state_is_tuple=True)
                outputs, output_states = tf.nn.bidirectional_dynamic_rnn(cell_fw, cell_bw,
                                                                         char_embeddings,
                                                                         sequence_length=word_lengths,
                                                                         dtype=tf.float32)

                # collect word character outputs for attention:
                output_fw, output_bw = outputs
                char_rnn_output = tf.concat([output_fw, output_bw], axis=-1)
                # shape = [batch X sentence-length X word-length X 2 * char-lstm-hidden-size]
                char_rnn_output = tf.reshape(char_rnn_output, [batch_size, max_sentence_len, max_word_len,
                                                               2 * self.config.hidden_size_char])
                self.char_rnn_output = char_rnn_output
                # self.char_rnn_out/ut = tf.nn.dropout(char_rnn_output, self.dropout)

                # concat word final states
                output_state_fw, output_state_bw = output_states
                output = tf.concat([output_state_fw.h, output_state_bw.h], axis=-1)
                # shape = (batch size, max sentence length, char hidden size)
                char_embeddings = tf.reshape(output,
                                             shape=[batch_size, max_sentence_len, 2 * self.config.hidden_size_char])

        analysis_embeddings = None
        if self.config.analysis_embeddings == "category":
            with tf.variable_scope("category_analysis"):
                cat_embeddings = []
                for cat in self.config.vocab_analysis:
                    analysis_ids = self.getattr("category_analyses", cat)
                    M = create_numpy_embeddings_matrix(len(self.config.vocab_analysis[cat]), self.config.dim_analysis)
                    analysis_embedding_matrix = tf.get_variable(
                        name="analysis_embedding_matrix_%s" % self.escape_category(cat),
                        initializer=M, dtype=tf.float32)
                    anal_embeddings = tf.nn.embedding_lookup(analysis_embedding_matrix,
                                                             analysis_ids,
                                                             name="analysis_embeddings_%s" % self.escape_category(cat))
                    # shape = [batch-size, max-sentence-length, analysis-embedding-size]
                    mask = tf.expand_dims(tf.cast(tf.cast(analysis_ids, tf.bool), tf.float32), -1)
                    anal_embeddings = tf.multiply(anal_embeddings, mask)
                    anal_embeddings_sum = tf.reduce_sum(anal_embeddings, axis=-2)
                    if self.config.analysis_embeddings_combination == "mean":
                        analysis_lengths = self.getattr("category_analysis_lengths", cat)
                        analysis_lengths = tf.expand_dims(tf.cast(analysis_lengths, tf.float32), -1)
                        analysis_lengths = tf.where(tf.equal(analysis_lengths, 0),
                                                    tf.ones_like(analysis_lengths),
                                                    analysis_lengths)
                        anal_embeddings_sum = tf.divide(anal_embeddings_sum, analysis_lengths)
                    cat_embeddings.append(anal_embeddings_sum)
                analysis_embeddings = tf.concat(cat_embeddings, axis=-1)
                with tf.control_dependencies([
                    tf.assert_rank(analysis_embeddings, 3),
                    tf.assert_equal(tf.shape(analysis_embeddings)[2],
                                    len(self.config.vocab_analysis) * self.config.dim_analysis)]):
                    analysis_embeddings = tf.identity(analysis_embeddings)
        elif self.config.analysis_embeddings == "tag":
            with tf.variable_scope("tag_analysis"):
                M = create_numpy_embeddings_matrix(self.config.nanalyses, self.config.dim_analysis)
                analysis_embedding_matrix = tf.get_variable(
                    name="analysis_embedding_matrix",
                    initializer=M,
                    dtype=tf.float32)
                analysis_embeddings_ = tf.nn.embedding_lookup(analysis_embedding_matrix,
                                                              self.analysis_ids,
                                                              name="analysis_embeddings")
                mask = tf.expand_dims(tf.cast(tf.cast(self.analysis_ids, tf.bool), tf.float32), -1)
                analysis_embeddings_ = tf.multiply(analysis_embeddings_, mask)
                # shape = [batch-size, max-sentence-length, analysis-embedding-size]
                analysis_embeddings = tf.reduce_sum(analysis_embeddings_, axis=-2)
                if self.config.analysis_embeddings_combination == "mean":
                    analysis_lengths = tf.expand_dims(tf.cast(self.analysis_lengths, tf.float32), -1)
                    # Handle division by zero
                    # 1) Replace 0's with 1's.
                    analysis_lengths = tf.where(tf.equal(analysis_lengths, 0),
                                                tf.ones_like(analysis_lengths),
                                                analysis_lengths)
                    analysis_embeddings = tf.divide(analysis_embeddings, analysis_lengths)
                    # 2)
                    # analysis_embeddings = tf.divide(analysis_embeddings, analysis_lengths)
                    # analysis_embeddings = tf.where(tf.is_nan(analysis_embeddings),
                    #                                tf.zeros_like(analysis_embeddings),
                    #                                analysis_embeddings)

        elif (self.config.analysis_embeddings == "attention_tag" or
                      self.config.analysis_embeddings == "input_attention_tag" or
                      self.config.analysis_embeddings == "input_attention_category"):
            with tf.variable_scope("attention_tag_analysis"):
                M = create_numpy_embeddings_matrix(self.config.nanalyses, self.config.dim_analysis)
                analysis_embedding_matrix = tf.get_variable(
                    name="analysis_embedding_matrix", initializer=M, dtype=tf.float32)
                self.analysis_attention_embeddings = tf.nn.embedding_lookup(analysis_embedding_matrix,
                                                                            self.analysis_ids,
                                                                            name="analysis_embeddings")
        elif self.config.analysis_embeddings == "attention_category":
            with tf.variable_scope("attention_category"):
                M = create_numpy_embeddings_matrix(self.config.nanalyses, self.config.dim_analysis)
                analysis_embedding_matrix = tf.get_variable(
                    name="analysis_embedding_matrix", initializer=M, dtype=tf.float32)
                self.analysis_attention_embeddings = tf.nn.embedding_lookup(analysis_embedding_matrix,
                                                                            self.analysis_ids,
                                                                            name="analysis_embeddings")

        if word_embeddings is not None and char_embeddings is not None:
            embeddings = tf.concat([word_embeddings, char_embeddings], axis=-1)
        elif word_embeddings is not None:
            embeddings = word_embeddings
        elif char_embeddings is not None:
            embeddings = char_embeddings

        if analysis_embeddings is not None:
            embeddings = tf.concat([embeddings, analysis_embeddings], axis=-1)

        if self.config.use_embeddings_batch_normalization is True:
            embeddings = tf.layers.batch_normalization(embeddings)

        self.word_embeddings = tf.layers.dropout(embeddings,
                                                 rate=1. - self.config.embeddings_dropout,
                                                 training=self.training_phase)

    def add_train_op(self, lr_method, lr, loss, clip=-1):
        """Defines self.train_op that performs an update on a batch

        Args:
            lr_method: (string) sgd method, for example "adam"
            lr: (tf.placeholder) tf.float32, learning rate
            loss: (tensor) tf.float32 loss to minimize
            clip: (python float) clipping of gradient. If < 0, no clipping

        """
        _lr_m = lr_method.lower()  # lower to make sure

        with tf.variable_scope("train_step"):
            if _lr_m == 'adam':  # sgd method
                optimizer = tf.train.AdamOptimizer(lr)
            elif _lr_m == 'adagrad':
                optimizer = tf.train.AdagradOptimizer(lr)
            elif _lr_m == 'sgd':
                optimizer = tf.train.GradientDescentOptimizer(lr)
            elif _lr_m == 'rmsprop':
                optimizer = tf.train.RMSPropOptimizer(self.config.lr)
            elif _lr_m == 'momentum':
                optimizer = tf.train.MomentumOptimizer(lr, self.config.momentum)
            else:
                raise NotImplementedError("Unknown method {}".format(_lr_m))

            if clip > 0:  # gradient clipping if clip is positive
                grads, vs = zip(*optimizer.compute_gradients(loss))
                grads, gnorm = tf.clip_by_global_norm(grads, clip)
                self.train_op = optimizer.apply_gradients(zip(grads, vs))
            else:
                self.train_op = optimizer.minimize(loss)

    def initialize_session(self):
        """Defines self.sess and initialize the variables"""
        self.logger.info("Initializing tf session")
        self.sess = tf.Session(config=tf.ConfigProto(**self.config.tf_session_config))
        self.sess.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()

    def restore_session(self, dir_model):
        """Reload weights into session

        Args:
            sess: tf.Session()
            dir_model: dir with weights

        """
        self.logger.info("Reloading the latest trained model...")
        self.saver.restore(self.sess, dir_model)

    def close_session(self):
        """Closes the session"""
        self.sess.close()
    
    def reset(self):
        """Closes the session and destroys the default graph."""
        self.close_session()
        tf.reset_default_graph()

    def add_summary(self):
        """Defines variables for Tensorboard

        Args:
            dir_output: (string) where the results are written

        """
        self.merged = tf.summary.merge_all()
        self.file_writer = tf.summary.FileWriter(self.config.dir_output,
                                                 self.sess.graph)
