# SyntaxGraphIndex class testing
import pytest
from types import SimpleNamespace
from typing import Any, cast

import estnltk.taggers.system.rule_taggers.deprel_components.graph as graph_module
from estnltk.taggers.system.rule_taggers.deprel_components.graph import SyntaxGraphIndex
from estnltk.taggers.system.rule_taggers.deprel_components.types import DirectionMode


def make_ann(
    token_id: int,
    head: int,
    text: str,
    upostag: str = "NOUN",
    xpostag: str = "S",
    deprel: str = "nmod",
    lemma: str = "_",
    feats: dict | None = None,
) -> SimpleNamespace:
    """Create a lightweight stanza-like annotation object for unit tests."""
    return SimpleNamespace(
        id=token_id,
        head=head,
        text=text,
        upostag=upostag,
        xpostag=xpostag,
        deprel=deprel,
        lemma=lemma,
        feats={} if feats is None else feats,
    )


class FakeLayer(list):
    """Mock estnltk Layer that holds annotations and lists its attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes = [
            "id",
            "head",
            "text",
            "upostag",
            "xpostag",
            "deprel",
            "lemma",
            "feats",
        ]


def make_layer(annotations):
    return FakeLayer(annotations)


def test_syntaxgraphindex_basics() -> None:
    """Basic behaviour: construction, node accessors and token order."""
    layer_ok = make_layer(
        [
            make_ann(1, 0, "root", deprel="root"),
            make_ann(2, 1, "left_child", deprel="nmod"),
            make_ann(3, 1, "right_child", deprel="obl"),
        ]
    )
    graph = SyntaxGraphIndex(cast(Any, layer_ok), sentence_id=0, sentence_span=(0, 15))

    # Check: basic accessors and tree validation
    assert graph.sent_id == 0
    assert graph.sentence_span == (0, 15)
    assert graph.token_order == [1, 2, 3]
    assert graph.has_node(2)
    # Check: non-existent node lookup
    assert not graph.has_node(99)
    root_node = graph.get_node(1)
    assert root_node is not None
    assert root_node.text == "root"
    assert graph.get_parent(1) is None
    parent_node = graph.get_parent(2)
    assert parent_node is not None
    assert parent_node.id == 1

    # Check: children, root nodes and tree validation
    assert [node.id for node in graph.get_children(1)] == [2, 3]
    assert [node.id for node in graph.get_root_nodes()] == [1]
    assert graph._validate_tree()


def test_syntaxgraphindex_iter_edges_and_nodes() -> None:
    """Iteration helpers: iter_nodes and iter_edges return expected sequences."""
    layer_ok = make_layer(
        [
            make_ann(1, 0, "root", deprel="root"),
            make_ann(2, 1, "left_child", deprel="nmod"),
            make_ann(3, 1, "right_child", deprel="obl"),
        ]
    )
    graph = SyntaxGraphIndex(cast(Any, layer_ok))

    # Check: iter_nodes yields nodes in token order
    assert [node.id for node in graph.iter_nodes()] == [1, 2, 3]

    edges_up = [
        (cast(Any, node).id, cast(Any, parent).id, direction)
        for node, parent, direction in graph.iter_edges(DirectionMode.UP)
    ]
    # Check: iter_edges with UP returns tuples (node, parent, UP)
    assert edges_up == [(2, 1, DirectionMode.UP), (3, 1, DirectionMode.UP)]

    edges_down = [
        (cast(Any, node).id, cast(Any, child).id, direction)
        for node, child, direction in graph.iter_edges(DirectionMode.DOWN)
    ]
    # Check: iter_edges with DOWN returns tuples (node, child, DOWN)
    assert edges_down == [(1, 2, DirectionMode.DOWN), (1, 3, DirectionMode.DOWN)]


def test_syntaxgraphindex_duplicate_ids_raises() -> None:
    layer_duplicate_ids = make_layer(
        [
            make_ann(1, 0, "root"),
            make_ann(1, 1, "duplicate"),
        ]
    )
    with pytest.raises(ValueError):
        SyntaxGraphIndex(cast(Any, layer_duplicate_ids))


def test_syntaxgraphindex_missing_head_raises() -> None:
    layer_missing_head = make_layer(
        [
            make_ann(1, 0, "root"),
            make_ann(2, 99, "orphan"),
        ]
    )
    with pytest.raises(ValueError):
        # Check: missing head references raise an error
        SyntaxGraphIndex(cast(Any, layer_missing_head))


def test_syntaxgraphindex_cycle_raises() -> None:
    layer_cycle = make_layer(
        [
            make_ann(1, 2, "a"),
            make_ann(2, 1, "b"),
        ]
    )
    with pytest.raises(ValueError):
        # Check: cyclical parent-child links raise an error
        SyntaxGraphIndex(cast(Any, layer_cycle))


def test_syntaxgraphindex_visualize_builds_ete3_tree(monkeypatch) -> None:
    """Visualisation should build a readable ete3 tree with labels and title."""
    # Skip test if ete3 is not installed
    pytest.importorskip("ete3")

    layer_ok = make_layer(
        [
            make_ann(1, 0, "root", deprel="root"),
            make_ann(2, 1, "child", deprel="nmod"),
        ]
    )
    graph = SyntaxGraphIndex(cast(Any, layer_ok))

    class FakeFace:
        def __init__(self, text, **kwargs):
            self.text = text
            self.kwargs = kwargs

    class FakeNodeStyle(dict):
        pass

    class FakeTitle:
        def __init__(self):
            self.faces = []

        def add_face(self, face, column=0):
            self.faces.append((face, column))

    class FakeTreeStyle:
        def __init__(self):
            self.show_leaf_name = None
            self.show_scale = None
            self.mode = None
            self.branch_vertical_margin = None
            self.title = FakeTitle()

    class FakeTreeNode:
        def __init__(self, name=""):
            self.name = name
            self.children = []
            self.faces = []
            self.style = None
            self.shown_with = None

        def set_style(self, style):
            self.style = style

        def add_face(self, face, column=0, position=None):
            self.faces.append((face, column, position))

        def add_child(self, child):
            self.children.append(child)
            return child

        def add_feature(self, attr, value):
            setattr(self, attr, value)

        def show(self, tree_style=None):
            self.shown_with = tree_style

    monkeypatch.setattr(graph_module, "Tree", FakeTreeNode)
    monkeypatch.setattr(graph_module, "NodeStyle", FakeNodeStyle)
    monkeypatch.setattr(graph_module, "TextFace", FakeFace)
    monkeypatch.setattr(graph_module, "TreeStyle", FakeTreeStyle)

    ete_root = graph.visualize(
        title="Demo tree",
        show=True,
    )

    ete_root = cast(Any, ete_root)

    assert ete_root.name == "1"
    assert len(ete_root.children) == 1
    assert ete_root.children[0].name == "2"

    # The default node label should now just be the token text
    root_label = ete_root.faces[0][0]
    assert root_label.text == "root"

    child_label = ete_root.children[0].faces[0][0]
    assert child_label.text == "child"

    # The default edge label should now just be the dependency relation
    child_edge_label = ete_root.children[0].faces[1][0]
    assert child_edge_label.text == "nmod"

    # Verify that other attributes are attached as features for the inspector
    assert hasattr(ete_root, "upostag")
    assert ete_root.upostag == "NOUN"
    assert hasattr(ete_root.children[0], "deprel")
    assert ete_root.children[0].deprel == "nmod"

    assert ete_root.shown_with is not None
    title_face = ete_root.shown_with.title.faces[0][0]
    assert title_face.text == "Demo tree"
