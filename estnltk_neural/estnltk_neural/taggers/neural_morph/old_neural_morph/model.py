import os
import math
from time import time
from multiprocessing import Queue, Process

import tensorflow as tf
import numpy as np

from .general_utils import Progbar
from .data_utils import iter_minibatches, pad_batch, create_numpy_embeddings_matrix


class Model(object):
    """Multiclass (softmax) model"""

    def __init__(self, config):
        """Initialises a model

        Args:
            config: (ConfigHolder) model configuration

        """
        self.config = config
        self.logger = config.logger
        self.sess = None
        self.saver = None

        self.idx_to_tag = {idx: tag for tag, idx in
                           self.config.vocab_tags.items()}

    def add_decoder_op(self):
        output_h = self.encoder_output[0]  # encoder h states
        nsteps = tf.shape(output_h)[1]

        output = tf.reshape(output_h, [-1, 2 * self.config.hidden_size_lstm])
        pred = tf.layers.dense(output, self.config.ntags)
        self.logits = tf.reshape(pred, [-1, nsteps, self.config.ntags])

    def add_pred_op(self):
        self.labels_pred = tf.cast(tf.argmax(self.logits, axis=-1), tf.int32)

    def add_loss_op(self):
        losses = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=self.logits,
                                                                labels=self.labels)
        mask = tf.sequence_mask(self.sequence_lengths)
        losses = tf.boolean_mask(losses, mask)
        self.loss = tf.reduce_mean(losses)

        tf.summary.scalar("loss", self.loss)

    def prebuild_feed_dict_batch(self, words, analyses, labels=None):
        # perform padding of the given data
        if self.config.use_char_embeddings:
            char_ids, word_ids = zip(*words)
            word_ids, sequence_lengths = pad_batch(word_ids, 0)
            char_ids, word_lengths = pad_batch(char_ids, pad_id=0, levels=2)
        else:
            word_ids, sequence_lengths = pad_batch(words, 0)

        # build feed dictionary
        feed = {'word_ids': word_ids,
                'sequence_lengths': sequence_lengths}

        if self.config.use_char_embeddings:
            feed['char_ids'] = char_ids
            feed['word_lengths'] = word_lengths

        analysis_ids, analysis_lengths = pad_batch(analyses, pad_id=0, levels=2)
        feed['analysis_ids'] = analysis_ids
        feed['analysis_lengths'] = analysis_lengths

        if labels is not None:
            labels, _ = pad_batch(labels, 0)
            feed['labels'] = labels

        return feed

    def get_final_feed_dict(self, training_phase, feed_dict, lr=None):
        fd = {self.training_phase: training_phase,
              self.word_ids: feed_dict['word_ids'],
              self.sequence_lengths: feed_dict['sequence_lengths']
              }

        if self.config.use_char_embeddings:
            fd[self.char_ids] = feed_dict['char_ids']
            fd[self.word_lengths] = feed_dict['word_lengths']

        fd[self.analysis_ids] = feed_dict['analysis_ids']
        fd[self.analysis_lengths] = feed_dict['analysis_lengths']

        if 'labels' in feed_dict:
            fd[self.labels] = feed_dict['labels']

        if lr is not None:
            fd[self.lr] = lr

        return fd, feed_dict['sequence_lengths']

    def get_feed_dict(self, training_phase, words, analyses, labels=None, lr=None):
        """Given a batch of data, initialises placeholders.

        Args:
            words: (list) list of sentences
            analyses: (list) list of morphological  analyses
            training_phase: (bool) True for training, False for inference
            labels: (list) list of label ids if training, None otherwise
            lr: (float) learning rate

        Returns:
            dict {placeholder: value}

        """
        feed = {self.training_phase: training_phase}

        # perform padding of the given data
        if self.config.use_char_embeddings:
            char_ids, word_ids = zip(*words)
            word_ids, sequence_lengths = pad_batch(word_ids, 0)
            char_ids, word_lengths = pad_batch(char_ids, pad_id=0,
                                               levels=2)
        else:
            word_ids, sequence_lengths = pad_batch(words, 0)

        # build feed dictionary
        feed[self.word_ids] = word_ids
        feed[self.sequence_lengths] = sequence_lengths

        if self.config.use_char_embeddings:
            feed[self.char_ids] = char_ids
            feed[self.word_lengths] = word_lengths

        analysis_ids, analysis_lengths = pad_batch(analyses, pad_id=0, levels=2)
        feed[self.analysis_ids] = analysis_ids
        feed[self.analysis_lengths] = analysis_lengths

        if labels is not None:
            labels, _ = pad_batch(labels, 0)
            feed[self.labels] = labels

        if lr is not None:
            feed[self.lr] = lr

        return feed, sequence_lengths

    def run_epoch(self, train, dev, train_eval, epoch):
        """Performs one complete pass over the train set and evaluate on dev

        Args:
            train: dataset that yields tuple of sentences, tags
            dev: dataset
            epoch: (int) index of the current epoch

        Returns:
            f1: (python float), score to select model on, higher is better

        """
        # progbar stuff for logging
        batch_size = self.config.batch_size
        nbatches = (len(train) + batch_size - 1) // batch_size
        prog = Progbar(target=nbatches)

        # iterate over dataset
        for i, (words, labels) in enumerate(iter_minibatches(train, batch_size)):
            fd, _ = self.get_feed_dict(True, words, labels, lr=self.config.lr)
            _, train_loss = self.sess.run([self.train_op, self.loss], feed_dict=fd)
            prog.update(i + 1, values=[("train loss", train_loss)])

        acc_train = self.evaluate(train_eval)
        acc_test = self.evaluate(dev)

        prog.update(i + 1, epoch, [("train loss", train_loss)],
                    exact=[("dev acc", acc_test), ("train acc", acc_train), ("lr", self.config.lr)])

        return acc_train, acc_test, train_loss

    def evaluate(self, test):
        """Evaluates performance on test set

        Args:
            test: dataset that yields tuple of (sentences, tags)

        Returns:
            metrics: (dict) metrics["acc"] = 98.4, ...

        """
        accs = []
        for words, labels in iter_minibatches(test, self.config.batch_size):
            labels_pred, sequence_lengths = self.predict_batch(words)
            for lbls_true, lbls_pred, length in zip(labels, labels_pred, sequence_lengths):
                # compare sentence labels
                lbls_true = lbls_true[:length]
                lbls_pred = lbls_pred[:length]
                accs += [a == b for (a, b) in zip(lbls_true, lbls_pred)]
        acc = np.mean(accs)
        return acc

    def predict_batch(self, words, analyses):
        """
        Args:
            words: list of sentences

        Returns:
            labels_pred: list of labels for each sentence
            sequence_length

        """
        fd, sequence_lengths = self.get_feed_dict(False, words, analyses)

        if self.config.use_crf:
            # get tag scores and transition params of CRF
            viterbi_sequences = []
            logits, trans_params = self.sess.run(
                [self.logits, self.trans_params], feed_dict=fd)

            # iterate over the sentences because no batching in vitervi_decode
            for logit, sequence_length in zip(logits, sequence_lengths):
                logit = logit[:sequence_length]  # keep only the valid steps
                viterbi_seq, viterbi_score = tf.contrib.crf.viterbi_decode(
                    logit, trans_params)
                viterbi_sequences += [viterbi_seq]
            return viterbi_sequences, sequence_lengths
        else:
            labels_pred = self.sess.run(self.labels_pred, feed_dict=fd)
            return labels_pred, sequence_lengths

    def predict(self, words_raw, analyses_raw):
        """Returns list of tags

        Args:
            words_raw: list of words (string), just one sentence (no batch)
            analyses_raw: list of lists of strings.

        Returns:
            preds: list of tags (string), one for each word in the sentence

        Example:

            predict(['Kõik', 'riigid'],
                    [['P pl n', 'P sg n'], ['S pl n']])
        """
        words = [self.config.processing_word_infer(w) for w in words_raw]
        analyses = [[self.config.processing_analysis(a) for a in anal]
                    for anal in analyses_raw]
        if type(words[0]) == tuple:
            words = zip(*words)
        pred_ids, _ = self.predict_batch([words], [analyses])
        preds = [self.idx_to_tag[idx] for idx in list(pred_ids[0])]
        return preds

    def evaluate(self, test):
        """Evaluates performance on test set

        Args:
            test: dataset that yields tuple of (sentences, tags)

        Returns:
            metrics: (dict) metrics["acc"] = 98.4, ...

        """
        accs = []
        for words, labels, analyses in iter_minibatches(test, self.config.eval_batch_size):
            labels_pred, sequence_lengths = self.predict_batch(words, analyses)
            for lbls_true, lbls_pred, snt_length in zip(labels, labels_pred, sequence_lengths):
                # compare sentence labels
                lbls_true = lbls_true[:snt_length]
                lbls_pred = lbls_pred[:snt_length]
                accs += [a == b for (a, b) in zip(lbls_true, lbls_pred)]
        acc = np.mean(accs)
        return acc

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

        self.labels = tf.placeholder(tf.int32, shape=[None, None], name="labels")

        # Placeholders for full-tag analyses
        # shape = (batch size, max length of sentence, max analyses per word)
        self.analysis_ids = tf.placeholder(tf.int32, shape=[None, None, None], name="analysis_ids")
        self.analysis_lengths = tf.placeholder(tf.int32, shape=[None, None], name="analysis_lengths")

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
        # Made this an inner import, because otherwise it produces ImportError 
        # due to the missing tensorflow.contrib (requires tensorflow < 2.0.0)
        from . import rnn_util
        with tf.variable_scope("bi-lstm"):
            cell_fw_list = [rnn_util.StatefulLSTMCell(self.config.hidden_size_lstm)
                            for _ in range(self.config.lstm_layers_num)]
            cell_bw_list = [rnn_util.StatefulLSTMCell(self.config.hidden_size_lstm)
                            for _ in range(self.config.lstm_layers_num)]

            if self.config.encoder_lstm_state_dropout < 1 or \
                            self.config.encoder_lstm_output_dropout < 1 or \
                            self.config.encoder_lstm_input_dropout < 1:
                state_keep_prob = 1.0 - (1.0 - self.config.encoder_lstm_state_dropout) * tf.cast(self.training_phase,
                                                                                                 tf.float32)
                input_keep_prob = 1.0 - (1.0 - self.config.encoder_lstm_input_dropout) * tf.cast(self.training_phase,
                                                                                                 tf.float32)
                output_keep_prob = 1.0 - (1.0 - self.config.encoder_lstm_output_dropout) * tf.cast(self.training_phase,
                                                                                                   tf.float32)
                cell_fw_list = [tf.contrib.rnn.DropoutWrapper(cell,
                                                              state_keep_prob=state_keep_prob,
                                                              input_keep_prob=input_keep_prob,
                                                              output_keep_prob=output_keep_prob)
                                for cell in cell_fw_list]
                cell_bw_list = [tf.contrib.rnn.DropoutWrapper(cell,
                                                              state_keep_prob=state_keep_prob,
                                                              input_keep_prob=input_keep_prob,
                                                              output_keep_prob=output_keep_prob)
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
        if self.config.analysis_embeddings == "tag":
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

        if word_embeddings is not None and char_embeddings is not None:
            embeddings = tf.concat([word_embeddings, char_embeddings], axis=-1)
        elif word_embeddings is not None:
            embeddings = word_embeddings
        elif char_embeddings is not None:
            embeddings = char_embeddings

        if analysis_embeddings is not None:
            embeddings = tf.concat([embeddings, analysis_embeddings], axis=-1)

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

    def save_session(self):
        """Saves session = weights"""
        if not os.path.exists(self.config.dir_model):
            os.makedirs(self.config.dir_model)
        self.saver.save(self.sess, self.config.dir_model)

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

    def iter_prebuilt_feed_dict_batches(self, dataset, batch_size):
        q = Queue(maxsize=self.config.batching_queque_size)
        Process(target=self.prebuild_feed_dict_batches,
                args=(q, dataset, batch_size)).start()
        while 1:
            item = q.get()
            if item == "END":
                raise StopIteration()
            feed_dict = item
            yield feed_dict

    def build(self):
        # NER specific functions
        self.add_placeholders()
        self.add_word_embeddings_op()
        self.add_encoder_op()
        self.add_decoder_op()
        self.add_pred_op()
        self.add_loss_op()

        # Generic functions that add training op and initialize session
        self.add_train_op(self.config.lr_method, self.lr, self.loss,
                          self.config.clip)
        self.initialize_session()  # now self.sess is defined and vars are init

    def prebuild_feed_dict_batches(self, queue, dataset, batch_size):
        for words, labels, analyses in iter_minibatches(dataset, batch_size):
            feed_dict = self.prebuild_feed_dict_batch(words, analyses, labels)
            queue.put(feed_dict)
        queue.put('END')

    def train(self, train, dev, train_eval):
        """Performs training with early stopping and lr decay"""
        updates, epoch, best_score, nepoch_no_imprv = 0, 0, 0, 0
        batch_size = self.config.batch_size
        max_epochs = self.config.max_epochs
        nbatches = (len(train) + batch_size - 1) // batch_size

        while epoch < max_epochs:
            # Run one epoch

            epoch_time = time()
            train_time = time()

            epoch_train_loss = 0
            iter = 0
            prog = Progbar(target=nbatches)

            for feed_dict in self.iter_prebuilt_feed_dict_batches(train, batch_size):
                fd, _ = self.get_final_feed_dict(True, feed_dict, lr=self.config.lr)
                _, train_loss = self.sess.run([self.train_op, self.loss], feed_dict=fd)
                epoch_train_loss += train_loss
                updates += 1

                if updates % self.config.lr_decay_step == 0:
                    # apply decay
                    if self.config.lr_decay_strategy == "on-no-improvement":
                        if acc_test < best_score:
                            self.config.lr *= self.config.lr_decay
                    elif self.config.lr_decay_strategy == "exponential":
                        self.config.lr *= self.config.lr_decay
                    elif self.config.lr_decay_strategy == "step":
                        self.config.lr = self.config.step_decay_init_lr * \
                                         math.pow(self.config.step_decay_drop, math.floor(
                                             (epoch) / self.config.step_decay_epochs_drop))
                    elif self.config.lr_decay_strategy is None:
                        pass
                    else:
                        raise ValueError("Invalid 'decay_strategy' setting: " + self.config.lr_decay_strategy)

                prog.update(iter + 1, values=[("train loss", train_loss)])
                iter += 1

            train_time = time() - train_time

            # evaluate epoch
            acc_train = self.evaluate(train_eval)

            eval_time = time()
            acc_test = self.evaluate(dev)
            eval_time = time() - eval_time

            epoch_time = time() - epoch_time

            # log epoch
            prog.update(iter + 1, epoch, [("train loss", train_loss)],
                        exact=[("dev acc", acc_test), ("train acc", acc_train), ("lr", self.config.lr)])
            self.write_epoch_results(epoch, acc_train, acc_test, epoch_train_loss / iter, nbatches,
                                     epoch_time=epoch_time,
                                     train_time=train_time,
                                     eval_time=eval_time)

            # early stopping and saving checkpoint
            if acc_test >= best_score:
                nepoch_no_imprv = 0
                self.save_session()
                best_score = acc_test
            else:
                nepoch_no_imprv += 1
                if nepoch_no_imprv >= self.config.nepoch_no_imprv:
                    self.logger.info("- early stopping {} epochs without improvement".format(nepoch_no_imprv))
                    break
            epoch += 1
        return best_score

    def write_epoch_results(self, epoch, acc_train, acc_test, train_loss, nbatches,
                            epoch_time, train_time, eval_time):
        with open(self.config.training_log, "a") as f:
            print(epoch, acc_train, acc_test, train_loss, nbatches, epoch_time, train_time, eval_time, sep=',', file=f,
                  flush=True)
