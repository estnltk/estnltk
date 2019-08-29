import tensorflow as tf

from .data_utils import pad_sequences, MISSING_CATEGORY_ID
from ..base_model import BaseModel


class Model(BaseModel):
    """Specialized class of Model for NER"""

    def __init__(self, config):
        super(Model, self).__init__(config)
        self.idx_to_tag = {idx: tag for tag, idx in
                           self.config.vocab_tags.items()}

    def add_placeholders(self):
        super().add_placeholders()
        # shape = (batch size, max length of sentence in batch)
        self.labels = tf.placeholder(tf.int32, shape=[None, None], name="labels")

    def get_feed_dict(self, training_phase, words, analyses, labels=None, lr=None):
        """Given some data, pad it and build a feed dictionary

        Args:
            words: list of sentences. A sentence is a list of ids of a list of
                words. A word is a list of ids
            labels: list of ids
            lr: (float) learning rate
            dropout: (float) keep prob

        Returns:
            dict {placeholder: value}

        """
        feed = {self.training_phase: training_phase}

        # perform padding of the given data
        if self.config.use_char_embeddings:
            char_ids, word_ids = zip(*words)
            word_ids, sequence_lengths = pad_sequences(word_ids, 0)
            char_ids, word_lengths = pad_sequences(char_ids, pad_tok=0,
                                                   nlevels=2)
        else:
            word_ids, sequence_lengths = pad_sequences(words, 0)

        # build feed dictionary
        feed[self.word_ids] = word_ids
        feed[self.sequence_lengths] = sequence_lengths

        if self.config.use_char_embeddings:
            feed[self.char_ids] = char_ids
            feed[self.word_lengths] = word_lengths

        if (self.config.analysis_embeddings == "tag" or
                    self.config.analysis_embeddings == "input_attention_tag"):
            analysis_ids, analysis_lengths = pad_sequences(analyses, pad_tok=0, nlevels=2)
            feed[self.analysis_ids] = analysis_ids
            feed[self.analysis_lengths] = analysis_lengths
        elif self.config.analysis_embeddings == "input_attention_category":
            for i in range(len(analyses)):
                for j in range(len(analyses[i])):
                    analyses[i][j] = list(set([c for cat_list in analyses[i][j] for c in cat_list]))
            analysis_ids, analysis_lengths = pad_sequences(analyses, pad_tok=0, nlevels=2)
            feed[self.analysis_ids] = analysis_ids
            feed[self.analysis_lengths] = analysis_lengths
        elif self.config.analysis_embeddings == "category":
            for cat_idx, cat in enumerate(self.config.vocab_analysis):
                matrix = []
                for snt in analyses:
                    cat_snt = []
                    for word in snt:
                        word_analyses = set([analysis[cat_idx] for analysis in word])
                        word_analyses = [a for a in word_analyses if a != MISSING_CATEGORY_ID]
                        cat_snt.append(word_analyses)
                    matrix.append(cat_snt)
                analysis_ids, analysis_lengths = pad_sequences(matrix, pad_tok=0, nlevels=2)
                feed[self.getattr("category_analyses", cat)] = analysis_ids
                feed[self.getattr("category_analysis_lengths", cat)] = analysis_lengths

        if labels is not None:
            labels, _ = pad_sequences(labels, 0)
            feed[self.labels] = labels

        if lr is not None:
            feed[self.lr] = lr

        return feed, sequence_lengths

    def add_decoder_op(self):
        output_h = self.encoder_output[0]  # encoder h states
        nsteps = tf.shape(output_h)[1]
        if (self.config.analysis_embeddings == "input_attention_tag" or
                    self.config.analysis_embeddings == "input_attention_category"):
            snt_num, snt_len, anal_num, anal_len = tf.unstack(tf.shape(self.analysis_attention_embeddings))
            memory = tf.reshape(self.analysis_attention_embeddings,
                                [-1, anal_num, self.config.dim_analysis])
            memory_length = tf.reshape(self.analysis_lengths, [-1])
            memory_length = tf.where(tf.equal(memory_length, 0),
                                     tf.ones_like(memory_length),
                                     memory_length)
            #attention_mechanism = tf.contrib.seq2seq.BahdanauAttention(
            #    num_units=self.config.dim_analysis,
            #    memory=memory,
            #    memory_sequence_length=memory_length)
            attention_mechanism = tf.contrib.seq2seq.LuongAttention(
                num_units=self.config.dim_analysis,
                memory=memory,
                memory_sequence_length=memory_length,
                scale=False)


            # query shape: [words, 2 * self.config.hidden_size_lstm]
            query = tf.reshape(output_h, [-1, 2 * self.config.hidden_size_lstm])
            alignments = attention_mechanism.__call__(query, None)
            alignments = tf.expand_dims(alignments, dim=2)
            # c shape: [words, analysis-dim]
            c = tf.reduce_sum(tf.multiply(memory, alignments), axis=1)
            if self.config.analysis_attention_project is True:
                h = tf.concat([query, c], axis=-1)
                output = tf.layers.dense(h,
                                         units=2 * self.config.hidden_size_lstm,
                                         use_bias=False,
                                         activation=tf.tanh)
            else:
                output = tf.concat([query, c], axis=-1)
        else:
            output = tf.reshape(output_h, [-1, 2 * self.config.hidden_size_lstm])
        pred = tf.layers.dense(output, self.config.ntags)
        self.logits = tf.reshape(pred, [-1, nsteps, self.config.ntags])

    def add_pred_op(self):
        """Defines self.labels_pred

        This op is defined only in the case where we don't use a CRF since in
        that case we can make the prediction "in the graph" (thanks to tf
        functions in other words). With theCRF, as the inference is coded
        in python and not in pure tensroflow, we have to make the prediciton
        outside the graph.
        """
        if not self.config.use_crf:
            self.labels_pred = tf.cast(tf.argmax(self.logits, axis=-1),
                                       tf.int32)

    def add_loss_op(self):
        """Defines the loss"""
        if self.config.use_crf:
            log_likelihood, trans_params = tf.contrib.crf.crf_log_likelihood(
                self.logits, self.labels, self.sequence_lengths)
            self.trans_params = trans_params  # need to evaluate it for decoding
            self.loss = tf.reduce_mean(-log_likelihood)
        else:
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(
                logits=self.logits, labels=self.labels)
            mask = tf.sequence_mask(self.sequence_lengths)
            losses = tf.boolean_mask(losses, mask)
            self.loss = tf.reduce_mean(losses)

        # for tensorboard
        tf.summary.scalar("loss", self.loss)

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

        Returns:
            preds: list of tags (string), one for each word in the sentence

        """
        words = [self.config.processing_word_infer(w) for w in words_raw]
        analyses = [[self.config.processing_analysis(a) for a in anal]
                    for anal in analyses_raw]
        if type(words[0]) == tuple:
            words = zip(*words)
        pred_ids, _ = self.predict_batch([words], [analyses])
        preds = [self.idx_to_tag[idx] for idx in list(pred_ids[0])]
        return preds
