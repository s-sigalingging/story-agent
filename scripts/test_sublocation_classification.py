from enum import Enum


# ============================================================
# BATCH 14B.2-C2-A — SUBLOCATION CLASSIFICATION CONTRACT
# ============================================================


class SpatialClassification(str, Enum):
    CANONICAL_SUBLOCATION = "CANONICAL_SUBLOCATION"
    SCENE_SPACE = "SCENE_SPACE"
    MOBILE_SPACE = "MOBILE_SPACE"
    SCENE_STATE = "SCENE_STATE"


def pass_test(
    number: int,
    description: str,
) -> None:
    print(
        f"TEST {number} — "
        f"{description} → PASSED"
    )


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(message)


def classify_spatial_reference(
    *,
    persistent_identity: bool,
    reusable: bool,
    canonical_parent_available: bool,
    framing_only: bool = False,
    temporary_state: bool = False,
    mobile_object: bool = False,
) -> SpatialClassification:

    # --------------------------------------------------------
    # Temporary state always belongs to scene state.
    # Example: "burning coal car".
    # --------------------------------------------------------

    if temporary_state:
        return SpatialClassification.SCENE_STATE

    # --------------------------------------------------------
    # Mobile objects are not world locations.
    # Example: a specific railway car.
    # --------------------------------------------------------

    if mobile_object:
        return SpatialClassification.MOBILE_SPACE

    # --------------------------------------------------------
    # Framing / positional descriptions are scene spaces.
    # Example: dock edge, corner table, office corner.
    # --------------------------------------------------------

    if framing_only:
        return SpatialClassification.SCENE_SPACE

    # --------------------------------------------------------
    # Canonical sublocations must be persistent,
    # reusable, and have a known canonical parent.
    # --------------------------------------------------------

    if (
        persistent_identity
        and reusable
        and canonical_parent_available
    ):
        return SpatialClassification.CANONICAL_SUBLOCATION

    # --------------------------------------------------------
    # Anything else remains production-level scene space.
    # --------------------------------------------------------

    return SpatialClassification.SCENE_SPACE


