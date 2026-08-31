from pathlib import Path
import os
import subprocess
import sys
from typing import List, Tuple


# ================================================================
# PROJECT ROOT
# ================================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# ================================================================
# TEST DEFINITIONS
# ================================================================


TESTS: List[
    Tuple[str, str]
] = [
    (
        "GENERATION_DOMAIN_MODEL",
        "scripts/test_generation_models.py",
    ),
    (
        "GENERATION_PROVIDER_CONTRACT",
        "scripts/test_generation_provider_contract.py",
    ),
    (
        "KEYFRAME_GENERATOR",
        "scripts/test_keyframe_generator.py",
    ),
    (
        "GENERATION_LINEAGE_STORE",
        "scripts/test_generation_store.py",
    ),
    (
        "GENERATION_RETRY",
        "scripts/test_generation_retry.py",
    ),
    (
        "GENERATION_REQUEST_COMPILER",
        "scripts/test_generation_request_compiler.py",
    ),
    (
        "GENERATION_PIPELINE_SUCCESS",
        "scripts/test_generation_pipeline_success.py",
    ),
    (
        "GENERATION_PIPELINE_FAILURE",
        "scripts/test_generation_pipeline_failure.py",
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


# ================================================================
# TEST RUNNER
# ================================================================


def run_test(
    name: str,
    relative_path: str,
) -> bool:

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

    test_path = (
        PROJECT_ROOT
        /
        relative_path
    )

    if not test_path.exists():

        print(
            "TEST FILE NOT FOUND:"
        )
        print(
            test_path
        )

        print(
            f"{name} → FAILED"
        )

        return False

    environment = (
        os.environ.copy()
    )

    existing_pythonpath = (
        environment.get(
            "PYTHONPATH",
            "",
        )
    )

    project_root_string = str(
        PROJECT_ROOT
    )

    if existing_pythonpath:

        environment[
            "PYTHONPATH"
        ] = (
            project_root_string
            +
            os.pathsep
            +
            existing_pythonpath
        )

    else:

        environment[
            "PYTHONPATH"
        ] = (
            project_root_string
        )

    completed = (
        subprocess.run(
            [
                sys.executable,
                str(
                    test_path
                ),
            ],
            cwd=str(
                PROJECT_ROOT
            ),
            env=environment,
            check=False,
        )
    )

    if (
        completed.returncode
        == 0
    ):

        print()
        print(
            f"{name} → PASSED"
        )

        return True

    print()
    print(
        f"{name} → FAILED"
    )

    print(
        "Exit code:",
        completed.returncode,
    )

    return False


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 12H.1 — GENERATION MASTER REGRESSION"
    )
    print(
        "========================================"
    )

    results = []

    for (
        name,
        relative_path,
    ) in TESTS:

        passed = (
            run_test(
                name=name,
                relative_path=(
                    relative_path
                ),
            )
        )

        results.append(
            (
                name,
                passed,
            )
        )

    # ============================================================
    # SUMMARY
    # ============================================================

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12H.1 SUMMARY"
    )
    print(
        "========================================"
    )

    passed_count = 0
    failed_count = 0

    for (
        name,
        passed,
    ) in results:

        if passed:

            status = "PASSED"
            passed_count += 1

        else:

            status = "FAILED"
            failed_count += 1

        print(
            f"{name} → {status}"
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

    # ============================================================
    # FINAL RESULT
    # ============================================================

    if failed_count:

        print(
            "BATCH 12H.1 FAILED"
        )

        raise SystemExit(
            1
        )

    print(
        "BATCH 12H.1 PASSED"
    )


if __name__ == "__main__":

    main()