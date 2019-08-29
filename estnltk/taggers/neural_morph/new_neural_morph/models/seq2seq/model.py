import numpy as np
import tensorflow as tf

from .data_utils import pad_sequences, PAD, SOS, EOS, MISSING_CATEGORY_ID
from ..base_model import BaseModel


class Model(BaseModel):
    """Specialized class of Model for NER"""

    def __init__(self, config):
        self.config = config
        self.logger = config.logger
        self.sess = None
        self.saver = None

        self.idx_to_tag = {idx: tag for tag, idx in
                           self.config.vocab_tags.items()}
        self.idx_to_word = {idx: word for word, idx in
                            self.config.vocab_words.items()}
        self.idx_to_char = {idx: c for c, idx in
                            self.config.vocab_chars.items()}

        self.sos_id = self.config.vocab_tags[SOS]
        self.eos_id = self.config.vocab_tags[EOS]
        self.pad_id = self.config.vocab_tags[PAD]
        assert self.pad_id == 0

    def add_placeholders(self):
        """Define placeholders = entries to computational graph"""

        self.training_phase = tf.placeholder(tf.bool, shape=[], name="training_phase")
        # shape = (batch size, max length of sentence in batch)
        self.word_ids = tf.placeholder(tf.int32, shape=[None, None], name="word_ids")
        self.sequence_lengths = tf.placeholder(tf.int32, shape=[None], name="sequence_lengths")
        self.word2sentence_map = tf.placeholder(tf.int32, shape=[None, None], name="word2sentence_map")

        self.tag_ids = tf.placeholder(tf.int32, shape=[None, None], name="tag_ids")
        self.tag_lengths = tf.placeholder(tf.int32, shape=[None], name="tag_lengths")

        # shape = (batch size, max length of sentence, max length of word)
        self.char_ids = tf.placeholder(tf.int32, shape=[None, None, None], name="char_ids")

        # shape = (batch_size, max_length of sentence)
        self.word_lengths = tf.placeholder(tf.int32, shape=[None, None], name="word_lengths")

        self.analysis_ids = tf.placeholder(tf.int32, shape=[None, None, None], name="analysis_ids")
        self.analysis_lengths = tf.placeholder(tf.int32, shape=[None, None], name="analysis_lengths")

        self.lr = tf.placeholder(dtype=tf.float32, shape=[], name="lr")

        # Placeholders for category-level analyses
        if self.config.analysis_embeddings == "category":
            for category in self.config.vocab_analysis:
                plh = tf.placeholder(tf.int32,
                                     shape=[None, None, None],
                                     name="category_analyses_{}".format(self.escape_category(category)))
                self.setattr("category_analyses", plh, category)

    def get_feed_dict(self, training_phase, words, analyses, labels=None, lr=None):
        """Given some data, pad it and build a feed dictionary

        Args:
            words: list of sentences. A sentence is a list of ids of a list of
                words. A word is a list of ids
            labels: list of ids
            lr: (float) learning rate

        Returns:
            dict {placeholder: value}

        """
        # build feed dictionary
        feed = {self.training_phase: training_phase}

        # perform padding of the given data
        if self.config.use_char_embeddings is True and self.config.use_word_embeddings is True:
            char_ids, word_ids = zip(*words)
            word_ids, sequence_lengths = pad_sequences(word_ids, self.pad_id)
            char_ids, word_lengths = pad_sequences(char_ids, pad_tok=self.pad_id, nlevels=2)
        elif self.config.use_word_embeddings is True:
            word_ids, sequence_lengths = pad_sequences(words, self.pad_id)
        elif self.config.use_char_embeddings is True:
            char_ids, word_lengths = pad_sequences(words, pad_tok=self.pad_id, nlevels=2)
            sequence_lengths = [len(snt) for snt in words]

        if self.config.use_word_embeddings:
            feed[self.word_ids] = word_ids

            if self.config.attention == "sentence":
                # build word -> sentence matrix
                word2sentence_map = np.full((len(word_ids), len(word_ids[0])), -1., dtype=np.int32)
                for snt_id, snt_len in enumerate(sequence_lengths):
                    word2sentence_map[snt_id, :snt_len] = snt_id
                feed[self.word2sentence_map] = word2sentence_map

        if self.config.use_char_embeddings:
            feed[self.char_ids] = char_ids
            feed[self.word_lengths] = word_lengths

        feed[self.sequence_lengths] = sequence_lengths

        if self.config.analysis_embeddings == "attention_tag" or self.config.analysis_embeddings == "tag":
            analysis_ids, analysis_lengths = pad_sequences(analyses, pad_tok=0, nlevels=2)
            feed[self.analysis_ids] = analysis_ids
            feed[self.analysis_lengths] = analysis_lengths
        elif self.config.analysis_embeddings == "attention_category":
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

        if labels is not None:
            word_tags = [word_tags + [self.eos_id, self.pad_id]
                         for sentence in labels for word_tags in sentence]
            tag_ids, tag_lengths = pad_sequences(word_tags, self.pad_id)
            feed[self.tag_ids] = tag_ids
            feed[self.tag_lengths] = tag_lengths  # Word tags include actual tags + eos-token + 1 pad-token.

        if lr is not None:
            feed[self.lr] = lr

        return feed, sequence_lengths

    def add_tag_embeddings_op(self):
        tag_embeddings = tf.get_variable(
            name="tag_embeddings",
            dtype=tf.float32,
            shape=[self.config.ntags, self.config.dim_tag])
        self.tag_embeddings = tag_embeddings

    def add_decoder_op(self):
        # reshape inputs to a list of words
        input_mask = tf.sequence_mask(self.sequence_lengths)
        encoder_output_h, encoder_output_c = self.encoder_output
        decoder_input_h = tf.boolean_mask(encoder_output_h, input_mask)
        decoder_input_c = tf.boolean_mask(encoder_output_c, input_mask)
        initial_state = tf.contrib.rnn.LSTMStateTuple(h=decoder_input_h, c=decoder_input_c)

        batch_size = tf.shape(decoder_input_h)[0]
        projection_layer = tf.layers.Dense(self.config.ntags, use_bias=True, name="decoder_proj")

        decoder_cell = tf.contrib.rnn.LSTMCell(
            num_units=2 * self.config.hidden_size_lstm)  # num_units = encoder backword and forward hidden states concatenated

        if (self.config.analysis_embeddings == "attention_tag" or
                    self.config.analysis_embeddings == "attention_category"):
            self.logger.warning("Using attention %s" % self.config.analysis_embeddings)
            # shape: [words X analysis-number X attention-embedding-size]
            analysis_attention_embeddings = tf.boolean_mask(self.analysis_attention_embeddings, input_mask)
            analysis_lengths = tf.boolean_mask(self.analysis_lengths, input_mask)
            # shape: [words]

            if self.config.attention_mechanism == 'luong':
                attention_mechanism = tf.contrib.seq2seq.LuongAttention(
                    num_units=2 * self.config.hidden_size_lstm,
                    memory=analysis_attention_embeddings,
                    memory_sequence_length=analysis_lengths,
                    scale=False)
            elif self.config.attention_mechanism == 'bahdanau':
                attention_mechanism = tf.contrib.seq2seq.BahdanauAttention(
                    num_units=2 * self.config.hidden_size_lstm,
                    memory=analysis_attention_embeddings,
                    memory_sequence_length=analysis_lengths)
            else:
                raise ValueError("Invalid attention mechanism '%s'" % self.config.attention_mechnism)

            decoder_cell = tf.contrib.seq2seq.AttentionWrapper(decoder_cell,
                                                               attention_mechanism,
                                                               attention_layer_size=2 * self.config.hidden_size_lstm)
            initial_state = decoder_cell.zero_state(dtype=tf.float32, batch_size=batch_size).clone(
                cell_state=initial_state)

        start_tokens = tf.tile([self.sos_id], [batch_size])

        # shift tags one step to the left and prepend 'sos' token.
        tag_ids_train = tf.concat([tf.expand_dims(start_tokens, 1), self.tag_ids[:, :-1]], 1)
        tags_train_embedded = tf.nn.embedding_lookup(self.tag_embeddings, tag_ids_train)
        tags_train_embedded = tf.layers.dropout(tags_train_embedded,
                                                rate=1 - self.config.tag_embeddings_dropout,
                                                training=self.training_phase)

        # Training
        if self.config.trainer == "basic":
            train_helper = tf.contrib.seq2seq.TrainingHelper(
                inputs=tags_train_embedded,
                sequence_length=self.tag_lengths,  # `tag-length` covers <sos-token, actual tags, eos-token>
            )
        elif self.config.trainer == "scheduled":
            train_helper = tf.contrib.seq2seq.ScheduledEmbeddingTrainingHelper(
                inputs=tags_train_embedded,
                sequence_length=self.tag_lengths,  # `tag-length` covers <sos-token, actual tags, eos-token>
                embedding=lambda ids: tf.nn.embedding_lookup(self.tag_embeddings, ids),
                sampling_probability=self.config.scheduled_trainer_sampling_prob)
        else:
            raise ValueError("Invalid trainer specified: '%s'" % self.config.trainer)

        train_decoder = tf.contrib.seq2seq.BasicDecoder(
            decoder_cell,
            train_helper,
            initial_state=initial_state,
            output_layer=projection_layer)

        decoder_outputs, final_state, decoder_sequence_lengths = tf.contrib.seq2seq.dynamic_decode(
            train_decoder,
            impute_finished=False)
        # logits = decoder_outputs.rnn_output
        logits = decoder_outputs[0]
        logits = tf.verify_tensor_all_finite(logits, "Logits not finite")

        # from padded training tags extracts actual-tags + eos-token:
        weights = tf.to_float(tf.not_equal(tag_ids_train, self.eos_id))
        weights = tf.to_float(tf.not_equal(weights, self.pad_id))
        loss = tf.contrib.seq2seq.sequence_loss(logits=logits,
                                                targets=self.tag_ids,
                                                weights=weights,
                                                name="sequence_loss",
                                                average_across_timesteps=False)
        self.loss = tf.reduce_sum(loss)

        # Scoring

        # 1. Score given labels
        scoring_helper = tf.contrib.seq2seq.TrainingHelper(
            inputs=tags_train_embedded,
            sequence_length=self.tag_lengths)
        scoring_decoder = tf.contrib.seq2seq.BasicDecoder(
            decoder_cell,
            scoring_helper,
            initial_state=initial_state,
            output_layer=projection_layer)
        scoring_outputs, _, scoring_sequence_lengths = tf.contrib.seq2seq.dynamic_decode(scoring_decoder)
        scoring_logits = scoring_outputs.rnn_output
        scoring_logits = tf.verify_tensor_all_finite(scoring_logits, "Scoring logits not finite")
        logits_flat = tf.reshape(scoring_logits, [-1, tf.shape(scoring_logits)[2]])
        softmax_scores_flat = tf.nn.softmax(logits_flat, dim=-1)
        tag_ids_train_flat = tf.reshape(self.tag_ids, [-1])
        indices = tf.concat([tf.expand_dims(tf.range(0, tf.shape(tag_ids_train_flat)[0]), 1),
                             tf.expand_dims(tag_ids_train_flat, 1)], axis=1)
        tag_softmax_scores_flat = tf.gather_nd(softmax_scores_flat, indices)
        tag_softmax_scores = tf.reshape(tag_softmax_scores_flat, [batch_size, -1])
        tag_mask = tf.sequence_mask(self.tag_lengths, tf.shape(tag_softmax_scores)[1])
        tag_softmax_scores = tf.multiply(tag_softmax_scores, tf.cast(tag_mask, tf.float32))
        tag_softmax_scores += tf.cast(tf.logical_not(tag_mask), tf.float32)
        scores = np.e ** -tf.div(tf.reduce_sum(tf.log(tag_softmax_scores), axis=-1),
                                 tf.cast(self.tag_lengths, tf.float32))
        self.labels_scores = scores

        # 2. Score best labels
        max_tag_softmax_scores = tf.reduce_max(tf.nn.softmax(scoring_logits, dim=-1), axis=-1)
        max_tag_mask = tf.sequence_mask(self.tag_lengths, tf.shape(max_tag_softmax_scores)[1])
        max_tag_softmax_scores = tf.multiply(max_tag_softmax_scores, tf.cast(max_tag_mask, tf.float32))
        max_tag_softmax_scores += tf.cast(tf.logical_not(max_tag_mask), tf.float32)
        max_scores = np.e ** -tf.div(tf.reduce_sum(tf.log(max_tag_softmax_scores), axis=-1),
                                     tf.cast(self.tag_lengths, tf.float32))
        self.labels_max_scores = max_scores
        self.labels_max_ids = tf.argmax(scoring_logits, axis=-1)

        # Inference
        infer_helper = tf.contrib.seq2seq.GreedyEmbeddingHelper(
            embedding=self.tag_embeddings,
            start_tokens=start_tokens,
            end_token=self.eos_id)

        infer_decoder = tf.contrib.seq2seq.BasicDecoder(
            decoder_cell,
            infer_helper,
            initial_state=initial_state,
            output_layer=projection_layer)

        final_outputs, final_state, final_sequence_lengths = tf.contrib.seq2seq.dynamic_decode(
            infer_decoder,
            maximum_iterations=self.config.decoder_maximum_iterations,
            impute_finished=True)

        decoder_logits = final_outputs.rnn_output
        decoder_logits = tf.verify_tensor_all_finite(decoder_logits, "Decoder Logits not finite")
        with tf.control_dependencies([tf.assert_rank(decoder_logits, 3),
                                      tf.assert_none_equal(tf.reduce_sum(decoder_logits), 0.),
                                      tf.assert_equal(tf.cast(tf.argmax(decoder_logits, axis=-1), tf.int32),
                                                      final_outputs.sample_id)]):
            decoder_logits = tf.identity(decoder_logits)

        self.decoder_logits = decoder_logits
        self.labels_pred = final_outputs.sample_id
        self.labels_pred_lengths = final_sequence_lengths

    def build(self):
        # NER specific functions
        self.add_placeholders()
        self.add_word_embeddings_op()
        self.add_tag_embeddings_op()
        self.add_encoder_op()
        self.add_decoder_op()
        self.add_train_op(self.config.lr_method, self.lr, self.loss, self.config.clip)

        self.initialize_session()

    def predict_batch(self, words, analyses):
        """
        Args:
            words: list of sentences

        Returns:
            labels_pred: list of labels for each sentence
            sequence_length

        """
        fd, sequence_lengths = self.get_feed_dict(False, words, analyses)
        # assert min(w for snt, snt_len in zip(fd[self.word_lengths], sequence_lengths) for w in snt[:snt_len]) > 0
        labels_pred, labels_pred_lengths = self.sess.run([self.labels_pred, self.labels_pred_lengths], feed_dict=fd)
        return labels_pred, labels_pred_lengths

    def predict(self, words_raw, analyses_raw):
        """Returns list of tags

        Args:
            words_raw: list of words (string), just one sentence (no batch)

        Returns:
            preds: list of tags (string), one for each word in the sentence

        """
        words = [self.config.processing_word_infer(w) for w in words_raw]
        if type(words[0]) == tuple:
            words = list(zip(*words))
        analyses = [[self.config.processing_analysis(a) for a in anal]
                    for anal in analyses_raw]
        labels_pred, labels_pred_lengths = self.predict_batch([words], [analyses])
        preds = [[self.idx_to_tag[tag_id] for tag_id in pred[:length][:-1]]
                 for pred, length in zip(labels_pred, labels_pred_lengths)]
        return ['|'.join(pred) for pred in preds]
