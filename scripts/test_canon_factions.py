import json
from pathlib import Path

from pydantic import ValidationError

from app.models.canon import (
    CanonStatus,
    FactionCanon,
)


# ============================================================
# BATCH 14B.2-B — CANON FACTION REGISTRY
# ============================================================


ROOT = Path(__file__).resolve().parents[1]

FACTIONS_PATH = (
    ROOT
    / "data"
    / "canon"
    / "oakhaven"
    / "v1"
    / "factions.json"
)


EXPECTED_FACTION_IDS = [
    "FACTION_PIKE_HILL_ELITE",
    "FACTION_OPD",
    "FACTION_CUSTODIANS_OF_MEMORY",
    "FACTION_WATERFRONT_COLLECTIVE",
    "FACTION_SHADOW_OPERATIVES",
]


EXPECTED_FACTION_NAMES = {
    "FACTION_PIKE_HILL_ELITE":
        "The Pike Hill Elite",

    "FACTION_OPD":
        "Oakhaven Police Department",

    "FACTION_CUSTODIANS_OF_MEMORY":
        "The Custodians of Memory",

    "FACTION_WATERFRONT_COLLECTIVE":
        "The Waterfront Collective",

    "FACTION_SHADOW_OPERATIVES":
        "The Shadow Operatives",
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


def load_faction_data() -> list[dict]:
    with FACTIONS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    require(
        isinstance(data, list),
        "factions.json root must be a list.",
    )

    return data


def load_factions() -> list[FactionCanon]:
    data = load_faction_data()

    try:
        return [
            FactionCanon.model_validate(item)
            for item in data
        ]
    except ValidationError as exc:
        raise AssertionError(
            "factions.json failed FactionCanon "
            "validation."
        ) from exc


def get_faction(
    factions: list[FactionCanon],
    faction_id: str,
) -> FactionCanon:
    for faction in factions:
        if faction.faction_id == faction_id:
            return faction

    raise AssertionError(
        f"Faction not found: {faction_id}"
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
        "BATCH 14B.2-B — CANON FACTION REGISTRY"
    )
    print("=" * 72)

    # --------------------------------------------------------
    # TEST 1
    # Faction registry exists.
    # --------------------------------------------------------

    require(
        FACTIONS_PATH.is_file(),
        "factions.json does not exist.",
    )

    pass_test(
        1,
        "faction registry exists",
    )

    # --------------------------------------------------------
    # TEST 2
    # Registry is valid JSON list.
    # --------------------------------------------------------

    raw_data = load_faction_data()

    require(
        isinstance(raw_data, list),
        "Faction registry is not a list.",
    )

    pass_test(
        2,
        "faction registry is valid JSON data",
    )

    # --------------------------------------------------------
    # TEST 3
    # Every faction validates.
    # --------------------------------------------------------

    factions = load_factions()

    require(
        all(
            isinstance(
                faction,
                FactionCanon,
            )
            for faction in factions
        ),
        "One or more factions failed validation.",
    )

    pass_test(
        3,
        "all factions validate against domain model",
    )

    # --------------------------------------------------------
    # TEST 4
    # Exactly five canonical factions exist.
    # --------------------------------------------------------

    require(
        len(factions) == 5,
        (
            "Oakhaven V1 must contain exactly "
            "five canonical factions."
        ),
    )

    pass_test(
        4,
        "exactly five canonical factions exist",
    )

    # --------------------------------------------------------
    # TEST 5
    # IDs are unique.
    # --------------------------------------------------------

    faction_ids = [
        faction.faction_id
        for faction in factions
    ]

    require(
        len(faction_ids)
        == len(set(faction_ids)),
        "Duplicate faction IDs detected.",
    )

    pass_test(
        5,
        "canonical faction IDs are unique",
    )

    # --------------------------------------------------------
    # TEST 6
    # Registry IDs remain stable.
    # --------------------------------------------------------

    require(
        faction_ids
        == EXPECTED_FACTION_IDS,
        (
            "Canonical faction registry or "
            "ordering changed."
        ),
    )

    pass_test(
        6,
        "canonical faction registry is stable",
    )

    # --------------------------------------------------------
    # TEST 7
    # Names remain stable.
    # --------------------------------------------------------

    for faction in factions:
        expected_name = (
            EXPECTED_FACTION_NAMES[
                faction.faction_id
            ]
        )

        require(
            faction.name == expected_name,
            (
                "Unexpected canonical name for "
                f"{faction.faction_id}."
            ),
        )

    pass_test(
        7,
        "canonical faction names are stable",
    )

    # --------------------------------------------------------
    # TEST 8
    # All factions remain hard canon.
    # --------------------------------------------------------

    require(
        all(
            faction.status
            == CanonStatus.HARD_CANON
            for faction in factions
        ),
        (
            "One or more canonical factions "
            "are not HARD_CANON."
        ),
    )

    pass_test(
        8,
        "all factions remain hard canon",
    )

    # --------------------------------------------------------
    # TEST 9
    # Every faction has a description.
    # --------------------------------------------------------

    require(
        all(
            faction.description.strip()
            for faction in factions
        ),
        (
            "One or more factions have no "
            "description."
        ),
    )

    pass_test(
        9,
        "all factions preserve descriptive identity",
    )

    # --------------------------------------------------------
    # TEST 10
    # Every faction has motivations.
    # --------------------------------------------------------

    require(
        all(
            len(faction.motivations) > 0
            for faction in factions
        ),
        (
            "One or more factions have no "
            "canonical motivations."
        ),
    )

    pass_test(
        10,
        "all factions preserve motivations",
    )

    # --------------------------------------------------------
    # TEST 11
    # Every faction has knowledge limits.
    # --------------------------------------------------------

    require(
        all(
            len(faction.knowledge_limits) > 0
            for faction in factions
        ),
        (
            "One or more factions have no "
            "knowledge boundaries."
        ),
    )

    pass_test(
        11,
        "all factions preserve knowledge boundaries",
    )

    # --------------------------------------------------------
    # TEST 12
    # Pike Hill does not know the complete truth.
    # --------------------------------------------------------

    pike = get_faction(
        factions,
        "FACTION_PIKE_HILL_ELITE",
    )

    pike_knowledge = normalized_text(
        pike.knowledge_limits
    )

    require(
        (
            "do not know"
            in pike_knowledge
        ),
        (
            "Pike Hill knowledge boundary no "
            "longer records its ignorance."
        ),
    )

    require(
        "1856" in pike_knowledge,
        (
            "Pike Hill's 1856 knowledge boundary "
            "is missing."
        ),
    )

    require(
        "pl-1930" in pike_knowledge,
        (
            "Pike Hill's PL-1930 misunderstanding "
            "is missing."
        ),
    )

    pass_test(
        12,
        "Pike Hill knowledge limitation is preserved",
    )

    # --------------------------------------------------------
    # TEST 13
    # OPD remains internally divided.
    # --------------------------------------------------------

    opd = get_faction(
        factions,
        "FACTION_OPD",
    )

    opd_description = (
        opd.description.lower()
    )

    opd_motivations = normalized_text(
        opd.motivations
    )

    opd_knowledge = normalized_text(
        opd.knowledge_limits
    )

    require(
        (
            "divided"
            in opd_description
            or "divided"
            in opd_knowledge
        ),
        (
            "OPD internal division is no longer "
            "represented."
        ),
    )

    require(
        "field" in (
            opd_description
            + " "
            + opd_motivations
            + " "
            + opd_knowledge
        ),
        (
            "OPD field-investigator perspective "
            "is missing."
        ),
    )

    pass_test(
        13,
        "OPD internal division is preserved",
    )

    # --------------------------------------------------------
    # TEST 14
    # Custodians may sincerely misinterpret evidence.
    # --------------------------------------------------------

    custodians = get_faction(
        factions,
        "FACTION_CUSTODIANS_OF_MEMORY",
    )

    custodians_knowledge = normalized_text(
        custodians.knowledge_limits
    )

    require(
        "misinterpret" in custodians_knowledge,
        (
            "Custodians no longer preserve their "
            "interpretive uncertainty."
        ),
    )

    require(
        (
            "incomplete"
            in custodians_knowledge
            or "fragmented"
            in custodians_knowledge
        ),
        (
            "Custodian evidence fragmentation "
            "is missing."
        ),
    )

    pass_test(
        14,
        "Custodian uncertainty is preserved",
    )

    # --------------------------------------------------------
    # TEST 15
    # Waterfront oral-history boundary preserved.
    # --------------------------------------------------------

    waterfront = get_faction(
        factions,
        "FACTION_WATERFRONT_COLLECTIVE",
    )

    waterfront_knowledge = normalized_text(
        waterfront.knowledge_limits
    )

    require(
        "oral" in waterfront_knowledge,
        (
            "Waterfront oral-history boundary "
            "is missing."
        ),
    )

    require(
        "distort" in waterfront_knowledge,
        (
            "Waterfront historical distortion "
            "is missing."
        ),
    )

    require(
        "complete truth"
        in waterfront_knowledge,
        (
            "Waterfront knowledge limitation "
            "is missing."
        ),
    )

    pass_test(
        15,
        "Waterfront oral-history boundary is preserved",
    )

    # --------------------------------------------------------
    # TEST 16
    # Shadow Operatives remain ignorant executors.
    # --------------------------------------------------------

    shadow = get_faction(
        factions,
        "FACTION_SHADOW_OPERATIVES",
    )

    shadow_knowledge = normalized_text(
        shadow.knowledge_limits
    )

    require(
        (
            "do not know"
            in shadow_knowledge
            or "without understanding"
            in shadow_knowledge
        ),
        (
            "Shadow Operatives no longer preserve "
            "their canonical ignorance."
        ),
    )

    require(
        "documents" in shadow_knowledge,
        (
            "Shadow Operatives document knowledge "
            "boundary is missing."
        ),
    )

    pass_test(
        16,
        "Shadow Operatives remain ignorant executors",
    )

    # --------------------------------------------------------
    # TEST 17
    # Membership never implies omniscience.
    # --------------------------------------------------------

    for faction in factions:
        knowledge_text = normalized_text(
            faction.knowledge_limits
        )

        require(
            (
                "does not imply"
                in knowledge_text
            ),
            (
                "Faction membership knowledge "
                "boundary missing for "
                f"{faction.faction_id}."
            ),
        )

    pass_test(
        17,
        "faction membership does not imply omniscience",
    )

    # --------------------------------------------------------
    # TEST 18
    # No character-specific knowledge is encoded here.
    # --------------------------------------------------------

    raw_serialized = json.dumps(
        raw_data,
        ensure_ascii=False,
    ).lower()

    forbidden_character_ids = [
        "char_julian",
        "char_clara",
        "char_sterling",
        "char_sam",
        "char_rossi",
    ]

    require(
        all(
            character_id
            not in raw_serialized
            for character_id
            in forbidden_character_ids
        ),
        (
            "Character-specific knowledge leaked "
            "into faction registry."
        ),
    )

    pass_test(
        18,
        "character-specific knowledge remains separate",
    )

    # --------------------------------------------------------
    # TEST 19
    # Registry remains provider agnostic.
    # --------------------------------------------------------

    forbidden_provider_terms = [
        "openai",
        "elevenlabs",
        "midjourney",
        "runway",
        "veo",
        "kling",
        "digen",
    ]

    require(
        all(
            provider
            not in raw_serialized
            for provider
            in forbidden_provider_terms
        ),
        (
            "Provider-specific data leaked into "
            "canonical faction registry."
        ),
    )

    pass_test(
        19,
        "faction registry remains provider-agnostic",
    )

    # --------------------------------------------------------
    # TEST 20
    # Serialization is deterministic.
    # --------------------------------------------------------

    serialized_a = [
        faction.model_dump(
            mode="json"
        )
        for faction in load_factions()
    ]

    serialized_b = [
        faction.model_dump(
            mode="json"
        )
        for faction in load_factions()
    ]

    require(
        serialized_a == serialized_b,
        (
            "Faction registry serialization "
            "is not deterministic."
        ),
    )

    pass_test(
        20,
        "faction registry is deterministic",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print(
        "BATCH 14B.2-B CANON FACTION REGISTRY PASSED"
    )
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()