def main() -> None:
    print()
    print(
        "BATCH 14B.2-C2-A — "
        "SUBLOCATION CLASSIFICATION CONTRACT"
    )
    print("=" * 76)

    # --------------------------------------------------------
    # TEST 1
    # Persistent reusable interior can be a sublocation.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=True,
        canonical_parent_available=True,
    )

    require(
        result
        == SpatialClassification.CANONICAL_SUBLOCATION,
        (
            "Persistent reusable interior was not "
            "classified as canonical sublocation."
        ),
    )

    pass_test(
        1,
        "persistent reusable interior can become sublocation",
    )

    # --------------------------------------------------------
    # TEST 2
    # Dock Edge is scene space.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=False,
        reusable=False,
        canonical_parent_available=True,
        framing_only=True,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        "Dock Edge should remain scene space.",
    )

    pass_test(
        2,
        "Dock Edge remains scene space",
    )

    # --------------------------------------------------------
    # TEST 3
    # Corner table is scene space.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=False,
        reusable=False,
        canonical_parent_available=True,
        framing_only=True,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        (
            "Corner table should not become "
            "canonical geography."
        ),
    )

    pass_test(
        3,
        "corner table remains scene space",
    )

    # --------------------------------------------------------
    # TEST 4
    # Office corner is scene space.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=False,
        reusable=False,
        canonical_parent_available=True,
        framing_only=True,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        (
            "Office corner should remain "
            "production-level space."
        ),
    )

    pass_test(
        4,
        "office corner remains scene space",
    )

    # --------------------------------------------------------
    # TEST 5
    # Burning state is not a location.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=False,
        reusable=False,
        canonical_parent_available=False,
        temporary_state=True,
    )

    require(
        result == SpatialClassification.SCENE_STATE,
        (
            "Burning coal car should be "
            "classified as scene state."
        ),
    )

    pass_test(
        5,
        "burning coal car remains scene state",
    )

    # --------------------------------------------------------
    # TEST 6
    # Specific railway car is mobile space.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=True,
        canonical_parent_available=True,
        mobile_object=True,
    )

    require(
        result == SpatialClassification.MOBILE_SPACE,
        (
            "Specific railway car should not "
            "become fixed world geography."
        ),
    )

    pass_test(
        6,
        "specific railway car remains mobile space",
    )

    # --------------------------------------------------------
    # TEST 7
    # Missing parent prevents canonical promotion.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=True,
        canonical_parent_available=False,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        (
            "Location without canonical parent "
            "was promoted prematurely."
        ),
    )

    pass_test(
        7,
        "unknown parent prevents canonical promotion",
    )

    # --------------------------------------------------------
    # TEST 8
    # One-off room is not automatically canon.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=False,
        canonical_parent_available=True,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        (
            "One-off room was incorrectly "
            "promoted to canonical sublocation."
        ),
    )

    pass_test(
        8,
        "one-off room is not automatically canonical",
    )

    # --------------------------------------------------------
    # TEST 9
    # Reusability alone is insufficient.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=False,
        reusable=True,
        canonical_parent_available=True,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        (
            "Reusable framing description was "
            "incorrectly promoted."
        ),
    )

    pass_test(
        9,
        "reusability alone cannot create canon",
    )

    # --------------------------------------------------------
    # TEST 10
    # Canonical parent alone is insufficient.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=False,
        reusable=False,
        canonical_parent_available=True,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        (
            "Parent membership alone incorrectly "
            "created a canonical sublocation."
        ),
    )

    pass_test(
        10,
        "parent membership alone cannot create canon",
    )

    # --------------------------------------------------------
    # TEST 11
    # Persistent + reusable + parent is sufficient.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=True,
        canonical_parent_available=True,
    )

    require(
        result
        == SpatialClassification.CANONICAL_SUBLOCATION,
        "Valid canonical sublocation was rejected.",
    )

    pass_test(
        11,
        "complete sublocation criteria are sufficient",
    )

    # --------------------------------------------------------
    # TEST 12
    # Temporary state overrides persistence.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=True,
        canonical_parent_available=True,
        temporary_state=True,
    )

    require(
        result == SpatialClassification.SCENE_STATE,
        (
            "Temporary state incorrectly became "
            "canonical geography."
        ),
    )

    pass_test(
        12,
        "temporary state overrides location promotion",
    )

    # --------------------------------------------------------
    # TEST 13
    # Mobile nature overrides persistence.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=True,
        canonical_parent_available=True,
        mobile_object=True,
    )

    require(
        result == SpatialClassification.MOBILE_SPACE,
        (
            "Mobile object incorrectly became "
            "fixed canonical geography."
        ),
    )

    pass_test(
        13,
        "mobile space cannot become fixed geography",
    )

    # --------------------------------------------------------
    # TEST 14
    # Framing overrides otherwise valid criteria.
    # --------------------------------------------------------

    result = classify_spatial_reference(
        persistent_identity=True,
        reusable=True,
        canonical_parent_available=True,
        framing_only=True,
    )

    require(
        result == SpatialClassification.SCENE_SPACE,
        (
            "Framing-only reference incorrectly "
            "became canonical geography."
        ),
    )

    pass_test(
        14,
        "framing description cannot become sublocation",
    )

    # --------------------------------------------------------
    # TEST 15
    # Classification is deterministic.
    # --------------------------------------------------------

    kwargs = {
        "persistent_identity": True,
        "reusable": True,
        "canonical_parent_available": True,
        "framing_only": False,
        "temporary_state": False,
        "mobile_object": False,
    }

    result_a = classify_spatial_reference(**kwargs)
    result_b = classify_spatial_reference(**kwargs)

    require(
        result_a == result_b,
        "Spatial classification is not deterministic.",
    )

    pass_test(
        15,
        "sublocation classification is deterministic",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 76)
    print(
        "BATCH 14B.2-C2-A "
        "SUBLOCATION CLASSIFICATION CONTRACT PASSED"
    )
    print("=" * 76)
    print()


if __name__ == "__main__":
    main()