from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


# ============================================================
# CANON ENUMS
# ============================================================


class CanonStatus(str, Enum):
    HARD_CANON = "HARD_CANON"
    SOFT_CANON = "SOFT_CANON"
    OPEN = "OPEN"
    LEGACY = "LEGACY"
    DEPRECATED = "DEPRECATED"
    NON_CANON = "NON_CANON"
    REVISED_CANON = "REVISED_CANON"
    HARD_CANON_IDENTITY_WITH_RESTRICTED_KNOWLEDGE = (
        "HARD_CANON_IDENTITY_WITH_RESTRICTED_KNOWLEDGE"
    )


class CanonDocumentStatus(str, Enum):
    DRAFT = "DRAFT"
    FROZEN_CANDIDATE = "FROZEN_CANDIDATE"
    FROZEN = "FROZEN"


class KnowledgeState(str, Enum):
    UNKNOWN = "UNKNOWN"
    SUSPECTED = "SUSPECTED"
    PARTIAL = "PARTIAL"
    KNOWN = "KNOWN"
    FALSE_BELIEF = "FALSE_BELIEF"


class AudienceKnowledgeState(str, Enum):
    NOT_REVEALED = "NOT_REVEALED"
    HINTED = "HINTED"
    PARTIALLY_REVEALED = "PARTIALLY_REVEALED"
    REVEALED = "REVEALED"
    MISDIRECTED = "MISDIRECTED"


class TruthValue(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    OPEN = "OPEN"


class RelationshipType(str, Enum):
    FAMILY = "FAMILY"
    ROMANTIC = "ROMANTIC"
    PROFESSIONAL = "PROFESSIONAL"
    ALLY = "ALLY"
    ADVERSARIAL = "ADVERSARIAL"
    INFORMANT = "INFORMANT"
    COMMAND = "COMMAND"
    COMMUNITY = "COMMUNITY"
    UNKNOWN = "UNKNOWN"


class LocationRelationType(str, Enum):
    CONTAINS = "CONTAINS"
    CONNECTED_TO = "CONNECTED_TO"
    ROAD_ROUTE = "ROAD_ROUTE"
    RAIL_ROUTE = "RAIL_ROUTE"
    TIDAL_ROUTE = "TIDAL_ROUTE"
    WALKING_ROUTE = "WALKING_ROUTE"


class ClueLevel(str, Enum):
    VISUAL = "VISUAL"
    BEHAVIORAL = "BEHAVIORAL"
    DIALOGUE_TESTIMONY = "DIALOGUE_TESTIMONY"
    LOCATION_ENVIRONMENT = "LOCATION_ENVIRONMENT"
    SYSTEMIC_HISTORICAL = "SYSTEMIC_HISTORICAL"


class NarrativeBeatType(str, Enum):
    HOOK = "HOOK"
    SETUP = "SETUP"
    DISCOVERY = "DISCOVERY"
    ESCALATION = "ESCALATION"
    REACTION = "REACTION"
    REINTERPRETATION = "REINTERPRETATION"
    CLIFFHANGER = "CLIFFHANGER"


class ShotNarrativeType(str, Enum):
    ESTABLISHING = "ESTABLISHING"
    PERFORMANCE = "PERFORMANCE"
    INSERT = "INSERT"
    REACTION = "REACTION"
    TRANSITION = "TRANSITION"
    ATMOSPHERIC = "ATMOSPHERIC"


# ============================================================
# CANON MANIFEST
# ============================================================


class CanonSourceReference(BaseModel):
    source_id: str
    path: str
    role: str
    authoritative: bool = False


class CanonManifest(BaseModel):
    universe_id: str
    universe_name: str

    canon_version: str
    document_status: CanonDocumentStatus

    present_day: int

    authority_document: str

    sources: list[CanonSourceReference] = Field(
        default_factory=list
    )

    derived_files: list[str] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_frozen_authority(self) -> CanonManifest:
        if (
            self.document_status == CanonDocumentStatus.FROZEN
            and not self.authority_document
        ):
            raise ValueError(
                "Frozen canon requires an authority document."
            )

        return self


# ============================================================
# WORLD CANON
# ============================================================


class HistoricalLayer(BaseModel):
    layer_id: str
    year_label: str

    name: str
    description: str

    status: CanonStatus

    established_truths: list[str] = Field(
        default_factory=list
    )

    unresolved_questions: list[str] = Field(
        default_factory=list
    )


class WorldRule(BaseModel):
    rule_id: str
    name: str

    description: str

    status: CanonStatus = CanonStatus.HARD_CANON

    prohibited_interpretations: list[str] = Field(
        default_factory=list
    )


class WorldCanon(BaseModel):
    world_id: str
    name: str

    core_statement: str
    narrative_principle: str

    genres: list[str] = Field(
        default_factory=list
    )

    historical_layers: list[HistoricalLayer] = Field(
        default_factory=list
    )

    rules: list[WorldRule] = Field(
        default_factory=list
    )


# ============================================================
# FACTION CANON
# ============================================================


class FactionCanon(BaseModel):
    faction_id: str
    name: str

    description: str

    status: CanonStatus = CanonStatus.HARD_CANON

    motivations: list[str] = Field(
        default_factory=list
    )

    knowledge_limits: list[str] = Field(
        default_factory=list
    )


# ============================================================
# CHARACTER CANON
# ============================================================


class CharacterIdentity(BaseModel):
    canonical_name: str

    aliases: list[str] = Field(
        default_factory=list
    )

    legacy_names: list[str] = Field(
        default_factory=list
    )


class CharacterVisualIdentity(BaseModel):
    age_range: str | None = None
    body_build: str | None = None

    facial_structure: str | None = None
    hair: str | None = None

    distinctive_marks: list[str] = Field(
        default_factory=list
    )

    wardrobe_language: list[str] = Field(
        default_factory=list
    )


class CharacterVoiceIdentity(BaseModel):
    characteristics: list[str] = Field(
        default_factory=list
    )

    provider_specific_reference: str | None = None

    provider_reference_is_canonical: bool = False

    @model_validator(mode="after")
    def validate_provider_reference(
        self,
    ) -> CharacterVoiceIdentity:
        if self.provider_reference_is_canonical:
            raise ValueError(
                "Provider-specific voice references "
                "cannot become canonical identity."
            )

        return self


class CharacterCanon(BaseModel):
    character_id: str

    identity: CharacterIdentity

    status: CanonStatus

    faction_ids: list[str] = Field(
        default_factory=list
    )

    primary_location_ids: list[str] = Field(
        default_factory=list
    )

    role: str | None = None

    description: str | None = None

    motivations: list[str] = Field(
        default_factory=list
    )

    fears: list[str] = Field(
        default_factory=list
    )

    blind_spots: list[str] = Field(
        default_factory=list
    )

    knowledge_limits: list[str] = Field(
        default_factory=list
    )

    visual_identity: CharacterVisualIdentity | None = None

    voice_identity: CharacterVoiceIdentity | None = None


# ============================================================
# RELATIONSHIP CANON
# ============================================================


class RelationshipCanon(BaseModel):
    relationship_id: str

    source_character_id: str
    target_character_id: str

    relationship_type: RelationshipType

    description: str | None = None

    status: CanonStatus = CanonStatus.HARD_CANON

    directional: bool = False

    @model_validator(mode="after")
    def validate_relationship(
        self,
    ) -> RelationshipCanon:
        if self.source_character_id == self.target_character_id:
            raise ValueError(
                "A character relationship cannot target itself."
            )

        return self


# ============================================================
# LOCATION CANON
# ============================================================


class LocationVisualIdentity(BaseModel):
    architecture: list[str] = Field(
        default_factory=list
    )

    materials: list[str] = Field(
        default_factory=list
    )

    landmarks: list[str] = Field(
        default_factory=list
    )

    environmental_character: list[str] = Field(
        default_factory=list
    )


class LocationCanon(BaseModel):
    location_id: str
    name: str

    description: str

    status: CanonStatus = CanonStatus.HARD_CANON

    parent_location_id: str | None = None

    sublocation_ids: list[str] = Field(
        default_factory=list
    )

    narrative_functions: list[str] = Field(
        default_factory=list
    )

    associated_faction_ids: list[str] = Field(
        default_factory=list
    )

    historical_layer_ids: list[str] = Field(
        default_factory=list
    )

    atmosphere_tags: list[str] = Field(
        default_factory=list
    )

    visual_identity: LocationVisualIdentity | None = None


class TravelConstraint(BaseModel):
    constraint_id: str

    source_location_id: str
    target_location_id: str

    relation_type: LocationRelationType

    minimum_minutes: int | None = None
    maximum_minutes: int | None = None

    available_start_time: str | None = None
    available_end_time: str | None = None

    description: str | None = None

    @model_validator(mode="after")
    def validate_duration(
        self,
    ) -> TravelConstraint:
        if (
            self.minimum_minutes is not None
            and self.minimum_minutes < 0
        ):
            raise ValueError(
                "minimum_minutes cannot be negative."
            )

        if (
            self.maximum_minutes is not None
            and self.maximum_minutes < 0
        ):
            raise ValueError(
                "maximum_minutes cannot be negative."
            )

        if (
            self.minimum_minutes is not None
            and self.maximum_minutes is not None
            and self.minimum_minutes > self.maximum_minutes
        ):
            raise ValueError(
                "minimum_minutes cannot exceed "
                "maximum_minutes."
            )

        return self


# ============================================================
# KNOWLEDGE GRAPH
# ============================================================


class CanonFact(BaseModel):
    fact_id: str

    statement: str

    truth_value: TruthValue

    status: CanonStatus

    historical_layer_id: str | None = None

    tags: list[str] = Field(
        default_factory=list
    )

    evidence_requirements: list[str] = Field(
        default_factory=list
    )


class CharacterKnowledge(BaseModel):
    character_id: str
    fact_id: str

    state: KnowledgeState

    belief_statement: str | None = None

    source_episode_id: str | None = None
    source_scene_number: int | None = None

    evidence_ids: list[str] = Field(
        default_factory=list
    )


class AudienceKnowledge(BaseModel):
    fact_id: str

    state: AudienceKnowledgeState

    source_episode_id: str | None = None
    source_scene_number: int | None = None

    evidence_ids: list[str] = Field(
        default_factory=list
    )


class KnowledgeCanon(BaseModel):
    facts: list[CanonFact] = Field(
        default_factory=list
    )

    character_knowledge: list[CharacterKnowledge] = Field(
        default_factory=list
    )

    audience_knowledge: list[AudienceKnowledge] = Field(
        default_factory=list
    )


# ============================================================
# CLUE / MYSTERY CANON
# ============================================================


class ClueRule(BaseModel):
    rule_id: str

    level: ClueLevel

    name: str
    description: str

    requirements: list[str] = Field(
        default_factory=list
    )


class MysteryRule(BaseModel):
    rule_id: str

    name: str
    description: str

    status: CanonStatus = CanonStatus.HARD_CANON

    prohibited_patterns: list[str] = Field(
        default_factory=list
    )


class MysteryCanon(BaseModel):
    clue_rules: list[ClueRule] = Field(
        default_factory=list
    )

    mystery_rules: list[MysteryRule] = Field(
        default_factory=list
    )


# ============================================================
# PRODUCTION STYLE CANON
# ============================================================


class VisualStyleCanon(BaseModel):
    rendering_language: list[str] = Field(
        default_factory=list
    )

    prohibited_styles: list[str] = Field(
        default_factory=list
    )

    palette_language: list[str] = Field(
        default_factory=list
    )


class PerformanceStyleCanon(BaseModel):
    preferred_motion: list[str] = Field(
        default_factory=list
    )

    prohibited_motion: list[str] = Field(
        default_factory=list
    )

    lip_sync_required_by_default: bool = False


class CameraStyleCanon(BaseModel):
    preferred_movements: list[str] = Field(
        default_factory=list
    )

    prohibited_movements: list[str] = Field(
        default_factory=list
    )


class SoundStyleCanon(BaseModel):
    vocabulary: list[str] = Field(
        default_factory=list
    )

    contextual_selection_required: bool = True


class EpisodeStructureCanon(BaseModel):
    target_minimum_seconds: int = 45
    target_maximum_seconds: int = 60

    recommended_primary_questions: int = 1
    recommended_meaningful_discoveries: int = 1
    recommended_reinterpretations: int = 1
    recommended_ending_hooks: int = 1

    allowed_narrative_beats: list[NarrativeBeatType] = Field(
        default_factory=lambda: list(NarrativeBeatType)
    )

    allowed_shot_types: list[ShotNarrativeType] = Field(
        default_factory=lambda: list(ShotNarrativeType)
    )

    non_dialogue_storytelling_allowed: bool = True

    @model_validator(mode="after")
    def validate_duration_range(
        self,
    ) -> EpisodeStructureCanon:
        if self.target_minimum_seconds <= 0:
            raise ValueError(
                "target_minimum_seconds must be positive."
            )

        if (
            self.target_maximum_seconds
            < self.target_minimum_seconds
        ):
            raise ValueError(
                "target_maximum_seconds cannot be lower "
                "than target_minimum_seconds."
            )

        return self


class ProductionStyleCanon(BaseModel):
    visual: VisualStyleCanon
    performance: PerformanceStyleCanon
    camera: CameraStyleCanon
    sound: SoundStyleCanon
    episode_structure: EpisodeStructureCanon


# ============================================================
# CANON MIGRATION / LEGACY SUPPORT
# ============================================================


class CanonNameMigration(BaseModel):
    entity_type: str

    legacy_value: str
    canonical_value: str

    reason: str | None = None


class CanonDeprecation(BaseModel):
    deprecation_id: str

    subject: str
    deprecated_interpretation: str

    replacement_interpretation: str | None = None

    reason: str | None = None


# ============================================================
# ROOT CANON BUNDLE
# ============================================================


class OakhavenCanon(BaseModel):
    manifest: CanonManifest

    world: WorldCanon

    factions: list[FactionCanon] = Field(
        default_factory=list
    )

    characters: list[CharacterCanon] = Field(
        default_factory=list
    )

    relationships: list[RelationshipCanon] = Field(
        default_factory=list
    )

    locations: list[LocationCanon] = Field(
        default_factory=list
    )

    travel_constraints: list[TravelConstraint] = Field(
        default_factory=list
    )

    knowledge: KnowledgeCanon

    mystery: MysteryCanon

    production_style: ProductionStyleCanon

    name_migrations: list[CanonNameMigration] = Field(
        default_factory=list
    )

    deprecations: list[CanonDeprecation] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @model_validator(mode="after")
    def validate_registry_integrity(
        self,
    ) -> OakhavenCanon:
        # ----------------------------------------------------
        # Build canonical registries.
        # ----------------------------------------------------

        character_ids = [
            character.character_id
            for character in self.characters
        ]

        faction_ids = [
            faction.faction_id
            for faction in self.factions
        ]

        location_ids = [
            location.location_id
            for location in self.locations
        ]

        fact_ids = [
            fact.fact_id
            for fact in self.knowledge.facts
        ]

        historical_layer_ids = [
            layer.layer_id
            for layer in self.world.historical_layers
        ]

        relationship_ids = [
            relationship.relationship_id
            for relationship in self.relationships
        ]

        travel_constraint_ids = [
            constraint.constraint_id
            for constraint in self.travel_constraints
        ]

        clue_rule_ids = [
            rule.rule_id
            for rule in self.mystery.clue_rules
        ]

        mystery_rule_ids = [
            rule.rule_id
            for rule in self.mystery.mystery_rules
        ]

        # ----------------------------------------------------
        # Registry uniqueness.
        # ----------------------------------------------------

        self._require_unique_ids(
            character_ids,
            "character",
        )

        self._require_unique_ids(
            faction_ids,
            "faction",
        )

        self._require_unique_ids(
            location_ids,
            "location",
        )

        self._require_unique_ids(
            fact_ids,
            "fact",
        )

        self._require_unique_ids(
            historical_layer_ids,
            "historical layer",
        )

        self._require_unique_ids(
            relationship_ids,
            "relationship",
        )

        self._require_unique_ids(
            travel_constraint_ids,
            "travel constraint",
        )

        self._require_unique_ids(
            clue_rule_ids,
            "clue rule",
        )

        self._require_unique_ids(
            mystery_rule_ids,
            "mystery rule",
        )

        character_id_set = set(character_ids)
        faction_id_set = set(faction_ids)
        location_id_set = set(location_ids)
        fact_id_set = set(fact_ids)
        historical_layer_id_set = set(
            historical_layer_ids
        )

        # ----------------------------------------------------
        # Character references.
        # ----------------------------------------------------

        for character in self.characters:
            for faction_id in character.faction_ids:
                self._require_reference(
                    faction_id,
                    faction_id_set,
                    (
                        f"Character {character.character_id} "
                        "references unknown faction"
                    ),
                )

            for location_id in character.primary_location_ids:
                self._require_reference(
                    location_id,
                    location_id_set,
                    (
                        f"Character {character.character_id} "
                        "references unknown primary location"
                    ),
                )

        # ----------------------------------------------------
        # Relationship references.
        # ----------------------------------------------------

        for relationship in self.relationships:
            self._require_reference(
                relationship.source_character_id,
                character_id_set,
                (
                    f"Relationship "
                    f"{relationship.relationship_id} "
                    "references unknown source character"
                ),
            )

            self._require_reference(
                relationship.target_character_id,
                character_id_set,
                (
                    f"Relationship "
                    f"{relationship.relationship_id} "
                    "references unknown target character"
                ),
            )

        # ----------------------------------------------------
        # Travel references.
        # ----------------------------------------------------

        for constraint in self.travel_constraints:
            self._require_reference(
                constraint.source_location_id,
                location_id_set,
                (
                    f"Travel constraint "
                    f"{constraint.constraint_id} "
                    "references unknown source location"
                ),
            )

            self._require_reference(
                constraint.target_location_id,
                location_id_set,
                (
                    f"Travel constraint "
                    f"{constraint.constraint_id} "
                    "references unknown target location"
                ),
            )

        # ----------------------------------------------------
        # Fact historical-layer references.
        # ----------------------------------------------------

        for fact in self.knowledge.facts:
            if fact.historical_layer_id is not None:
                self._require_reference(
                    fact.historical_layer_id,
                    historical_layer_id_set,
                    (
                        f"Fact {fact.fact_id} references "
                        "unknown historical layer"
                    ),
                )

        # ----------------------------------------------------
        # Character knowledge references.
        # ----------------------------------------------------

        character_fact_pairs: list[
            tuple[str, str]
        ] = []

        for knowledge in self.knowledge.character_knowledge:
            self._require_reference(
                knowledge.character_id,
                character_id_set,
                (
                    "Character knowledge references "
                    "unknown character"
                ),
            )

            self._require_reference(
                knowledge.fact_id,
                fact_id_set,
                (
                    "Character knowledge references "
                    "unknown fact"
                ),
            )

            character_fact_pairs.append(
                (
                    knowledge.character_id,
                    knowledge.fact_id,
                )
            )

        self._require_unique_pairs(
            character_fact_pairs,
            "character/fact knowledge",
        )

        # ----------------------------------------------------
        # Audience knowledge references.
        # ----------------------------------------------------

        audience_fact_ids: list[str] = []

        for knowledge in self.knowledge.audience_knowledge:
            self._require_reference(
                knowledge.fact_id,
                fact_id_set,
                (
                    "Audience knowledge references "
                    "unknown fact"
                ),
            )

            audience_fact_ids.append(
                knowledge.fact_id
            )

        self._require_unique_ids(
            audience_fact_ids,
            "audience/fact knowledge",
        )

                # ----------------------------------------------------
        # Location semantic references.
        # ----------------------------------------------------

        for location in self.locations:
            for faction_id in location.associated_faction_ids:
                self._require_reference(
                    faction_id,
                    faction_id_set,
                    (
                        f"Location {location.location_id} "
                        "references unknown associated faction"
                    ),
                )

            for historical_layer_id in location.historical_layer_ids:
                self._require_reference(
                    historical_layer_id,
                    historical_layer_id_set,
                    (
                        f"Location {location.location_id} "
                        "references unknown historical layer"
                    ),
                )

        # ----------------------------------------------------
        # Location hierarchy references.
        # ----------------------------------------------------

        location_by_id = {
            location.location_id: location
            for location in self.locations
        }

        for location in self.locations:
            if (
                location.parent_location_id
                == location.location_id
            ):
                raise ValueError(
                    f"Location {location.location_id} "
                    "cannot be its own parent."
                )

            if (
                location.location_id
                in location.sublocation_ids
            ):
                raise ValueError(
                    f"Location {location.location_id} "
                    "cannot contain itself as a sublocation."
                )

            if location.parent_location_id is not None:
                self._require_reference(
                    location.parent_location_id,
                    location_id_set,
                    (
                        f"Location {location.location_id} "
                        "references unknown parent location"
                    ),
                )

            self._require_unique_ids(
                location.sublocation_ids,
                (
                    f"sublocation of "
                    f"{location.location_id}"
                ),
            )

            for sublocation_id in location.sublocation_ids:
                self._require_reference(
                    sublocation_id,
                    location_id_set,
                    (
                        f"Location {location.location_id} "
                        "references unknown sublocation"
                    ),
                )

        # ----------------------------------------------------
        # Parent/child hierarchy consistency.
        # ----------------------------------------------------

        for location in self.locations:
            if location.parent_location_id is not None:
                parent = location_by_id[
                    location.parent_location_id
                ]

                if (
                    location.location_id
                    not in parent.sublocation_ids
                ):
                    raise ValueError(
                        f"Location {location.location_id} "
                        f"declares parent "
                        f"{location.parent_location_id}, "
                        "but the parent does not declare "
                        "the child as a sublocation."
                    )

            for sublocation_id in location.sublocation_ids:
                child = location_by_id[
                    sublocation_id
                ]

                if (
                    child.parent_location_id
                    != location.location_id
                ):
                    raise ValueError(
                        f"Location {location.location_id} "
                        f"declares sublocation "
                        f"{sublocation_id}, but the child "
                        "does not declare the matching "
                        "parent location."
                    )

        # ----------------------------------------------------
        # Detect location hierarchy cycles.
        # ----------------------------------------------------

        self._validate_location_hierarchy_cycles(
            location_by_id
        )

        return self

    @staticmethod
    def _require_unique_ids(
        values: list[str],
        entity_name: str,
    ) -> None:
        if len(values) != len(set(values)):
            raise ValueError(
                f"Duplicate {entity_name} IDs detected."
            )

    @staticmethod
    def _require_unique_pairs(
        values: list[tuple[str, str]],
        entity_name: str,
    ) -> None:
        if len(values) != len(set(values)):
            raise ValueError(
                f"Duplicate {entity_name} records detected."
            )

    @staticmethod
    def _require_reference(
        value: str,
        registry: set[str],
        context: str,
    ) -> None:
        if value not in registry:
            raise ValueError(
                f"{context}: {value}"
            )

    @staticmethod
    def _validate_location_hierarchy_cycles(
        location_by_id: dict[str, LocationCanon],
    ) -> None:
        for location_id in location_by_id:
            visited: set[str] = set()
            current_id: str | None = location_id

            while current_id is not None:
                if current_id in visited:
                    raise ValueError(
                        "Location hierarchy cycle detected "
                        f"at {current_id}."
                    )

                visited.add(current_id)

                current = location_by_id[current_id]

                current_id = (
                    current.parent_location_id
                )