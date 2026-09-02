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
# SAFETY
# ================================================================


def require_execute_flag() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Perform exactly one real Gemini image "
            "generation request."
        )
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Required to permit the real network "
            "generation call."
        ),
    )

    args = parser.parse_args()

    if not args.execute:

        print()
        print(
            "REAL GEMINI GENERATION NOT EXECUTED"
        )
        print(
            "========================================"
        )
        print(
            "This script performs a billable/network "
            "Gemini image request."
        )
        print()
        print(
            "Run explicitly with:"
        )
        print()
        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_smoke.py "
            "--execute"
        )
        print()

        raise SystemExit(
            0
        )


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 13E.2 — FIRST REAL GEMINI IMAGE"
    )
    print(
        "========================================"
    )

    # ============================================================
    # EXPLICIT EXECUTION GUARD
    # ============================================================

    require_execute_flag()

    print(
        "TEST 1 — explicit execution guard → PASSED"
    )

    # ============================================================
    # CREDENTIAL CHECK
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
    # UNIQUE SMOKE TEST LINEAGE
    #
    # Unique ID prevents accidental overwrite if this script is
    # intentionally executed again later.
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
        "GEN_REQ_REAL_GEMINI_SMOKE_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_SMOKE"
    )

    shot_id = (
        "EP_REAL_GEMINI_SMOKE-S01-SHOT01"
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
        "smoke"
    )

    artifact_store = (
        GenerationArtifactStore(
            base_path=str(
                artifact_root
            )
        )
    )

    # ============================================================
    # GENERATION REQUEST
    #
    # Deliberately:
    # - one request
    # - no reference images
    # - no orchestration
    # - no GenerationRunner
    # - no retry
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
                "for a dark mystery drama. "
                "A solitary detective stands beside a wooden desk "
                "in a dimly lit office at night. "
                "A warm desk lamp creates controlled dramatic "
                "lighting while the background remains dark and "
                "restrained. "
                "The composition should feel atmospheric, "
                "serious, cinematic, and suitable for a premium "
                "animated short film."
            ),
            negative_prompt=(
                "Avoid readable text, distorted anatomy, "
                "extra fingers, exaggerated facial expressions, "
                "rain, visual clutter, logos, watermarks, "
                "and overly bright background lighting."
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
                    "REAL_GEMINI_SMOKE_TEST"
                ),
            },
        )
    )

    print(
        "TEST 3 — one real generation request prepared → PASSED"
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
            "Smoke request is incompatible "
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
    # THE ONE REAL NETWORK CALL
    # ============================================================

    print()
    print(
        "Executing exactly ONE real Gemini "
        "generation attempt..."
    )
    print()

    attempt = (
        provider.generate(
            request=request,
            attempt_number=1,
        )
    )

    # ============================================================
    # RESULT
    # ============================================================

    if (
        attempt.status
        != GenerationStatus.SUCCEEDED
    ):

        print(
            "REAL GENERATION RESULT → FAILED"
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
        "TEST 5 — real Gemini request succeeded → PASSED"
    )

    # ============================================================
    # OUTPUT CONTRACT
    # ============================================================

    if (
        len(
            attempt.outputs
        )
        != 1
    ):

        raise AssertionError(
            "Expected exactly one smoke-test output."
        )

    output = (
        attempt.outputs[0]
    )

    output_path = Path(
        output.output_path
    )

    if (
        not output_path.exists()
        or
        not output_path.is_file()
    ):

        raise AssertionError(
            "Gemini generation succeeded but "
            "physical artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated artifact is empty."
        )

    print(
        "TEST 6 — real image artifact materialized → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "REAL IMAGE GENERATED"
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
        "========================================"
    )
    print(
        "BATCH 13E.2 FIRST REAL GEMINI IMAGE PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()