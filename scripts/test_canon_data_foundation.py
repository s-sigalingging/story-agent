import json
from pathlib import Path

from pydantic import ValidationError

from app.models.canon import (
    CanonDocumentStatus,
    CanonManifest,
    CanonStatus,
    WorldCanon,
)


# ============================================================
# BATCH 14B.2-A — CANON DATA FOUNDATION
# ============================================================


ROOT = Path(__file__).resolve().parents[1]

CANON_ROOT = (
    ROOT
    / "data"
    / "canon"
    / "oakhaven"
    / "v1"
)

MANIFEST_PATH = CANON_ROOT / "manifest.json"
WORLD_PATH = CANON_ROOT / "world.json"
TIMELINE_PATH = CANON_ROOT / "timeline.json"

AUTHORITY_PATH = (
    ROOT
    / "docs"
    / "canon"
    / "OAKHAVEN_CANON_V1.md"
)


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


def load_json(path: Path) -> dict:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ============================================================
# TEST RUNNER
# ============================================================


def main() -> None:
    print()
    print(
        "BATCH 14B.2-A — CANON DATA FOUNDATION"
    )
    print("=" * 68)

    # --------------------------------------------------------
    # TEST 1
    # Foundation files exist.
    # --------------------------------------------------------

    require(
        MANIFEST_PATH.is_file(),
        "manifest.json does not exist.",
    )

    require(
        WORLD_PATH.is_file(),
        "world.json does not exist.",
    )

    require(
        TIMELINE_PATH.is_file(),
        "timeline.json does not exist.",
    )

    pass_test(
        1,
        "canon foundation files exist",
    )

    # --------------------------------------------------------
    # TEST 2
    # Human-readable authority exists.
    # --------------------------------------------------------

    require(
        AUTHORITY_PATH.is_file(),
        (
            "Frozen human-readable canon "
            "authority does not exist."
        ),
    )

    pass_test(
        2,
        "human-readable canon authority exists",
    )

    # --------------------------------------------------------
    # Load source data.
    # --------------------------------------------------------

    manifest_data = load_json(
        MANIFEST_PATH
    )

    world_data = load_json(
        WORLD_PATH
    )

    timeline_data = load_json(
        TIMELINE_PATH
    )

    # --------------------------------------------------------
    # TEST 3
    # Manifest validates against domain model.
    # --------------------------------------------------------

    try:
        manifest = CanonManifest.model_validate(
            manifest_data
        )
    except ValidationError as exc:
        raise AssertionError(
            "manifest.json failed CanonManifest "
            "validation."
        ) from exc

    pass_test(
        3,
        "manifest validates against domain model",
    )

    # --------------------------------------------------------
    # TEST 4
    # World validates against domain model.
    # --------------------------------------------------------

    try:
        world = WorldCanon.model_validate(
            world_data
        )
    except ValidationError as exc:
        raise AssertionError(
            "world.json failed WorldCanon "
            "validation."
        ) from exc

    pass_test(
        4,
        "world validates against domain model",
    )

    # --------------------------------------------------------
    # TEST 5
    # Canon identity is stable.
    # --------------------------------------------------------

    require(
        manifest.universe_id
        == "UNIVERSE_OAKHAVEN",
        "Unexpected universe ID.",
    )

    require(
        manifest.universe_name
        == "OAKHAVEN",
        "Unexpected universe name.",
    )

    require(
        world.world_id
        == "WORLD_OAKHAVEN",
        "Unexpected world ID.",
    )

    require(
        world.name == "Oakhaven",
        "Unexpected world name.",
    )

    pass_test(
        5,
        "Oakhaven identity is stable",
    )

    # --------------------------------------------------------
    # TEST 6
    # Canon version is V1.
    # --------------------------------------------------------

    require(
        manifest.canon_version == "1.0",
        "Unexpected canon version.",
    )

    require(
        timeline_data.get(
            "canon_version"
        ) == manifest.canon_version,
        (
            "Timeline canon version does not "
            "match manifest."
        ),
    )

    pass_test(
        6,
        "canon version is consistent",
    )

    # --------------------------------------------------------
    # TEST 7
    # Canon is formally frozen.
    # --------------------------------------------------------

    require(
        manifest.document_status
        == CanonDocumentStatus.FROZEN,
        "Machine-readable canon is not FROZEN.",
    )

    pass_test(
        7,
        "machine-readable canon is frozen",
    )

    # --------------------------------------------------------
    # TEST 8
    # Authority path resolves.
    # --------------------------------------------------------

    expected_authority = (
        "docs/canon/OAKHAVEN_CANON_V1.md"
    )

    require(
        manifest.authority_document
        == expected_authority,
        "Unexpected authority document.",
    )

    resolved_authority = (
        ROOT / manifest.authority_document
    )

    require(
        resolved_authority.is_file(),
        (
            "Manifest authority_document does "
            "not resolve to a real file."
        ),
    )

    pass_test(
        8,
        "manifest authority resolves correctly",
    )

    # --------------------------------------------------------
    # TEST 9
    # Present day remains 2026.
    # --------------------------------------------------------

    require(
        manifest.present_day == 2026,
        "Oakhaven present day changed.",
    )

    pass_test(
        9,
        "present day remains 2026",
    )

    # --------------------------------------------------------
    # TEST 10
    # Exactly four historical layers exist.
    # --------------------------------------------------------

    require(
        len(world.historical_layers) == 4,
        (
            "Oakhaven V1 must contain exactly "
            "four historical layers."
        ),
    )

    pass_test(
        10,
        "four historical layers are registered",
    )

    # --------------------------------------------------------
    # TEST 11
    # Historical layer IDs are stable.
    # --------------------------------------------------------

    expected_layer_ids = [
        "HIST_1856",
        "HIST_1930",
        "HIST_1970S",
        "HIST_2026_PRESENT",
    ]

    actual_layer_ids = [
        layer.layer_id
        for layer in world.historical_layers
    ]

    require(
        actual_layer_ids
        == expected_layer_ids,
        (
            "Historical layer registry or "
            "ordering changed."
        ),
    )

    pass_test(
        11,
        "historical layer registry is stable",
    )

    # --------------------------------------------------------
    # TEST 12
    # Historical layer names are stable.
    # --------------------------------------------------------

    expected_names = [
        "The Illegal Foundation",
        "The Industrial Cover-Up",
        "The Bureaucratic Erasure",
        "The Current Tragedies",
    ]

    actual_names = [
        layer.name
        for layer in world.historical_layers
    ]

    require(
        actual_names == expected_names,
        "Historical layer names changed.",
    )

    pass_test(
        12,
        "historical layer identities are stable",
    )

    # --------------------------------------------------------
    # TEST 13
    # Historical layers remain hard canon.
    # --------------------------------------------------------

    require(
        all(
            layer.status
            == CanonStatus.HARD_CANON
            for layer
            in world.historical_layers
        ),
        (
            "One or more historical layers "
            "are not HARD_CANON."
        ),
    )

    pass_test(
        13,
        "historical layers remain hard canon",
    )

    # --------------------------------------------------------
    # TEST 14
    # Timeline identifies the correct universe.
    # --------------------------------------------------------

    require(
        timeline_data.get(
            "timeline_id"
        ) == "TIMELINE_OAKHAVEN_V1",
        "Unexpected timeline ID.",
    )

    require(
        timeline_data.get(
            "universe_id"
        ) == manifest.universe_id,
        (
            "Timeline universe does not match "
            "manifest universe."
        ),
    )

    pass_test(
        14,
        "timeline identity is valid",
    )

    # --------------------------------------------------------
    # TEST 15
    # Timeline references only registered layers.
    # --------------------------------------------------------

    timeline_layer_ids = (
        timeline_data.get(
            "historical_layer_order",
            [],
        )
    )

    registered_layer_ids = {
        layer.layer_id
        for layer in world.historical_layers
    }

    require(
        all(
            layer_id
            in registered_layer_ids
            for layer_id
            in timeline_layer_ids
        ),
        (
            "Timeline references an unknown "
            "historical layer."
        ),
    )

    pass_test(
        15,
        "timeline references registered layers only",
    )

    # --------------------------------------------------------
    # TEST 16
    # Timeline contains every historical layer once.
    # --------------------------------------------------------

    require(
        len(timeline_layer_ids)
        == len(set(timeline_layer_ids)),
        (
            "Timeline contains duplicate "
            "historical layers."
        ),
    )

    require(
        set(timeline_layer_ids)
        == registered_layer_ids,
        (
            "Timeline does not contain exactly "
            "the registered historical layers."
        ),
    )

    pass_test(
        16,
        "timeline covers every historical layer once",
    )

    # --------------------------------------------------------
    # TEST 17
    # Timeline order is canonical.
    # --------------------------------------------------------

    require(
        timeline_layer_ids
        == expected_layer_ids,
        "Canonical historical order changed.",
    )

    pass_test(
        17,
        "historical chronology is canonical",
    )

    # --------------------------------------------------------
    # TEST 18
    # Timeline does not duplicate historical lore.
    # --------------------------------------------------------

    forbidden_timeline_fields = {
        "description",
        "status",
        "established_truths",
        "unresolved_questions",
        "historical_layers",
    }

    require(
        not (
            forbidden_timeline_fields
            & set(timeline_data.keys())
        ),
        (
            "timeline.json duplicates historical "
            "lore owned by world.json."
        ),
    )

    pass_test(
        18,
        "timeline remains a reference index",
    )

    # --------------------------------------------------------
    # TEST 19
    # Narrative principle is preserved.
    # --------------------------------------------------------

    require(
        world.narrative_principle
        == (
            "No generation knows the "
            "complete truth."
        ),
        (
            "Core narrative knowledge "
            "principle changed."
        ),
    )

    pass_test(
        19,
        "knowledge-boundary principle is preserved",
    )

    # --------------------------------------------------------
    # TEST 20
    # Foundation serialization is deterministic.
    # --------------------------------------------------------

    manifest_a = (
        CanonManifest.model_validate(
            manifest_data
        ).model_dump(
            mode="json"
        )
    )

    manifest_b = (
        CanonManifest.model_validate(
            load_json(MANIFEST_PATH)
        ).model_dump(
            mode="json"
        )
    )

    world_a = (
        WorldCanon.model_validate(
            world_data
        ).model_dump(
            mode="json"
        )
    )

    world_b = (
        WorldCanon.model_validate(
            load_json(WORLD_PATH)
        ).model_dump(
            mode="json"
        )
    )

    require(
        manifest_a == manifest_b,
        (
            "Manifest validation is "
            "not deterministic."
        ),
    )

    require(
        world_a == world_b,
        (
            "World validation is "
            "not deterministic."
        ),
    )

    pass_test(
        20,
        "canon foundation is deterministic",
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 68)
    print(
        "BATCH 14B.2-A CANON DATA FOUNDATION PASSED"
    )
    print("=" * 68)
    print()


if __name__ == "__main__":
    main()