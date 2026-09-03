from pydantic import ValidationError

from app.models.canon import (
    AudienceKnowledge,
    AudienceKnowledgeState,
    CameraStyleCanon,
    CanonDocumentStatus,
    CanonFact,
    CanonManifest,
    CanonStatus,
    CharacterCanon,
    CharacterIdentity,
    CharacterKnowledge,
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
    SoundStyleCanon,
    TravelConstraint,
    TruthValue,
    VisualStyleCanon,
    WorldCanon,
)


# ============================================================
# BATCH 14B.1-B — CANON REFERENTIAL INTEGRITY CONTRACT
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
# BASE FIXTURES
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
            "Characters discover historical truth "
            "through incomplete evidence."
        ),
        genres=[
            "Historical mystery",
            "Crime mystery",
            "Noir",
        ],
        historical_layers=[
            HistoricalLayer(
                layer_id="HIST_1856",
                year_label="1856",
                name="The Illegal Foundation",
                description=(
                    "The earliest established historical "
                    "layer."
                ),
                status=CanonStatus.HARD_CANON,
            ),
            HistoricalLayer(
                layer_id="HIST_1930",
                year_label="1930",
                name="The Industrial Cover-Up",
                description=(
                    "Records and ownership history were "
                    "systematically altered."
                ),
                status=CanonStatus.HARD_CANON,
            ),
        ],
    )


def build_factions() -> list[FactionCanon]:
    return [
        FactionCanon(
            faction_id="FACTION_OPD",
            name="Oakhaven Police Department",
            description="Oakhaven police institution.",
        ),
        FactionCanon(
            faction_id="FACTION_WATERFRONT",
            name="Waterfront Community",
            description=(
                "Workers and residents connected to "
                "Oakhaven's waterfront."
            ),
        ),
    ]


def build_locations() -> list[LocationCanon]:
    return [
        LocationCanon(
            location_id="LOC_OLD_DOCKS",
            name="Old Docks",
            description=(
                "Historic waterfront district."
            ),
            sublocation_ids=[
                "LOC_DOCK_EDGE",
            ],
        ),
        LocationCanon(
            location_id="LOC_DOCK_EDGE",
            name="Dock Edge",
            description=(
                "Exposed edge of the old dock."
            ),
            parent_location_id="LOC_OLD_DOCKS",
        ),
        LocationCanon(
            location_id="LOC_DISTRICT_POLICE",
            name="District Police",
            description=(
                "Institutional police headquarters."
            ),
        ),
        LocationCanon(
            location_id="LOC_CENTRAL_DEPOT",
            name="Central Depot",
            description=(
                "Rail and freight hub."
            ),
        ),
    ]


def build_characters() -> list[CharacterCanon]:
    return [
        CharacterCanon(
            character_id="CHAR_JULIAN_VANCE",
            identity=CharacterIdentity(
                canonical_name="Detective Julian Vance",
            ),
            status=CanonStatus.HARD_CANON,
            faction_ids=[
                "FACTION_OPD",
            ],
            primary_location_ids=[
                "LOC_DISTRICT_POLICE",
            ],
            role="INVESTIGATOR",
        ),
        CharacterCanon(
            character_id="CHAR_CLARA_REN_RENDRA",
            identity=CharacterIdentity(
                canonical_name="Clara Ren Rendra",
            ),
            status=CanonStatus.HARD_CANON,
            faction_ids=[
                "FACTION_WATERFRONT",
            ],
            primary_location_ids=[
                "LOC_OLD_DOCKS",
            ],
            role="INVESTIGATIVE_ALLY",
        ),
    ]


def build_facts() -> list[CanonFact]:
    return [
        CanonFact(
            fact_id="FACT_1856_ILLEGAL_FOUNDATION",
            statement=(
                "Modern Oakhaven's foundation involved "
                "unlawful land seizure."
            ),
            truth_value=TruthValue.TRUE,
            status=CanonStatus.HARD_CANON,
            historical_layer_id="HIST_1856",
        ),
        CanonFact(
            fact_id="FACT_1930_RECORD_ERASURE",
            statement=(
                "Historical ownership records were "
                "altered during the 1930 cover-up."
            ),
            truth_value=TruthValue.TRUE,
            status=CanonStatus.HARD_CANON,
            historical_layer_id="HIST_1930",
        ),
    ]


