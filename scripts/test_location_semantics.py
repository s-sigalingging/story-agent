from pydantic import ValidationError

from app.models.canon import (
    CameraStyleCanon,
    CanonDocumentStatus,
    CanonManifest,
    CanonStatus,
    EpisodeStructureCanon,
    FactionCanon,
    HistoricalLayer,
    KnowledgeCanon,
    LocationCanon,
    MysteryCanon,
    OakhavenCanon,
    PerformanceStyleCanon,
    ProductionStyleCanon,
    SoundStyleCanon,
    VisualStyleCanon,
    WorldCanon,
)


# ============================================================
# BATCH 14B.2-C0 — LOCATION SEMANTIC CONTRACT
# ============================================================


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
    except ValidationError:
        return

    raise AssertionError(message)


def build_manifest() -> CanonManifest:
    return CanonManifest(
        universe_id="UNIVERSE_OAKHAVEN",
        universe_name="OAKHAVEN",
        canon_version="1.0",
        document_status=CanonDocumentStatus.FROZEN,
        present_day=2026,
        authority_document=(
            "docs/canon/OAKHAVEN_CANON_V1.md"
        ),
    )


def build_world() -> WorldCanon:
    return WorldCanon(
        world_id="WORLD_OAKHAVEN",
        name="Oakhaven",
        core_statement=(
            "Oakhaven is a coastal city built on "
            "inherited lies."
        ),
        narrative_principle=(
            "No generation knows the complete truth."
        ),
        historical_layers=[
            HistoricalLayer(
                layer_id="HIST_1856",
                year_label="1856",
                name="The Illegal Foundation",
                description="Historical foundation layer.",
                status=CanonStatus.HARD_CANON,
            ),
            HistoricalLayer(
                layer_id="HIST_1930",
                year_label="1930",
                name="The Industrial Cover-Up",
                description="Industrial cover-up layer.",
                status=CanonStatus.HARD_CANON,
            ),
        ],
    )


def build_factions() -> list[FactionCanon]:
    return [
        FactionCanon(
            faction_id="FACTION_OPD",
            name="Oakhaven Police Department",
            description="Police institution.",
        ),
        FactionCanon(
            faction_id="FACTION_WATERFRONT_COLLECTIVE",
            name="The Waterfront Collective",
            description="Waterfront community.",
        ),
    ]


def build_production_style() -> ProductionStyleCanon:
    return ProductionStyleCanon(
        visual=VisualStyleCanon(),
        performance=PerformanceStyleCanon(),
        camera=CameraStyleCanon(),
        sound=SoundStyleCanon(),
        episode_structure=EpisodeStructureCanon(),
    )


def build_bundle(
    locations: list[LocationCanon],
) -> OakhavenCanon:
    return OakhavenCanon(
        manifest=build_manifest(),
        world=build_world(),
        factions=build_factions(),
        characters=[],
        relationships=[],
        locations=locations,
        travel_constraints=[],
        knowledge=KnowledgeCanon(),
        mystery=MysteryCanon(),
        production_style=build_production_style(),
    )


