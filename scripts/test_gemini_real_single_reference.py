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
    GenerationReferenceAsset,
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
            "Perform exactly one real Gemini image generation "
            "using one reference image while forcing a clearly "
            "different target scene."
        )
    )

    parser.add_argument(
        "--reference",
        required=True,
        help=(
            "Path to the character reference image."
        ),
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Explicitly permit the real Gemini network request."
        ),
    )

    return parser.parse_args()


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 13F.1-B — IDENTITY DISENTANGLEMENT TEST"
    )
    print(
        "========================================"
    )

    args = (
        parse_arguments()
    )

    # ============================================================
    # TEST 1 — REFERENCE EXISTS
    # ============================================================

    reference_path = (
        Path(
            args.reference
        )
        .expanduser()
        .resolve()
    )

    if (
        not reference_path.exists()
        or
        not reference_path.is_file()
    ):

        raise FileNotFoundError(
            "Reference image was not found: "
            f"{reference_path}"
        )

    if (
        reference_path.stat().st_size
        <= 0
    ):

        raise ValueError(
            "Reference image is empty."
        )

    print(
        "TEST 1 — physical reference found → PASSED"
    )

    print(
        "         reference:",
        reference_path,
    )

    # ============================================================
    # TEST 2 — EXECUTION GUARD
    # ============================================================

    if (
        not args.execute
    ):

        print(
            "TEST 2 — execution guard active → PASSED"
        )

        print()
        print(
            "REAL GENERATION NOT EXECUTED"
        )
        print(
            "----------------------------------------"
        )
        print(
            "Reference validation succeeded."
        )
        print()
        print(
            "To execute exactly ONE real Gemini request:"
        )
        print()
        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_single_reference.py "
            f'--reference "{reference_path}" '
            "--execute"
        )
        print()

        return

    print(
        "TEST 2 — explicit execution permission → PASSED"
    )

    # ============================================================
    # TEST 3 — CREDENTIAL
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
        "TEST 3 — Gemini credential available → PASSED"
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
        "GEN_REQ_REAL_GEMINI_IDENTITY_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_IDENTITY"
    )

    shot_id = (
        "EP_REAL_GEMINI_IDENTITY-S01-SHOT01"
    )

    # ============================================================
    # REFERENCE ASSET
    # ============================================================

    reference_asset = (
        GenerationReferenceAsset(
            asset_id=(
                "ASSET_CHARACTER_REFERENCE_SMOKE"
            ),
            entity_id=(
                "CHARACTER_REFERENCE_SMOKE"
            ),
            asset_type=(
                "CHARACTER"
            ),
            name=(
                "Character Identity Reference"
            ),
            reference_path=(
                str(
                    reference_path
                )
            ),
        )
    )

    # ============================================================
    # TEST 4 — REQUEST
    #
    # Target scene is intentionally very different from the
    # reference image.
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
                "Use the supplied image ONLY as the visual identity "
                "reference for the person. Preserve the same facial "
                "structure, apparent age, hairstyle, facial proportions, "
                "and overall identity of the referenced man. "
                ""
                "Create a clearly DIFFERENT scene from the reference. "
                "Show the same man standing alone on an empty railway "
                "platform at night. Use a medium close-up composition "
                "from approximately chest level upward. The character "
                "is standing upright and is not touching any objects. "
                "Use cool station lighting with subtle distant practical "
                "lights and a dark platform background. "
                ""
                "The environment, pose, camera framing, furniture, "
                "props, and composition must be different from the "
                "reference image. Preserve the character identity only, "
                "not the original scene. "
                ""
                "The result should feel like a polished cinematic "
                "animated mystery film frame."
            ),
            negative_prompt=(
                "Do not reproduce the original office. "
                "Do not show a desk. "
                "Do not show a desk lamp. "
                "Do not show bookshelves. "
                "Do not show a telephone. "
                "Do not show paperwork on a desk. "
                "Do not recreate the original pose or camera angle. "
                "Do not copy the original composition. "
                "Do not redesign the character's face. "
                "Do not significantly change apparent age or hairstyle. "
                "Avoid exaggerated facial expressions, distorted anatomy, "
                "readable text, logos, watermarks, and visual clutter."
            ),
            reference_assets=[
                reference_asset
            ],
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
                    "REAL_GEMINI_IDENTITY_DISENTANGLEMENT"
                ),
                "reference_count": (
                    "1"
                ),
                "target_scene": (
                    "RAILWAY_PLATFORM"
                ),
            },
        )
    )

    assert (
        len(
            request.reference_assets
        )
        == 1
    )

    print(
        "TEST 4 — identity-only reference request prepared → PASSED"
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
        "identity_smoke"
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
    # TEST 5 — CAPABILITY GATE
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
            "Identity test request is incompatible "
            "with Gemini provider capabilities: "
            +
            "; ".join(
                capability_result.issues
            )
        )

    print(
        "TEST 5 — provider accepts identity reference → PASSED"
    )

    # ============================================================
    # ONE REAL GENERATION ATTEMPT
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini identity "
        "disentanglement generation..."
    )
    print()

    attempt = (
        provider.generate(
            request=request,
            attempt_number=1,
        )
    )

    # ============================================================
    # TEST 6 — GENERATION SUCCESS
    # ============================================================

    if (
        attempt.status
        != GenerationStatus.SUCCEEDED
    ):

        print(
            "REAL IDENTITY GENERATION → FAILED"
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
        "TEST 6 — identity generation succeeded → PASSED"
    )

    # ============================================================
    # TEST 7 — EXACTLY ONE OUTPUT
    # ============================================================

    if (
        len(
            attempt.outputs
        )
        != 1
    ):

        raise AssertionError(
            "Expected exactly one generated output."
        )

    output = (
        attempt.outputs[0]
    )

    print(
        "TEST 7 — exactly one output returned → PASSED"
    )

    # ============================================================
    # TEST 8 — PHYSICAL ARTIFACT
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
            "Gemini reported success but identity "
            "artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated identity artifact is empty."
        )

    print(
        "TEST 8 — identity artifact materialized → PASSED"
    )

    # ============================================================
    # TEST 9 — LINEAGE
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
        "TEST 9 — identity generation lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "IDENTITY TEST IMAGE GENERATED"
    )
    print(
        "----------------------------------------"
    )

    print(
        "Provider:",
        attempt.provider,
    )

    print(
        "Reference:",
        reference_path,
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
        "This batch is not considered visually PASSED "
        "until reference and output are compared."
    )

    print()

    print(
        "========================================"
    )
    print(
        "BATCH 13F.1-B TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()