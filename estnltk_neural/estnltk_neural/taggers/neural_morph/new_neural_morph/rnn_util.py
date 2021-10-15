import tensorflow as tf
from tensorflow.python.ops import variable_scope as vs
from tensorflow.contrib.rnn import LSTMCell, LSTMStateTuple, LayerNormBasicLSTMCell
from tensorflow.python.ops import array_ops


def _like_rnncell(cell):
    """Checks that a given object is an RNNCell by using duck typing."""
    conditions = [hasattr(cell, "output_size"), hasattr(cell, "state_size"),
                  hasattr(cell, "zero_state"), callable(cell)]
    return all(conditions)


class StatefulLayerNormBasicLSTMCell(LayerNormBasicLSTMCell):
    def __init__(self, *args, **kwargs):
        super(StatefulLayerNormBasicLSTMCell, self).__init__(*args, **kwargs)

    @property
    def output_size(self):
        return (self.state_size, super(StatefulLayerNormBasicLSTMCell, self).output_size)

    def call(self, input, state):
        output, next_state = super(StatefulLayerNormBasicLSTMCell, self).call(input, state)
        emit_output = (next_state, output)
        return emit_output, next_state


class StatefulLSTMCell(LSTMCell):
    def __init__(self, *args, **kwargs):
        super(StatefulLSTMCell, self).__init__(*args, **kwargs)

    @property
    def output_size(self):
        return (self.state_size, super(StatefulLSTMCell, self).output_size)

    def call(self, input, state):
        output, next_state = super(StatefulLSTMCell, self).call(input, state)
        emit_output = (next_state, output)
        return emit_output, next_state


def bidirectional_dynamic_rnn(cell_fw, cell_bw, inputs, sequence_length=None,
                              initial_state_fw=None, initial_state_bw=None,
                              dtype=None, parallel_iterations=None,
                              swap_memory=False, time_major=False, scope=None):
    if not _like_rnncell(cell_fw):
        raise TypeError("cell_fw must be an instance of RNNCell")
    if not _like_rnncell(cell_bw):
        raise TypeError("cell_bw must be an instance of RNNCell")

    with vs.variable_scope(scope or "bidirectional_rnn"):
        # Forward direction
        with vs.variable_scope("fw") as fw_scope:
            output_fw, output_state_fw = tf.nn.dynamic_rnn(
                cell=cell_fw, inputs=inputs, sequence_length=sequence_length,
                initial_state=initial_state_fw, dtype=dtype,
                parallel_iterations=parallel_iterations, swap_memory=swap_memory,
                time_major=time_major, scope=fw_scope)

        # Backward direction
        if not time_major:
            time_dim = 1
            batch_dim = 0
        else:
            time_dim = 0
            batch_dim = 1

        def _reverse(input_, seq_lengths, seq_dim, batch_dim):
            if seq_lengths is not None:
                return array_ops.reverse_sequence(
                    input=input_, seq_lengths=seq_lengths,
                    seq_dim=seq_dim, batch_dim=batch_dim)
            else:
                return array_ops.reverse(input_, axis=[seq_dim])

        with vs.variable_scope("bw") as bw_scope:
            inputs_reverse = _reverse(
                inputs, seq_lengths=sequence_length,
                seq_dim=time_dim, batch_dim=batch_dim)
            tmp, output_state_bw = tf.nn.dynamic_rnn(
                cell=cell_bw, inputs=inputs_reverse, sequence_length=sequence_length,
                initial_state=initial_state_bw, dtype=dtype,
                parallel_iterations=parallel_iterations, swap_memory=swap_memory,
                time_major=time_major, scope=bw_scope)

    # reverse backword results
    output_bw_states_rev, output_bw_output_rev = tmp
    output_bw_output = _reverse(
        output_bw_output_rev, seq_lengths=sequence_length,
        seq_dim=time_dim, batch_dim=batch_dim)
    output_bw_states_c = _reverse(
        output_bw_states_rev.c, seq_lengths=sequence_length,
        seq_dim=time_dim, batch_dim=batch_dim)
    output_bw_states = LSTMStateTuple(h=output_bw_output,
                                      c=output_bw_states_c)
    output_bw = (output_bw_states, output_bw_output)

    # merge outputs
    outputs = (output_fw, output_bw)
    output_states = (output_state_fw, output_state_bw)

    return (outputs, output_states)


def stack_bidirectional_dynamic_rnn(cells_fw,
                                    cells_bw,
                                    inputs,
                                    initial_states_fw=None,
                                    initial_states_bw=None,
                                    dtype=None,
                                    sequence_length=None,
                                    parallel_iterations=None,
                                    time_major=False,
                                    scope=None):
    if not cells_fw:
        raise ValueError("Must specify at least one fw cell for BidirectionalRNN.")
    if not cells_bw:
        raise ValueError("Must specify at least one bw cell for BidirectionalRNN.")
    if not isinstance(cells_fw, list):
        raise ValueError("cells_fw must be a list of RNNCells (one per layer).")
    if not isinstance(cells_bw, list):
        raise ValueError("cells_bw must be a list of RNNCells (one per layer).")
    if len(cells_fw) != len(cells_bw):
        raise ValueError("Forward and Backward cells must have the same depth.")
    if (initial_states_fw is not None and
            (not isinstance(initial_states_fw, list) or
                     len(initial_states_fw) != len(cells_fw))):
        raise ValueError(
            "initial_states_fw must be a list of state tensors (one per layer).")
    if (initial_states_bw is not None and
            (not isinstance(initial_states_bw, list) or
                     len(initial_states_bw) != len(cells_bw))):
        raise ValueError(
            "initial_states_bw must be a list of state tensors (one per layer).")

    prev_layer_h = inputs
    prev_layer_c = inputs

    with vs.variable_scope(scope or "stack_bidirectional_rnn"):
        for i, (cell_fw, cell_bw) in enumerate(zip(cells_fw, cells_bw)):
            initial_state_fw = None
            initial_state_bw = None
            if initial_states_fw:
                initial_state_fw = initial_states_fw[i]
            if initial_states_bw:
                initial_state_bw = initial_states_bw[i]

            with vs.variable_scope("cell_%d" % i):
                outputs, (state_fw, state_bw) = bidirectional_dynamic_rnn(
                    cell_fw,
                    cell_bw,
                    prev_layer_h,
                    initial_state_fw=initial_state_fw,
                    initial_state_bw=initial_state_bw,
                    sequence_length=sequence_length,
                    parallel_iterations=parallel_iterations,
                    dtype=dtype,
                    time_major=time_major)
                # Concat the outputs to create the new input.
                (output_fw_states, _), (output_bw_states, _) = outputs
                prev_layer_h = array_ops.concat([output_fw_states.h, output_bw_states.h], 2)
                prev_layer_c = array_ops.concat([output_fw_states.c, output_bw_states.c], 2)

    return prev_layer_h, prev_layer_c
