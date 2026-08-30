import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "test_outputs"
    / "batch10d6_final_regression.json"
)


SUITES = [
    {
        "name": "PROP_REGRESSION_MATRIX",
        "script": (
            PROJECT_ROOT
            / "scripts"
            / "test_prop_regression_matrix.py"
        ),
        "result_file": (
            PROJECT_ROOT
            / "data"
            / "test_outputs"
            / "batch10d4e_prop_regression_matrix.json"
        ),
        "expected": {
            "status": "PASSED",
            "total_tests": 18,
            "passed": 18,
            "failed": 0,
        },
    },
    {
        "name": "CHARACTER_INTERACTION_MATRIX",
        "script": (
            PROJECT_ROOT
            / "scripts"
            / "test_character_interaction_matrix.py"
        ),
        "result_file": (
            PROJECT_ROOT
            / "data"
            / "test_outputs"
            / "batch10d5c_interaction_selection_matrix.json"
        ),
        "expected": {
            "status": "PASSED",
            "total_tests": 12,
            "passed": 12,
            "failed": 0,
        },
    },
    {
        "name": "GENERALIZATION_HARNESS",
        "script": (
            PROJECT_ROOT
            / "scripts"
            / "test_generalization.py"
        ),
        "result_file": (
            PROJECT_ROOT
            / "data"
            / "test_outputs"
            / "batch10d1"
            / "summary.json"
        ),
        "expected": {
            "status": "PASSED",
            "total_cases": 5,
            "passed": 5,
            "failed": 0,
        },
    },
    {
        "name": "SEMANTIC_GENERALIZATION_AUDIT",
        "script": (
            PROJECT_ROOT
            / "scripts"
            / "test_semantic_generalization.py"
        ),
        "result_file": (
            PROJECT_ROOT
            / "data"
            / "test_outputs"
            / "batch10d2_semantic_audit.json"
        ),
        "expected": {
            "status": "PASSED",
            "total_cases": 5,
            "passed_cases": 5,
            "failed_cases": 0,
            "failed_checks": 0,
        },
    },
]


HARDCODE_TERMS = [
    "Julian",
    "Ren",
    "Sterling",
    "Sam Bell",
    "Samuel Bell",
    "Oakhaven",
    "EP001",
    "Mira",
    "Lena",
    "Nadia",
    "Theo",
    "Arin",
    "Sora",
    "Mysterious Document",
    "Old Brass Key",
    "Metal Compass",
    "Old Map",
    "Metal Container",
    "Ceramic Mug",
    "Warning Panel",
    "PROP_MYSTERIOUS_DOCUMENT",
    "CHAR_JULIAN",
]


# ================================================================
# SUITE EXECUTION
# ================================================================

def run_suite(
    suite: Dict[str, Any],
) -> Dict[str, Any]:

    script = suite["script"]

    if not script.exists():

        return {
            "name": suite["name"],
            "status": "FAILED",
            "errors": [
                f"Missing test script: {script}"
            ],
            "stdout": "",
            "stderr": "",
        }

    print()
    print(
        "========================================"
    )
    print(
        suite["name"]
    )
    print(
        "========================================"
    )

    process = subprocess.run(
        [
            sys.executable,
            str(script),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    if process.stdout:

        print(
            process.stdout.rstrip()
        )

    if process.stderr:

        print(
            process.stderr.rstrip()
        )

    errors: List[str] = []

    result_file = (
        suite["result_file"]
    )

    if not result_file.exists():

        errors.append(
            "Expected result file was not created: "
            f"{result_file}"
        )

        return {
            "name": suite["name"],
            "status": "FAILED",
            "return_code": (
                process.returncode
            ),
            "errors": errors,
            "stdout": (
                process.stdout
            ),
            "stderr": (
                process.stderr
            ),
        }

    try:

        with result_file.open(
            "r",
            encoding="utf-8",
        ) as f:

            result_data = json.load(f)

    except Exception as exc:

        errors.append(
            "Could not parse result JSON: "
            f"{exc}"
        )

        result_data = {}

    for (
        key,
        expected_value,
    ) in suite[
        "expected"
    ].items():

        actual_value = (
            result_data.get(
                key
            )
        )

        if (
            actual_value
            != expected_value
        ):

            errors.append(
                f"{key}: expected "
                f"{expected_value!r}, "
                f"got {actual_value!r}"
            )

    if process.returncode != 0:

        errors.append(
            "Test process returned non-zero "
            f"exit code {process.returncode}."
        )

    return {
        "name": suite["name"],
        "status": (
            "PASSED"
            if not errors
            else "FAILED"
        ),
        "return_code": (
            process.returncode
        ),
        "result_file": str(
            result_file.relative_to(
                PROJECT_ROOT
            )
        ),
        "expected": (
            suite["expected"]
        ),
        "actual": {
            key: (
                result_data.get(
                    key
                )
            )
            for key
            in suite[
                "expected"
            ]
        },
        "errors": errors,
    }


# ================================================================
# HARDCODE AUDIT
# ================================================================

def build_hardcode_pattern(
    term: str,
) -> re.Pattern:
    """
    Build a case-insensitive exact-term matcher.

    The previous scanner used substring matching, which caused false
    positives such as:

        Ren  -> current, reference, different
        Arin -> bearing

    This matcher requires the complete term to be isolated from Python
    identifier characters (letters, digits, and underscore).

    Multi-word phrases still match normally:

        Old Brass Key

    Stable IDs containing underscores also match as complete units:

        CHAR_JULIAN
    """

    escaped = (
        re.escape(
            term
        )
    )

    # Allow ordinary whitespace variation inside multi-word phrases
    # while preserving the exact phrase/token sequence.
    escaped = (
        escaped.replace(
            r"\ ",
            r"\s+",
        )
    )

    return re.compile(
        rf"(?<![A-Za-z0-9_])"
        rf"{escaped}"
        rf"(?![A-Za-z0-9_])",
        flags=re.IGNORECASE,
    )


def hardcode_audit() -> Dict[str, Any]:

    app_dir = (
        PROJECT_ROOT
        / "app"
    )

    findings = []

    patterns = {
        term: (
            build_hardcode_pattern(
                term
            )
        )
        for term in HARDCODE_TERMS
    }

    for path in sorted(
        app_dir.rglob(
            "*.py"
        )
    ):

        if (
            "__pycache__"
            in path.parts
        ):
            continue

        try:

            text = path.read_text(
                encoding="utf-8"
            )

        except Exception as exc:

            findings.append({
                "file": str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "term": (
                    "READ_ERROR"
                ),
                "line": None,
                "content": str(exc),
            })

            continue

        lines = (
            text.splitlines()
        )

        for (
            line_number,
            line,
        ) in enumerate(
            lines,
            start=1,
        ):

            for (
                term,
                pattern,
            ) in patterns.items():

                if (
                    pattern.search(
                        line
                    )
                    is None
                ):
                    continue

                findings.append({
                    "file": str(
                        path.relative_to(
                            PROJECT_ROOT
                        )
                    ),
                    "term": term,
                    "line": (
                        line_number
                    ),
                    "content": (
                        line.strip()
                    ),
                })

    return {
        "status": (
            "PASSED"
            if not findings
            else "FAILED"
        ),
        "match_mode": (
            "EXACT_TERM_WITH_IDENTIFIER_BOUNDARIES"
        ),
        "terms_checked": (
            HARDCODE_TERMS
        ),
        "finding_count": (
            len(findings)
        ),
        "findings": (
            findings
        ),
    }


# ================================================================
# MAIN
# ================================================================

def main() -> int:

    print()
    print(
        "BATCH 10D.6 — "
        "FINAL GENERALIZATION REGRESSION"
    )

    suite_results = []

    for suite in SUITES:

        suite_results.append(
            run_suite(
                suite
            )
        )

    print()
    print(
        "========================================"
    )
    print(
        "HARDCODE AUDIT"
    )
    print(
        "========================================"
    )

    hardcode_result = (
        hardcode_audit()
    )

    print(
        "Hardcode findings:",
        hardcode_result[
            "finding_count"
        ],
    )

    for finding in (
        hardcode_result[
            "findings"
        ]
    ):

        print(
            f"{finding['file']}:"
            f"{finding['line']} "
            f"[{finding['term']}] "
            f"{finding['content']}"
        )

    failed_suites = [
        item
        for item in suite_results
        if item["status"]
        != "PASSED"
    ]

    final_passed = (
        not failed_suites
        and
        hardcode_result[
            "status"
        ]
        == "PASSED"
    )

    output = {
        "batch": "10D.6",
        "status": (
            "PASSED"
            if final_passed
            else "FAILED"
        ),
        "suite_count": (
            len(
                suite_results
            )
        ),
        "passed_suites": (
            len(
                suite_results
            )
            -
            len(
                failed_suites
            )
        ),
        "failed_suites": (
            len(
                failed_suites
            )
        ),
        "suites": (
            suite_results
        ),
        "hardcode_audit": (
            hardcode_result
        ),
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
        "BATCH 10D.6 FINAL SUMMARY"
    )
    print(
        "========================================"
    )

    for result in (
        suite_results
    ):

        print(
            result["name"],
            "→",
            result["status"],
        )

    print(
        "HARDCODE_AUDIT",
        "→",
        hardcode_result[
            "status"
        ],
    )

    print()

    print(
        "Passed suites:",
        output[
            "passed_suites"
        ],
    )

    print(
        "Failed suites:",
        output[
            "failed_suites"
        ],
    )

    print(
        "Hardcode findings:",
        hardcode_result[
            "finding_count"
        ],
    )

    print(
        "Saved:",
        OUTPUT_FILE.relative_to(
            PROJECT_ROOT
        ),
    )

    print()

    if final_passed:

        print(
            "BATCH 10D.6 PASSED"
        )

        return 0

    print(
        "BATCH 10D.6 FAILED"
    )

    return 1


if __name__ == "__main__":

    sys.exit(
        main()
    )
