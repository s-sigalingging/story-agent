import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from app.analyzers.prop_analyzer import (
    PropAnalyzer,
)
from app.models.episode import (
    Episode,
)


OUTPUT_FILE = Path(
    "data/test_outputs/"
    "batch10d4e_prop_regression_matrix.json"
)


TESTS: List[Dict[str, Any]] = [

    # ============================================================
    # BASIC PHYSICAL PROP EXTRACTION
    # ============================================================

    {
        "name": "basic_box",
        "visual_description": (
            "A person examines a small wooden box."
        ),
        "expected_exact": [
            "Small Wooden Box"
        ],
    },

    {
        "name": "basic_mug",
        "visual_description": (
            "A person holds a plain ceramic mug."
        ),
        "expected_exact": [
            "Plain Ceramic Mug"
        ],
    },

    # ============================================================
    # INTERACTION MORPHOLOGY
    # ============================================================

    {
        "name": "continuous_holding",
        "visual_description": (
            "A person is holding a plain metal compass."
        ),
        "expected_exact": [
            "Plain Metal Compass"
        ],
    },

    {
        "name": "continuous_studying",
        "visual_description": (
            "A person is studying an old paper map."
        ),
        "expected_exact": [
            "Old Paper Map"
        ],
    },

    {
        "name": "continuous_carrying",
        "visual_description": (
            "A person is carrying a leather bag."
        ),
        "expected_exact": [
            "Leather Bag"
        ],
    },

    # ============================================================
    # OBJECT PHRASE BOUNDARIES
    # ============================================================

    {
        "name": "spatial_across_boundary",
        "visual_description": (
            "A person studies an old map spread across "
            "a wooden table."
        ),
        "expected_exact": [
            "Old Map"
        ],
    },

    {
        "name": "participial_marked_boundary",
        "visual_description": (
            "A person discovers a metal container "
            "marked with a red symbol."
        ),
        "expected_exact": [
            "Metal Container"
        ],
    },

    {
        "name": "spatial_against_boundary",
        "visual_description": (
            "A person examines a wooden crate "
            "against the wall."
        ),
        "expected_exact": [
            "Wooden Crate"
        ],
    },

    # ============================================================
    # VALID PARTICIPIAL MODIFIER PRESERVATION
    # ============================================================

    {
        "name": "preserve_painted_modifier",
        "visual_description": (
            "A person examines a painted wooden box."
        ),
        "expected_exact": [
            "Painted Wooden Box"
        ],
    },

    {
        "name": "preserve_broken_modifier",
        "visual_description": (
            "A person examines a broken metal key."
        ),
        "expected_exact": [
            "Broken Metal Key"
        ],
    },

    # ============================================================
    # FALSE POSITIVE SUPPRESSION
    # ============================================================

    {
        "name": "reject_relaxed_sip",
        "visual_description": (
            "A person takes a relaxed sip."
        ),
        "expected_exact": [],
    },

    {
        "name": "reject_nervous_smile",
        "visual_description": (
            "A person gives a nervous smile."
        ),
        "expected_exact": [],
    },

    {
        "name": "reject_quick_glance",
        "visual_description": (
            "A person gives a quick glance."
        ),
        "expected_exact": [],
    },

    {
        "name": "reject_adverb_tail",
        "visual_description": (
            "A person examines the marking cautiously."
        ),
        "expected_exact": [],
    },

    # ============================================================
    # MULTI-PROP RECALL
    # ============================================================

    {
        "name": "multi_prop_recall",
        "visual_description": (
            "A person studies an old map spread across "
            "a wooden table while another person is "
            "holding a plain metal compass."
        ),
        "characters": [
            "Person",
            "Other Person",
        ],
        "expected_contains": [
            "Old Map",
            "Plain Metal Compass",
        ],
    },

    # ============================================================
    # DECLARED PROP AUTHORITY
    # ============================================================

    {
        "name": "declared_prop_preserved",
        "props": [
            "Wooden Container",
        ],
        "visual_description": (
            "A person opens a plain wooden container."
        ),
        "expected_exact": [
            "Wooden Container"
        ],
    },

    {
        "name": "declared_single_token_conservative",
        "props": [
            "Key",
        ],
        "visual_description": (
            "A person examines a red key."
        ),
        "expected_exact": [
            "Key",
            "Red Key",
        ],
    },

    # ============================================================
    # DISTINCT OBJECT PRESERVATION
    # ============================================================

    {
        "name": "different_material_objects",
        "props": [
            "Wooden Box",
        ],
        "visual_description": (
            "A person examines a metal box."
        ),
        "expected_exact": [
            "Wooden Box",
            "Metal Box",
        ],
    },
]


def build_episode(
    index: int,
    test: Dict[str, Any],
) -> Episode:

    return Episode(
        episode_id=(
            f"EP_PROP_REG_{index:03d}"
        ),
        title=(
            test["name"]
        ),
        target_duration_seconds=8,
        scenes=[
            {
                "scene_number": 1,
                "duration_seconds": 8,
                "visual_description": (
                    test[
                        "visual_description"
                    ]
                ),
                "characters": (
                    test.get(
                        "characters",
                        [
                            "Person"
                        ],
                    )
                ),
                "location": (
                    "Test Room"
                ),
                "props": (
                    test.get(
                        "props",
                        [],
                    )
                ),
                "dialogue": "",
                "narrative_purpose": "",
            }
        ],
    )


def main() -> int:

    analyzer = (
        PropAnalyzer()
    )

    results = []

    print()
    print(
        "BATCH 10D.4E — "
        "PROP REGRESSION MATRIX"
    )
    print()

    for index, test in enumerate(
        TESTS,
        start=1,
    ):

        episode = (
            build_episode(
                index=index,
                test=test,
            )
        )

        analysis = (
            analyzer.analyze(
                episode
            )
        )

        resolved = (
            analysis
            .scenes[0]
            .resolved_props
        )

        passed = True

        expected_exact = (
            test.get(
                "expected_exact"
            )
        )

        expected_contains = (
            test.get(
                "expected_contains",
                []
            )
        )

        errors = []

        if (
            expected_exact
            is not None
        ):

            if (
                resolved
                != expected_exact
            ):

                passed = False

                errors.append(
                    "Exact mismatch. "
                    f"Expected "
                    f"{expected_exact!r}, "
                    f"got {resolved!r}."
                )

        for expected in (
            expected_contains
        ):

            if (
                expected
                not in resolved
            ):

                passed = False

                errors.append(
                    "Missing expected "
                    f"prop {expected!r}."
                )

        result = {
            "test": (
                test["name"]
            ),
            "status": (
                "PASSED"
                if passed
                else "FAILED"
            ),
            "resolved_props": (
                resolved
            ),
            "expected_exact": (
                expected_exact
            ),
            "expected_contains": (
                expected_contains
            ),
            "errors": errors,
        }

        results.append(
            result
        )

        print(
            test["name"],
            "→",
            result["status"],
            resolved,
        )

    failed = [
        item
        for item in results
        if item["status"]
        == "FAILED"
    ]

    output = {
        "batch": "10D.4E",
        "status": (
            "PASSED"
            if not failed
            else "FAILED"
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
        "BATCH 10D.4E SUMMARY"
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

    if failed:

        print(
            "BATCH 10D.4E FAILED"
        )

        return 1

    print(
        "BATCH 10D.4E PASSED"
    )

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )