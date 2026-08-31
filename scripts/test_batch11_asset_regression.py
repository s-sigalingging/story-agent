import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


TEST_SCRIPTS = [
    (
        "ASSET_REGISTRY",
        "scripts/test_asset_registry.py",
    ),
    (
        "ASSET_RESOLVER",
        "scripts/test_asset_resolver.py",
    ),
    (
        "ASSET_VALIDATION",
        "scripts/test_asset_validation.py",
    ),
    (
        "ASSET_PLAN_HYDRATION",
        "scripts/test_asset_plan_hydration.py",
    ),
    (
        "ASSET_PIPELINE_BLOCKED",
        "scripts/test_asset_pipeline_blocked.py",
    ),
    (
        "ASSET_PIPELINE_READY",
        "scripts/test_asset_pipeline_ready.py",
    ),
]


ASSET_PRODUCTION_FILES = [
    (
        PROJECT_ROOT
        / "app"
        / "models"
        / "asset_registry.py"
    ),
    (
        PROJECT_ROOT
        / "app"
        / "assets"
        / "registry.py"
    ),
    (
        PROJECT_ROOT
        / "app"
        / "assets"
        / "resolver.py"
    ),
    (
        PROJECT_ROOT
        / "app"
        / "assets"
        / "validator.py"
    ),
    (
        PROJECT_ROOT
        / "app"
        / "assets"
        / "store.py"
    ),
]


FORBIDDEN_TERMS = [
    "Julian",
    "Ren",
    "Sterling",
    "Sam Bell",
    "Samuel Bell",
    "Oakhaven",
    "EP001",
    "Mira",
    "Nadia",
    "Theo",
    "Arin",
    "Sora",
    "Mysterious Document",
    "Old Brass Key",
    "CHAR_JULIAN",
    "PROP_MYSTERIOUS_DOCUMENT",
]


# ================================================================
# TEST RUNNER
# ================================================================


def run_test(
    name: str,
    relative_path: str,
) -> bool:

    script_path = (
        PROJECT_ROOT
        / relative_path
    )

    if not script_path.exists():

        print(
            f"{name} → FAILED"
        )

        print(
            "   Missing test file:"
        )

        print(
            f"   {relative_path}"
        )

        return False

    result = subprocess.run(
        [
            sys.executable,
            str(
                script_path
            ),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    if result.stdout:

        print(
            result.stdout.rstrip()
        )

    if result.stderr:

        print(
            result.stderr.rstrip()
        )

    if (
        result.returncode
        != 0
    ):

        print(
            f"{name} → FAILED"
        )

        return False

    print(
        f"{name} → PASSED"
    )

    return True


# ================================================================
# HARDCODE MATCHING
# ================================================================


def build_hardcode_pattern(
    term: str,
) -> re.Pattern:
    """
    Build a case-insensitive exact-term matcher.

    This avoids substring false positives such as:

        Ren
        -> reference
        -> rendering
        -> current

        Arin
        -> bearing

    Terms must be isolated from Python identifier characters.

    Multi-word phrases still match normally:

        Old Brass Key

    Stable identifiers containing underscores also match as
    complete values:

        CHAR_JULIAN
    """

    escaped = (
        re.escape(
            term
        )
    )

    # Permit normal whitespace variation in multi-word phrases.
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


# ================================================================
# HARDCODE AUDIT
# ================================================================


def run_hardcode_audit() -> bool:

    print()
    print(
        "ASSET HARDCODE AUDIT"
    )
    print(
        "========================================"
    )

    findings = []

    patterns = {
        term: (
            build_hardcode_pattern(
                term
            )
        )
        for term in (
            FORBIDDEN_TERMS
        )
    }

    for path in (
        ASSET_PRODUCTION_FILES
    ):

        if not path.exists():

            findings.append({
                "file": str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                ),
                "line": 0,
                "term": "MISSING_FILE",
                "content": "",
            })

            continue

        lines = (
            path.read_text(
                encoding="utf-8"
            )
            .splitlines()
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
                    "line": (
                        line_number
                    ),
                    "term": term,
                    "content": (
                        line.strip()
                    ),
                })

    if findings:

        for finding in findings:

            print(
                f"{finding['file']}:"
                f"{finding['line']} "
                f"[{finding['term']}] "
                f"{finding['content']}"
            )

        print(
            "ASSET HARDCODE AUDIT → FAILED"
        )

        return False

    print(
        "Match mode: "
        "EXACT_TERM_WITH_IDENTIFIER_BOUNDARIES"
    )

    print(
        "Hardcode findings: 0"
    )

    print(
        "ASSET HARDCODE AUDIT → PASSED"
    )

    return True


# ================================================================
# MAIN
# ================================================================


def main() -> int:

    print()
    print(
        "BATCH 11G — "
        "ASSET SYSTEM REGRESSION"
    )
    print(
        "========================================"
    )

    results = []

    for (
        name,
        path,
    ) in TEST_SCRIPTS:

        print()
        print(
            "----------------------------------------"
        )
        print(
            name
        )
        print(
            "----------------------------------------"
        )

        passed = (
            run_test(
                name=name,
                relative_path=path,
            )
        )

        results.append(
            (
                name,
                passed,
            )
        )

    hardcode_passed = (
        run_hardcode_audit()
    )

    results.append(
        (
            "ASSET_HARDCODE_AUDIT",
            hardcode_passed,
        )
    )

    passed_count = sum(
        1
        for (
            _,
            passed,
        )
        in results
        if passed
    )

    failed_count = (
        len(results)
        -
        passed_count
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 11G SUMMARY"
    )
    print(
        "========================================"
    )

    for (
        name,
        passed,
    ) in results:

        print(
            f"{name} "
            f"→ "
            f"{'PASSED' if passed else 'FAILED'}"
        )

    print()

    print(
        "Passed:",
        passed_count,
    )

    print(
        "Failed:",
        failed_count,
    )

    print()

    if failed_count:

        print(
            "BATCH 11G FAILED"
        )

        return 1

    print(
        "BATCH 11G PASSED"
    )

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )