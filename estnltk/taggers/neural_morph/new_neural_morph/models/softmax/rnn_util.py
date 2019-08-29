import tensorflow as tf
from tensorflow.python.ops import variable_scope as vs
from tensorflow.contrib.rnn import LSTMCell, LSTMStateTuple
from tensorflow.python.ops import array_ops


def _like_rnncell(cell):
    """Checks that a given object is an RNNCell by using duck typing."""
    conditions = [hasattr(cell, "output_size"), hasattr(cell, "state_size"),
                  hasattr(cell, "zero_state"), callable(cell)]
    return all(conditions)


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
