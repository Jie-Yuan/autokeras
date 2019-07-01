import autokeras as ak
import kerastuner
import pytest

import numpy as np
import tensorflow as tf


@pytest.fixture(scope='module')
def tmp_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('test_hyper_block')


def test_xception_block(tmp_dir):
    x_train = np.random.rand(100, 32, 32, 3)
    y_train = np.random.randint(10, size=100)
    y_train = tf.keras.utils.to_categorical(y_train)

    input_node = ak.Input()
    output_node = input_node
    output_node = ak.XceptionBlock()(output_node)
    output_node = ak.ClassificationHead()(output_node)

    input_node.shape = (32, 32, 3)
    output_node[0].shape = (10,)

    graph = ak.GraphAutoModel(input_node, output_node, directory=tmp_dir)
    model = graph.build(kerastuner.HyperParameters())
    model.fit(x_train, y_train, epochs=1, batch_size=100, verbose=False)
    result = model.predict(x_train)

    assert result.shape == (100, 10)


def test_rnn_block(tmp_dir):
    x_train = np.random.rand(100,32,32)
    y_train = np.random.rand(100)
    input_node = ak.Input()
    output_node = input_node
    output_node = ak.RNNBlock(bidirectional=True,return_sequences=False)(output_node)
    output_node = ak.RegressionHead()(output_node)

    input_node.shape = (32, 32)
    output_node[0].shape = (1,)

    auto_model = ak.GraphAutoModel(input_node, output_node,directory=tmp_dir)
    model = auto_model.build(kerastuner.HyperParameters())
    model.fit(x_train, y_train, epochs=2)
    result = model.predict(x_train)

    assert result.shape == (100, 1)


def test_seq2seq(tmp_dir):
    # Autoencoder setup
    x_train = np.random.rand(100,32,32)
    input_node = ak.Input()
    output_node = input_node
    output_node = ak.S2SBlock()(output_node)
    output_node = ak.SequenceHead()(output_node)

    input_node.shape = (32, 32)
    output_node[0].shape = (32,32)

    auto_model = ak.GraphAutoModel(input_node, output_node,directory=tmp_dir)
    model = auto_model.build(kerastuner.HyperParameters())
    model.fit(x_train, x_train, epochs=2)
    result = model.predict(x_train)

    assert result.shape == (100, 32, 32)

