from pathlib import Path
import re


# ============================================================
# BATCH 14A.4 — OAKHAVEN CANON V1 REGRESSION VALIDATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
CANON_PATH = ROOT_DIR / "docs" / "canon" / "OAKHAVEN_CANON_V1.md"


def pass_test(number: int, description: str) -> None:
    print(
        f"TEST {number} — {description} → PASSED"
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> None:
    print()
    print(
        "BATCH 14A.4 — OAKHAVEN CANON V1 REGRESSION VALIDATION"
    )
    print("=" * 68)

    # --------------------------------------------------------
    # TEST 1 — canonical document exists
    # --------------------------------------------------------

    require(
        CANON_PATH.exists(),
        f"Canonical document does not exist: {CANON_PATH}",
    )

    require(
        CANON_PATH.is_file(),
        f"Canonical path is not a file: {CANON_PATH}",
    )

    pass_test(
        1,
        "canonical document exists",
    )

    canon = CANON_PATH.read_text(
        encoding="utf-8"
    )

    normalized = normalize(canon)

    # --------------------------------------------------------
    # TEST 2 — frozen canon metadata valid
    # --------------------------------------------------------

    required_metadata = [
        "# OAKHAVEN CANON v1.0",
        "**Canon Version:** 1.0",
        "**Universe:** OAKHAVEN",
        "**Present Day:** 2026",
        "**Status:** FROZEN",
    ]

    for item in required_metadata:
        require(
            item in canon,
            f"Missing frozen canon metadata: {item}",
        )

    require(
        "**Status:** FROZEN CANDIDATE" not in canon,
        "Canon is still marked as FROZEN CANDIDATE.",
    )

    pass_test(
        2,
        "frozen canon metadata valid",
    )

    # --------------------------------------------------------
    # TEST 3 — canon version is V1
    # --------------------------------------------------------

    require(
        "**Canon Version:** 1.0" in canon,
        "Canon version must be 1.0.",
    )

    require(
        "**Universe:** OAKHAVEN" in canon,
        "Canon universe must be OAKHAVEN.",
    )

    pass_test(
        3,
        "canon version is V1",
    )

    # --------------------------------------------------------
    # TEST 4 — world identity defined
    # --------------------------------------------------------

    required_world_terms = [
        "Historical mystery",
        "Crime mystery",
        "Noir",
        "Investigative drama",
        "grounded historical realism",
    ]

    for term in required_world_terms:
        require(
            term in canon,
            f"Missing world identity term: {term}",
        )

    pass_test(
        4,
        "world identity defined",
    )

    # --------------------------------------------------------
    # TEST 5 — historical layers defined
    # --------------------------------------------------------

    historical_layers = [
        "HISTORICAL LAYER I — 1856",
        "THE ILLEGAL FOUNDATION",
        "HISTORICAL LAYER II — 1930",
        "THE INDUSTRIAL COVER-UP",
        "HISTORICAL LAYER III — 1970s",
        "THE BUREAUCRATIC ERASURE",
        "HISTORICAL LAYER IV — 2026",
        "THE CURRENT TRAGEDIES",
    ]

    for layer in historical_layers:
        require(
            layer in canon,
            f"Missing historical layer: {layer}",
        )

    pass_test(
        5,
        "historical layers defined",
    )

    # --------------------------------------------------------
    # TEST 6 — all canonical locations registered
    # --------------------------------------------------------

    canonical_locations = [
        "LOC_OLD_DOCKS",
        "LOC_FISH_MARKET_ALLEY",
        "LOC_DISTRICT_POLICE",
        "LOC_THE_ANCHOR",
        "LOC_TENEMENTS",
        "LOC_PIKE_HILL_MANOR",
        "LOC_ST_JUDES",
        "LOC_CITY_ARCHIVES",
        "LOC_CENTRAL_DEPOT",
        "LOC_BLACKWOOD",
    ]

    for location_id in canonical_locations:
        require(
            location_id in canon,
            f"Missing canonical location: {location_id}",
        )

    pass_test(
        6,
        "all canonical locations registered",
    )

    # --------------------------------------------------------
    # TEST 7 — all 24 characters registered
    # --------------------------------------------------------

    canonical_characters = [
        "CHAR_ALISTAIR_PIKE",
        "CHAR_KIERAN_PIKE",
        "CHAR_VIVIENNE_CROSS",
        "CHAR_ELEANOR_HARROW_PIKE",
        "CHAR_ARCHIBALD_WHITMORE",
        "CHAR_THOMAS_STERLING",
        "CHAR_JULIAN_VANCE",
        "CHAR_MARCUS_BRODY",
        "CHAR_FRANK_OMALLEY",
        "CHAR_EVELYN_MERCER",
        "CHAR_ARTHUR_PENDELTON",
        "CHAR_CLARA_REN_RENDRA",
        "CHAR_CALEB_FINCH",
        "CHAR_NORA_HAYES",
        "CHAR_SILAS_THORNE",
        "CHAR_JONAH_MILLER",
        "CHAR_MARTHA_KOWALSKI",
        "CHAR_ELIOT_VALE",
        "CHAR_SAMUEL_BELL",
        "CHAR_LILA_MILLER",
        "CHAR_HARLAN_ROURKE",
        "CHAR_VICTOR_KANE",
        "CHAR_GIDEON_ROSSI",
        "CHAR_IRIS",
    ]

    require(
        len(canonical_characters) == 24,
        "Expected exactly 24 canonical character IDs.",
    )

    for character_id in canonical_characters:
        require(
            character_id in canon,
            f"Missing canonical character: {character_id}",
        )

    pass_test(
        7,
        "all 24 characters registered",
    )

    # --------------------------------------------------------
    # TEST 8 — canonical character IDs unique
    # --------------------------------------------------------

    registered_character_ids = re.findall(
        r"^## (CHAR_[A-Z0-9_]+)$",
        canon,
        flags=re.MULTILINE,
    )

    require(
        len(registered_character_ids) == 24,
        (
            "Expected exactly 24 registered character sections, "
            f"found {len(registered_character_ids)}."
        ),
    )

    require(
        len(registered_character_ids)
        == len(set(registered_character_ids)),
        "Duplicate canonical character IDs detected.",
    )

    require(
        set(registered_character_ids)
        == set(canonical_characters),
        (
            "Registered character IDs differ from the expected "
            "Canon v1 character registry."
        ),
    )

    pass_test(
        8,
        "canonical character registry is unique and stable",
    )

    # --------------------------------------------------------
    # TEST 9 — legacy renames recorded
    # --------------------------------------------------------

    rename_pairs = [
        ("Julian Pike", "Alistair Pike"),
        ("Archibald Sterling", "Archibald Whitmore"),
        ("Eleanor Vance-Pike", "Eleanor Harrow-Pike"),
        ("Gideon Finch", "Caleb Finch"),
        ("Eliot Vane", "Eliot Vale"),
        (
            'Martha "Mama" Kross',
            'Martha "Mama" Kowalski',
        ),
        (
            'Harlan "The Hook" Vance',
            'Harlan "The Hook" Rourke',
        ),
    ]

    for legacy_name, canonical_name in rename_pairs:
        require(
            legacy_name in canon,
            f"Missing legacy name: {legacy_name}",
        )

        require(
            canonical_name in canon,
            f"Missing canonical rename target: {canonical_name}",
        )

    pass_test(
        9,
        "legacy renames recorded",
    )

    # --------------------------------------------------------
    # TEST 10 — factions defined
    # --------------------------------------------------------

    factions = [
        "FACTION_PIKE_ELITE",
        "FACTION_OPD",
        "FACTION_CUSTODIANS",
        "FACTION_WATERFRONT",
        "FACTION_SHADOW_OPERATIVES",
    ]

    for faction in factions:
        require(
            faction in canon,
            f"Missing faction: {faction}",
        )

    pass_test(
        10,
        "canonical factions defined",
    )

    # --------------------------------------------------------
    # TEST 11 — knowledge boundaries defined
    # --------------------------------------------------------

    knowledge_dimensions = [
        "WORLD_TRUTH",
        "CHARACTER_KNOWLEDGE",
        "CHARACTER_BELIEF",
        "AUDIENCE_KNOWLEDGE",
    ]

    for dimension in knowledge_dimensions:
        require(
            dimension in canon,
            f"Missing knowledge dimension: {dimension}",
        )

    require(
        (
            "A character may not knowingly act upon information "
            "that they have not canonically learned."
        )
        in canon,
        "Character knowledge boundary rule is missing.",
    )

    require(
        (
            "Pipeline components must not transfer WORLD_TRUTH "
            "automatically into CHARACTER_KNOWLEDGE."
        )
        in canon,
        "World-truth isolation rule is missing.",
    )

    pass_test(
        11,
        "character knowledge boundaries defined",
    )

    # --------------------------------------------------------
    # TEST 12 — PL-1930 semantics defined
    # --------------------------------------------------------

    require(
        "Canonical Identifier: PL-1930" in canon,
        "PL-1930 is not defined as canonical.",
    )

    require(
        "A-1930" in canon,
        "Deprecated A-1930 identifier is not recorded.",
    )

    require(
        (
            "PL-1930 is not a magical single document "
            "that explains the entire mystery."
        )
        in canon,
        "PL-1930 anti-magic-document rule is missing.",
    )

    pass_test(
        12,
        "PL-1930 semantics defined",
    )

    # --------------------------------------------------------
    # TEST 13 — canon states defined
    # --------------------------------------------------------

    canon_states = [
        "HARD_CANON",
        "SOFT_CANON",
        "OPEN",
        "LEGACY",
        "DEPRECATED",
        "NON_CANON",
    ]

    for state in canon_states:
        require(
            state in canon,
            f"Missing canon state: {state}",
        )

    require(
        (
            "OPEN means that the answer has intentionally "
            "not yet been established."
        )
        in canon,
        "OPEN canon semantics are missing.",
    )

    pass_test(
        13,
        "truth/belief/open states defined",
    )

    # --------------------------------------------------------
    # TEST 14 — supernatural boundary defined
    # --------------------------------------------------------

    require(
        "Oakhaven is not a supernatural universe."
        in canon,
        "No-supernatural rule is missing.",
    )

    require(
        "The fog is not supernatural."
        in canon,
        "Fog supernatural boundary is missing.",
    )

    pass_test(
        14,
        "supernatural rule defined",
    )

    # --------------------------------------------------------
    # TEST 15 — EP001–EP004 narrative spine preserved
    # --------------------------------------------------------

    episodes = [
        "# 30. EP001 — A BED OF MUD",
        "# 31. EP002 — ERASED LINES",
        "# 32. EP003 — THE MISSING PAGES",
        "# 33. EP004 — THE COAL LINES",
    ]

    for episode in episodes:
        require(
            episode in canon,
            f"Missing revised episode spine: {episode}",
        )

    pass_test(
        15,
        "EP001–EP004 narrative spine preserved",
    )

    # --------------------------------------------------------
    # TEST 16 — deprecated lore explicitly recorded
    # --------------------------------------------------------

    deprecated_material = [
        "A-1930 as the active identifier",
        (
            "Julian's father appearing at the top "
            "of an original-landowner list"
        ),
        "unsupported exact deduction of three missing pages",
        (
            "Thomas Sterling as a simplistic "
            "all-knowing villain"
        ),
        (
            "Gideon Rossi possessing complete knowledge "
            "of the conspiracy"
        ),
    ]

    for item in deprecated_material:
        require(
            item in canon,
            f"Missing deprecated lore entry: {item}",
        )

    pass_test(
        16,
        "deprecated lore explicitly recorded",
    )

    # --------------------------------------------------------
    # TEST 17 — unresolved mysteries remain OPEN
    # --------------------------------------------------------

    require(
        "# 35. JULIAN'S FATHER" in canon,
        "Julian's father OPEN section is missing.",
    )

    father_section_start = canon.index(
        "# 35. JULIAN'S FATHER"
    )

    father_section_end = canon.index(
        "# 36. VISUAL RENDERING LANGUAGE"
    )

    father_section = canon[
        father_section_start:father_section_end
    ]

    require(
        "Status: OPEN" in father_section,
        "Julian's father must remain OPEN.",
    )

    forbidden_father_resolutions = [
        "Status: GUILTY",
        "Status: INNOCENT",
        "Status: PIKE_MEMBER",
    ]

    for resolution in forbidden_father_resolutions:
        require(
            resolution not in father_section,
            (
                "Julian's father was resolved prematurely: "
                f"{resolution}"
            ),
        )

    pass_test(
        17,
        "unresolved mysteries remain OPEN",
    )

    # --------------------------------------------------------
    # TEST 18 — production identity defined
    # --------------------------------------------------------

    production_sections = [
        "# 36. VISUAL RENDERING LANGUAGE",
        "# 37. CHARACTER VISUAL CONSISTENCY",
        "# 38. LOCATION VISUAL CONSISTENCY",
        "# 39. PROP VISUAL CONSISTENCY",
        "# 40. PERFORMANCE LANGUAGE",
        "# 41. CAMERA LANGUAGE",
        "# 42. IDENTITY VISIBILITY RULE",
        "# 43. SOUND LANGUAGE",
        "# 44. NON-DIALOGUE STORYTELLING",
        "# 45. EPISODE STRUCTURE",
    ]

    for section in production_sections:
        require(
            section in canon,
            f"Missing production identity section: {section}",
        )

    pass_test(
        18,
        "production identity defined",
    )

    # --------------------------------------------------------
    # TEST 19 — provider-specific voice IDs non-canonical
    # --------------------------------------------------------

    require(
        (
            "Provider-specific voice IDs are production "
            "references, not HARD_CANON."
        )
        in canon,
        "Provider-agnostic voice rule is missing.",
    )

    require(
        (
            "Specific ElevenLabs voice names or IDs may change "
            "without changing character canon."
        )
        in canon,
        "Voice-provider boundary is missing.",
    )

    pass_test(
        19,
        "provider-specific voice IDs are non-canonical",
    )

    # --------------------------------------------------------
    # TEST 20 — canon is formally frozen
    # --------------------------------------------------------

    require(
        "# 49. CANON CHANGE POLICY" in canon,
        "Canon change policy section is missing.",
    )

    require(
        "Canon v1.0 must not be silently retconned."
        in canon,
        "Silent-retcon prohibition is missing.",
    )

    require(
        "# 50. FREEZE DECLARATION" in canon,
        "Freeze declaration is missing.",
    )

    require(
        "This document is FROZEN." in canon,
        "Formal frozen declaration is missing.",
    )

    require(
        (
            "Batch 14A.4 canon freeze validation "
            "passed successfully."
        )
        in canon,
        "Freeze-validation declaration is missing.",
    )

    require(
        (
            "Changes to this canon must follow the Canon Change "
            "Policy defined in this document."
        )
        in canon,
        "Frozen canon change-control statement is missing.",
    )

    require(
        "This document is currently a FROZEN CANDIDATE."
        not in canon,
        "Obsolete frozen-candidate declaration remains.",
    )

    pass_test(
        20,
        "canon is formally frozen",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 68)
    print(
        "BATCH 14A.4 OAKHAVEN CANON V1 REGRESSION VALIDATION PASSED"
    )
    print("=" * 68)
    print()
    print("OAKHAVEN CANON v1.0")
    print("STATUS: FROZEN")
    print()


if __name__ == "__main__":
    main()