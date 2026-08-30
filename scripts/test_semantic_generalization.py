import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


# ================================================================
# CONFIGURATION
# ================================================================

INPUT_DIR = Path(
    "data/test_outputs/batch10d1"
)

OUTPUT_FILE = Path(
    "data/test_outputs/"
    "batch10d2_semantic_audit.json"
)


# ================================================================
# EXPECTED SEMANTICS
# ================================================================

TEST_CASES: Dict[
    str,
    Dict[str, Any]
] = {

    # ------------------------------------------------------------
    # A — COMEDY / IMAGE PROP
    # ------------------------------------------------------------

    "A_COMEDY_IMAGE": {
        "file": (
            "a_comedy_image_orchestration.json"
        ),
        "expected_characters": [
            "Mira",
        ],
        "expected_location": (
            "Sunny Kitchen"
        ),
        "expected_prop_name_contains": [
            "photograph",
        ],
        "expected_primary_name": (
            "Mira"
        ),
        "expected_primary_interaction": (
            "STUDY"
        ),
        "expected_modalities": {
            "IMAGE",
        },
        "forbidden_modalities": {
            "TEXT",
            "MARKING",
        },
    },

    # ------------------------------------------------------------
    # B — SCI-FI / TEXT + MARKING
    # ------------------------------------------------------------

    "B_SCIFI_TEXT": {
        "file": (
            "b_scifi_text_orchestration.json"
        ),
        "expected_characters": [
            "Lena",
        ],
        "expected_location": (
            "Reactor Control Room"
        ),
        "expected_prop_name_contains": [
            "warning",
            "panel",
        ],
        "expected_primary_name": (
            "Lena"
        ),
        "expected_primary_interaction": (
            "STUDY"
        ),
        "required_content_signals": {
            "MARKING",
        },
        "expect_text_sensitive": True,
    },

    # ------------------------------------------------------------
    # C — ACTION / MARKING
    # ------------------------------------------------------------

    "C_ACTION_MARKING": {
        "file": (
            "c_action_marking_orchestration.json"
        ),
        "expected_characters": [
            "Nadia",
        ],
        "expected_location": (
            "Abandoned Warehouse"
        ),
        "expected_prop_name_contains": [
            "container",
        ],
        "expected_primary_name": (
            "Nadia"
        ),
        "expected_modalities": {
            "MARKING",
        },
        "expect_text_sensitive": True,
    },

    # ------------------------------------------------------------
    # D — ORDINARY PROP
    # ------------------------------------------------------------

    "D_ORDINARY_PROP": {
        "file": (
            "d_ordinary_prop_orchestration.json"
        ),
        "expected_characters": [
            "Theo",
        ],
        "expected_location": (
            "Small Kitchen"
        ),
        "expected_prop_name_contains": [
            "mug",
        ],
        "expected_primary_name": (
            "Theo"
        ),
        "expected_modalities": set(),
        "expect_text_sensitive": False,
        "expect_no_content_prompt_rules": True,
    },

    # ------------------------------------------------------------
    # E — MULTI ENTITY
    # ------------------------------------------------------------

    "E_MULTI_ENTITY": {
        "file": (
            "e_multi_entity_orchestration.json"
        ),
        "expected_characters": [
            "Arin",
            "Sora",
        ],
        "expected_location": (
            "Explorer Cabin"
        ),
        "expected_primary_name": (
            "Arin"
        ),
        "expected_primary_interaction": (
            "STUDY"
        ),
        "expected_supporting": {
            "Sora": {
                "role": (
                    "SUPPORTING_PRESENCE"
                ),
                "allowed_interactions": {
                    "STAND_BESIDE",
                    "WATCH",
                },
            }
        },

        # These are intentionally stricter because
        # 10D.1 already exposed possible extraction issues.
        "expected_prop_concepts": [
            "map",
            "compass",
        ],
    },
}


# ================================================================
# GENERIC HELPERS
# ================================================================

def normalize(
    value: Optional[str],
) -> str:

    return (
        value
        or ""
    ).strip().lower()


def get_stage(
    result: Dict[str, Any],
    stage_name: str,
) -> Dict[str, Any]:

    for stage in result.get(
        "stages",
        []
    ):

        if (
            stage.get("stage")
            == stage_name
        ):

            return (
                stage.get(
                    "details",
                    {}
                )
            )

    return {}


def first_scene(
    stage: Dict[str, Any],
) -> Dict[str, Any]:

    scenes = (
        stage.get(
            "scenes",
            []
        )
    )

    if not scenes:
        return {}

    return scenes[0]


