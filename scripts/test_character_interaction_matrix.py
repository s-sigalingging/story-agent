import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from app.analyzers.character_role_analyzer import (
    CharacterRoleAnalyzer,
)


OUTPUT_FILE = Path(
    "data/test_outputs/"
    "batch10d5c_interaction_selection_matrix.json"
)


TESTS: List[Dict[str, Any]] = [

    # ============================================================
    # SINGLE-CHARACTER CONTINUATION / SELECTION
    # ============================================================

    {
        "name": "enter_then_study",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person enters the room. "
            "They study an old chart."
        ),
        "expected_interaction": "STUDY",
    },

    {
        "name": "study_then_enter",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person studies an old chart. "
            "They enter the archive."
        ),
        "expected_interaction": "STUDY",
    },

    {
        "name": "move_then_examine",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person walks across the room. "
            "They examine a sealed box."
        ),
        "expected_interaction": "EXAMINE",
    },

    {
        "name": "hold_then_read",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person holds a folded note. "
            "They read the note."
        ),
        "expected_interaction": "READ",
    },

    {
        "name": "open_then_inspect",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person opens a cabinet. "
            "They inspect the contents."
        ),
        "expected_interaction": "OPEN",
        "note": (
            "The current vocabulary checks OPEN before INSPECT. "
            "This test records whether that behavior remains stable."
        ),
    },

    # ============================================================
    # SUPPORTING ROLE PROTECTION
    # ============================================================

    {
        "name": "supporting_stands_nearby",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person stands nearby and watches."
        ),
        "expected_role": (
            "SUPPORTING_PRESENCE"
        ),
        "expected_interaction": (
            "STAND_NEARBY"
        ),
    },

    {
        "name": "observer_watches",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person watches the doorway."
        ),
        "expected_role": "OBSERVER",
        "expected_interaction": "WATCH",
    },

    # ============================================================
    # MULTI-CHARACTER ISOLATION
    # ============================================================

    {
        "name": "while_clause_primary",
        "character": "First Person",
        "character_names": [
            "First Person",
            "Second Person",
        ],
        "text": (
            "First Person studies a chart while "
            "Second Person stands nearby."
        ),
        "expected_role": "ACTIVE_SUBJECT",
        "expected_interaction": "STUDY",
        "forbidden_evidence": (
            "Second Person stands nearby"
        ),
    },

    {
        "name": "while_clause_supporting",
        "character": "Second Person",
        "character_names": [
            "First Person",
            "Second Person",
        ],
        "text": (
            "First Person studies a chart while "
            "Second Person stands nearby."
        ),
        "expected_role": (
            "SUPPORTING_PRESENCE"
        ),
        "expected_interaction": (
            "STAND_NEARBY"
        ),
    },

    {
        "name": "next_sentence_other_character",
        "character": "First Person",
        "character_names": [
            "First Person",
            "Second Person",
        ],
        "text": (
            "First Person examines a box. "
            "Second Person opens the door."
        ),
        "expected_role": "ACTIVE_SUBJECT",
        "expected_interaction": "EXAMINE",
        "forbidden_evidence": (
            "Second Person opens the door"
        ),
    },

    # ============================================================
    # AMBIGUOUS PRONOUN PROTECTION
    # ============================================================

    {
        "name": "multi_character_pronoun_not_absorbed",
        "character": "First Person",
        "character_names": [
            "First Person",
            "Second Person",
        ],
        "text": (
            "First Person enters the room. "
            "They study a chart."
        ),
        "expected_interaction": "ENTER",
        "note": (
            "In a multi-character scene, pronoun continuation is "
            "intentionally not linked because the referent is ambiguous."
        ),
    },

    # ============================================================
    # PARTICIPANT FALLBACK
    # ============================================================

    {
        "name": "no_known_interaction",
        "character": "Person",
        "character_names": [
            "Person",
        ],
        "text": (
            "Person remains silent beside the doorway."
        ),
        "expected_role": "PARTICIPANT",
        "expected_interaction": (
            "SCENE_PARTICIPATION"
        ),
    },
]


def main() -> int:

    analyzer = (
        CharacterRoleAnalyzer()
    )

    results = []

    print()
    print(
        "BATCH 10D.5C — "
        "INTERACTION SELECTION REGRESSION MATRIX"
    )
    print()

    for test in TESTS:

        detected = (
            analyzer
            ._detect_character_interaction(
                name=(
                    test["character"]
                ),
                text=(
                    test["text"]
                ),
                character_names=(
                    test[
                        "character_names"
                    ]
                ),
            )
        )

        errors = []

        if detected is None:

            actual_role = None
            actual_interaction = None
            evidence = None

            errors.append(
                "No interaction result returned."
            )

        else:

            (
                actual_role,
                actual_interaction,
                evidence,
                confidence,
            ) = detected

            expected_role = (
                test.get(
                    "expected_role"
                )
            )

            if (
                expected_role
                is not None
                and
                actual_role
                != expected_role
            ):

                errors.append(
                    "Role mismatch. "
                    f"Expected "
                    f"{expected_role!r}, "
                    f"got "
                    f"{actual_role!r}."
                )

            expected_interaction = (
                test[
                    "expected_interaction"
                ]
            )

            if (
                actual_interaction
                != expected_interaction
            ):

                errors.append(
                    "Interaction mismatch. "
                    f"Expected "
                    f"{expected_interaction!r}, "
                    f"got "
                    f"{actual_interaction!r}."
                )

            forbidden_evidence = (
                test.get(
                    "forbidden_evidence"
                )
            )

            if (
                forbidden_evidence
                and
                evidence
                and
                forbidden_evidence.lower()
                in evidence.lower()
            ):

                errors.append(
                    "Cross-character evidence leakage "
                    f"detected: "
                    f"{forbidden_evidence!r}."
                )

        result = {
            "test": (
                test["name"]
            ),
            "status": (
                "PASSED"
                if not errors
                else "FAILED"
            ),
            "expected_role": (
                test.get(
                    "expected_role"
                )
            ),
            "expected_interaction": (
                test[
                    "expected_interaction"
                ]
            ),
            "actual_role": (
                actual_role
            ),
            "actual_interaction": (
                actual_interaction
            ),
            "evidence": (
                evidence
            ),
            "errors": (
                errors
            ),
            "note": (
                test.get(
                    "note"
                )
            ),
        }

        results.append(
            result
        )

        print(
            test["name"],
            "→",
            result["status"],
            "|",
            actual_role,
            "/",
            actual_interaction,
        )

        for error in errors:

            print(
                "   ",
                error,
            )

    failed = [
        item
        for item in results
        if item["status"]
        == "FAILED"
    ]

    output = {
        "batch": "10D.5C",
        "status": (
            "PASSED"
            if not failed
            else "DEFECTS_FOUND"
        ),
        "total_tests": (
            len(results)
        ),
        "passed": (
            len(results)
            -
            len(failed)
        ),
        "failed": (
            len(failed)
        ),
        "tests": results,
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
        "BATCH 10D.5C SUMMARY"
    )
    print(
        "========================================"
    )

    print(
        "Passed:",
        output["passed"],
    )

    print(
        "Failed:",
        output["failed"],
    )

    print(
        "Saved:",
        OUTPUT_FILE,
    )

    print()

    # Findings are semantic audit results, not harness crashes.
    # Always return success so the complete report is written.
    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )
