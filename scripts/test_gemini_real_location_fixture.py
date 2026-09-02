import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from app.generation import (
    GeminiGenerationProvider,
    GenerationArtifactStore,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationRequest,
    GenerationStatus,
    GenerationType,
)


# ================================================================
# ARGUMENTS
# ================================================================


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Generate exactly one stylistically compatible "
            "dummy location fixture using the real Gemini API."
        )
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Explicitly permit one real Gemini network request."
        ),
    )

    return parser.parse_args()


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 13F.2-A — LOCATION FIXTURE GENERATION"
    )
    print(
        "========================================"
    )

    args = (
        parse_arguments()
    )

    # ============================================================
    # TEST 1 — EXECUTION GUARD
    # ============================================================

    if (
        not args.execute
    ):

        print(
            "TEST 1 — execution guard active → PASSED"
        )

        print()
        print(
            "REAL GENERATION NOT EXECUTED"
        )
        print(
            "----------------------------------------"
        )
        print(
            "This test will generate exactly ONE "
            "real Gemini location fixture."
        )
        print()
        print(
            "Run explicitly with:"
        )
        print()
        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_location_fixture.py "
            "--execute"
        )
        print()

        return

    print(
        "TEST 1 — explicit execution permission → PASSED"
    )

    # ============================================================
    # TEST 2 — CREDENTIAL
    # ============================================================

    api_key = (
        os.getenv(
            "GEMINI_API_KEY"
        )
    )

    if (
        api_key is None
        or
        not api_key.strip()
    ):

        raise RuntimeError(
            "GEMINI_API_KEY is not set."
        )

    print(
        "TEST 2 — Gemini credential available → PASSED"
    )

    # ============================================================
    # LINEAGE
    # ============================================================

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y%m%dT%H%M%SZ"
        )
    )

    request_id = (
        "GEN_REQ_REAL_GEMINI_LOCATION_FIXTURE_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_LOCATION_FIXTURE"
    )

    shot_id = (
        "EP_REAL_GEMINI_LOCATION_FIXTURE-S01-SHOT01"
    )

    # ============================================================
    # TEST 3 — REQUEST
    #
    # Important:
    # This is deliberately NOT a canonical production location.
    # It exists only as a visual test fixture for Batch 13F.2.
    # ============================================================

    request = (
        GenerationRequest(
            request_id=(
                request_id
            ),
            episode_id=(
                episode_id
            ),
            shot_id=(
                shot_id
            ),
            generation_type=(
                GenerationType.KEYFRAME
            ),
            prompt=(
                "Create a polished cinematic animated film frame "
                "showing an EMPTY old industrial dock warehouse "
                "at night. "
                ""
                "The visual language should match a premium dark "
                "mystery illustrated film: realistic stylized forms, "
                "restrained noir atmosphere, subtle painted texture, "
                "controlled cinematic lighting, deep shadows, and "
                "muted colors. "
                ""
                "Show a large warehouse interior with aged wooden "
                "support beams, old cargo crates, worn floorboards, "
                "large industrial windows, distant dock structures, "
                "and a few dim practical lights. "
                ""
                "Use a wide environmental composition that clearly "
                "establishes the architecture of the location. "
                "The environment should feel old, quiet, atmospheric, "
                "and slightly ominous, but still believable and "
                "production-ready for a cinematic mystery story. "
                ""
                "There must be NO PEOPLE and NO HUMAN FIGURES. "
                "This image is intended to serve purely as a "
                "location reference."
            ),
            negative_prompt=(
                "No people. "
                "No human figures. "
                "No silhouettes of people. "
                "No faces. "
                "No detective. "
                "No foreground character. "
                "No office desk. "
                "No office bookshelf. "
                "No telephone. "
                "No modern office furniture. "
                "Avoid readable text, logos, watermarks, "
                "distorted architecture, excessive visual clutter, "
                "bright daylight, cheerful lighting, "
                "and highly saturated colors."
            ),
            reference_assets=[],
            output=(
                GenerationOutputSpec(
                    width=1080,
                    height=1920,
                    aspect_ratio=(
                        "9:16"
                    ),
                    output_format=(
                        "png"
                    ),
                )
            ),
            metadata={
                "purpose": (
                    "TEST_LOCATION_FIXTURE"
                ),
                "canonical_asset": (
                    "false"
                ),
                "fixture_type": (
                    "LOCATION"
                ),
                "fixture_theme": (
                    "DARK_MYSTERY_DOCK_WAREHOUSE"
                ),
            },
        )
    )

    assert (
        request.reference_assets
        == []
    )

    print(
        "TEST 3 — text-only location request prepared → PASSED"
    )

    # ============================================================
    # ARTIFACT STORE
    # ============================================================

    artifact_root = (
        Path(
            "data"
        )
        /
        "generated"
        /
        "gemini"
        /
        "test_fixtures"
        /
        "location"
    )

    artifact_store = (
        GenerationArtifactStore(
            base_path=str(
                artifact_root
            )
        )
    )

    # ============================================================
    # PROVIDER
    # ============================================================

    provider = (
        GeminiGenerationProvider(
            artifact_store=(
                artifact_store
            ),
            model=(
                "gemini-3.1-flash-image"
            ),
            api_key_env=(
                "GEMINI_API_KEY"
            ),
            network_enabled=True,
        )
    )

    # ============================================================
    # TEST 4 — CAPABILITY GATE
    # ============================================================

    capability_result = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    if (
        not capability_result.compatible
    ):

        raise RuntimeError(
            "Location fixture request is incompatible "
            "with Gemini provider capabilities: "
            +
            "; ".join(
                capability_result.issues
            )
        )

    print(
        "TEST 4 — provider capability gate → PASSED"
    )

    # ============================================================
    # ONE REAL NETWORK CALL
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini location "
        "fixture generation..."
    )
    print()

    attempt = (
        provider.generate(
            request=request,
            attempt_number=1,
        )
    )

    # ============================================================
    # TEST 5 — GENERATION SUCCESS
    # ============================================================

    if (
        attempt.status
        != GenerationStatus.SUCCEEDED
    ):

        print(
            "REAL LOCATION GENERATION → FAILED"
        )

        if (
            attempt.error
            is not None
        ):

            print(
                "Error code:",
                attempt.error.code,
            )

            print(
                "Retryable:",
                attempt.error.retryable,
            )

            print(
                "Message:",
                attempt.error.message,
            )

        print()
        print(
            "No automatic retry will be performed."
        )

        raise SystemExit(
            1
        )

    print(
        "TEST 5 — real location generation succeeded → PASSED"
    )

    # ============================================================
    # TEST 6 — EXACTLY ONE OUTPUT
    # ============================================================

    if (
        len(
            attempt.outputs
        )
        != 1
    ):

        raise AssertionError(
            "Expected exactly one location fixture output."
        )

    output = (
        attempt.outputs[0]
    )

    print(
        "TEST 6 — exactly one output returned → PASSED"
    )

    # ============================================================
    # TEST 7 — PHYSICAL ARTIFACT
    # ============================================================

    output_path = (
        Path(
            output.output_path
        )
    )

    if (
        not output_path.exists()
        or
        not output_path.is_file()
    ):

        raise AssertionError(
            "Gemini reported success but location "
            "fixture artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated location fixture is empty."
        )

    print(
        "TEST 7 — location artifact materialized → PASSED"
    )

    # ============================================================
    # TEST 8 — LINEAGE
    # ============================================================

    expected_attempt_id = (
        f"{request_id}"
        "_ATTEMPT_001"
    )

    expected_output_id = (
        f"{request_id}"
        "_ATTEMPT_001_OUTPUT_001"
    )

    assert (
        attempt.attempt_id
        ==
        expected_attempt_id
    )

    assert (
        output.output_id
        ==
        expected_output_id
    )

    print(
        "TEST 8 — location fixture lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "LOCATION FIXTURE GENERATED"
    )
    print(
        "----------------------------------------"
    )

    print(
        "Provider:",
        attempt.provider,
    )

    print(
        "Request ID:",
        request.request_id,
    )

    print(
        "Attempt ID:",
        attempt.attempt_id,
    )

    print(
        "Output ID:",
        output.output_id,
    )

    print(
        "Output path:",
        output.output_path,
    )

    print(
        "File size:",
        output_path.stat().st_size,
        "bytes",
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "This image is a TEST FIXTURE only."
    )

    print(
        "It must not be registered as a canonical "
        "production location asset."
    )

    print()

    print(
        "Visual review criteria:"
    )

    print(
        "- no character or human figure"
    )

    print(
        "- dark cinematic mystery style"
    )

    print(
        "- clearly recognizable warehouse environment"
    )

    print(
        "- visual language compatible with character fixture"
    )

    print(
        "- sufficiently different from the office reference"
    )

    print()

    print(
        "========================================"
    )
    print(
        "BATCH 13F.2-A TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL FIXTURE REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()