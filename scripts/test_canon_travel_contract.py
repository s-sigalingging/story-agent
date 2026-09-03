from pydantic import ValidationError

from app.models.canon import (
    LocationRelationType,
    TravelConstraint,
)


# ============================================================
# BATCH 14B.2-C3-A — GEOGRAPHY & TRAVEL DOMAIN CONTRACT
# ============================================================


TRAVEL_RELATION_TYPES = {
    LocationRelationType.CONNECTED_TO,
    LocationRelationType.ROAD_ROUTE,
    LocationRelationType.RAIL_ROUTE,
    LocationRelationType.TIDAL_ROUTE,
    LocationRelationType.WALKING_ROUTE,
}


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


def require_validation_error(
    callback,
    message: str,
) -> None:
    try:
        callback()
    except (ValidationError, ValueError):
        return

    raise AssertionError(message)


def build_basic_route(
    **overrides,
) -> TravelConstraint:
    data = {
        "constraint_id": "TRAVEL_TEST_ROUTE",
        "source_location_id": "LOC_OLD_DOCKS",
        "target_location_id": "LOC_CENTRAL_DEPOT",
        "relation_type": (
            LocationRelationType.ROAD_ROUTE
        ),
        "minimum_minutes": 10,
        "maximum_minutes": 20,
        "description": (
            "Canonical travel route between "
            "the Old Docks and Central Depot."
        ),
    }

    data.update(overrides)

    return TravelConstraint(**data)


# ============================================================
# TEST RUNNER
# ============================================================


