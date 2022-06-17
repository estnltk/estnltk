import pytest
from estnltk.collocation_net.base_collocation_net import BaseCollocationNet
from estnltk.downloader import get_resource_paths

# Try to get the resources for CollocationNet. If missing, do nothing. It's up for the user to download the missing resources
COLLOCATION_NET_PATH = get_resource_paths("collocation_net", only_latest=True, download_missing=False)

@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_unknown_word():
    cn = BaseCollocationNet()
    with pytest.raises(ValueError):
        index = cn.row_index('testsõna')


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_predict():
    cn = BaseCollocationNet()
    pred = cn.predict_column_probabilities("kohv", ["tugev", "kange"])
    assert isinstance(pred[0][0], str)
    assert isinstance(pred[0][1], float)
    assert pred[0][0] == "kange"


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_possible_collocates_output():
    cn = BaseCollocationNet()
    nouns = cn.rows_used_with("kange", 5)
    adjectives = cn.columns_used_with("kohv", 5)
    assert len(nouns) == 5
    assert len(adjectives) == 5


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_similar_nouns():
    cn = BaseCollocationNet()
    similar_nouns = cn.similar_rows("kohv", 1)
    assert similar_nouns[0] in cn.rows


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_similar_adjectives():
    cn = BaseCollocationNet()
    similar_adjectives = cn.similar_columns("kange", 1)
    assert similar_adjectives[0] in cn.columns


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_topic():
    cn = BaseCollocationNet()
    topic = cn.topic("kohv")
    assert isinstance(topic, list)
    assert "kohv" in topic


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_characterisation():
    cn = BaseCollocationNet()
    char = cn.characterisation("kohv", 3, 5)
    assert isinstance(char, list)
    assert len(char) == 3

    first_topic = char[0]
    assert isinstance(first_topic, tuple)

    assert isinstance(first_topic[0], float)
    assert isinstance(first_topic[1], list)
    assert len(first_topic[1]) == 5


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_predict_for_several():
    cn = BaseCollocationNet()
    pred = cn.predict_for_several_rows(["kohv", "tee"], 1)
    assert len(pred) == 1
    pred = pred[0]
    assert isinstance(pred[0], str)
    assert isinstance(pred[1], float)


@pytest.mark.skipif(COLLOCATION_NET_PATH is None,
                    reason="CollocationNet's resources have not been downloaded. Use estnltk.download('collocation_net') to fetch the missing resources.")
def test_predict_topic_for_several():
    cn = BaseCollocationNet()
    pred = cn.predict_topic_for_several_rows(["kohv", "tee"], 1)
    assert len(pred) == 1
    pred = pred[0]
    assert isinstance(pred[0], list)
    assert isinstance(pred[1], float)
