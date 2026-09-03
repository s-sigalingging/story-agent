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
            "character and location references while forcing a "
            "substantially different camera viewpoint."
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
            "Explicitly permit exactly one real Gemini "
            "network generation attempt."
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
        "BATCH 13F.2-C — LOCATION VIEWPOINT DISENTANGLEMENT"
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
    # TEST 3 — DISTINCT REFERENCES
    # ============================================================

    if (
        character_path
        ==
        location_path
    ):

        raise ValueError(
            "Character and location references "
            "must be different physical files."
        )

    print(
        "TEST 3 — references are physically distinct → PASSED"
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
            "This experiment will request a substantially "
            "different camera viewpoint while preserving "
            "character and location identity."
        )

        print()

        print(
            "To execute exactly ONE billable Gemini request:"
        )

        print()

        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_location_viewpoint.py "
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
        "GEN_REQ_REAL_GEMINI_VIEWPOINT_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_VIEWPOINT"
    )

    shot_id = (
        "EP_REAL_GEMINI_VIEWPOINT-S01-SHOT01"
    )

    # ============================================================
    # CHARACTER REFERENCE
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
    # LOCATION REFERENCE
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
                "Location Identity Fixture"
            ),
            reference_path=(
                str(
                    location_path
                )
            ),
        )
    )

    # ============================================================
    # TEST 6 — VIEWPOINT-DISENTANGLEMENT REQUEST
    #
    # Important:
    #
    # We deliberately ask for a substantially different viewpoint,
    # but we do NOT claim that unseen architecture in the single
    # location reference has exact canonical geometry.
    #
    # The test is whether Gemini can preserve the location's
    # recognizable visual identity while creating a new shot.
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
                "Preserve the same man's recognizable facial identity, "
                "apparent age, hairstyle, facial proportions, "
                "silhouette, and coherent wardrobe language. "
                ""
                "REFERENCE 2 is the LOCATION identity reference. "
                "Preserve the recognizable visual language of that "
                "same old dock warehouse: aged heavy timber beams, "
                "weathered wooden construction, worn floorboards, "
                "industrial windows, cargo storage elements, "
                "dock-side atmosphere, muted colors, deep shadows, "
                "and dim practical lighting. "
                ""
                "Create a NEW cinematic shot inside this same "
                "warehouse environment, but use a SUBSTANTIALLY "
                "DIFFERENT CAMERA VIEWPOINT from REFERENCE 2. "
                ""
                "Do NOT recreate the original camera placement. "
                "Do NOT reproduce the original central aisle "
                "composition. "
                ""
                "Place the camera deeper inside the warehouse, "
                "offset toward the dock-side portion of the building, "
                "and look diagonally across the interior toward the "
                "large industrial windows and timber structure. "
                ""
                "The image should reveal a different arrangement "
                "of foreground and background elements appropriate "
                "to this new camera position. "
                ""
                "Show the same man from REFERENCE 1 standing near "
                "one of the large timber support columns, quietly "
                "observing the warehouse. "
                ""
                "Use a medium-wide cinematic framing. "
                "The character must remain clearly visible, but the "
                "location itself is the primary subject of this test. "
                ""
                "Preserve the LOCATION IDENTITY rather than copying "
                "the exact LOCATION COMPOSITION. "
                ""
                "The result should feel like another camera setup "
                "filmed inside the same warehouse, not a redesigned "
                "warehouse and not a transformed copy of the "
                "reference frame. "
                ""
                "Keep the same premium dark mystery illustrated "
                "film language and integrate the character naturally "
                "into the warehouse lighting."
            ),
            negative_prompt=(
                "Do not reproduce the exact camera viewpoint from "
                "the location reference. "
                "Do not reproduce the original central aisle framing. "
                "Do not place every crate, column, window, and machine "
                "in the same screen position as the location reference. "
                "Do not simply insert the character into the original "
                "location image. "
                "Do not create a completely unrelated warehouse. "
                "Do not create a modern warehouse. "
                "Do not replace timber architecture with concrete "
                "or futuristic architecture. "
                "Do not reproduce the office from the character "
                "reference. "
                "Do not show an office desk, office telephone, "
                "or office bookshelves. "
                "Do not create a railway platform. "
                "Do not redesign the character's face. "
                "Do not replace him with a different man. "
                "Do not radically change his apparent age or "
                "hairstyle. "
                "Do not create a collage or split screen. "
                "Avoid distorted architecture, distorted anatomy, "
                "extra limbs, readable text, logos, watermarks, "
                "bright daylight, highly saturated colors, "
                "and excessive visual clutter."
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
                    "REAL_GEMINI_LOCATION_VIEWPOINT_DISENTANGLEMENT"
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
                "camera_requirement": (
                    "SUBSTANTIALLY_DIFFERENT_VIEWPOINT"
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
        "TEST 6 — new-viewpoint request prepared → PASSED"
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
        "location_viewpoint_smoke"
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
            "Location viewpoint request is incompatible "
            "with Gemini provider capabilities: "
            +
            "; ".join(
                capability_result.issues
            )
        )

    print(
        "TEST 7 — provider accepts viewpoint request → PASSED"
    )

    # ============================================================
    # EXACTLY ONE REAL ATTEMPT
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini location-viewpoint "
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
            "REAL LOCATION VIEWPOINT GENERATION → FAILED"
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
        "TEST 8 — viewpoint generation succeeded → PASSED"
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
            "Gemini reported success but the viewpoint "
            "artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated viewpoint artifact is empty."
        )

    print(
        "TEST 10 — viewpoint artifact materialized → PASSED"
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
        "TEST 11 — viewpoint lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "LOCATION VIEWPOINT IMAGE GENERATED"
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
        "Technical execution alone does NOT pass Batch 13F.2-C."
    )

    print()

    print(
        "Visual review must determine:"
    )

    print(
        "- camera viewpoint is substantially different"
    )

    print(
        "- warehouse still reads as the same location"
    )

    print(
        "- timber/material/lighting language is preserved"
    )

    print(
        "- output does not simply copy the location composition"
    )

    print(
        "- character remains visually coherent"
    )

    print(
        "- office and railway environments do not leak in"
    )

    print()

    print(
        "========================================"
    )
    print(
        "BATCH 13F.2-C TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()