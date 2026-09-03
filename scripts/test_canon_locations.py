import json
from pathlib import Path

from pydantic import ValidationError

from app.models.canon import (
    CanonStatus,
    LocationCanon,
)


# ============================================================
# BATCH 14B.2-C1-R — PRIMARY LOCATION REGISTRY REGRESSION
# Hierarchy-aware regression for the ten Oakhaven root locations.
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


EXPECTED_PRIMARY_LOCATION_IDS = [
    "LOC_PIKE_HILL_MANOR",
    "LOC_ST_JUDES",
    "LOC_CITY_ARCHIVES",
    "LOC_DISTRICT_POLICE",
    "LOC_THE_ANCHOR",
    "LOC_CENTRAL_DEPOT",
    "LOC_TENEMENTS",
    "LOC_BLACKWOOD",
    "LOC_OLD_DOCKS",
    "LOC_FISH_MARKET_ALLEY",
]


EXPECTED_PRIMARY_LOCATION_NAMES = {
    "LOC_PIKE_HILL_MANOR":
        "Pike Hill Manor Estate",

    "LOC_ST_JUDES":
        "St. Jude's Hospital",

    "LOC_CITY_ARCHIVES":
        "City Archives",

    "LOC_DISTRICT_POLICE":
        "District Police",

    "LOC_THE_ANCHOR":
        "The Anchor",

    "LOC_CENTRAL_DEPOT":
        "Central Depot & Train Station",

    "LOC_TENEMENTS":
        "The Tenements",

    "LOC_BLACKWOOD":
        "Blackwood Cemetery & Salt Marsh",

    "LOC_OLD_DOCKS":
        "The Old Docks & Warehouses",

    "LOC_FISH_MARKET_ALLEY":
        "Fish Market Alley",
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


def get_primary_locations(
    locations: list[LocationCanon],
) -> list[LocationCanon]:
    return [
        location
        for location in locations
        if location.parent_location_id is None
    ]


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
        "BATCH 14B.2-C1-R — "
        "PRIMARY LOCATION REGISTRY REGRESSION"
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
    # TEST 2 — registry is valid JSON data
    # --------------------------------------------------------

    raw_data = load_raw_locations()

    require(
        isinstance(raw_data, list),
        "Location registry is not a list.",
    )

    pass_test(
        2,
        "location registry is valid JSON data",
    )

    # --------------------------------------------------------
    # TEST 3 — every registered location validates
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
        3,
        "all registered locations validate against domain model",
    )

    # --------------------------------------------------------
    # TEST 4 — primary locations are derived from hierarchy
    # --------------------------------------------------------

    primary_locations = get_primary_locations(
        locations
    )

    require(
        all(
            location.parent_location_id is None
            for location in primary_locations
        ),
        (
            "Primary-location derivation returned "
            "a child location."
        ),
    )

    pass_test(
        4,
        "primary locations are derived from hierarchy",
    )

    # --------------------------------------------------------
    # TEST 5 — exactly ten primary locations remain
    # --------------------------------------------------------

    require(
        len(primary_locations) == 10,
        (
            "Oakhaven V1 must contain exactly "
            "ten primary/root locations."
        ),
    )

    pass_test(
        5,
        "exactly ten primary locations remain",
    )

    # --------------------------------------------------------
    # TEST 6 — all registered IDs remain unique
    # --------------------------------------------------------

    all_location_ids = [
        location.location_id
        for location in locations
    ]

    require(
        len(all_location_ids)
        == len(set(all_location_ids)),
        "Duplicate canonical location IDs detected.",
    )

    pass_test(
        6,
        "all canonical location IDs are unique",
    )

    # --------------------------------------------------------
    # TEST 7 — primary registry IDs remain stable
    # --------------------------------------------------------

    primary_ids = [
        location.location_id
        for location in primary_locations
    ]

    require(
        primary_ids
        == EXPECTED_PRIMARY_LOCATION_IDS,
        (
            "Primary location registry or "
            "ordering changed."
        ),
    )

    pass_test(
        7,
        "primary location registry remains stable",
    )

    # --------------------------------------------------------
    # TEST 8 — primary names remain stable
    # --------------------------------------------------------

    for location in primary_locations:
        expected_name = (
            EXPECTED_PRIMARY_LOCATION_NAMES[
                location.location_id
            ]
        )

        require(
            location.name == expected_name,
            (
                "Unexpected canonical name for "
                f"{location.location_id}."
            ),
        )

    pass_test(
        8,
        "primary location names remain stable",
    )

    # --------------------------------------------------------
    # TEST 9 — all primary locations remain hard canon
    # --------------------------------------------------------

    require(
        all(
            location.status
            == CanonStatus.HARD_CANON
            for location in primary_locations
        ),
        (
            "One or more primary locations "
            "are not HARD_CANON."
        ),
    )

    pass_test(
        9,
        "all primary locations remain hard canon",
    )

    # --------------------------------------------------------
    # TEST 10 — primary locations remain root nodes
    # --------------------------------------------------------

    require(
        all(
            location.parent_location_id is None
            for location in primary_locations
        ),
        (
            "A primary location unexpectedly "
            "has a parent."
        ),
    )

    pass_test(
        10,
        "primary locations remain root nodes",
    )

    # --------------------------------------------------------
    # TEST 11 — sublocations may now exist
    # --------------------------------------------------------

    child_locations = [
        location
        for location in locations
        if location.parent_location_id is not None
    ]

    require(
        len(child_locations) >= 1,
        (
            "Hierarchy-aware registry expected "
            "at least one canonical sublocation."
        ),
    )

    pass_test(
        11,
        "canonical sublocations can coexist with primary registry",
    )

    # --------------------------------------------------------
    # TEST 12 — every primary location has narrative function
    # --------------------------------------------------------

    require(
        all(
            len(location.narrative_functions) > 0
            for location in primary_locations
        ),
        (
            "One or more primary locations have "
            "no narrative function."
        ),
    )

    pass_test(
        12,
        "all primary locations preserve narrative function",
    )

    # --------------------------------------------------------
    # TEST 13 — every primary location has atmosphere
    # --------------------------------------------------------

    require(
        all(
            len(location.atmosphere_tags) > 0
            for location in primary_locations
        ),
        (
            "One or more primary locations have "
            "no atmosphere identity."
        ),
    )

    pass_test(
        13,
        "all primary locations preserve atmosphere identity",
    )

    # --------------------------------------------------------
    # TEST 14 — every primary location has visual identity
    # --------------------------------------------------------

    require(
        all(
            location.visual_identity is not None
            for location in primary_locations
        ),
        (
            "One or more primary locations have "
            "no visual identity."
        ),
    )

    pass_test(
        14,
        "all primary locations preserve visual identity",
    )

    # --------------------------------------------------------
    # TEST 15 — Old Docks preserves PL-1930 role
    # --------------------------------------------------------

    docks = get_location(
        primary_locations,
        "LOC_OLD_DOCKS",
    )

    docks_text = (
        docks.description.lower()
        + " "
        + normalized_text(
            docks.narrative_functions
        )
    )

    require(
        "pl-1930" in docks_text,
        (
            "Old Docks no longer preserves its "
            "PL-1930 narrative association."
        ),
    )

    require(
        "HIST_1930"
        in docks.historical_layer_ids,
        (
            "Old Docks lost its 1930 "
            "historical association."
        ),
    )

    pass_test(
        15,
        "Old Docks preserves PL-1930 association",
    )

    # --------------------------------------------------------
    # TEST 16 — City Archives preserves documentary role
    # --------------------------------------------------------

    archives = get_location(
        primary_locations,
        "LOC_CITY_ARCHIVES",
    )

    archives_text = (
        archives.description.lower()
        + " "
        + normalized_text(
            archives.narrative_functions
        )
    )

    require(
        (
            "document"
            in archives_text
            or "archive"
            in archives_text
        ),
        "City Archives lost documentary role.",
    )

    require(
        (
            "fragment"
            in archives_text
            or "manipulat"
            in archives_text
            or "falsif"
            in archives_text
        ),
        (
            "City Archives lost its unreliable "
            "record semantics."
        ),
    )

    pass_test(
        16,
        "City Archives preserves documentary role",
    )

    # --------------------------------------------------------
    # TEST 17 — Tenements preserves oral memory
    # --------------------------------------------------------

    tenements = get_location(
        primary_locations,
        "LOC_TENEMENTS",
    )

    tenements_text = (
        tenements.description.lower()
        + " "
        + normalized_text(
            tenements.narrative_functions
        )
    )

    require(
        (
            "oral history"
            in tenements_text
            or "collective memory"
            in tenements_text
        ),
        (
            "Tenements lost its community "
            "memory role."
        ),
    )

    require(
        "HIST_1930"
        in tenements.historical_layer_ids,
        (
            "Tenements lost its 1930 "
            "historical association."
        ),
    )

    pass_test(
        17,
        "Tenements preserves oral-memory role",
    )

    # --------------------------------------------------------
    # TEST 18 — Blackwood preserves evidence role
    # --------------------------------------------------------

    blackwood = get_location(
        primary_locations,
        "LOC_BLACKWOOD",
    )

    blackwood_text = (
        blackwood.description.lower()
        + " "
        + normalized_text(
            blackwood.narrative_functions
        )
    )

    require(
        "1930" in blackwood_text,
        (
            "Blackwood lost its connection "
            "to the 1930 tragedy."
        ),
    )

    require(
        "HIST_1930"
        in blackwood.historical_layer_ids,
        (
            "Blackwood lost its canonical "
            "1930 historical layer."
        ),
    )

    require(
        (
            "tide"
            in blackwood_text
            or "tide-dependent"
            in blackwood.atmosphere_tags
        ),
        (
            "Blackwood lost its tide-dependent "
            "environment identity."
        ),
    )

    pass_test(
        18,
        "Blackwood preserves historical evidence role",
    )

    # --------------------------------------------------------
    # TEST 19 — The Anchor remains neutral ground
    # --------------------------------------------------------

    anchor = get_location(
        primary_locations,
        "LOC_THE_ANCHOR",
    )

    anchor_text = (
        anchor.description.lower()
        + " "
        + normalized_text(
            anchor.narrative_functions
        )
    )

    require(
        "neutral" in anchor_text,
        (
            "The Anchor no longer preserves "
            "its neutral-ground role."
        ),
    )

    require(
        (
            "information"
            in anchor_text
            or "testimony"
            in anchor_text
        ),
        (
            "The Anchor lost its information "
            "exchange role."
        ),
    )

    pass_test(
        19,
        "The Anchor remains neutral ground",
    )

    # --------------------------------------------------------
    # TEST 20 — provider agnostic
    # --------------------------------------------------------

    serialized_text = json.dumps(
        raw_data,
        ensure_ascii=False,
    ).lower()

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
            "canonical location registry."
        ),
    )

    pass_test(
        20,
        "location registry remains provider-agnostic",
    )

    # --------------------------------------------------------
    # TEST 21 — execution state remains separate
    # --------------------------------------------------------

    forbidden_execution_terms = [
        "generation_status",
        "provider_job_id",
        "output_image_path",
        "generation_request_id",
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
            "into location canon."
        ),
    )

    pass_test(
        21,
        "location registry remains separate from execution",
    )

    # --------------------------------------------------------
    # TEST 22 — deterministic serialization
    # --------------------------------------------------------

    serialized_a = [
        location.model_dump(
            mode="json"
        )
        for location in load_locations()
    ]

    serialized_b = [
        location.model_dump(
            mode="json"
        )
        for location in load_locations()
    ]

    require(
        serialized_a == serialized_b,
        (
            "Location registry serialization "
            "is not deterministic."
        ),
    )

    pass_test(
        22,
        "hierarchy-aware location registry is deterministic",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print(
        "BATCH 14B.2-C1-R "
        "PRIMARY LOCATION REGISTRY REGRESSION PASSED"
    )
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()