def build_knowledge() -> KnowledgeCanon:
    return KnowledgeCanon(
        facts=build_facts(),
        character_knowledge=[
            CharacterKnowledge(
                character_id="CHAR_JULIAN_VANCE",
                fact_id="FACT_1856_ILLEGAL_FOUNDATION",
                state=KnowledgeState.UNKNOWN,
            ),
            CharacterKnowledge(
                character_id="CHAR_CLARA_REN_RENDRA",
                fact_id="FACT_1856_ILLEGAL_FOUNDATION",
                state=KnowledgeState.PARTIAL,
            ),
        ],
        audience_knowledge=[
            AudienceKnowledge(
                fact_id="FACT_1856_ILLEGAL_FOUNDATION",
                state=(
                    AudienceKnowledgeState.NOT_REVEALED
                ),
            ),
            AudienceKnowledge(
                fact_id="FACT_1930_RECORD_ERASURE",
                state=AudienceKnowledgeState.HINTED,
            ),
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
                    "Observable evidence may establish "
                    "or challenge a theory."
                ),
            ),
        ],
        mystery_rules=[
            MysteryRule(
                rule_id="RULE_FAIR_PLAY",
                name="Fair Play",
                description=(
                    "Mystery resolution must be supported "
                    "by established evidence."
                ),
            ),
        ],
    )


def build_production_style() -> ProductionStyleCanon:
    return ProductionStyleCanon(
        visual=VisualStyleCanon(),
        performance=PerformanceStyleCanon(),
        camera=CameraStyleCanon(),
        sound=SoundStyleCanon(),
        episode_structure=EpisodeStructureCanon(),
    )


def build_bundle(
    *,
    factions: list[FactionCanon] | None = None,
    characters: list[CharacterCanon] | None = None,
    relationships: list[RelationshipCanon] | None = None,
    locations: list[LocationCanon] | None = None,
    travel_constraints: list[TravelConstraint] | None = None,
    knowledge: KnowledgeCanon | None = None,
) -> OakhavenCanon:
    return OakhavenCanon(
        manifest=build_manifest(),
        world=build_world(),
        factions=(
            build_factions()
            if factions is None
            else factions
        ),
        characters=(
            build_characters()
            if characters is None
            else characters
        ),
        relationships=(
            []
            if relationships is None
            else relationships
        ),
        locations=(
            build_locations()
            if locations is None
            else locations
        ),
        travel_constraints=(
            []
            if travel_constraints is None
            else travel_constraints
        ),
        knowledge=(
            build_knowledge()
            if knowledge is None
            else knowledge
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
        "BATCH 14B.1-B — CANON REFERENTIAL INTEGRITY CONTRACT"
    )
    print("=" * 72)

    # --------------------------------------------------------
    # TEST 1 — unknown character faction rejected
    # --------------------------------------------------------

    characters = build_characters()

    characters[0] = characters[0].model_copy(
        update={
            "faction_ids": [
                "FACTION_DOES_NOT_EXIST",
            ]
        }
    )

    require_validation_error(
        lambda: build_bundle(
            characters=characters
        ),
        "Unknown character faction was accepted.",
    )

    pass_test(
        1,
        "unknown character faction is rejected",
    )

    # --------------------------------------------------------
    # TEST 2 — unknown character location rejected
    # --------------------------------------------------------

    characters = build_characters()

    characters[0] = characters[0].model_copy(
        update={
            "primary_location_ids": [
                "LOC_DOES_NOT_EXIST",
            ]
        }
    )

    require_validation_error(
        lambda: build_bundle(
            characters=characters
        ),
        "Unknown character location was accepted.",
    )

    pass_test(
        2,
        "unknown character location is rejected",
    )

    # --------------------------------------------------------
    # TEST 3 — unknown relationship source rejected
    # --------------------------------------------------------

    relationships = [
        RelationshipCanon(
            relationship_id="REL_INVALID_SOURCE",
            source_character_id="CHAR_UNKNOWN",
            target_character_id="CHAR_JULIAN_VANCE",
            relationship_type=RelationshipType.ALLY,
        )
    ]

    require_validation_error(
        lambda: build_bundle(
            relationships=relationships
        ),
        "Unknown relationship source was accepted.",
    )

    pass_test(
        3,
        "unknown relationship source is rejected",
    )

    # --------------------------------------------------------
    # TEST 4 — unknown relationship target rejected
    # --------------------------------------------------------

    relationships = [
        RelationshipCanon(
            relationship_id="REL_INVALID_TARGET",
            source_character_id="CHAR_JULIAN_VANCE",
            target_character_id="CHAR_UNKNOWN",
            relationship_type=RelationshipType.ALLY,
        )
    ]

    require_validation_error(
        lambda: build_bundle(
            relationships=relationships
        ),
        "Unknown relationship target was accepted.",
    )

    pass_test(
        4,
        "unknown relationship target is rejected",
    )

    # --------------------------------------------------------
    # TEST 5 — unknown travel source rejected
    # --------------------------------------------------------

    travel = [
        TravelConstraint(
            constraint_id="TRAVEL_INVALID_SOURCE",
            source_location_id="LOC_UNKNOWN",
            target_location_id="LOC_CENTRAL_DEPOT",
            relation_type=(
                LocationRelationType.ROAD_ROUTE
            ),
        )
    ]

    require_validation_error(
        lambda: build_bundle(
            travel_constraints=travel
        ),
        "Unknown travel source was accepted.",
    )

    pass_test(
        5,
        "unknown travel source is rejected",
    )

    # --------------------------------------------------------
    # TEST 6 — unknown travel target rejected
    # --------------------------------------------------------

    travel = [
        TravelConstraint(
            constraint_id="TRAVEL_INVALID_TARGET",
            source_location_id="LOC_OLD_DOCKS",
            target_location_id="LOC_UNKNOWN",
            relation_type=(
                LocationRelationType.ROAD_ROUTE
            ),
        )
    ]

    require_validation_error(
        lambda: build_bundle(
            travel_constraints=travel
        ),
        "Unknown travel target was accepted.",
    )

    pass_test(
        6,
        "unknown travel target is rejected",
    )

    # --------------------------------------------------------
    # TEST 7 — unknown knowledge owner rejected
    # --------------------------------------------------------

    knowledge = build_knowledge()

    knowledge.character_knowledge.append(
        CharacterKnowledge(
            character_id="CHAR_UNKNOWN",
            fact_id="FACT_1930_RECORD_ERASURE",
            state=KnowledgeState.UNKNOWN,
        )
    )

    require_validation_error(
        lambda: build_bundle(
            knowledge=knowledge
        ),
        "Unknown character knowledge owner was accepted.",
    )

    pass_test(
        7,
        "unknown character knowledge owner is rejected",
    )

    # --------------------------------------------------------
    # TEST 8 — unknown character knowledge fact rejected
    # --------------------------------------------------------

    knowledge = build_knowledge()

    knowledge.character_knowledge.append(
        CharacterKnowledge(
            character_id="CHAR_JULIAN_VANCE",
            fact_id="FACT_UNKNOWN",
            state=KnowledgeState.UNKNOWN,
        )
    )

    require_validation_error(
        lambda: build_bundle(
            knowledge=knowledge
        ),
        "Unknown character knowledge fact was accepted.",
    )

    pass_test(
        8,
        "unknown character knowledge fact is rejected",
    )

    # --------------------------------------------------------
    # TEST 9 — unknown audience fact rejected
    # --------------------------------------------------------

    knowledge = build_knowledge()

    knowledge.audience_knowledge.append(
        AudienceKnowledge(
            fact_id="FACT_UNKNOWN",
            state=(
                AudienceKnowledgeState.NOT_REVEALED
            ),
        )
    )

    require_validation_error(
        lambda: build_bundle(
            knowledge=knowledge
        ),
        "Unknown audience knowledge fact was accepted.",
    )

    pass_test(
        9,
        "unknown audience knowledge fact is rejected",
    )

    # --------------------------------------------------------
    # TEST 10 — unknown historical layer rejected
    # --------------------------------------------------------

    knowledge = build_knowledge()

    knowledge.facts.append(
        CanonFact(
            fact_id="FACT_INVALID_HISTORY",
            statement="Invalid historical reference.",
            truth_value=TruthValue.TRUE,
            status=CanonStatus.HARD_CANON,
            historical_layer_id="HIST_UNKNOWN",
        )
    )

    require_validation_error(
        lambda: build_bundle(
            knowledge=knowledge
        ),
        "Unknown historical layer was accepted.",
    )

    pass_test(
        10,
        "unknown historical layer reference is rejected",
    )

    # --------------------------------------------------------
    # TEST 11 — unknown parent location rejected
    # --------------------------------------------------------

    locations = build_locations()

    locations.append(
        LocationCanon(
            location_id="LOC_INVALID_CHILD",
            name="Invalid Child",
            description="Invalid hierarchy fixture.",
            parent_location_id="LOC_UNKNOWN",
        )
    )

    require_validation_error(
        lambda: build_bundle(
            locations=locations
        ),
        "Unknown parent location was accepted.",
    )

    pass_test(
        11,
        "unknown parent location is rejected",
    )

    # --------------------------------------------------------
    # TEST 12 — unknown sublocation rejected
    # --------------------------------------------------------

    locations = build_locations()

    locations[0] = locations[0].model_copy(
        update={
            "sublocation_ids": [
                "LOC_DOCK_EDGE",
                "LOC_UNKNOWN",
            ]
        }
    )

    require_validation_error(
        lambda: build_bundle(
            locations=locations
        ),
        "Unknown sublocation was accepted.",
    )

    pass_test(
        12,
        "unknown sublocation is rejected",
    )

    # --------------------------------------------------------
    # TEST 13 — duplicate character/fact rejected
    # --------------------------------------------------------

    knowledge = build_knowledge()

    knowledge.character_knowledge.append(
        CharacterKnowledge(
            character_id="CHAR_JULIAN_VANCE",
            fact_id="FACT_1856_ILLEGAL_FOUNDATION",
            state=KnowledgeState.KNOWN,
        )
    )

    require_validation_error(
        lambda: build_bundle(
            knowledge=knowledge
        ),
        (
            "Duplicate character/fact knowledge "
            "record was accepted."
        ),
    )

    pass_test(
        13,
        "duplicate character/fact knowledge is rejected",
    )

    # --------------------------------------------------------
    # TEST 14 — duplicate audience/fact rejected
    # --------------------------------------------------------

    knowledge = build_knowledge()

    knowledge.audience_knowledge.append(
        AudienceKnowledge(
            fact_id="FACT_1856_ILLEGAL_FOUNDATION",
            state=AudienceKnowledgeState.REVEALED,
        )
    )

    require_validation_error(
        lambda: build_bundle(
            knowledge=knowledge
        ),
        (
            "Duplicate audience/fact knowledge "
            "record was accepted."
        ),
    )

    pass_test(
        14,
        "duplicate audience/fact knowledge is rejected",
    )

    # --------------------------------------------------------
    # TEST 15 — hierarchy self-reference rejected
    # --------------------------------------------------------

    locations = [
        LocationCanon(
            location_id="LOC_SELF",
            name="Invalid Self Location",
            description="Invalid hierarchy fixture.",
            parent_location_id="LOC_SELF",
            sublocation_ids=[
                "LOC_SELF",
            ],
        )
    ]

    require_validation_error(
        lambda: build_bundle(
            characters=[],
            locations=locations,
            knowledge=KnowledgeCanon(),
        ),
        "Location self-reference was accepted.",
    )

    pass_test(
        15,
        "location hierarchy self-reference is rejected",
    )

    # --------------------------------------------------------
    # TEST 16 — inconsistent parent/child rejected
    # --------------------------------------------------------

    locations = [
        LocationCanon(
            location_id="LOC_PARENT",
            name="Parent",
            description="Parent fixture.",
            sublocation_ids=[],
        ),
        LocationCanon(
            location_id="LOC_CHILD",
            name="Child",
            description="Child fixture.",
            parent_location_id="LOC_PARENT",
        ),
    ]

    require_validation_error(
        lambda: build_bundle(
            characters=[],
            locations=locations,
            knowledge=KnowledgeCanon(),
        ),
        (
            "Inconsistent parent/child hierarchy "
            "was accepted."
        ),
    )

    pass_test(
        16,
        "inconsistent parent/child hierarchy is rejected",
    )

    # --------------------------------------------------------
    # TEST 17 — multi-node hierarchy cycle rejected
    # --------------------------------------------------------

    locations = [
        LocationCanon(
            location_id="LOC_A",
            name="A",
            description="Cycle fixture A.",
            parent_location_id="LOC_C",
            sublocation_ids=[
                "LOC_B",
            ],
        ),
        LocationCanon(
            location_id="LOC_B",
            name="B",
            description="Cycle fixture B.",
            parent_location_id="LOC_A",
            sublocation_ids=[
                "LOC_C",
            ],
        ),
        LocationCanon(
            location_id="LOC_C",
            name="C",
            description="Cycle fixture C.",
            parent_location_id="LOC_B",
            sublocation_ids=[
                "LOC_A",
            ],
        ),
    ]

    require_validation_error(
        lambda: build_bundle(
            characters=[],
            locations=locations,
            knowledge=KnowledgeCanon(),
        ),
        "Multi-node location cycle was accepted.",
    )

    pass_test(
        17,
        "multi-node location hierarchy cycle is rejected",
    )

    # --------------------------------------------------------
    # TEST 18 — valid cross-registry graph accepted
    # --------------------------------------------------------

    relationship = RelationshipCanon(
        relationship_id="REL_JULIAN_REN",
        source_character_id="CHAR_JULIAN_VANCE",
        target_character_id="CHAR_CLARA_REN_RENDRA",
        relationship_type=RelationshipType.ALLY,
        description="Investigative allies.",
    )

    travel = TravelConstraint(
        constraint_id="TRAVEL_DOCKS_DEPOT",
        source_location_id="LOC_OLD_DOCKS",
        target_location_id="LOC_CENTRAL_DEPOT",
        relation_type=LocationRelationType.ROAD_ROUTE,
        minimum_minutes=10,
        maximum_minutes=20,
    )

    bundle = build_bundle(
        relationships=[
            relationship,
        ],
        travel_constraints=[
            travel,
        ],
    )

    require(
        len(bundle.relationships) == 1,
        "Valid relationship was not preserved.",
    )

    require(
        len(bundle.travel_constraints) == 1,
        "Valid travel constraint was not preserved.",
    )

    pass_test(
        18,
        "valid cross-registry references are accepted",
    )

    # --------------------------------------------------------
    # TEST 19 — valid hierarchy and knowledge graph accepted
    # --------------------------------------------------------

    bundle = build_bundle()

    old_docks = next(
        location
        for location in bundle.locations
        if location.location_id == "LOC_OLD_DOCKS"
    )

    dock_edge = next(
        location
        for location in bundle.locations
        if location.location_id == "LOC_DOCK_EDGE"
    )

    require(
        "LOC_DOCK_EDGE" in old_docks.sublocation_ids,
        "Valid parent lost its child reference.",
    )

    require(
        dock_edge.parent_location_id
        == "LOC_OLD_DOCKS",
        "Valid child lost its parent reference.",
    )

    require(
        len(bundle.knowledge.character_knowledge) == 2,
        "Valid character knowledge graph was damaged.",
    )

    require(
        len(bundle.knowledge.audience_knowledge) == 2,
        "Valid audience knowledge graph was damaged.",
    )

    pass_test(
        19,
        "valid hierarchy and knowledge graph are accepted",
    )

    # --------------------------------------------------------
    # TEST 20 — integrity validation deterministic
    # --------------------------------------------------------

    bundle_a = build_bundle()
    bundle_b = build_bundle()

    require(
        bundle_a.model_dump(mode="json")
        == bundle_b.model_dump(mode="json"),
        (
            "Equivalent validated canon graphs "
            "serialize differently."
        ),
    )

    invalid_characters_a = build_characters()
    invalid_characters_b = build_characters()

    invalid_characters_a[0] = (
        invalid_characters_a[0].model_copy(
            update={
                "faction_ids": [
                    "FACTION_UNKNOWN",
                ]
            }
        )
    )

    invalid_characters_b[0] = (
        invalid_characters_b[0].model_copy(
            update={
                "faction_ids": [
                    "FACTION_UNKNOWN",
                ]
            }
        )
    )

    def get_validation_message(
        characters: list[CharacterCanon],
    ) -> str:
        try:
            build_bundle(
                characters=characters
            )
        except ValidationError as exc:
            return str(exc)

        raise AssertionError(
            "Invalid graph unexpectedly passed."
        )

    error_a = get_validation_message(
        invalid_characters_a
    )

    error_b = get_validation_message(
        invalid_characters_b
    )

    require(
        error_a == error_b,
        (
            "Equivalent integrity violations produced "
            "different validation results."
        ),
    )

    pass_test(
        20,
        "referential integrity validation is deterministic",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print(
        "BATCH 14B.1-B CANON REFERENTIAL INTEGRITY CONTRACT PASSED"
    )
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()