# ValueCondition class testing
from types import SimpleNamespace
from typing import Any, cast

from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
    NestedValueCondition,
    NodeConstraint,
    ValueCondition,
)
from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    ConditionMode,
    DirectionMode,
    EdgeContext,
)
import pytest


def test_valuecondition_exact_and_negation() -> None:
    exact = ValueCondition(mode=ConditionMode.EXACT, value="NOUN")
    # Check: exact mode matches only identical value
    assert exact.matches("NOUN")
    assert not exact.matches("VERB")

    # Check: negation mode inverts exact match
    neg = ValueCondition(mode=ConditionMode.NEGATION, value="VERB")
    assert neg.matches("NOUN")
    assert not neg.matches("VERB")


def test_valuecondition_membership_and_not_membership() -> None:
    membership = ValueCondition(mode=ConditionMode.MEMBERSHIP, value=("NOUN", "ADJ"))
    # Check: membership mode accepts items in the tuple
    assert membership.matches("NOUN")
    assert not membership.matches("VERB")

    not_membership = ValueCondition(
        mode=ConditionMode.NOT_MEMBERSHIP, value=("NOUN", "ADJ")
    )
    # Check: not-membership accepts values not in the tuple
    assert not_membership.matches("VERB")
    assert not not_membership.matches("NOUN")


def test_valuecondition_wildcard_and_missing() -> None:
    wildcard = ValueCondition(mode=ConditionMode.WILDCARD, value=None)
    # Check: wildcard matches any value including None
    assert wildcard.matches("anything")
    assert wildcard.matches(None)

    exact_missing = ValueCondition(
        mode=ConditionMode.EXACT, value="NOUN", allow_missing=True
    )
    # Check: allow_missing lets exact match succeed for None
    assert exact_missing.matches(None)


def test_valuecondition_normalizer_and_constructor_validation() -> None:
    exact_norm = ValueCondition(
        mode=ConditionMode.EXACT,
        value="Noun",
        normalizer=lambda x: x.lower() if isinstance(x, str) else x,
    )
    # Check: normalizer is applied before matching
    assert exact_norm.matches("NOUN")

    # Check: constructor validation raises on invalid params and bad normalizer
    with pytest.raises(ValueError):
        ValueCondition(mode=ConditionMode.EXACT, value=None)
    with pytest.raises(ValueError):
        ValueCondition(mode=ConditionMode.WILDCARD, value="not-none")
    with pytest.raises(ValueError):
        ValueCondition(mode=ConditionMode.NOT_MEMBERSHIP, value=None)
    with pytest.raises(TypeError):
        bad_normalizer = cast(Any, "not-callable")
        ValueCondition(
            mode=ConditionMode.EXACT, value="NOUN", normalizer=bad_normalizer
        )


def test_valuecondition_regex_matching() -> None:
    regex = ValueCondition(mode=ConditionMode.REGEX, value=r"^NO.*")
    # Check: regex mode matches strings that satisfy the pattern
    assert regex.matches("NOUN")
    assert regex.matches("NOM")
    assert not regex.matches("VERB")


# NestedValueCondition class testing
def test_nestedvaluecondition_exact_required_and_forbidden() -> None:
    exact = NestedValueCondition(
        mode=ConditionMode.EXACT,
        required={"Case": "Gen", "Number": "Sing"},
        forbidden={"Polarity": "Neg"},
        allow_extra_keys=False,
    )
    # Check: required and forbidden features are enforced and missing keys fail
    assert exact.matches({"Case": "Gen", "Number": "Sing", "Polarity": "Pos"})
    assert not exact.matches({"Case": "Nom", "Number": "Sing", "Polarity": "Pos"})
    assert not exact.matches({"Case": "Gen", "Number": "Sing", "Polarity": "Neg"})
    assert not exact.matches({"Case": "Gen", "Polarity": "Pos"})


def test_nestedvaluecondition_allow_missing_and_extra_keys() -> None:
    exact_allow_missing = NestedValueCondition(
        mode=ConditionMode.EXACT,
        required={"Case": "Gen", "Number": "Sing"},
        forbidden={"Polarity": "Neg"},
        allow_missing=True,
        allow_extra_keys=True,
    )
    # Check: allow_missing and allow_extra_keys affect matching behaviour
    assert exact_allow_missing.matches({"Case": "Gen"})

    exact_no_extra = NestedValueCondition(
        mode=ConditionMode.EXACT,
        required={"Case": "Gen"},
        forbidden={"Polarity": "Neg"},
        allow_extra_keys=False,
    )
    # Check: extra keys rejected when allow_extra_keys=False
    assert not exact_no_extra.matches({"Case": "Gen", "Other": "X"})

    exact_with_extra = NestedValueCondition(
        mode=ConditionMode.EXACT,
        required={"Case": "Gen"},
        forbidden={"Polarity": "Neg"},
        allow_extra_keys=True,
    )
    # Check: extra keys accepted when allow_extra_keys=True
    assert exact_with_extra.matches({"Case": "Gen", "Other": "X"})


def test_nestedvaluecondition_negation_and_wildcard() -> None:
    neg = NestedValueCondition(
        mode=ConditionMode.NEGATION,
        required={"Case": "Gen", "Number": "Sing"},
        forbidden={"Polarity": "Neg"},
    )
    # Check: negation inverts required set; forbidden still blocks matches
    assert not neg.matches({"Case": "Gen", "Number": "Sing"})
    assert neg.matches({"Case": "Gen", "Number": "Plur"})
    assert not neg.matches({"Case": "Gen", "Number": "Plur", "Polarity": "Neg"})

    wildcard = NestedValueCondition(mode=ConditionMode.WILDCARD)
    # Check: wildcard accepts any dict or None
    assert wildcard.matches({"anything": "goes"})
    assert wildcard.matches(None)


def test_nestedvaluecondition_normalizer_and_constructor_validation() -> None:
    norm_cond = NestedValueCondition(
        mode=ConditionMode.EXACT,
        required={"Case": "gEn"},
        forbidden={"Polarity": "nEg"},
        normalizer=lambda x: x.lower() if isinstance(x, str) else x,
        allow_extra_keys=True,
    )
    # Check: normalizer is applied to feature values before comparison
    assert norm_cond.matches({"Case": "GEN", "Polarity": "pos"})

    # Check: constructor validation for required args and normalizer type
    with pytest.raises(ValueError):
        NestedValueCondition(mode=ConditionMode.EXACT)
    with pytest.raises(ValueError):
        NestedValueCondition(mode=ConditionMode.WILDCARD, required={"Case": "Gen"})
    with pytest.raises(TypeError):
        bad_normalizer = cast(Any, "not-callable")
        NestedValueCondition(
            mode=ConditionMode.EXACT,
            required={"Case": "Gen"},
            normalizer=bad_normalizer,
        )


def test_nestedvaluecondition_nested_and_string_structures() -> None:
    nested = NestedValueCondition(
        mode=ConditionMode.EXACT,
        required={
            "Case": {"primary": "Gen", "alternatives": ["Gen", "Nom"]},
            "Number": {"value": {"kind": "Sing"}},
        },
        allow_extra_keys=True,
    )
    # Check: nested structures are matched by deep comparison
    assert nested.matches(
        {
            "Case": {"primary": "Gen", "alternatives": ["Gen", "Nom"]},
            "Number": {"value": {"kind": "Sing"}},
            "Extra": "ignored",
        }
    )
    # Check: mismatch in nested fields fails
    assert not nested.matches(
        {
            "Case": {"primary": "Nom", "alternatives": ["Gen", "Nom"]},
            "Number": {"value": {"kind": "Sing"}},
        }
    )

    list_pattern = NestedValueCondition(
        mode=ConditionMode.MEMBERSHIP,
        required=[{"Case": "Gen"}, {"Number": "Sing"}],
    )
    # Check: membership mode over list structures
    assert list_pattern.matches([{"Case": "Gen"}, {"Number": "Plur"}])
    assert not list_pattern.matches([{"Case": "Part"}, {"Number": "Plur"}])

    string_feats = NestedValueCondition(
        mode=ConditionMode.EXACT,
        required="_",
        allow_missing=True,
    )
    # Check: string-based feature patterns are supported
    assert string_feats.matches("_")


# NodeConstraint class testing
def make_node(
    text: str = "test",
    upostag: str = "NOUN",
    xpostag: str = "S",
    lemma: str = "kass",
    deprel: str = "nmod",
    feats: dict | None = None,
) -> SimpleNamespace:
    """Create a lightweight span-like node object for NodeConstraint tests."""
    return SimpleNamespace(
        text=text,
        upostag=upostag,
        xpostag=xpostag,
        lemma=lemma,
        deprel=deprel,
        feats={} if feats is None else feats,
    )


def test_nodeconstraint_happy_path_and_scalar_mismatch() -> None:
    node = make_node(
        upostag="NOUN",
        xpostag="S",
        lemma="lendur",
        deprel="nmod",
        feats={"sg": "sg", "n": "n"},
    )

    constraint = NodeConstraint(
        role="target",
        attribute_conditions={
            "upostag": ValueCondition(ConditionMode.EXACT, "NOUN"),
            "xpostag": ValueCondition(ConditionMode.EXACT, "S"),
            "lemma": ValueCondition(ConditionMode.EXACT, "lendur"),
            "deprel": ValueCondition(ConditionMode.EXACT, "nmod"),
        },
        nested_attribute_conditions={
            "feats": NestedValueCondition(
                mode=ConditionMode.EXACT,
                required={"sg": "sg", "n": "n"},
                allow_extra_keys=True,
            )
        },
    )
    # Check: a node matching all attribute and feat constraints succeeds
    assert constraint.matches(node)

    wrong_node = make_node(upostag="VERB", xpostag="V", lemma="andma", deprel="root")
    # Check: a node with wrong scalar attributes fails
    assert not constraint.matches(wrong_node)


def test_nodeconstraint_feature_mismatch_and_predicates() -> None:
    constraint = NodeConstraint(
        role="target",
        attribute_conditions={
            "upostag": ValueCondition(ConditionMode.EXACT, "NOUN"),
            "xpostag": ValueCondition(ConditionMode.EXACT, "S"),
            "lemma": ValueCondition(ConditionMode.EXACT, "lendur"),
            "deprel": ValueCondition(ConditionMode.EXACT, "nmod"),
        },
        nested_attribute_conditions={
            "feats": NestedValueCondition(
                mode=ConditionMode.EXACT,
                required={"sg": "sg", "n": "n"},
                allow_extra_keys=True,
            )
        },
    )
    feature_mismatch_node = make_node(
        upostag="NOUN",
        xpostag="S",
        lemma="lendur",
        deprel="nmod",
        feats={"sg": "sg", "g": "g"},
    )
    # Check: feature mismatch causes node constraint to fail
    assert not constraint.matches(feature_mismatch_node)

    def pred_ok(node: Any) -> bool:
        return node.text.startswith("l")

    def pred_fail(node: Any) -> bool:
        return node.text.endswith("z")

    pred_constraint_ok = NodeConstraint(role="pred_test", extra_predicates=(pred_ok,))
    pred_constraint_fail = NodeConstraint(
        role="pred_test", extra_predicates=(pred_fail,)
    )
    predicate_node = make_node(text="lendur")
    # Check: extra_predicates are evaluated; good predicate passes, bad fails
    assert pred_constraint_ok.matches(predicate_node)
    assert not pred_constraint_fail.matches(predicate_node)


