from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Iterable,
    Self,
    Any,
)
from estnltk import Span, Layer
from estnltk.taggers.system.rule_taggers.deprel_components.types import DirectionMode

# Optional dependencies: initialized to None so they don't break import
# They are loaded dynamically inside the methods that require them
Tree = None
NodeStyle = None
TextFace = None
TreeStyle = None


class SyntaxGraphIndex:
    """
    A class to represent the dependency syntax graph of a sentence, indexed by token IDs.

    The graph is built from an estnltk Layer containing the sentence annotations, and provides methods to access nodes, parents, children, and edges in the dependency graph.

    ## Attributes:
    - **sentences_layer** (`Layer`): The layer containing the stanza syntax annotations for the sentence from which the graph index is built.
    - **nodes_by_id** (`Dict[int, Span]`): A mapping from token IDs to their corresponding estnltk Span annotations.
    - **parent_by_id** (`Dict[int, Optional[int]]`): A mapping from token IDs to their parent token IDs in the dependency graph.
    - **children_by_id** (`Dict[int, List[int]]`): A mapping from token IDs to a list of their child token IDs in the dependency graph.
    - **token_order** (`List[int]`): A list of token IDs in the order they appear in the sentence.
    - **sent_id** (`Optional[int]`): The ID of the sentence being indexed.
    - **sentence_span** (`Optional[Tuple[int, int]]`): The character span of the sentence in the original text.

    ## Methods:
    - :func:`~SyntaxGraphIndex.__init__`: Initializes the graph index from the given sentences layer.
    - :func:`~SyntaxGraphIndex.build_from_layer`: Builds the graph index from the provided sentences layer.
    - :func:`~SyntaxGraphIndex.get_node`: Retrieves the estnltk Span annotation for a given token ID.
    - :func:`~SyntaxGraphIndex.get_parent`: Retrieves the parent node of a given token ID in the dependency graph.
    - :func:`~SyntaxGraphIndex.get_children`: Retrieves the child nodes of a given token ID in the dependency graph.
    - :func:`~SyntaxGraphIndex.iter_nodes`: Iterates over all nodes in the graph in the order they appear in the sentence.
    - :func:`~SyntaxGraphIndex.iter_edges`: Iterates over all edges in the graph, optionally filtering by direction (up, down, or both).
    - :func:`~SyntaxGraphIndex.get_root_nodes`: Retrieves the root nodes of the dependency graph (nodes with no parent).
    - :func:`~SyntaxGraphIndex.has_node`: Checks if a given token ID exists in the graph.
    """

    stanza_syntax: Layer
    nodes_by_id: Dict[int, Span]
    parent_by_id: Dict[int, Optional[int]]
    children_by_id: Dict[int, List[int]]
    token_order: List[int]
    sent_id: Optional[int]
    sentence_span: Optional[Tuple[int, int]]
    lookup_cache: Dict[Tuple, Any]

    def __init__(
        self: Self,
        stanza_syntax_layer: Layer,
        sentence_id: Optional[int] = None,
        sentence_span: Optional[Tuple[int, int]] = None,
    ) -> None:
        """
        Initializes the SyntaxGraphIndex from the given sentences layer.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being initialized.
            stanza_syntax_layer (Layer): The layer containing the stanza syntax annotations for the sentence from which to build the graph index.
            sentence_id (Optional[int], optional): The ID of the sentence being indexed. Defaults to None.
            sentence_span (Optional[Tuple[int, int]], optional): The character span of the sentence in the original text. Defaults to None.
        """

        # Initialize the graph index from the given sentences layer
        self.stanza_syntax: Layer = stanza_syntax_layer
        self.nodes_by_id: Dict[int, Span] = {}
        self.parent_by_id: Dict[int, Optional[int]] = {}
        self.children_by_id: Dict[int, List[int]] = {}
        self.token_order: List[int] = []
        self.sent_id: Optional[int] = sentence_id
        self.sentence_span: Optional[Tuple[int, int]] = sentence_span
        self.lookup_cache = {}

        # Build the graph index from the sentences layer
        self.build_from_layer(self.stanza_syntax)

        # Validate the graph structure (optional, can be commented out if not needed)
        if not self._validate_tree():
            raise ValueError(
                "The provided stanza syntax layer does not form a valid tree structure."
            )

    def build_from_layer(self: Self, stanza_syntax: Layer) -> None:
        """
        Builds the graph index from the provided syntax layer.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being built.
            stanza_syntax (Layer): The layer containing the stanza syntax annotations for the sentence from which to build the graph index.
        """
        # Build the graph index from the provided sentences layer
        for ann in stanza_syntax:
            if ann.id in self.nodes_by_id:
                raise ValueError(f"Duplicate token id encountered: {ann.id}")
            self.nodes_by_id[ann.id] = ann
            self.parent_by_id[ann.id] = ann.head
            self.children_by_id[ann.id] = []
            self.token_order.append(ann.id)

        # Populate the children_by_id mapping based on the parent_by_id mapping
        for ann in stanza_syntax:
            if ann.head == 0:
                continue
            if ann.head not in self.children_by_id:
                raise ValueError(
                    f"Invalid head reference: token {ann.id} points to missing head {ann.head}."
                )
            self.children_by_id[ann.head].append(ann.id)

    def get_node(self: Self, token_id: int) -> Optional[Span]:
        """
        Gets the estnltk Span annotation for a given token ID.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being queried.
            token_id (int): The ID of the token for which to retrieve the annotation.

        Returns:
            Optional[Span]: The estnltk Span annotation corresponding to the given token ID, or None if the token ID does not exist in the graph index.
        """
        return self.nodes_by_id.get(token_id)

    def get_parent(self: Self, token_id: int) -> Optional[Span]:
        """
        Gets the parent node of a given token ID in the dependency graph.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being queried.
            token_id (int): The ID of the token for which to retrieve the parent node.

        Returns:
            Optional[Span]: The estnltk Span annotation corresponding to the parent node of the given token ID in the dependency graph, or None if the token ID does not exist in the graph index or if it is a root node (with no parent).
        """
        parent_id = self.parent_by_id.get(token_id)
        if parent_id is not None:
            return self.nodes_by_id.get(parent_id)
        return None

    def get_children(self: Self, token_id: int) -> List[Span]:
        """
        Gets the child nodes of a given token ID in the dependency graph.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being queried.
            token_id (int): The ID of the token for which to retrieve the child nodes.

        Returns:
            List[Span]: A list of estnltk Span annotations corresponding to the child nodes of the given token ID in the dependency graph. If the token ID does not exist in the graph index or has no children, an empty list is returned.
        """
        child_ids = self.children_by_id.get(token_id, [])
        return [self.nodes_by_id[child_id] for child_id in child_ids]

    def iter_nodes(self: Self) -> Iterable[Span]:
        """
        Iterates over all nodes in the graph in the order they appear in the sentence.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being iterated over.

        Returns:
            Iterable[Span]: An iterator that yields estnltk Span annotations for each node in the graph, in the order they appear in the sentence.

        Yields:
            Span: The estnltk Span annotation for each node in the graph, yielded in the order they appear in the sentence.
        """
        for token_id in self.token_order:
            yield self.nodes_by_id[token_id]

    def iter_edges(
        self: Self, direction: DirectionMode = DirectionMode.BOTH
    ) -> Iterable[Tuple[Optional[Span], Optional[Span], DirectionMode]]:
        """
        Iterates over all edges in the graph, optionally filtering by direction (up, down, or both).

        Args:
            self (Self): The instance of the SyntaxGraphIndex being iterated over.
            direction (DirectionMode, optional): The direction of edges to iterate over. Can be DirectionMode.UP for parent-child edges, DirectionMode.DOWN for child-parent edges, or DirectionMode.BOTH for all edges. Defaults to DirectionMode.BOTH.

        Returns:
            Iterable[Tuple[Optional[Span], Optional[Span], str]]: _description_

        Yields:
            Iterator[Iterable[Tuple[Optional[Span], Optional[Span], str]]]: _description_
        """
        for token_id in self.token_order:
            node = self.nodes_by_id[token_id]
            parent_id = self.parent_by_id.get(token_id)
            if parent_id is not None and parent_id != 0:
                parent_node = self.nodes_by_id.get(parent_id)
                if direction in [DirectionMode.BOTH, DirectionMode.UP]:
                    # Move from id to head (up the tree)
                    yield (node, parent_node, DirectionMode.UP)
                if direction in [DirectionMode.BOTH, DirectionMode.DOWN]:
                    # Move from head to id (down the tree)
                    if parent_id != 0:
                        # Skip the root node which has no parent (head = 0)
                        yield (parent_node, node, DirectionMode.DOWN)

    def get_root_nodes(self: Self) -> List[Span]:
        """
        Gets the root nodes of the dependency graph (nodes with no parent).

        Args:
            self (Self): The instance of the SyntaxGraphIndex being queried.

        Returns:
            List[Span]: A list of estnltk Span annotations corresponding to the root nodes of the dependency graph (nodes with no parent). If there are no root nodes, an empty list is returned.
        """
        root_nodes = []
        for token_id in self.token_order:
            if self.parent_by_id.get(token_id) == 0:  # Root nodes have head = 0
                root_nodes.append(self.nodes_by_id[token_id])
        return root_nodes

    def has_node(self: Self, token_id: int) -> bool:
        """
        Checks if a given token ID exists in the graph.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being queried.
            token_id (int): The ID of the token to check for existence in the graph.

        Returns:
            bool: True if the given token ID exists in the graph index, False otherwise.
        """
        return token_id in self.nodes_by_id

    def _get_all_span_attributes(
        self: Self,
        span: Span,
        attributes_to_show_in_inspector: Optional[List[str]] = None,
        ignore_attributes: List[str] = ["children", "parent_span"],
    ) -> Dict[str, Any]:
        """
        Extracts all available attributes from an estnltk Span to be used as features
        for graph nodes/edges.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being queried.
            span (Span): The estnltk Span annotation from which to extract attributes.
            attributes_to_show_in_inspector (Optional[List[str]], optional): Attributes to display in the node inspector.
            ignore_attributes (List[str], optional): Attributes to ignore when extracting features for graph nodes/edges. Defaults to ["children", "parent_span"].

        Returns:
            Dict[str, Any]: A dictionary containing all available attributes of the span, including basic properties (text, id, start, end) and standard layer attributes (lemma, upostag, xpostag, feats, etc.). Attributes with None values are excluded from the dictionary.
        """
        attrs = {}

        # Include attributes to show in the inspector
        if attributes_to_show_in_inspector is not None:
            for attr in attributes_to_show_in_inspector:
                val = getattr(span, attr, None)
                if val is not None:
                    attrs[attr] = val
            return attrs

        # Include standard layer attributes (lemma, upostag, xpostag, feats, etc.)
        for attr in self.stanza_syntax.attributes:
            if attr in ignore_attributes:
                continue
            val = getattr(span, attr, None)
            if val is not None:
                attrs[attr] = val
        return attrs

    def _format_node_label(
        self: Self, token_id: int, with_node_labels: List[str]
    ) -> str:
        """
        Build a human-readable node label for graph visualisation.

        By default, the label includes only the token text, keeping the
        visualisation clean. Other attributes can be included via
        `with_node_labels`, but are best viewed in the node inspector.
        """
        node = self.nodes_by_id[token_id]
        label_parts = []
        for attr in with_node_labels:
            value = getattr(node, attr, None)
            if value is not None:
                label_parts.append(str(value))
        return "\n".join(label_parts)

    def _format_edge_label(
        self: Self, child_id: int, with_edge_labels: List[str]
    ) -> str:
        """
        Build the dependency-label text for an edge.

        By default, the label includes only the dependency relation.
        Other attributes can be included via `with_edge_labels`, but are
        best viewed in the edge/node inspector.
        """
        child_node = self.nodes_by_id[child_id]
        label_parts = []
        for attr in with_edge_labels:
            value = getattr(child_node, attr, None)
            if value is not None:
                label_parts.append(str(value))
        return "\n".join(label_parts)

    def to_networkx_graph(
        self: Self,
        with_node_labels: List[str] = ["text"],
        with_edge_labels: List[str] = ["deprel"],
    ) -> Any:
        """
        Convert the indexed tree into a NetworkX directed graph.

        Returns:
            networkx.DiGraph: A directed graph with parent-to-child edges.

        Raises:
            ImportError: If NetworkX is not installed.
        """
        try:
            import networkx as nx
        except ImportError as exc:
            raise ImportError(
                "SyntaxGraphIndex.to_networkx_graph() requires the 'networkx' package."
                "Please install it using `pip install networkx`."
            ) from exc

        graph = nx.DiGraph()

        for token_id in self.token_order:
            node = self.nodes_by_id[token_id]
            node_attrs = self._get_all_span_attributes(node)

            graph.add_node(
                token_id,
                label=self._format_node_label(
                    token_id, with_node_labels=with_node_labels
                ),
                **node_attrs,
            )

        for child_id in self.token_order:
            parent_id = self.parent_by_id.get(child_id)
            if parent_id is None or parent_id == 0:
                continue
            child_node = self.nodes_by_id[child_id]
            edge_attrs = self._get_all_span_attributes(child_node)

            graph.add_edge(
                parent_id,
                child_id,
                label=self._format_edge_label(
                    child_id, with_edge_labels=with_edge_labels
                ),
                **edge_attrs,
            )

        return graph

    def visualize(
        self: Self,
        with_node_labels: List[str] = ["text"],
        with_edge_labels: List[str] = ["deprel"],
        attributes_to_show_in_inspector: Optional[List[str]] = None,
        font_size: int = 8,
        title: Optional[str] = None,
        highlight_token_ids: Optional[Iterable[int]] = None,
        show: bool = True,
    ) -> Any:
        """
        Visualise the dependency tree as a readable tree diagram.

        Args:
            with_node_labels (List[str], optional): Which attributes to show on nodes.
            with_edge_labels (List[str], optional): Which attributes to show on edges.
            attributes_to_show_in_inspector (Optional[List[str]], optional): Attributes to display in the node inspector.
            font_size (int, optional): Font size used for the rendered text.
            title (Optional[str], optional): Optional tree title.
            highlight_token_ids (Optional[Iterable[int]], optional): Token IDs to
                highlight with a different node background colour.
            show (bool, optional): Whether to display the rendered tree immediately.

        Returns:
            TreeNode: The rendered ete3 tree root.
        """
        global Tree, NodeStyle, TextFace, TreeStyle

        if any(cls is None for cls in [Tree, NodeStyle, TextFace, TreeStyle]):
            try:
                from ete3 import Tree as _Tree
                from ete3.treeview.main import NodeStyle as _NodeStyle
                from ete3.treeview.faces import TextFace as _TextFace
                from ete3.treeview.main import TreeStyle as _TreeStyle
            except ImportError as exc:
                raise ImportError(
                    "The 'ete3' package is required for visualization. "
                    "Please install it using `pip install ete3` or visit "
                    "http://etetoolkit.org/ for more details."
                ) from exc

            Tree = _Tree
            NodeStyle = _NodeStyle
            TextFace = _TextFace
            TreeStyle = _TreeStyle

        # Assert that the ete3 classes have been loaded successfully
        assert (
            Tree is not None
            and NodeStyle is not None
            and TextFace is not None
            and TreeStyle is not None
        ), "Failed to load ete3 classes for visualization."

        tree_node_cls = Tree
        node_style_cls = NodeStyle
        text_face_cls = TextFace
        tree_style_cls = TreeStyle

        highlight_token_ids = set(highlight_token_ids or [])

        def build_subtree(token_id: int) -> Any:
            """Recursively build an ete3 subtree from one token."""

            node = tree_node_cls(name=str(token_id))

            style = node_style_cls()
            style["size"] = 0
            style["hz_line_width"] = 1
            style["vt_line_width"] = 1
            style["fgcolor"] = "#4a6fa5"
            if token_id in highlight_token_ids:
                style["bgcolor"] = "#ffe08a"
            node.set_style(style)

            label_text = self._format_node_label(
                token_id, with_node_labels=with_node_labels
            )
            node.add_face(
                text_face_cls(label_text, fsize=font_size),
                column=0,
                position="branch-right",
            )

            if with_edge_labels:
                edge_text = self._format_edge_label(
                    token_id, with_edge_labels=with_edge_labels
                )
                if edge_text:
                    node.add_face(
                        text_face_cls(
                            edge_text,
                            fsize=max(font_size - 1, 6),
                            fgcolor="#666666",
                        ),
                        column=0,
                        position="branch-top",
                    )

            # Add all attributes as features to the ete3 node for the node inspector
            span = self.nodes_by_id[token_id]
            node_attrs = self._get_all_span_attributes(
                span, attributes_to_show_in_inspector
            )
            for attr, value in node_attrs.items():
                node.add_feature(attr, value)

            for child_id in self.children_by_id.get(token_id, []):
                node.add_child(build_subtree(child_id))

            return node

        roots = self.get_root_nodes()
        if not roots:
            raise ValueError("Cannot visualise an empty syntax graph.")

        if len(roots) == 1:
            ete_root = build_subtree(int(getattr(roots[0], "id")))
        else:
            ete_root = tree_node_cls(name="")
            dummy_style = node_style_cls()
            dummy_style["size"] = 0
            dummy_style["hz_line_width"] = 0
            dummy_style["vt_line_width"] = 0
            ete_root.set_style(dummy_style)
            for root in roots:
                ete_root.add_child(build_subtree(int(getattr(root, "id"))))

        ts = tree_style_cls()
        ts.show_leaf_name = False
        ts.show_scale = False
        ts.mode = "r"
        ts.branch_vertical_margin = 12

        if title:
            ts.title.add_face(
                text_face_cls(title, fsize=font_size + 2, bold=True), column=0
            )

        if show:
            ete_root.show(tree_style=ts)

        return ete_root

    def _build_visualization_title(self: Self) -> str:
        """
        Create a default title for the visualisation.
        """
        sentence_id = (
            f"Sentence {self.sent_id}" if self.sent_id is not None else "Sentence"
        )
        if self.sentence_span is None:
            return f"{sentence_id} dependency tree"
        return f"{sentence_id} dependency tree {self.sentence_span}"

    def _validate_tree(self: Self) -> bool:
        """
        Validates that the graph forms a proper tree structure. Checks for cycles, missing heads, and orphan references.

        Args:
            self (Self): The instance of the SyntaxGraphIndex being validated.

        Returns:
            bool: True if the graph forms a valid tree structure, False otherwise. A valid tree structure means that there are no cycles in the parent-child relationships, all nodes have a valid head (except for root nodes), and there are no orphan references (nodes that reference a non-existent head).
        """
        # Check for cycles using a depth-first search
        visited = set()

        def _dfs(node_id: int, parent_id: Optional[int]) -> bool:
            """
            Performs a depth-first search to detect cycles in the graph.

            Args:
                node_id (int): The ID of the current node being visited in the depth-first search.
                parent_id (Optional[int]): The ID of the parent node of the current node in the depth-first search. This is used to avoid false positive cycle detection when traversing back to the parent node.

            Returns:
                bool: True if no cycles are detected in the graph, False if a cycle is detected. A cycle is detected if a node is visited more than once during the depth-first search, indicating that there is a circular reference in the parent-child relationships of the graph.
            """
            if node_id in visited:
                return False  # Cycle detected
            visited.add(node_id)
            for child_id in self.children_by_id.get(node_id, []):
                if child_id == parent_id:
                    continue  # Skip the parent node to avoid false positive cycle detection
                if not _dfs(child_id, node_id):
                    return False
            return True

        # Check for valid heads and orphan references
        for token_id in self.token_order:
            parent_id = self.parent_by_id.get(token_id)
            if (
                parent_id is not None  # A head is specified
                and parent_id != 0  # Root nodes have head = 0, so we allow that
                and parent_id
                not in self.nodes_by_id  # The specified head does not exist in the graph
            ):
                return False  # Orphan reference detected (node references a non-existent head)

        # Check for cycles starting from root nodes
        root_nodes = self.get_root_nodes()
        if not root_nodes:
            return False

        for root_node in root_nodes:
            root_id = int(getattr(root_node, "id"))
            if not _dfs(root_id, None):
                return False  # Cycle detected

        # Every node must be reachable from some root.
        if len(visited) != len(self.token_order):
            return False

        return True
