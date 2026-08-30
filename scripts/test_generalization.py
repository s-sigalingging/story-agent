import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List


# ================================================================
# CONFIGURATION
# ================================================================

BASE_URL = "http://127.0.0.1:8000"

DATA_DIR = Path(
    "data"
)

OUTPUT_DIR = Path(
    "data/test_outputs/batch10d1"
)

WORLD_PREFIX = (
    "generalization-test"
)


# ================================================================
# SYNTHETIC EPISODES
# ================================================================

TEST_CASES: List[
    Dict[str, Any]
] = [

    # ------------------------------------------------------------
    # CASE A — COMEDY / IMAGE-BEARING PROP
    # ------------------------------------------------------------

    {
        "case_id": (
            "A_COMEDY_IMAGE"
        ),
        "episode": {
            "episode_id": (
                "EP_TEST_10D_A"
            ),
            "title": (
                "The Embarrassing Photo"
            ),
            "target_duration_seconds": 12,
            "style": {
                "tone": (
                    "Warm comedy"
                ),
                "visual_style": (
                    "Stylized 3D animation"
                ),
            },
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 12,
                    "visual_description": (
                        "Mira enters a sunny kitchen and "
                        "notices an old photograph on the "
                        "table. She studies the photograph "
                        "and reacts with an embarrassed smile."
                    ),
                    "characters": [
                        "Mira"
                    ],
                    "location": (
                        "Sunny Kitchen"
                    ),
                    "dialogue": "",
                }
            ],
        },
    },

    # ------------------------------------------------------------
    # CASE B — SCI-FI / TEXT + MARKING
    # ------------------------------------------------------------

    {
        "case_id": (
            "B_SCIFI_TEXT"
        ),
        "episode": {
            "episode_id": (
                "EP_TEST_10D_B"
            ),
            "title": (
                "Warning Seven"
            ),
            "target_duration_seconds": 15,
            "style": {
                "tone": (
                    "Tense science fiction"
                ),
                "visual_style": (
                    "Cinematic realistic science fiction"
                ),
            },
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 15,
                    "visual_description": (
                        "Engineer Lena studies a warning "
                        "panel inside the reactor control "
                        "room. The panel displays warning "
                        "code RX-7 and a triangular hazard "
                        "symbol. Lena realizes the reactor "
                        "is unstable."
                    ),
                    "characters": [
                        "Lena"
                    ],
                    "location": (
                        "Reactor Control Room"
                    ),
                    "dialogue": (
                        "That code should not be active."
                    ),
                }
            ],
        },
    },

    # ------------------------------------------------------------
    # CASE C — ACTION / MARKING
    # ------------------------------------------------------------

    {
        "case_id": (
            "C_ACTION_MARKING"
        ),
        "episode": {
            "episode_id": (
                "EP_TEST_10D_C"
            ),
            "title": (
                "The Marked Container"
            ),
            "target_duration_seconds": 12,
            "style": {
                "tone": (
                    "Tense action thriller"
                ),
                "visual_style": (
                    "Cinematic action animation"
                ),
            },
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 12,
                    "visual_description": (
                        "Nadia searches an abandoned "
                        "warehouse and discovers a metal "
                        "container marked with a distinctive "
                        "red serpent symbol. She examines "
                        "the marking cautiously."
                    ),
                    "characters": [
                        "Nadia"
                    ],
                    "location": (
                        "Abandoned Warehouse"
                    ),
                    "dialogue": "",
                }
            ],
        },
    },

    # ------------------------------------------------------------
    # CASE D — ORDINARY PROP
    # ------------------------------------------------------------

    {
        "case_id": (
            "D_ORDINARY_PROP"
        ),
        "episode": {
            "episode_id": (
                "EP_TEST_10D_D"
            ),
            "title": (
                "Morning Coffee"
            ),
            "target_duration_seconds": 10,
            "style": {
                "tone": (
                    "Quiet everyday comedy"
                ),
                "visual_style": (
                    "Stylized 3D animation"
                ),
            },
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 10,
                    "visual_description": (
                        "Theo walks into a small kitchen, "
                        "picks up a plain ceramic mug from "
                        "the counter, and takes a relaxed sip."
                    ),
                    "characters": [
                        "Theo"
                    ],
                    "location": (
                        "Small Kitchen"
                    ),
                    "dialogue": "",
                }
            ],
        },
    },

    # ------------------------------------------------------------
    # CASE E — MULTI CHARACTER / MULTI PROP
    # ------------------------------------------------------------

    {
        "case_id": (
            "E_MULTI_ENTITY"
        ),
        "episode": {
            "episode_id": (
                "EP_TEST_10D_E"
            ),
            "title": (
                "The Map"
            ),
            "target_duration_seconds": 18,
            "style": {
                "tone": (
                    "Adventure mystery"
                ),
                "visual_style": (
                    "Stylized cinematic animation"
                ),
            },
            "scenes": [
                {
                    "scene_number": 1,
                    "duration_seconds": 18,
                    "visual_description": (
                        "Arin studies an old map spread "
                        "across a wooden table while Sora "
                        "stands beside him holding a plain "
                        "metal compass. The map contains a "
                        "hand-drawn route and a black star "
                        "marking the destination. Arin points "
                        "to the black star while Sora watches."
                    ),
                    "characters": [
                        "Arin",
                        "Sora",
                    ],
                    "location": (
                        "Explorer Cabin"
                    ),
                    "dialogue": (
                        "This is where the trail ends."
                    ),
                }
            ],
        },
    },
]


# ================================================================
# HTTP
# ================================================================

def request_json(
    method: str,
    url: str,
) -> Dict[str, Any]:

    request = (
        urllib.request.Request(
            url=url,
            headers={
                "Accept": (
                    "application/json"
                ),
            },
            method=method,
        )
    )

    try:

        with urllib.request.urlopen(
            request
        ) as response:

            return json.loads(
                response
                .read()
                .decode(
                    "utf-8"
                )
            )

    except urllib.error.HTTPError as exc:

        response_body = (
            exc.read()
            .decode(
                "utf-8",
                errors="replace",
            )
        )

        raise RuntimeError(
            f"HTTP {exc.code} "
            f"for {url}\n"
            f"{response_body}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "Could not connect to the API. "
            "Make sure FastAPI is running at "
            f"{BASE_URL}."
        ) from exc


# ================================================================
# EPISODE FILE
# ================================================================

def episode_file_path(
    episode_id: str,
) -> Path:
    """
    Match the episode path convention used by app/main.py.

    Example:

        EP_TEST_10D_A
            ↓
        data/ep_test_10d_a.json
    """

    return (
        DATA_DIR
        /
        f"{episode_id.lower()}.json"
    )


def write_episode_file(
    episode: Dict[str, Any],
) -> Path:

    episode_id = (
        episode[
            "episode_id"
        ]
    )

    path = episode_file_path(
        episode_id
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            episode,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return path


# ================================================================
# STAGE HELPERS
# ================================================================

def stage_map(
    result: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:

    return {
        stage["stage"]: stage
        for stage
        in result.get(
            "stages",
            []
        )
    }


def validate_pipeline_structure(
    result: Dict[str, Any],
) -> List[str]:

    errors: List[str] = []

    expected_stages = [
        "STORY_ANALYSIS",
        "STORY_STRUCTURE",
        "PROP_ANALYSIS",
        "ENTITY_ANALYSIS",
        "CHARACTER_ROLE_ANALYSIS",
        "PROP_CONTENT_ANALYSIS",
        "SCENE_ANALYSIS",
        "PRODUCTION_INTENT",
        "CONTINUITY_ANALYSIS",
        "STATE_MANAGEMENT",
        "WORLD_STATE",
        "PRODUCTION_PLANNING",
        "ASSET_PLANNING",
        "PRODUCTION_EXECUTION",
        "PRODUCTION_PROMPTS",
    ]

    stages = stage_map(
        result
    )

    for expected in expected_stages:

        if expected not in stages:

            errors.append(
                f"Missing stage: "
                f"{expected}"
            )

            continue

        status = (
            stages[
                expected
            ].get(
                "status"
            )
        )

        if status != "PASSED":

            errors.append(
                f"{expected} status is "
                f"{status!r}, expected "
                "'PASSED'."
            )

    final_status = (
        result.get(
            "status"
        )
    )

    if (
        final_status
        != "WAITING_HUMAN_APPROVAL"
    ):

        errors.append(
            "Final pipeline status is "
            f"{final_status!r}, expected "
            "'WAITING_HUMAN_APPROVAL'."
        )

    return errors


# ================================================================
# TEST EXECUTION
# ================================================================

def run_case(
    test_case: Dict[str, Any],
) -> Dict[str, Any]:

    case_id = (
        test_case[
            "case_id"
        ]
    )

    episode = (
        test_case[
            "episode"
        ]
    )

    episode_id = (
        episode[
            "episode_id"
        ]
    )

    world_id = (
        f"{WORLD_PREFIX}-"
        f"{case_id.lower()}"
    )

    print()
    print(
        "========================================"
    )
    print(
        case_id
    )
    print(
        "========================================"
    )

    # ------------------------------------------------------------
    # WRITE EPISODE USING REAL API FILE CONTRACT
    # ------------------------------------------------------------

    episode_path = (
        write_episode_file(
            episode
        )
    )

    print(
        "Episode file:",
        episode_path,
    )

    # ------------------------------------------------------------
    # ORCHESTRATE THROUGH REAL API
    # ------------------------------------------------------------

    orchestrate_url = (
        f"{BASE_URL}"
        f"/episodes/{episode_id}"
        f"/orchestrate"
        f"?world_id={world_id}"
    )

    print(
        "Running full orchestration..."
    )

    result = (
        request_json(
            method="POST",
            url=orchestrate_url,
        )
    )

    # ------------------------------------------------------------
    # SAVE COMPLETE OUTPUT
    # ------------------------------------------------------------

    result_file = (
        OUTPUT_DIR
        /
        f"{case_id.lower()}"
        "_orchestration.json"
    )

    result_file.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # ------------------------------------------------------------
    # VALIDATE
    # ------------------------------------------------------------

    errors = (
        validate_pipeline_structure(
            result
        )
    )

    status = (
        "PASSED"
        if not errors
        else "FAILED"
    )

    print(
        "Pipeline:",
        status,
    )

    if errors:

        for error in errors:

            print(
                " -",
                error,
            )

    return {
        "case_id": case_id,
        "episode_id": episode_id,
        "episode_file": str(
            episode_path
        ),
        "status": status,
        "errors": errors,
        "output_file": str(
            result_file
        ),
    }


# ================================================================
# MAIN
# ================================================================

def main() -> int:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = []

    print()
    print(
        "BATCH 10D.1 — "
        "GENERALIZATION TEST HARNESS"
    )

    for test_case in TEST_CASES:

        try:

            result = (
                run_case(
                    test_case
                )
            )

        except Exception as exc:

            result = {
                "case_id": (
                    test_case[
                        "case_id"
                    ]
                ),
                "episode_id": (
                    test_case[
                        "episode"
                    ][
                        "episode_id"
                    ]
                ),
                "status": "FAILED",
                "errors": [
                    str(exc)
                ],
                "output_file": None,
            }

            print(
                "FAILED:",
                exc,
            )

        results.append(
            result
        )

    passed = sum(
        item["status"]
        == "PASSED"
        for item in results
    )

    failed = (
        len(results)
        -
        passed
    )

    summary = {
        "batch": "10D.1",
        "status": (
            "PASSED"
            if failed == 0
            else "FAILED"
        ),
        "total_cases": (
            len(results)
        ),
        "passed": passed,
        "failed": failed,
        "cases": results,
    }

    summary_file = (
        OUTPUT_DIR
        /
        "summary.json"
    )

    summary_file.write_text(
        json.dumps(
            summary,
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
        "BATCH 10D.1 SUMMARY"
    )
    print(
        "========================================"
    )

    for result in results:

        print(
            result["case_id"],
            "→",
            result["status"],
        )

    print()

    print(
        "Passed:",
        passed,
    )

    print(
        "Failed:",
        failed,
    )

    print(
        "Summary:",
        summary_file,
    )

    print()

    if failed == 0:

        print(
            "BATCH 10D.1 PASSED"
        )

        return 0

    print(
        "BATCH 10D.1 FAILED"
    )

    return 1


if __name__ == "__main__":

    sys.exit(
        main()
    )