def test_nodeconstraint_selectivity_describe_and_validation() -> None:
    unconstrained = NodeConstraint(role="a")
    exact_upos = NodeConstraint(
        role="b",
        attribute_conditions={"upostag": ValueCondition(ConditionMode.EXACT, "NOUN")},
    )
    exact_upos_plus_feats = NodeConstraint(
        role="c",
        attribute_conditions={"upostag": ValueCondition(ConditionMode.EXACT, "NOUN")},
        nested_attribute_conditions={
            "feats": NestedValueCondition(
                mode=ConditionMode.EXACT, required={"sg": "sg"}, allow_extra_keys=True
            )
        },
    )
    # Check: selectivity scoring increases with added constraints
    assert unconstrained.score_selectivity() < exact_upos.score_selectivity()
    assert exact_upos.score_selectivity() < exact_upos_plus_feats.score_selectivity()

    constraint = NodeConstraint(
        role="target",
        attribute_conditions={"upostag": ValueCondition(ConditionMode.EXACT, "NOUN")},
        nested_attribute_conditions={
            "feats": NestedValueCondition(
                mode=ConditionMode.EXACT, required={"sg": "sg"}, allow_extra_keys=True
            )
        },
    )
    desc = constraint.describe()
    # Check: describe includes role, attribute and feat info
    assert "Role: target" in desc
    assert "Attribute 'upostag':" in desc and "Nested 'feats':" in desc

    # Check: constructor validation for role and types
    with pytest.raises(TypeError):
        NodeConstraint(role="")
    with pytest.raises(TypeError):
        bad_attribute_conditions = cast(Any, {"upostag": "not-a-valuecondition"})
        NodeConstraint(role="bad_upos", attribute_conditions=bad_attribute_conditions)
    with pytest.raises(TypeError):
        bad_feats_condition = cast(Any, {"feats": "not-a-nestedvaluecondition"})
        NodeConstraint(
            role="bad_feats", nested_attribute_conditions=bad_feats_condition
        )
    with pytest.raises(TypeError):
        bad_predicates = cast(Any, [lambda n: True])
        NodeConstraint(role="bad_preds", extra_predicates=bad_predicates)
    with pytest.raises(TypeError):
        bad_predicate_member = cast(Any, ("not-callable",))
        NodeConstraint(role="bad_pred_member", extra_predicates=bad_predicate_member)
    with pytest.raises(ValueError):
        NodeConstraint(
            role="bad_dict",
            attribute_conditions={
                "misc": ValueCondition(ConditionMode.EXACT, {"Case": "Gen"})
            },
        )


def test_nodeconstraint_feats_allowed_in_attribute_conditions() -> None:
    """Ensure that nested_attribute_conditions can contain a NestedValueCondition under 'feats'."""
    node = make_node(feats={"sg": "sg", "n": "n"})
    constraint = NodeConstraint(
        role="feat_attr",
        nested_attribute_conditions={
            "feats": NestedValueCondition(
                mode=ConditionMode.EXACT,
                required={"sg": "sg", "n": "n"},
                allow_extra_keys=True,
            )
        },
    )
    assert constraint.matches(node)


# EdgeConstraint class testing
def make_edge_context(
    direction: DirectionMode,
    hops: int,
) -> EdgeContext:
    """Build an EdgeContext instance for tests."""
    ctx = EdgeContext(
        direction=direction,
        hops=hops,
    )
    return ctx


def test_edgeconstraint_up_and_direction_mismatch() -> None:
    c_up = EdgeConstraint(
        direction=DirectionMode.UP,
        min_hops=1,
        max_hops=2,
    )
    ctx_up_ok = make_edge_context(DirectionMode.UP, 1)
    # Check: matching works for correct direction and hops
    assert c_up.matches(ctx_up_ok)

    ctx_wrong_dir = make_edge_context(DirectionMode.DOWN, 1)
    # Check: wrong direction does not match
    assert not c_up.matches(ctx_wrong_dir)


def test_edgeconstraint_both_direction_and_hops() -> None:
    c_both = EdgeConstraint(
        direction=DirectionMode.BOTH,
        min_hops=1,
        max_hops=3,
    )
    # Check: BOTH direction accepts both up and down when hops are OK
    assert c_both.matches(make_edge_context(DirectionMode.UP, 2))
    assert c_both.matches(make_edge_context(DirectionMode.DOWN, 2))
    c_up = EdgeConstraint(
        direction=DirectionMode.UP,
        min_hops=1,
        max_hops=2,
    )
    # Check: mismatched hops fall outside allowed ranges
    assert not c_up.matches(make_edge_context(DirectionMode.UP, 0))
    assert not c_up.matches(make_edge_context(DirectionMode.UP, 3))


def test_edgeconstraint_policy_describe_and_validation() -> None:
    c_up = EdgeConstraint(
        direction=DirectionMode.UP,
        min_hops=1,
        max_hops=2,
    )

    # Check: describe contains human-readable direction and hops info
    desc = c_up.describe()
    assert "Direction: up" in desc
    assert "Hops:" in desc

    with pytest.raises(TypeError):
        bad_direction = cast(Any, "up")
        EdgeConstraint(direction=bad_direction)
    with pytest.raises(ValueError):
        EdgeConstraint(direction=DirectionMode.UP, min_hops=-1)
    with pytest.raises(ValueError):
        EdgeConstraint(direction=DirectionMode.UP, max_hops=-1)
    with pytest.raises(ValueError):
        EdgeConstraint(direction=DirectionMode.UP, min_hops=3, max_hops=1)