def add_check(
    checks: List[
        Dict[str, Any]
    ],
    name: str,
    passed: bool,
    expected: Any = None,
    actual: Any = None,
    severity: str = "ERROR",
):

    checks.append({
        "check": name,
        "status": (
            "PASSED"
            if passed
            else "FAILED"
        ),
        "severity": (
            "NONE"
            if passed
            else severity
        ),
        "expected": expected,
        "actual": actual,
    })


# ================================================================
# ENTITY AUDIT
# ================================================================

def audit_entities(
    result: Dict[str, Any],
    config: Dict[str, Any],
    checks: List[
        Dict[str, Any]
    ],
):

    entity_stage = get_stage(
        result,
        "ENTITY_ANALYSIS",
    )

    scene_stage = get_stage(
        result,
        "SCENE_ANALYSIS",
    )

    scene = first_scene(
        scene_stage
    )

    registry = (
        entity_stage.get(
            "registry",
            {}
        )
    )

    actual_characters = {
        item.get(
            "name"
        )
        for item
        in (
            registry.get(
                "characters",
                {}
            ).values()
        )
    }

    expected_characters = set(
        config.get(
            "expected_characters",
            []
        )
    )

    add_check(
        checks,
        "characters_resolved",
        expected_characters.issubset(
            actual_characters
        ),
        sorted(
            expected_characters
        ),
        sorted(
            actual_characters
        ),
    )

    actual_location = (
        scene.get(
            "location"
        )
    )

    expected_location = (
        config.get(
            "expected_location"
        )
    )

    add_check(
        checks,
        "location_resolved",
        (
            normalize(
                actual_location
            )
            ==
            normalize(
                expected_location
            )
        ),
        expected_location,
        actual_location,
    )


# ================================================================
# PROP EXTRACTION AUDIT
# ================================================================

def audit_props(
    result: Dict[str, Any],
    config: Dict[str, Any],
    checks: List[
        Dict[str, Any]
    ],
):

    prop_stage = get_stage(
        result,
        "PROP_ANALYSIS",
    )

    scene = first_scene(
        prop_stage
    )

    resolved_props = (
        scene.get(
            "resolved_props",
            []
        )
    )

    normalized_props = [
        normalize(
            item
        )
        for item
        in resolved_props
    ]

    expected_contains = (
        config.get(
            "expected_prop_name_contains",
            []
        )
    )

    for token in expected_contains:

        matched = any(
            normalize(
                token
            )
            in prop
            for prop in normalized_props
        )

        add_check(
            checks,
            (
                "prop_contains_"
                f"{normalize(token)}"
            ),
            matched,
            token,
            resolved_props,
        )

    expected_concepts = (
        config.get(
            "expected_prop_concepts",
            []
        )
    )

    for concept in expected_concepts:

        matched = any(
            normalize(
                concept
            )
            in prop
            for prop in normalized_props
        )

        add_check(
            checks,
            (
                "prop_concept_"
                f"{normalize(concept)}"
            ),
            matched,
            concept,
            resolved_props,
            severity="SEMANTIC_DEFECT",
        )

    # ------------------------------------------------------------
    # PROP NAME QUALITY
    # ------------------------------------------------------------

    suspicious_tail_terms = {
        "a",
        "an",
        "the",
        "across",
        "inside",
        "on",
        "at",
        "while",
        "with",
    }

    for prop in resolved_props:

        words = (
            normalize(
                prop
            ).split()
        )

        if not words:
            continue

        suspicious = (
            words[-1]
            in suspicious_tail_terms
        )

        add_check(
            checks,
            (
                "clean_prop_name:"
                f"{prop}"
            ),
            not suspicious,
            (
                "Prop name should end on "
                "the object phrase."
            ),
            prop,
            severity="SEMANTIC_DEFECT",
        )


# ================================================================
# CHARACTER ROLE AUDIT
# ================================================================

def audit_roles(
    result: Dict[str, Any],
    config: Dict[str, Any],
    checks: List[
        Dict[str, Any]
    ],
):

    role_stage = get_stage(
        result,
        "CHARACTER_ROLE_ANALYSIS",
    )

    scene = first_scene(
        role_stage
    )

    expected_primary = (
        config.get(
            "expected_primary_name"
        )
    )

    actual_primary = (
        scene.get(
            "primary_subject_name"
        )
    )

    add_check(
        checks,
        "primary_subject",
        (
            normalize(
                expected_primary
            )
            ==
            normalize(
                actual_primary
            )
        ),
        expected_primary,
        actual_primary,
    )

    roles = {
        item.get("name"): item
        for item
        in scene.get(
            "characters",
            []
        )
    }

    expected_interaction = (
        config.get(
            "expected_primary_interaction"
        )
    )

    if expected_interaction:

        primary_role = (
            roles.get(
                actual_primary,
                {}
            )
        )

        actual_interaction = (
            primary_role.get(
                "interaction"
            )
        )

        add_check(
            checks,
            "primary_interaction",
            (
                actual_interaction
                ==
                expected_interaction
            ),
            expected_interaction,
            actual_interaction,
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )

    for (
        character_name,
        expected,
    ) in (
        config.get(
            "expected_supporting",
            {}
        ).items()
    ):

        actual = (
            roles.get(
                character_name,
                {}
            )
        )

        add_check(
            checks,
            (
                "supporting_role:"
                f"{character_name}"
            ),
            (
                actual.get("role")
                ==
                expected["role"]
            ),
            expected["role"],
            actual.get(
                "role"
            ),
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )

        allowed = (
            expected.get(
                "allowed_interactions",
                set(),
            )
        )

        if allowed:

            actual_interaction = (
                actual.get(
                    "interaction"
                )
            )

            add_check(
                checks,
                (
                    "supporting_interaction:"
                    f"{character_name}"
                ),
                (
                    actual_interaction
                    in allowed
                ),
                sorted(
                    allowed
                ),
                actual_interaction,
                severity=(
                    "SEMANTIC_DEFECT"
                ),
            )


# ================================================================
# PROP CONTENT AUDIT
# ================================================================

def audit_prop_content(
    result: Dict[str, Any],
    config: Dict[str, Any],
    checks: List[
        Dict[str, Any]
    ],
):

    content_stage = get_stage(
        result,
        "PROP_CONTENT_ANALYSIS",
    )

    scene = first_scene(
        content_stage
    )

    props = (
        scene.get(
            "props",
            []
        )
    )

    actual_modalities = set()

    actual_text_sensitive = False

    for prop in props:

        actual_modalities.update(
            prop.get(
                "content_modalities",
                []
            )
        )

        if prop.get(
            "text_sensitive"
        ):

            actual_text_sensitive = True

    if (
        "expected_modalities"
        in config
    ):

        expected = (
            config[
                "expected_modalities"
            ]
        )

        add_check(
            checks,
            "content_modalities",
            (
                actual_modalities
                ==
                expected
            ),
            sorted(
                expected
            ),
            sorted(
                actual_modalities
            ),
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )

    required_signals = (
        config.get(
            "required_content_signals",
            set(),
        )
    )

    for signal in required_signals:

        add_check(
            checks,
            (
                "required_content_signal:"
                f"{signal}"
            ),
            (
                signal
                in actual_modalities
            ),
            signal,
            sorted(
                actual_modalities
            ),
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )

    forbidden = (
        config.get(
            "forbidden_modalities",
            set(),
        )
    )

    for signal in forbidden:

        add_check(
            checks,
            (
                "forbidden_content_signal:"
                f"{signal}"
            ),
            (
                signal
                not in actual_modalities
            ),
            (
                f"{signal} absent"
            ),
            sorted(
                actual_modalities
            ),
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )

    if (
        "expect_text_sensitive"
        in config
    ):

        expected = (
            config[
                "expect_text_sensitive"
            ]
        )

        add_check(
            checks,
            "text_sensitive",
            (
                actual_text_sensitive
                is expected
            ),
            expected,
            actual_text_sensitive,
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )


# ================================================================
# PRODUCTION / PROMPT AUDIT
# ================================================================

def audit_prompts(
    result: Dict[str, Any],
    config: Dict[str, Any],
    checks: List[
        Dict[str, Any]
    ],
):

    prompt_stage = get_stage(
        result,
        "PRODUCTION_PROMPTS",
    )

    scene = first_scene(
        prompt_stage
    )

    prompts = (
        scene.get(
            "prompts",
            []
        )
    )

    all_image = " ".join(
        item.get(
            "image_prompt",
            ""
        )
        for item in prompts
    )

    all_video = " ".join(
        item.get(
            "video_prompt",
            ""
        )
        for item in prompts
    )

    all_negative = " ".join(
        item.get(
            "negative_prompt",
            ""
        )
        or ""
        for item in prompts
    )

    if config.get(
        "expect_no_content_prompt_rules"
    ):

        add_check(
            checks,
            (
                "ordinary_prop_no_image_"
                "content_rules"
            ),
            (
                "Prop content requirements:"
                not in all_image
            ),
            False,
            (
                "Prop content requirements:"
                in all_image
            ),
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )

        add_check(
            checks,
            (
                "ordinary_prop_no_video_"
                "content_rules"
            ),
            (
                "Prop content preservation:"
                not in all_video
            ),
            False,
            (
                "Prop content preservation:"
                in all_video
            ),
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )

        content_terms = [
            "changing text",
            "changing markings",
            "image reinterpretation",
        ]

        leaked = [
            term
            for term in content_terms
            if term in all_negative
        ]

        add_check(
            checks,
            (
                "ordinary_prop_no_negative_"
                "semantic_leakage"
            ),
            not leaked,
            [],
            leaked,
            severity=(
                "SEMANTIC_DEFECT"
            ),
        )


# ================================================================
# SINGLE CASE
# ================================================================

def audit_case(
    case_id: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:

    path = (
        INPUT_DIR
        /
        config["file"]
    )

    if not path.exists():

        return {
            "case_id": case_id,
            "status": "FAILED",
            "errors": [
                (
                    "Missing orchestration "
                    f"file: {path}"
                )
            ],
            "checks": [],
        }

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:

        result = json.load(f)

    checks: List[
        Dict[str, Any]
    ] = []

    add_check(
        checks,
        "pipeline_status",
        (
            result.get(
                "status"
            )
            ==
            "WAITING_HUMAN_APPROVAL"
        ),
        "WAITING_HUMAN_APPROVAL",
        result.get(
            "status"
        ),
    )

    audit_entities(
        result,
        config,
        checks,
    )

    audit_props(
        result,
        config,
        checks,
    )

    audit_roles(
        result,
        config,
        checks,
    )

    audit_prop_content(
        result,
        config,
        checks,
    )

    audit_prompts(
        result,
        config,
        checks,
    )

    failed_checks = [
        item
        for item in checks
        if item["status"]
        == "FAILED"
    ]

    return {
        "case_id": case_id,
        "status": (
            "PASSED"
            if not failed_checks
            else "FAILED"
        ),
        "failed_count": (
            len(
                failed_checks
            )
        ),
        "checks": checks,
    }


# ================================================================
# MAIN
# ================================================================

def main() -> int:

    results = []

    print()
    print(
        "BATCH 10D.2 — "
        "SEMANTIC GENERALIZATION AUDIT"
    )
    print()

    for (
        case_id,
        config,
    ) in TEST_CASES.items():

        result = (
            audit_case(
                case_id,
                config,
            )
        )

        results.append(
            result
        )

        print(
            case_id,
            "→",
            result["status"],
        )

        for check in (
            result.get(
                "checks",
                []
            )
        ):

            if (
                check["status"]
                == "FAILED"
            ):

                print(
                    "  FAIL:",
                    check["check"],
                )

                print(
                    "    expected:",
                    check["expected"],
                )

                print(
                    "    actual:",
                    check["actual"],
                )

    failed_cases = [
        item
        for item in results
        if item["status"]
        == "FAILED"
    ]

    failed_checks = [
        check
        for result in results
        for check
        in result.get(
            "checks",
            []
        )
        if check["status"]
        == "FAILED"
    ]

    defects_by_severity: Dict[
        str,
        int
    ] = {}

    for check in failed_checks:

        severity = (
            check.get(
                "severity",
                "ERROR",
            )
        )

        defects_by_severity[
            severity
        ] = (
            defects_by_severity.get(
                severity,
                0,
            )
            + 1
        )

    output = {
        "batch": "10D.2",
        "status": (
            "PASSED"
            if not failed_cases
            else "DEFECTS_FOUND"
        ),
        "total_cases": (
            len(results)
        ),
        "passed_cases": (
            len(results)
            -
            len(failed_cases)
        ),
        "failed_cases": (
            len(failed_cases)
        ),
        "failed_checks": (
            len(failed_checks)
        ),
        "defects_by_severity": (
            defects_by_severity
        ),
        "cases": results,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 10D.2 SUMMARY"
    )
    print(
        "========================================"
    )

    print(
        "Cases:",
        len(results),
    )

    print(
        "Cases with defects:",
        len(failed_cases),
    )

    print(
        "Failed semantic checks:",
        len(failed_checks),
    )

    print(
        "Defects by severity:",
        defects_by_severity,
    )

    print()

    print(
        "Saved:",
        OUTPUT_FILE,
    )

    print()

    # A semantic audit finding defects is not a harness crash.
    # Exit successfully so the complete report is always produced.
    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )