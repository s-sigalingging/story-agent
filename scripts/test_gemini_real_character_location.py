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
            "Perform exactly one real Gemini generation using "
            "one character reference and one location reference."
        )
    )

    parser.add_argument(
        "--character-reference",
        required=True,
        help=(
            "Path to the character reference image."
        ),
    )

    parser.add_argument(
        "--location-reference",
        required=True,
        help=(
            "Path to the location reference image."
        ),
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
# PHYSICAL REFERENCE VALIDATION
# ================================================================


def validate_reference(
    path_value: str,
    label: str,
) -> Path:

    path = (
        Path(
            path_value
        )
        .expanduser()
        .resolve()
    )

    if (
        not path.exists()
        or
        not path.is_file()
    ):

        raise FileNotFoundError(
            f"{label} reference was not found: "
            f"{path}"
        )

    if (
        path.stat().st_size
        <= 0
    ):

        raise ValueError(
            f"{label} reference is empty: "
            f"{path}"
        )

    return path


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 13F.2-B — CHARACTER + LOCATION GROUNDING"
    )
    print(
        "========================================"
    )

    args = (
        parse_arguments()
    )

    # ============================================================
    # TEST 1 — CHARACTER REFERENCE
    # ============================================================

    character_path = (
        validate_reference(
            path_value=(
                args.character_reference
            ),
            label=(
                "Character"
            ),
        )
    )

    print(
        "TEST 1 — physical character reference found → PASSED"
    )

    print(
        "         character:",
        character_path,
    )

    # ============================================================
    # TEST 2 — LOCATION REFERENCE
    # ============================================================

    location_path = (
        validate_reference(
            path_value=(
                args.location_reference
            ),
            label=(
                "Location"
            ),
        )
    )

    print(
        "TEST 2 — physical location reference found → PASSED"
    )

    print(
        "         location:",
        location_path,
    )

    # ============================================================
    # TEST 3 — REFERENCES ARE DISTINCT FILES
    # ============================================================

    if (
        character_path
        ==
        location_path
    ):

        raise ValueError(
            "Character and location references "
            "must be different files."
        )

    print(
        "TEST 3 — character and location references are distinct → PASSED"
    )

    # ============================================================
    # TEST 4 — EXECUTION GUARD
    # ============================================================

    if (
        not args.execute
    ):

        print(
            "TEST 4 — execution guard active → PASSED"
        )

        print()
        print(
            "REAL GENERATION NOT EXECUTED"
        )
        print(
            "----------------------------------------"
        )

        print(
            "Both references were validated successfully."
        )

        print()

        print(
            "To execute exactly ONE billable Gemini request:"
        )

        print()

        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_character_location.py "
            f'--character-reference "{character_path}" '
            f'--location-reference "{location_path}" '
            "--execute"
        )

        print()

        return

    print(
        "TEST 4 — explicit execution permission → PASSED"
    )

    # ============================================================
    # TEST 5 — CREDENTIAL
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
        "TEST 5 — Gemini credential available → PASSED"
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
        "GEN_REQ_REAL_GEMINI_CHAR_LOC_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_CHAR_LOC"
    )

    shot_id = (
        "EP_REAL_GEMINI_CHAR_LOC-S01-SHOT01"
    )

    # ============================================================
    # CHARACTER REFERENCE ASSET
    # ============================================================

    character_reference = (
        GenerationReferenceAsset(
            asset_id=(
                "ASSET_CHARACTER_FIXTURE"
            ),
            entity_id=(
                "CHARACTER_FIXTURE"
            ),
            asset_type=(
                "CHARACTER"
            ),
            name=(
                "Character Identity Fixture"
            ),
            reference_path=(
                str(
                    character_path
                )
            ),
        )
    )

    # ============================================================
    # LOCATION REFERENCE ASSET
    # ============================================================

    location_reference = (
        GenerationReferenceAsset(
            asset_id=(
                "ASSET_LOCATION_FIXTURE"
            ),
            entity_id=(
                "LOCATION_FIXTURE"
            ),
            asset_type=(
                "LOCATION"
            ),
            name=(
                "Location Environment Fixture"
            ),
            reference_path=(
                str(
                    location_path
                )
            ),
        )
    )

    # ============================================================
    # TEST 6 — MULTI-REFERENCE REQUEST
    #
    # The prompt explicitly assigns different semantic roles to
    # each supplied reference.
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
                "Two visual reference images are supplied. "
                ""
                "REFERENCE 1 is the CHARACTER identity reference. "
                "Use it only to preserve the man's facial identity, "
                "apparent age, hairstyle, facial proportions, "
                "overall appearance, and coherent wardrobe language. "
                ""
                "REFERENCE 2 is the LOCATION reference. "
                "Use it to preserve the visual identity and architecture "
                "of the dock warehouse: the tall timber structure, "
                "aged wooden beams, large industrial windows, "
                "wooden floorboards, cargo crates, dock atmosphere, "
                "and dim cinematic practical lighting. "
                ""
                "Create a NEW cinematic shot that combines these two "
                "references naturally. "
                ""
                "Show the same man from REFERENCE 1 walking slowly "
                "through the center of the warehouse from REFERENCE 2. "
                "He is no longer inside an office. "
                "He is not standing on a railway platform. "
                "He is not touching a desk or paperwork. "
                ""
                "Use a medium-wide cinematic composition showing enough "
                "of the character to identify him clearly while also "
                "showing enough warehouse architecture to recognize "
                "REFERENCE 2. "
                ""
                "The character should look physically integrated into "
                "the warehouse lighting and environment rather than "
                "pasted into the scene. "
                ""
                "Use restrained body language and a serious expression. "
                "The result should feel like one coherent premium "
                "animated mystery film frame, not a collage."
            ),
            negative_prompt=(
                "Do not reproduce the office from REFERENCE 1. "
                "Do not show the original office desk. "
                "Do not show the office telephone. "
                "Do not show office bookshelves. "
                "Do not reproduce the railway platform from the earlier "
                "identity test. "
                "Do not redesign the character's face. "
                "Do not replace the character with a different man. "
                "Do not radically change apparent age or hairstyle. "
                "Do not replace the warehouse with a generic interior. "
                "Do not create a modern warehouse. "
                "Do not create a collage or split-screen composition. "
                "Avoid exaggerated expressions, distorted anatomy, "
                "extra limbs, readable text, logos, watermarks, "
                "bright daylight, highly saturated colors, "
                "and visual clutter."
            ),
            reference_assets=[
                character_reference,
                location_reference,
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
                    "REAL_GEMINI_CHARACTER_LOCATION_GROUNDING"
                ),
                "reference_count": (
                    "2"
                ),
                "reference_1_role": (
                    "CHARACTER"
                ),
                "reference_2_role": (
                    "LOCATION"
                ),
                "canonical_asset": (
                    "false"
                ),
            },
        )
    )

    assert (
        len(
            request.reference_assets
        )
        == 2
    )

    assert (
        request.reference_assets[
            0
        ].asset_type
        ==
        "CHARACTER"
    )

    assert (
        request.reference_assets[
            1
        ].asset_type
        ==
        "LOCATION"
    )

    print(
        "TEST 6 — two-role generation request prepared → PASSED"
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
        "character_location_smoke"
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
    # TEST 7 — CAPABILITY GATE
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
            "Character + location request is incompatible "
            "with Gemini provider capabilities: "
            +
            "; ".join(
                capability_result.issues
            )
        )

    print(
        "TEST 7 — provider accepts two references → PASSED"
    )

    # ============================================================
    # EXACTLY ONE REAL GENERATION ATTEMPT
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini character + location "
        "generation..."
    )
    print()

    attempt = (
        provider.generate(
            request=request,
            attempt_number=1,
        )
    )

    # ============================================================
    # TEST 8 — GENERATION SUCCESS
    # ============================================================

    if (
        attempt.status
        != GenerationStatus.SUCCEEDED
    ):

        print(
            "REAL CHARACTER + LOCATION GENERATION → FAILED"
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
        "TEST 8 — character + location generation succeeded → PASSED"
    )

    # ============================================================
    # TEST 9 — EXACTLY ONE OUTPUT
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
        attempt.outputs[
            0
        ]
    )

    print(
        "TEST 9 — exactly one output returned → PASSED"
    )

    # ============================================================
    # TEST 10 — PHYSICAL ARTIFACT
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
            "Gemini reported success but the "
            "combined artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated combined artifact is empty."
        )

    print(
        "TEST 10 — combined artifact materialized → PASSED"
    )

    # ============================================================
    # TEST 11 — LINEAGE
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
        "TEST 11 — multi-reference lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "CHARACTER + LOCATION IMAGE GENERATED"
    )
    print(
        "----------------------------------------"
    )

    print(
        "Provider:",
        attempt.provider,
    )

    print(
        "Character reference:",
        character_path,
    )

    print(
        "Location reference:",
        location_path,
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
        "Technical execution alone does NOT pass Batch 13F.2-B."
    )

    print(
        "Visual review must confirm:"
    )

    print(
        "- recognizable character identity from reference A"
    )

    print(
        "- recognizable warehouse identity from reference B"
    )

    print(
        "- new pose and composition"
    )

    print(
        "- character lighting integrated with warehouse lighting"
    )

    print(
        "- no office or railway-scene carryover"
    )

    print(
        "- result looks coherent rather than composited"
    )

    print()

    print(
        "========================================"
    )
    print(
        "BATCH 13F.2-B TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()