from pydantic import ValidationError

from app.models.canon import (
    AudienceKnowledge,
    AudienceKnowledgeState,
    CameraStyleCanon,
    CanonFact,
    CanonManifest,
    CanonStatus,
    CanonSourceReference,
    CharacterCanon,
    CharacterIdentity,
    CharacterKnowledge,
    CharacterVoiceIdentity,
    ClueLevel,
    ClueRule,
    EpisodeStructureCanon,
    FactionCanon,
    HistoricalLayer,
    KnowledgeCanon,
    KnowledgeState,
    LocationCanon,
    LocationRelationType,
    MysteryCanon,
    MysteryRule,
    OakhavenCanon,
    PerformanceStyleCanon,
    ProductionStyleCanon,
    RelationshipCanon,
    RelationshipType,
    ShotNarrativeType,
    SoundStyleCanon,
    TravelConstraint,
    TruthValue,
    VisualStyleCanon,
    WorldCanon,
    WorldRule,
    CanonDocumentStatus,
)


# ============================================================
# BATCH 14B.1-A — CANON DOMAIN MODEL CONTRACT
# ============================================================


def pass_test(number: int, description: str) -> None:
    print(
        f"TEST {number} — {description} → PASSED"
    )


def require(condition: bool, message: str) -> None:
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


# ============================================================
# FIXTURE BUILDERS
# ============================================================


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
        sources=[
            CanonSourceReference(
                source_id="SOURCE_CANON_V1",
                path=(
                    "docs/canon/"
                    "OAKHAVEN_CANON_V1.md"
                ),
                role="HUMAN_READABLE_AUTHORITY",
                authoritative=True,
            )
        ],
        derived_files=[
            "data/canon/oakhaven/v1/manifest.json",
        ],
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
            "Every generation inherits only fragments "
            "of the historical truth."
        ),
        genres=[
            "Historical mystery",
            "Crime mystery",
            "Noir",
            "Investigative drama",
        ],
        historical_layers=[
            HistoricalLayer(
                layer_id="HIST_1856",
                year_label="1856",
                name="The Illegal Foundation",
                description=(
                    "The deepest currently established "
                    "historical layer."
                ),
                status=CanonStatus.HARD_CANON,
                established_truths=[
                    (
                        "Land belonging to an existing "
                        "fishing community was unlawfully "
                        "seized."
                    )
                ],
            )
        ],
        rules=[
            WorldRule(
                rule_id="RULE_NO_SUPERNATURAL",
                name="No Supernatural Rule",
                description=(
                    "Apparently supernatural events must "
                    "have material explanations."
                ),
                prohibited_interpretations=[
                    "Literal supernatural causation"
                ],
            )
        ],
    )


def build_faction() -> FactionCanon:
    return FactionCanon(
        faction_id="FACTION_OPD",
        name="Oakhaven Police Department",
        description=(
            "Institutional police organization operating "
            "within Oakhaven."
        ),
        motivations=[
            "Maintain civic order",
        ],
        knowledge_limits=[
            (
                "The organization does not automatically "
                "know the complete historical truth."
            )
        ],
    )


def build_character(
    character_id: str = "CHAR_JULIAN_VANCE",
    name: str = "Detective Julian Vance",
) -> CharacterCanon:
    return CharacterCanon(
        character_id=character_id,
        identity=CharacterIdentity(
            canonical_name=name,
        ),
        status=CanonStatus.HARD_CANON,
        faction_ids=[
            "FACTION_OPD",
        ],
        primary_location_ids=[
            "LOC_DISTRICT_POLICE",
        ],
        role="INVESTIGATOR",
        motivations=[
            "Discover the truth",
        ],
        blind_spots=[
            "Overtrusts written records",
        ],
        knowledge_limits=[
            (
                "Does not initially know the complete "
                "truth about 1856."
            )
        ],
    )


def build_location(
    location_id: str = "LOC_DISTRICT_POLICE",
    name: str = "District Police",
) -> LocationCanon:
    return LocationCanon(
        location_id=location_id,
        name=name,
        description=(
            "Institutional center of the Oakhaven "
            "Police Department."
        ),
    )


def build_fact(
    fact_id: str = "FACT_1856_ILLEGAL_FOUNDATION",
) -> CanonFact:
    return CanonFact(
        fact_id=fact_id,
        statement=(
            "The foundation of modern Oakhaven involved "
            "unlawful land seizure."
        ),
        truth_value=TruthValue.TRUE,
        status=CanonStatus.HARD_CANON,
        historical_layer_id="HIST_1856",
    )


def build_knowledge() -> KnowledgeCanon:
    return KnowledgeCanon(
        facts=[
            build_fact(),
        ],
        character_knowledge=[
            CharacterKnowledge(
                character_id="CHAR_JULIAN_VANCE",
                fact_id="FACT_1856_ILLEGAL_FOUNDATION",
                state=KnowledgeState.UNKNOWN,
            )
        ],
        audience_knowledge=[
            AudienceKnowledge(
                fact_id="FACT_1856_ILLEGAL_FOUNDATION",
                state=(
                    AudienceKnowledgeState.NOT_REVEALED
                ),
            )
        ],
    )


def build_mystery() -> MysteryCanon:
    return MysteryCanon(
        clue_rules=[
            ClueRule(
                rule_id="CLUE_VISUAL",
                level=ClueLevel.VISUAL,
                name="Visual Evidence",
                description=(
                    "Visible evidence creates a question."
                ),
                requirements=[
                    "Must be observable",
                ],
            )
        ],
        mystery_rules=[
            MysteryRule(
                rule_id="RULE_FAIR_PLAY",
                name="Fair Play",
                description=(
                    "Evidence required for resolution "
                    "must be available to the audience."
                ),
                prohibited_patterns=[
                    "Unsupported resolution",
                ],
            )
        ],
    )


def build_production_style() -> ProductionStyleCanon:
    return ProductionStyleCanon(
        visual=VisualStyleCanon(
            rendering_language=[
                "cinematic stylized illustration",
                "grounded human anatomy",
            ],
            prohibited_styles=[
                "hyper-realistic photography",
                "anime rendering",
            ],
        ),
        performance=PerformanceStyleCanon(
            preferred_motion=[
                "subtle eye movement",
                "minor posture change",
            ],
            prohibited_motion=[
                "unnecessary dramatic head turns",
            ],
            lip_sync_required_by_default=False,
        ),
        camera=CameraStyleCanon(
            preferred_movements=[
                "static composition",
                "slow push",
            ],
            prohibited_movements=[
                "rapid zoom",
                "whip pan",
            ],
        ),
        sound=SoundStyleCanon(
            vocabulary=[
                "distant waves",
                "wooden pier creaks",
                "distant railway metal",
            ],
            contextual_selection_required=True,
        ),
        episode_structure=EpisodeStructureCanon(),
    )


def build_bundle(
    characters: list[CharacterCanon] | None = None,
    factions: list[FactionCanon] | None = None,
    locations: list[LocationCanon] | None = None,
    knowledge: KnowledgeCanon | None = None,
) -> OakhavenCanon:
    return OakhavenCanon(
        manifest=build_manifest(),
        world=build_world(),
        factions=(
            factions
            if factions is not None
            else [build_faction()]
        ),
        characters=(
            characters
            if characters is not None
            else [build_character()]
        ),
        relationships=[],
        locations=(
            locations
            if locations is not None
            else [build_location()]
        ),
        travel_constraints=[],
        knowledge=(
            knowledge
            if knowledge is not None
            else build_knowledge()
        ),
        mystery=build_mystery(),
        production_style=build_production_style(),
    )


# ============================================================
# TESTS
# ============================================================


def main() -> None:
    print()
    print(
        "BATCH 14B.1-A — CANON DOMAIN MODEL CONTRACT"
    )
    print("=" * 68)

    # --------------------------------------------------------
    # TEST 1
    # Frozen canon requires an authority document.
    # --------------------------------------------------------

    require_validation_error(
        lambda: CanonManifest(
            universe_id="UNIVERSE_OAKHAVEN",
            universe_name="OAKHAVEN",
            canon_version="1.0",
            document_status=(
                CanonDocumentStatus.FROZEN
            ),
            present_day=2026,
            authority_document="",
        ),
        (
            "Frozen canon accepted an empty "
            "authority document."
        ),
    )

    pass_test(
        1,
        "frozen canon requires authority document",
    )

    # --------------------------------------------------------
    # TEST 2
    # Valid frozen manifest is supported.
    # --------------------------------------------------------

    manifest = build_manifest()

    require(
        manifest.document_status
        == CanonDocumentStatus.FROZEN,
        "Frozen manifest did not preserve status.",
    )

    require(
        manifest.authority_document
        == "docs/canon/OAKHAVEN_CANON_V1.md",
        "Authority document was not preserved.",
    )

    pass_test(
        2,
        "frozen canon manifest is supported",
    )

    # --------------------------------------------------------
    # TEST 3
    # OPEN world truth must be representable.
    # --------------------------------------------------------

    open_fact = CanonFact(
        fact_id="FACT_JULIAN_FATHER_GUILT",
        statement=(
            "Julian's father participated in the "
            "historical crimes."
        ),
        truth_value=TruthValue.OPEN,
        status=CanonStatus.OPEN,
    )

    require(
        open_fact.truth_value == TruthValue.OPEN,
        "OPEN truth value was not preserved.",
    )

    require(
        open_fact.status == CanonStatus.OPEN,
        "OPEN canon status was not preserved.",
    )

    pass_test(
        3,
        "OPEN world truth is supported",
    )

    # --------------------------------------------------------
    # TEST 4
    # World truth and character knowledge are separate.
    # --------------------------------------------------------

    fact = build_fact()

    julian_knowledge = CharacterKnowledge(
        character_id="CHAR_JULIAN_VANCE",
        fact_id=fact.fact_id,
        state=KnowledgeState.UNKNOWN,
    )

    require(
        fact.truth_value == TruthValue.TRUE,
        "World truth fixture must be TRUE.",
    )

    require(
        julian_knowledge.state
        == KnowledgeState.UNKNOWN,
        (
            "Character knowledge was incorrectly derived "
            "from world truth."
        ),
    )

    pass_test(
        4,
        "character knowledge is separate from world truth",
    )

    # --------------------------------------------------------
    # TEST 5
    # False belief must be representable independently.
    # --------------------------------------------------------

    alistair_belief = CharacterKnowledge(
        character_id="CHAR_ALISTAIR_PIKE",
        fact_id="FACT_1856_ILLEGAL_FOUNDATION",
        state=KnowledgeState.FALSE_BELIEF,
        belief_statement=(
            "The Pike family's historical ownership "
            "claims were legitimate."
        ),
    )

    require(
        alistair_belief.state
        == KnowledgeState.FALSE_BELIEF,
        "FALSE_BELIEF state was not preserved.",
    )

    require(
        alistair_belief.belief_statement is not None,
        "False belief lost its belief statement.",
    )

    pass_test(
        5,
        "false character beliefs are supported",
    )

    # --------------------------------------------------------
    # TEST 6
    # Audience knowledge remains independent.
    # --------------------------------------------------------

    audience = AudienceKnowledge(
        fact_id="FACT_1856_ILLEGAL_FOUNDATION",
        state=(
            AudienceKnowledgeState.PARTIALLY_REVEALED
        ),
        source_episode_id="EP004",
        source_scene_number=4,
    )

    require(
        audience.state
        == AudienceKnowledgeState.PARTIALLY_REVEALED,
        "Audience knowledge state was not preserved.",
    )

    require(
        audience.source_episode_id == "EP004",
        "Audience reveal lineage was not preserved.",
    )

    pass_test(
        6,
        "audience knowledge is independently tracked",
    )

    # --------------------------------------------------------
    # TEST 7
    # Provider voice references cannot become canonical.
    # --------------------------------------------------------

    require_validation_error(
        lambda: CharacterVoiceIdentity(
            characteristics=[
                "deep",
                "controlled",
                "mature",
            ],
            provider_specific_reference=(
                "ELEVENLABS_VOICE_X"
            ),
            provider_reference_is_canonical=True,
        ),
        (
            "Provider-specific voice reference was allowed "
            "to become canonical."
        ),
    )

    pass_test(
        7,
        "provider voice references cannot become canon",
    )

    # --------------------------------------------------------
    # TEST 8
    # Provider references are allowed as non-canonical data.
    # --------------------------------------------------------

    voice = CharacterVoiceIdentity(
        characteristics=[
            "deep",
            "controlled",
            "institutional authority",
        ],
        provider_specific_reference=(
            "LEGACY_PROVIDER_REFERENCE"
        ),
        provider_reference_is_canonical=False,
    )

    require(
        voice.provider_specific_reference
        == "LEGACY_PROVIDER_REFERENCE",
        "Non-canonical provider reference was lost.",
    )

    require(
        voice.provider_reference_is_canonical is False,
        (
            "Provider reference unexpectedly became "
            "canonical."
        ),
    )

    pass_test(
        8,
        "non-canonical provider references are supported",
    )

    # --------------------------------------------------------
    # TEST 9
    # Duplicate character IDs rejected.
    # --------------------------------------------------------

    duplicate_characters = [
        build_character(),
        build_character(
            character_id="CHAR_JULIAN_VANCE",
            name="Duplicate Julian",
        ),
    ]

    require_validation_error(
        lambda: build_bundle(
            characters=duplicate_characters
        ),
        "Duplicate character IDs were accepted.",
    )

    pass_test(
        9,
        "duplicate character IDs are rejected",
    )

    # --------------------------------------------------------
    # TEST 10
    # Duplicate faction IDs rejected.
    # --------------------------------------------------------

    duplicate_factions = [
        build_faction(),
        FactionCanon(
            faction_id="FACTION_OPD",
            name="Duplicate OPD",
            description="Invalid duplicate faction.",
        ),
    ]

    require_validation_error(
        lambda: build_bundle(
            factions=duplicate_factions
        ),
        "Duplicate faction IDs were accepted.",
    )

    pass_test(
        10,
        "duplicate faction IDs are rejected",
    )

    # --------------------------------------------------------
    # TEST 11
    # Duplicate location IDs rejected.
    # --------------------------------------------------------

    duplicate_locations = [
        build_location(),
        build_location(
            location_id="LOC_DISTRICT_POLICE",
            name="Duplicate Police Location",
        ),
    ]

    require_validation_error(
        lambda: build_bundle(
            locations=duplicate_locations
        ),
        "Duplicate location IDs were accepted.",
    )

    pass_test(
        11,
        "duplicate location IDs are rejected",
    )

    # --------------------------------------------------------
    # TEST 12
    # Duplicate fact IDs rejected.
    # --------------------------------------------------------

    duplicate_knowledge = KnowledgeCanon(
        facts=[
            build_fact(),
            build_fact(
                fact_id="FACT_1856_ILLEGAL_FOUNDATION"
            ),
        ],
    )

    require_validation_error(
        lambda: build_bundle(
            knowledge=duplicate_knowledge
        ),
        "Duplicate fact IDs were accepted.",
    )

    pass_test(
        12,
        "duplicate fact IDs are rejected",
    )

    # --------------------------------------------------------
    # TEST 13
    # Self relationships rejected.
    # --------------------------------------------------------

    require_validation_error(
        lambda: RelationshipCanon(
            relationship_id="REL_INVALID_SELF",
            source_character_id="CHAR_JULIAN_VANCE",
            target_character_id="CHAR_JULIAN_VANCE",
            relationship_type=RelationshipType.ALLY,
        ),
        "Self relationship was accepted.",
    )

    pass_test(
        13,
        "self relationships are rejected",
    )

    # --------------------------------------------------------
    # TEST 14
    # Valid relationships remain explicit.
    # --------------------------------------------------------

    relationship = RelationshipCanon(
        relationship_id="REL_JULIAN_REN_ALLY",
        source_character_id="CHAR_JULIAN_VANCE",
        target_character_id="CHAR_CLARA_REN_RENDRA",
        relationship_type=RelationshipType.ALLY,
        description="Investigative allies.",
        directional=False,
    )

    require(
        relationship.relationship_type
        == RelationshipType.ALLY,
        "Relationship type was not preserved.",
    )

    require(
        relationship.source_character_id
        != relationship.target_character_id,
        "Valid relationship became self-referential.",
    )

    pass_test(
        14,
        "character relationships remain explicit",
    )

    # --------------------------------------------------------
    # TEST 15
    # Invalid travel duration rejected.
    # --------------------------------------------------------

    require_validation_error(
        lambda: TravelConstraint(
            constraint_id="TRAVEL_INVALID",
            source_location_id="LOC_PIKE_HILL_MANOR",
            target_location_id="LOC_OLD_DOCKS",
            relation_type=(
                LocationRelationType.ROAD_ROUTE
            ),
            minimum_minutes=40,
            maximum_minutes=30,
        ),
        (
            "Travel constraint accepted minimum duration "
            "greater than maximum duration."
        ),
    )

    pass_test(
        15,
        "invalid travel duration is rejected",
    )

    # --------------------------------------------------------
    # TEST 16
    # Canonical travel windows are representable.
    # --------------------------------------------------------

    tidal_route = TravelConstraint(
        constraint_id="TRAVEL_BLACKWOOD_TIDAL",
        source_location_id="LOC_BLACKWOOD",
        target_location_id="LOC_SALT_MARSH_PATH",
        relation_type=LocationRelationType.TIDAL_ROUTE,
        available_start_time="01:00",
        available_end_time="04:00",
        description=(
            "Tideland route available during low tide."
        ),
    )

    require(
        tidal_route.available_start_time == "01:00",
        "Tidal route start time was not preserved.",
    )

    require(
        tidal_route.available_end_time == "04:00",
        "Tidal route end time was not preserved.",
    )

    pass_test(
        16,
        "conditional travel windows are supported",
    )

    # --------------------------------------------------------
    # TEST 17
    # Non-dialogue storytelling is first-class.
    # --------------------------------------------------------

    structure = EpisodeStructureCanon()

    require(
        structure.non_dialogue_storytelling_allowed
        is True,
        (
            "Non-dialogue storytelling must be enabled "
            "by default."
        ),
    )

    require(
        ShotNarrativeType.ATMOSPHERIC
        in structure.allowed_shot_types,
        "ATMOSPHERIC shot type is missing.",
    )

    require(
        ShotNarrativeType.TRANSITION
        in structure.allowed_shot_types,
        "TRANSITION shot type is missing.",
    )

    require(
        ShotNarrativeType.ESTABLISHING
        in structure.allowed_shot_types,
        "ESTABLISHING shot type is missing.",
    )

    require(
        ShotNarrativeType.REACTION
        in structure.allowed_shot_types,
        "REACTION shot type is missing.",
    )

    pass_test(
        17,
        "non-dialogue storytelling is first-class",
    )

    # --------------------------------------------------------
    # TEST 18
    # Episode duration contract enforced.
    # --------------------------------------------------------

    require_validation_error(
        lambda: EpisodeStructureCanon(
            target_minimum_seconds=60,
            target_maximum_seconds=45,
        ),
        "Invalid episode duration range was accepted.",
    )

    valid_structure = EpisodeStructureCanon(
        target_minimum_seconds=45,
        target_maximum_seconds=60,
    )

    require(
        valid_structure.target_minimum_seconds == 45,
        "Minimum episode duration was not preserved.",
    )

    require(
        valid_structure.target_maximum_seconds == 60,
        "Maximum episode duration was not preserved.",
    )

    pass_test(
        18,
        "episode duration contract is enforced",
    )

    # --------------------------------------------------------
    # TEST 19
    # Complete root canon bundle can be instantiated.
    # --------------------------------------------------------

    bundle = build_bundle()

    require(
        bundle.manifest.universe_name == "OAKHAVEN",
        "Root canon bundle lost universe identity.",
    )

    require(
        len(bundle.characters) == 1,
        "Root bundle character registry is invalid.",
    )

    require(
        len(bundle.locations) == 1,
        "Root bundle location registry is invalid.",
    )

    require(
        len(bundle.knowledge.facts) == 1,
        "Root bundle knowledge registry is invalid.",
    )

    pass_test(
        19,
        "root canon bundle can be instantiated",
    )

    # --------------------------------------------------------
    # TEST 20
    # Model serialization is deterministic.
    # --------------------------------------------------------

    bundle_a = build_bundle()
    bundle_b = build_bundle()

    dump_a = bundle_a.model_dump(
        mode="json"
    )

    dump_b = bundle_b.model_dump(
        mode="json"
    )

    require(
        dump_a == dump_b,
        "Equivalent canon bundles serialize differently.",
    )

    pass_test(
        20,
        "canon serialization is deterministic",
    )

    # --------------------------------------------------------
    # TEST 21
    # Provider-agnostic root serialization.
    # --------------------------------------------------------

    serialized = bundle.model_dump(
        mode="json"
    )

    serialized_text = str(serialized)

    forbidden_provider_markers = [
        "openai",
        "gemini",
        "vertex_ai",
        "vertexai",
        "replicate",
        "fal.ai",
        "fal_ai",
        "midjourney",
    ]

    serialized_lower = serialized_text.lower()

    for marker in forbidden_provider_markers:
        require(
            marker not in serialized_lower,
            (
                "Canon domain unexpectedly depends on "
                f"provider marker: {marker}"
            ),
        )

    pass_test(
        21,
        "canon domain remains provider-agnostic",
    )

    # --------------------------------------------------------
    # TEST 22
    # Canon domain contains no generation execution state.
    # --------------------------------------------------------

    forbidden_execution_fields = [
        "provider_job_id",
        "generation_result",
        "generation_status",
        "output_image_path",
        "sdk_request",
        "api_key",
    ]

    for field_name in forbidden_execution_fields:
        require(
            field_name not in serialized_text,
            (
                "Canon domain leaked production execution "
                f"field: {field_name}"
            ),
        )

    pass_test(
        22,
        "canon remains separate from generation execution",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 68)
    print(
        "BATCH 14B.1-A CANON DOMAIN MODEL CONTRACT PASSED"
    )
    print("=" * 68)
    print()


if __name__ == "__main__":
    main()