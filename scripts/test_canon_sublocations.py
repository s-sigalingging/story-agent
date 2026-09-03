import json
from pathlib import Path

from pydantic import ValidationError

from app.models.canon import (
    CanonStatus,
    LocationCanon,
)


# ============================================================
# BATCH 14B.2-C2-B — CANONICAL SUBLOCATION REGISTRY
# ============================================================


ROOT = Path(__file__).resolve().parents[1]

LOCATIONS_PATH = (
    ROOT
    / "data"
    / "canon"
    / "oakhaven"
    / "v1"
    / "locations.json"
)


EXPECTED_SUBLOCATION_IDS = [
    "LOC_OPD_BASEMENT_HOLDING_CELLS",
    "LOC_BLACKWOOD_TIDELAND_PATH",
]


EXPECTED_PARENT_MAP = {
    "LOC_OPD_BASEMENT_HOLDING_CELLS":
        "LOC_DISTRICT_POLICE",

    "LOC_BLACKWOOD_TIDELAND_PATH":
        "LOC_BLACKWOOD",
}


EXPECTED_CHILDREN_MAP = {
    "LOC_DISTRICT_POLICE": [
        "LOC_OPD_BASEMENT_HOLDING_CELLS",
    ],

    "LOC_BLACKWOOD": [
        "LOC_BLACKWOOD_TIDELAND_PATH",
    ],
}


FORBIDDEN_CANONICAL_LOCATION_IDS = {
    "LOC_DOCK_EDGE",
    "LOC_JULIAN_S_OFFICE",
    "LOC_STERLING_S_OFFICE",
    "LOC_POLICE_ARCHIVE_ROOM",
    "LOC_ANCHOR_CORNER_TABLE",
    "LOC_DEPOT_CARGO_AREA",
    "LOC_COAL_CAR_4",
    "LOC_BURNING_COAL_CAR",
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


def load_raw_locations() -> list[dict]:
    with LOCATIONS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    require(
        isinstance(data, list),
        "locations.json root must be a list.",
    )

    return data


def load_locations() -> list[LocationCanon]:
    raw_data = load_raw_locations()

    try:
        return [
            LocationCanon.model_validate(item)
            for item in raw_data
        ]
    except ValidationError as exc:
        raise AssertionError(
            "locations.json failed "
            "LocationCanon validation."
        ) from exc


def get_location(
    locations: list[LocationCanon],
    location_id: str,
) -> LocationCanon:
    for location in locations:
        if location.location_id == location_id:
            return location

    raise AssertionError(
        f"Location not found: {location_id}"
    )


def get_sublocations(
    locations: list[LocationCanon],
) -> list[LocationCanon]:
    return [
        location
        for location in locations
        if location.parent_location_id is not None
    ]


def normalized_text(
    values: list[str],
) -> str:
    return " ".join(values).lower()


# ============================================================
# TEST RUNNER
# ============================================================


def main() -> None:
    print()
    print(
        "BATCH 14B.2-C2-B — "
        "CANONICAL SUBLOCATION REGISTRY"
    )
    print("=" * 80)

    # --------------------------------------------------------
    # TEST 1 — registry exists
    # --------------------------------------------------------

    require(
        LOCATIONS_PATH.is_file(),
        "locations.json does not exist.",
    )

    pass_test(
        1,
        "location registry exists",
    )

    # --------------------------------------------------------
    # TEST 2 — all locations validate
    # --------------------------------------------------------

    locations = load_locations()

    require(
        all(
            isinstance(
                location,
                LocationCanon,
            )
            for location in locations
        ),
        "One or more locations failed validation.",
    )

    pass_test(
        2,
        "all locations validate against domain model",
    )

    # --------------------------------------------------------
    # TEST 3 — exactly two canonical sublocations
    # --------------------------------------------------------

    sublocations = get_sublocations(
        locations
    )

    require(
        len(sublocations) == 2,
        (
            "Oakhaven V1 currently requires "
            "exactly two canonical sublocations."
        ),
    )

    pass_test(
        3,
        "exactly two canonical sublocations exist",
    )

    # --------------------------------------------------------
    # TEST 4 — sublocation registry stable
    # --------------------------------------------------------

    sublocation_ids = [
        location.location_id
        for location in sublocations
    ]

    require(
        sublocation_ids
        == EXPECTED_SUBLOCATION_IDS,
        (
            "Canonical sublocation registry "
            "or ordering changed."
        ),
    )

    pass_test(
        4,
        "canonical sublocation registry is stable",
    )

    # --------------------------------------------------------
    # TEST 5 — all sublocations hard canon
    # --------------------------------------------------------

    require(
        all(
            location.status
            == CanonStatus.HARD_CANON
            for location in sublocations
        ),
        (
            "One or more canonical sublocations "
            "are not HARD_CANON."
        ),
    )

    pass_test(
        5,
        "all canonical sublocations remain hard canon",
    )

    # --------------------------------------------------------
    # TEST 6 — every sublocation has canonical parent
    # --------------------------------------------------------

    all_location_ids = {
        location.location_id
        for location in locations
    }

    for location in sublocations:
        require(
            location.parent_location_id
            in all_location_ids,
            (
                f"{location.location_id} references "
                "an unknown parent."
            ),
        )

    pass_test(
        6,
        "every sublocation has registered parent",
    )

    # --------------------------------------------------------
    # TEST 7 — expected parent assignments stable
    # --------------------------------------------------------

    for sublocation_id, parent_id in (
        EXPECTED_PARENT_MAP.items()
    ):
        location = get_location(
            locations,
            sublocation_id,
        )

        require(
            location.parent_location_id
            == parent_id,
            (
                f"{sublocation_id} expected parent "
                f"{parent_id}, found "
                f"{location.parent_location_id}."
            ),
        )

    pass_test(
        7,
        "canonical sublocation parents are stable",
    )

    # --------------------------------------------------------
    # TEST 8 — parent-to-child links stable
    # --------------------------------------------------------

    for parent_id, expected_children in (
        EXPECTED_CHILDREN_MAP.items()
    ):
        parent = get_location(
            locations,
            parent_id,
        )

        require(
            parent.sublocation_ids
            == expected_children,
            (
                f"{parent_id} child registry "
                "changed unexpectedly."
            ),
        )

    pass_test(
        8,
        "parent-to-child links are stable",
    )

    # --------------------------------------------------------
    # TEST 9 — hierarchy is bidirectional
    # --------------------------------------------------------

    for child in sublocations:
        parent = get_location(
            locations,
            child.parent_location_id,
        )

        require(
            child.location_id
            in parent.sublocation_ids,
            (
                f"{child.location_id} points to "
                f"{parent.location_id}, but parent "
                "does not point back to child."
            ),
        )

    pass_test(
        9,
        "parent-child hierarchy is bidirectional",
    )

    # --------------------------------------------------------
    # TEST 10 — children do not claim themselves
    # --------------------------------------------------------

    for location in locations:
        require(
            location.location_id
            not in location.sublocation_ids,
            (
                f"{location.location_id} contains "
                "itself as a child."
            ),
        )

    pass_test(
        10,
        "location hierarchy contains no self-reference",
    )

    # --------------------------------------------------------
    # TEST 11 — sublocations currently remain leaf nodes
    # --------------------------------------------------------

    require(
        all(
            location.sublocation_ids == []
            for location in sublocations
        ),
        (
            "Current Oakhaven V1 sublocations "
            "must remain leaf nodes."
        ),
    )

    pass_test(
        11,
        "canonical sublocations remain leaf nodes",
    )

    # --------------------------------------------------------
    # TEST 12 — OPD holding cells semantic identity
    # --------------------------------------------------------

    cells = get_location(
        locations,
        "LOC_OPD_BASEMENT_HOLDING_CELLS",
    )

    cells_text = (
        cells.description.lower()
        + " "
        + normalized_text(
            cells.narrative_functions
        )
        + " "
        + normalized_text(
            cells.atmosphere_tags
        )
    )

    require(
        "holding" in cells_text,
        (
            "OPD holding cells lost their "
            "detention identity."
        ),
    )

    require(
        (
            "basement" in cells_text
            or "underground" in cells_text
        ),
        (
            "OPD holding cells lost their "
            "underground identity."
        ),
    )

    require(
        "damp" in cells_text,
        (
            "OPD holding cells lost their "
            "damp environmental identity."
        ),
    )

    pass_test(
        12,
        "OPD holding-cell identity is preserved",
    )

    # --------------------------------------------------------
    # TEST 13 — Tideland Path semantic identity
    # --------------------------------------------------------

    tideland = get_location(
        locations,
        "LOC_BLACKWOOD_TIDELAND_PATH",
    )

    tideland_text = (
        tideland.description.lower()
        + " "
        + normalized_text(
            tideland.narrative_functions
        )
        + " "
        + normalized_text(
            tideland.atmosphere_tags
        )
    )

    require(
        "path" in tideland_text,
        (
            "Tideland Path lost its route identity."
        ),
    )

    require(
        (
            "tide" in tideland_text
            or "tidal" in tideland_text
        ),
        (
            "Tideland Path lost its tidal identity."
        ),
    )

    require(
        (
            "time-constrained" in tideland_text
            or "low-tide" in tideland_text
            or "low tide" in tideland_text
        ),
        (
            "Tideland Path lost its constrained "
            "access identity."
        ),
    )

    pass_test(
        13,
        "Tideland Path identity is preserved",
    )

    # --------------------------------------------------------
    # TEST 14 — Tideland Path retains 1930 association
    # --------------------------------------------------------

    require(
        "HIST_1930"
        in tideland.historical_layer_ids,
        (
            "Tideland Path lost its canonical "
            "1930 association."
        ),
    )

    pass_test(
        14,
        "Tideland Path preserves 1930 association",
    )

    # --------------------------------------------------------
    # TEST 15 — OPD cells retain OPD association
    # --------------------------------------------------------

    require(
        "FACTION_OPD"
        in cells.associated_faction_ids,
        (
            "OPD holding cells lost their "
            "OPD association."
        ),
    )

    pass_test(
        15,
        "OPD holding cells preserve faction association",
    )

    # --------------------------------------------------------
    # TEST 16 — legacy scene spaces excluded
    # --------------------------------------------------------

    require(
        FORBIDDEN_CANONICAL_LOCATION_IDS.isdisjoint(
            all_location_ids
        ),
        (
            "A production-only spatial reference "
            "was promoted into World Canon."
        ),
    )

    pass_test(
        16,
        "legacy scene spaces remain outside World Canon",
    )

    # --------------------------------------------------------
    # TEST 17 — Dock Edge specifically excluded
    # --------------------------------------------------------

    require(
        "LOC_DOCK_EDGE"
        not in all_location_ids,
        (
            "Legacy LOC_DOCK_EDGE leaked into "
            "canonical geography."
        ),
    )

    pass_test(
        17,
        "Dock Edge remains production scene space",
    )

    # --------------------------------------------------------
    # TEST 18 — Julian's Office not silently promoted
    # --------------------------------------------------------

    require(
        "LOC_JULIAN_S_OFFICE"
        not in all_location_ids,
        (
            "Julian's Office was promoted without "
            "canonical parent evidence."
        ),
    )

    pass_test(
        18,
        "Julian's Office remains unpromoted",
    )

    # --------------------------------------------------------
    # TEST 19 — mobile coal car excluded
    # --------------------------------------------------------

    require(
        "LOC_COAL_CAR_4"
        not in all_location_ids,
        (
            "Mobile railway car leaked into "
            "fixed world geography."
        ),
    )

    pass_test(
        19,
        "mobile coal car remains outside fixed geography",
    )

    # --------------------------------------------------------
    # TEST 20 — scene state excluded
    # --------------------------------------------------------

    require(
        "LOC_BURNING_COAL_CAR"
        not in all_location_ids,
        (
            "Temporary burning state leaked into "
            "canonical geography."
        ),
    )

    pass_test(
        20,
        "temporary scene state remains outside geography",
    )

    # --------------------------------------------------------
    # TEST 21 — no travel schedule embedded in location
    # --------------------------------------------------------

    raw_data = load_raw_locations()

    serialized_text = json.dumps(
        raw_data,
        ensure_ascii=False,
    ).lower()

    forbidden_travel_fields = [
        '"minimum_minutes"',
        '"maximum_minutes"',
        '"available_start_time"',
        '"available_end_time"',
    ]

    require(
        all(
            field
            not in serialized_text
            for field in forbidden_travel_fields
        ),
        (
            "Travel/accessibility scheduling leaked "
            "into location registry."
        ),
    )

    pass_test(
        21,
        "travel scheduling remains separate from location identity",
    )

    # --------------------------------------------------------
    # TEST 22 — provider agnostic
    # --------------------------------------------------------

    forbidden_provider_terms = [
        "openai",
        "elevenlabs",
        "midjourney",
        "runway",
        "kling",
        "veo",
        "digen",
    ]

    require(
        all(
            provider
            not in serialized_text
            for provider in forbidden_provider_terms
        ),
        (
            "Provider-specific data leaked into "
            "sublocation canon."
        ),
    )

    pass_test(
        22,
        "sublocation registry remains provider-agnostic",
    )

    # --------------------------------------------------------
    # TEST 23 — execution state excluded
    # --------------------------------------------------------

    forbidden_execution_terms = [
        "generation_status",
        "provider_job_id",
        "generation_request_id",
        "output_image_path",
        "seed",
    ]

    require(
        all(
            term
            not in serialized_text
            for term in forbidden_execution_terms
        ),
        (
            "Generation execution state leaked "
            "into sublocation canon."
        ),
    )

    pass_test(
        23,
        "sublocation registry remains separate from execution",
    )

    # --------------------------------------------------------
    # TEST 24 — deterministic classification
    # --------------------------------------------------------

    sublocations_a = [
        location.model_dump(mode="json")
        for location in get_sublocations(
            load_locations()
        )
    ]

    sublocations_b = [
        location.model_dump(mode="json")
        for location in get_sublocations(
            load_locations()
        )
    ]

    require(
        sublocations_a == sublocations_b,
        (
            "Canonical sublocation registry "
            "is not deterministic."
        ),
    )

    pass_test(
        24,
        "canonical sublocation registry is deterministic",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print(
        "BATCH 14B.2-C2-B "
        "CANONICAL SUBLOCATION REGISTRY PASSED"
    )
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()