def main() -> None:
    print()
    print(
        "BATCH 14B.2-C0 — LOCATION SEMANTIC CONTRACT"
    )
    print("=" * 72)

    # --------------------------------------------------------
    # TEST 1 — narrative functions supported
    # --------------------------------------------------------

    location = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        narrative_functions=[
            "Opening crime scene",
            "Waterfront investigation",
        ],
    )

    require(
        len(location.narrative_functions) == 2,
        "Narrative functions were not preserved.",
    )

    pass_test(
        1,
        "location narrative functions are supported",
    )

    # --------------------------------------------------------
    # TEST 2 — faction associations supported
    # --------------------------------------------------------

    location = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        associated_faction_ids=[
            "FACTION_WATERFRONT_COLLECTIVE",
        ],
    )

    require(
        location.associated_faction_ids
        == ["FACTION_WATERFRONT_COLLECTIVE"],
        "Faction association was not preserved.",
    )

    pass_test(
        2,
        "location faction associations are supported",
    )

    # --------------------------------------------------------
    # TEST 3 — historical associations supported
    # --------------------------------------------------------

    location = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        historical_layer_ids=[
            "HIST_1930",
        ],
    )

    require(
        location.historical_layer_ids
        == ["HIST_1930"],
        "Historical association was not preserved.",
    )

    pass_test(
        3,
        "location historical associations are supported",
    )

    # --------------------------------------------------------
    # TEST 4 — atmosphere tags supported
    # --------------------------------------------------------

    location = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        atmosphere_tags=[
            "maritime",
            "industrial decay",
            "damp",
        ],
    )

    require(
        "maritime" in location.atmosphere_tags,
        "Atmosphere tag was not preserved.",
    )

    pass_test(
        4,
        "location atmosphere tags are supported",
    )

    # --------------------------------------------------------
    # TEST 5 — unknown faction association rejected
    # --------------------------------------------------------

    location = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        associated_faction_ids=[
            "FACTION_UNKNOWN",
        ],
    )

    require_validation_error(
        lambda: build_bundle(
            locations=[location]
        ),
        "Unknown location faction was accepted.",
    )

    pass_test(
        5,
        "unknown location faction is rejected",
    )

    # --------------------------------------------------------
    # TEST 6 — unknown historical layer rejected
    # --------------------------------------------------------

    location = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        historical_layer_ids=[
            "HIST_UNKNOWN",
        ],
    )

    require_validation_error(
        lambda: build_bundle(
            locations=[location]
        ),
        "Unknown historical layer was accepted.",
    )

    pass_test(
        6,
        "unknown location historical layer is rejected",
    )

    # --------------------------------------------------------
    # TEST 7 — valid semantic graph accepted
    # --------------------------------------------------------

    location = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        associated_faction_ids=[
            "FACTION_WATERFRONT_COLLECTIVE",
        ],
        historical_layer_ids=[
            "HIST_1930",
        ],
        narrative_functions=[
            "Crime scene",
            "Historical investigation",
        ],
        atmosphere_tags=[
            "maritime",
            "industrial decay",
        ],
    )

    bundle = build_bundle(
        locations=[location]
    )

    require(
        len(bundle.locations) == 1,
        "Valid semantic location was lost.",
    )

    pass_test(
        7,
        "valid location semantic graph is accepted",
    )

    # --------------------------------------------------------
    # TEST 8 — semantics remain distinct from travel
    # --------------------------------------------------------

    serialized = location.model_dump(
        mode="json"
    )

    forbidden_travel_fields = [
        "minimum_minutes",
        "maximum_minutes",
        "available_start_time",
        "available_end_time",
        "relation_type",
    ]

    for field_name in forbidden_travel_fields:
        require(
            field_name not in serialized,
            (
                "Travel semantics leaked into "
                f"LocationCanon: {field_name}"
            ),
        )

    pass_test(
        8,
        "location semantics remain separate from travel",
    )

    # --------------------------------------------------------
    # TEST 9 — semantics remain provider-agnostic
    # --------------------------------------------------------

    serialized_text = str(
        serialized
    ).lower()

    forbidden_provider_terms = [
        "openai",
        "gemini",
        "elevenlabs",
        "runway",
        "kling",
        "midjourney",
    ]

    for provider in forbidden_provider_terms:
        require(
            provider not in serialized_text,
            (
                "Provider dependency leaked into "
                f"location semantics: {provider}"
            ),
        )

    pass_test(
        9,
        "location semantics remain provider-agnostic",
    )

    # --------------------------------------------------------
    # TEST 10 — optional semantics remain optional
    # --------------------------------------------------------

    minimal_location = LocationCanon(
        location_id="LOC_MINIMAL",
        name="Minimal Location",
        description="Minimal valid location.",
    )

    require(
        minimal_location.narrative_functions == [],
        "Narrative functions should default empty.",
    )

    require(
        minimal_location.associated_faction_ids == [],
        "Faction associations should default empty.",
    )

    require(
        minimal_location.historical_layer_ids == [],
        "Historical associations should default empty.",
    )

    require(
        minimal_location.atmosphere_tags == [],
        "Atmosphere tags should default empty.",
    )

    pass_test(
        10,
        "location semantic fields remain optional",
    )

    # --------------------------------------------------------
    # TEST 11 — serialization deterministic
    # --------------------------------------------------------

    location_a = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        narrative_functions=[
            "Crime scene",
        ],
        associated_faction_ids=[
            "FACTION_WATERFRONT_COLLECTIVE",
        ],
        historical_layer_ids=[
            "HIST_1930",
        ],
        atmosphere_tags=[
            "maritime",
        ],
    )

    location_b = LocationCanon(
        location_id="LOC_OLD_DOCKS",
        name="Old Docks",
        description="Historic waterfront district.",
        narrative_functions=[
            "Crime scene",
        ],
        associated_faction_ids=[
            "FACTION_WATERFRONT_COLLECTIVE",
        ],
        historical_layer_ids=[
            "HIST_1930",
        ],
        atmosphere_tags=[
            "maritime",
        ],
    )

    require(
        location_a.model_dump(mode="json")
        == location_b.model_dump(mode="json"),
        (
            "Equivalent location semantics "
            "serialize differently."
        ),
    )

    pass_test(
        11,
        "location semantic serialization is deterministic",
    )

    # --------------------------------------------------------
    # TEST 12 — no execution state leaked
    # --------------------------------------------------------

    forbidden_execution_fields = [
        "generation_status",
        "provider_job_id",
        "output_image_path",
        "prompt",
        "seed",
    ]

    for field_name in forbidden_execution_fields:
        require(
            field_name not in serialized,
            (
                "Production execution field leaked "
                f"into location canon: {field_name}"
            ),
        )

    pass_test(
        12,
        "location canon remains separate from execution state",
    )

    print()
    print("=" * 72)
    print(
        "BATCH 14B.2-C0 LOCATION SEMANTIC CONTRACT PASSED"
    )
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()