def main() -> None:
    print()
    print(
        "BATCH 14B.2-C3-A — "
        "GEOGRAPHY & TRAVEL DOMAIN CONTRACT"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # TEST 1 — basic road route supported
    # --------------------------------------------------------

    route = build_basic_route()

    require(
        route.relation_type
        == LocationRelationType.ROAD_ROUTE,
        "ROAD_ROUTE was not preserved.",
    )

    pass_test(
        1,
        "road travel route is supported",
    )

    # --------------------------------------------------------
    # TEST 2 — connected-to relation supported
    # --------------------------------------------------------

    route = build_basic_route(
        relation_type=(
            LocationRelationType.CONNECTED_TO
        ),
    )

    require(
        route.relation_type
        == LocationRelationType.CONNECTED_TO,
        "CONNECTED_TO was not preserved.",
    )

    pass_test(
        2,
        "generic geographic connection is supported",
    )

    # --------------------------------------------------------
    # TEST 3 — rail route supported
    # --------------------------------------------------------

    route = build_basic_route(
        relation_type=(
            LocationRelationType.RAIL_ROUTE
        ),
    )

    require(
        route.relation_type
        == LocationRelationType.RAIL_ROUTE,
        "RAIL_ROUTE was not preserved.",
    )

    pass_test(
        3,
        "rail travel route is supported",
    )

    # --------------------------------------------------------
    # TEST 4 — walking route supported
    # --------------------------------------------------------

    route = build_basic_route(
        relation_type=(
            LocationRelationType.WALKING_ROUTE
        ),
    )

    require(
        route.relation_type
        == LocationRelationType.WALKING_ROUTE,
        "WALKING_ROUTE was not preserved.",
    )

    pass_test(
        4,
        "walking travel route is supported",
    )

    # --------------------------------------------------------
    # TEST 5 — tidal route supported
    # --------------------------------------------------------

    route = build_basic_route(
        relation_type=(
            LocationRelationType.TIDAL_ROUTE
        ),
    )

    require(
        route.relation_type
        == LocationRelationType.TIDAL_ROUTE,
        "TIDAL_ROUTE was not preserved.",
    )

    pass_test(
        5,
        "tidal travel route is supported",
    )

    # --------------------------------------------------------
    # TEST 6 — containment excluded from travel vocabulary
    # --------------------------------------------------------

    require(
        LocationRelationType.CONTAINS
        not in TRAVEL_RELATION_TYPES,
        (
            "CONTAINS must remain hierarchy semantics, "
            "not travel semantics."
        ),
    )

    pass_test(
        6,
        "containment remains separate from travel semantics",
    )

    # --------------------------------------------------------
    # TEST 7 — zero-minute duration supported
    # --------------------------------------------------------

    route = build_basic_route(
        minimum_minutes=0,
        maximum_minutes=0,
    )

    require(
        route.minimum_minutes == 0
        and route.maximum_minutes == 0,
        "Zero-minute duration was not preserved.",
    )

    pass_test(
        7,
        "zero-minute duration is representable",
    )

    # --------------------------------------------------------
    # TEST 8 — negative minimum rejected
    # --------------------------------------------------------

    require_validation_error(
        lambda: build_basic_route(
            minimum_minutes=-1,
        ),
        "Negative minimum duration was accepted.",
    )

    pass_test(
        8,
        "negative minimum duration is rejected",
    )

    # --------------------------------------------------------
    # TEST 9 — negative maximum rejected
    # --------------------------------------------------------

    require_validation_error(
        lambda: build_basic_route(
            maximum_minutes=-1,
        ),
        "Negative maximum duration was accepted.",
    )

    pass_test(
        9,
        "negative maximum duration is rejected",
    )

    # --------------------------------------------------------
    # TEST 10 — inverted duration rejected
    # --------------------------------------------------------

    require_validation_error(
        lambda: build_basic_route(
            minimum_minutes=30,
            maximum_minutes=10,
        ),
        (
            "Travel route accepted minimum duration "
            "greater than maximum duration."
        ),
    )

    pass_test(
        10,
        "inverted duration range is rejected",
    )

    # --------------------------------------------------------
    # TEST 11 — minimum-only duration supported
    # --------------------------------------------------------

    route = build_basic_route(
        minimum_minutes=15,
        maximum_minutes=None,
    )

    require(
        route.minimum_minutes == 15
        and route.maximum_minutes is None,
        "Minimum-only duration was not preserved.",
    )

    pass_test(
        11,
        "minimum-only travel duration is supported",
    )

    # --------------------------------------------------------
    # TEST 12 — maximum-only duration supported
    # --------------------------------------------------------

    route = build_basic_route(
        minimum_minutes=None,
        maximum_minutes=20,
    )

    require(
        route.minimum_minutes is None
        and route.maximum_minutes == 20,
        "Maximum-only duration was not preserved.",
    )

    pass_test(
        12,
        "maximum-only travel duration is supported",
    )

    # --------------------------------------------------------
    # TEST 13 — unknown duration supported
    # --------------------------------------------------------

    route = build_basic_route(
        minimum_minutes=None,
        maximum_minutes=None,
    )

    require(
        route.minimum_minutes is None
        and route.maximum_minutes is None,
        "Unknown travel duration was not preserved.",
    )

    pass_test(
        13,
        "unknown travel duration is representable",
    )

    # --------------------------------------------------------
    # TEST 14 — conditional access window supported
    # --------------------------------------------------------

    route = build_basic_route(
        constraint_id="TRAVEL_BLACKWOOD_TIDAL",
        source_location_id="LOC_BLACKWOOD",
        target_location_id=(
            "LOC_BLACKWOOD_TIDELAND_PATH"
        ),
        relation_type=(
            LocationRelationType.TIDAL_ROUTE
        ),
        minimum_minutes=None,
        maximum_minutes=None,
        available_start_time="01:00",
        available_end_time="04:00",
        description=(
            "Tideland Path is traversable during "
            "the canonical low-tide window."
        ),
    )

    require(
        route.available_start_time == "01:00",
        "Conditional start time was not preserved.",
    )

    require(
        route.available_end_time == "04:00",
        "Conditional end time was not preserved.",
    )

    pass_test(
        14,
        "conditional accessibility window is supported",
    )

    # --------------------------------------------------------
    # TEST 15 — canonical Tideland ID is representable
    # --------------------------------------------------------

    require(
        route.target_location_id
        == "LOC_BLACKWOOD_TIDELAND_PATH",
        (
            "Canonical Tideland Path ID "
            "was not preserved."
        ),
    )

    pass_test(
        15,
        "canonical Tideland Path identity is supported",
    )

    # --------------------------------------------------------
    # TEST 16 — source and target remain explicit
    # --------------------------------------------------------

    route = build_basic_route()

    require(
        route.source_location_id
        == "LOC_OLD_DOCKS",
        "Travel source was not preserved.",
    )

    require(
        route.target_location_id
        == "LOC_CENTRAL_DEPOT",
        "Travel target was not preserved.",
    )

    pass_test(
        16,
        "travel direction remains explicit",
    )

    # --------------------------------------------------------
    # TEST 17 — reverse direction is independently expressible
    # --------------------------------------------------------

    reverse_route = build_basic_route(
        constraint_id=(
            "TRAVEL_CENTRAL_DEPOT_TO_OLD_DOCKS"
        ),
        source_location_id="LOC_CENTRAL_DEPOT",
        target_location_id="LOC_OLD_DOCKS",
    )

    require(
        reverse_route.source_location_id
        == "LOC_CENTRAL_DEPOT"
        and reverse_route.target_location_id
        == "LOC_OLD_DOCKS",
        (
            "Reverse travel direction cannot "
            "be represented independently."
        ),
    )

    pass_test(
        17,
        "directional travel edges are supported",
    )

    # --------------------------------------------------------
    # TEST 18 — description remains optional
    # --------------------------------------------------------

    route = build_basic_route(
        description=None,
    )

    require(
        route.description is None,
        "Optional travel description was not preserved.",
    )

    pass_test(
        18,
        "travel description remains optional",
    )

    # --------------------------------------------------------
    # TEST 19 — constraint identity remains explicit
    # --------------------------------------------------------

    route = build_basic_route(
        constraint_id="TRAVEL_EXPLICIT_ID",
    )

    require(
        route.constraint_id
        == "TRAVEL_EXPLICIT_ID",
        "Travel constraint ID was not preserved.",
    )

    pass_test(
        19,
        "travel constraint identity remains explicit",
    )

    # --------------------------------------------------------
    # TEST 20 — deterministic serialization
    # --------------------------------------------------------

    route_a = build_basic_route().model_dump(
        mode="json"
    )

    route_b = build_basic_route().model_dump(
        mode="json"
    )

    require(
        route_a == route_b,
        (
            "TravelConstraint serialization "
            "is not deterministic."
        ),
    )

    pass_test(
        20,
        "travel serialization is deterministic",
    )

    # --------------------------------------------------------
    # TEST 21 — provider agnostic
    # --------------------------------------------------------

    field_names = {
        field_name.lower()
        for field_name
        in TravelConstraint.model_fields
    }

    forbidden_provider_fields = {
        "provider",
        "provider_id",
        "model",
        "model_id",
        "openai",
        "elevenlabs",
        "midjourney",
        "runway",
        "kling",
        "veo",
        "digen",
    }

    require(
        field_names.isdisjoint(
            forbidden_provider_fields
        ),
        (
            "TravelConstraint contains "
            "provider-specific fields."
        ),
    )

    pass_test(
        21,
        "travel domain remains provider-agnostic",
    )

    # --------------------------------------------------------
    # TEST 22 — execution state remains separate
    # --------------------------------------------------------

    forbidden_execution_fields = {
        "generation_status",
        "generation_request_id",
        "provider_job_id",
        "output_path",
        "output_image_path",
        "seed",
    }

    require(
        field_names.isdisjoint(
            forbidden_execution_fields
        ),
        (
            "Execution state leaked into "
            "TravelConstraint."
        ),
    )

    pass_test(
        22,
        "travel domain remains separate from execution",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print(
        "BATCH 14B.2-C3-A "
        "GEOGRAPHY & TRAVEL DOMAIN CONTRACT PASSED"
    )
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()