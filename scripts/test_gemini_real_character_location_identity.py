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
            "character and location references with tighter framing "
            "for visual character identity verification."
        )
    )

    parser.add_argument(
        "--character-reference",
        required=True,
        help="Path to the character identity reference image.",
    )

    parser.add_argument(
        "--location-reference",
        required=True,
        help="Path to the location identity reference image.",
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
        Path(path_value)
        .expanduser()
        .resolve()
    )

    if (
        not path.exists()
        or
        not path.is_file()
    ):
        raise FileNotFoundError(
            f"{label} reference was not found: {path}"
        )

    if path.stat().st_size <= 0:
        raise ValueError(
            f"{label} reference is empty: {path}"
        )

    return path


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 13F.2-D — TIGHTER CHARACTER + LOCATION IDENTITY"
    )
    print(
        "========================================"
    )

    args = parse_arguments()

    # ============================================================
    # TEST 1 — CHARACTER REFERENCE
    # ============================================================

    character_path = validate_reference(
        path_value=args.character_reference,
        label="Character",
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

    location_path = validate_reference(
        path_value=args.location_reference,
        label="Location",
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

    if character_path == location_path:
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

    if not args.execute:

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
            "This experiment will generate a tighter "
            "character shot inside the referenced location."
        )

        print()
        print(
            "The purpose is to make the face large enough "
            "for direct visual identity comparison."
        )

        print()
        print(
            "To execute exactly ONE billable Gemini request:"
        )

        print()
        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_character_location_identity.py "
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

    api_key = os.getenv(
        "GEMINI_API_KEY"
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
        datetime.now(timezone.utc)
        .strftime("%Y%m%dT%H%M%SZ")
    )

    request_id = (
        "GEN_REQ_REAL_GEMINI_CHARLOC_IDENTITY_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_CHARLOC_IDENTITY"
    )

    shot_id = (
        "EP_REAL_GEMINI_CHARLOC_IDENTITY-S01-SHOT01"
    )

    # ============================================================
    # CHARACTER REFERENCE
    # ============================================================

    character_reference = GenerationReferenceAsset(
        asset_id="ASSET_CHARACTER_FIXTURE",
        entity_id="CHARACTER_FIXTURE",
        asset_type="CHARACTER",
        name="Character Identity Fixture",
        reference_path=str(character_path),
    )

    # ============================================================
    # LOCATION REFERENCE
    # ============================================================

    location_reference = GenerationReferenceAsset(
        asset_id="ASSET_LOCATION_FIXTURE",
        entity_id="LOCATION_FIXTURE",
        asset_type="LOCATION",
        name="Location Identity Fixture",
        reference_path=str(location_path),
    )

    # ============================================================
    # TEST 6 — TIGHTER IDENTITY REQUEST
    #
    # This experiment deliberately gives the character enough
    # screen space for facial identity inspection.
    #
    # It is NOT intended to replace wide cinematography.
    #
    # We are separating:
    #
    #   wide-shot environment / silhouette consistency
    #
    # from:
    #
    #   medium-shot facial identity consistency
    #
    # ============================================================

    request = GenerationRequest(
        request_id=request_id,
        episode_id=episode_id,
        shot_id=shot_id,
        generation_type=GenerationType.KEYFRAME,
        prompt=(
            "Two visual reference images are supplied. "

            "REFERENCE 1 is the CHARACTER identity reference. "
            "The man in REFERENCE 1 is the canonical identity "
            "for this test. Preserve his recognizable facial "
            "identity as closely as possible: the same apparent "
            "age, facial proportions, jaw structure, nose shape, "
            "eye placement, brow structure, hairstyle, hairline, "
            "and overall facial character. "

            "Preserve the same dark fedora, long dark overcoat, "
            "formal suit, white shirt, dark tie, and restrained "
            "noir detective appearance. "

            "REFERENCE 2 is the LOCATION identity reference. "
            "The scene must take place inside that same old "
            "dock warehouse. Preserve its recognizable aged "
            "heavy timber construction, industrial windows, "
            "weathered wooden surfaces, dock-side atmosphere, "
            "cargo elements, muted palette, deep shadows, "
            "and dim practical lighting. "

            "Create a NEW cinematic camera setup inside the "
            "warehouse. "

            "Frame the same man from approximately the waist "
            "or lower chest upward in a MEDIUM SHOT. "

            "His face must be clearly visible and contain enough "
            "detail for direct identity comparison with "
            "REFERENCE 1. "

            "Do not hide the face in deep shadow. "
            "Use soft directional warehouse lighting so that "
            "the eyes, nose, jaw, cheek structure, and other "
            "recognizable facial features remain readable. "

            "The man is standing beside a heavy timber support "
            "column inside the warehouse, quietly studying "
            "something outside the frame. "

            "His posture is controlled and still. "
            "Use a subtle three-quarter body orientation while "
            "keeping most of his face visible to the camera. "

            "The warehouse must remain clearly recognizable "
            "behind him. Include enough environmental context "
            "to establish that this is the same dock warehouse, "
            "but do not allow the environment to make the "
            "character tiny in the frame. "

            "This must feel like a tighter camera setup from "
            "the same cinematic sequence, not a portrait studio "
            "photograph and not a recreation of the office "
            "shown in the character reference. "

            "Preserve the premium dark mystery illustrated-film "
            "visual language shared by both references. "

            "The priorities for this image are, in order: "
            "first, preserve CHARACTER FACIAL IDENTITY; "
            "second, preserve CHARACTER WARDROBE IDENTITY; "
            "third, preserve LOCATION IDENTITY; "
            "fourth, create a coherent new cinematic composition."
        ),
        negative_prompt=(
            "Do not replace the man with a different person. "
            "Do not redesign his face. "
            "Do not significantly change his apparent age. "
            "Do not change his hairstyle or hairline. "
            "Do not obscure the face with extreme darkness. "
            "Do not make the face tiny, blurry, vague, distant, "
            "featureless, or unreadable. "
            "Do not crop the entire face out of frame. "
            "Do not turn the head fully away from the camera. "
            "Do not create an extreme profile view. "
            "Do not remove the fedora, overcoat, suit, shirt, "
            "or tie. "
            "Do not reproduce the office from the character "
            "reference. "
            "Do not show the office desk, green desk lamp, "
            "telephone, filing cabinet, or bookshelves from "
            "the character reference. "
            "Do not create a railway station or train platform. "
            "Do not create a modern warehouse. "
            "Do not replace the timber dock warehouse with "
            "concrete, futuristic, or unrelated architecture. "
            "Do not copy the exact composition of either "
            "reference image. "
            "Do not create a collage or split screen. "
            "Avoid distorted anatomy, extra fingers, extra limbs, "
            "readable text, logos, watermarks, bright daylight, "
            "highly saturated colors, and excessive visual clutter."
        ),
        reference_assets=[
            character_reference,
            location_reference,
        ],
        output=GenerationOutputSpec(
            width=1080,
            height=1920,
            aspect_ratio="9:16",
            output_format="png",
        ),
        metadata={
            "purpose": (
                "REAL_GEMINI_CHARACTER_LOCATION_IDENTITY"
            ),
            "reference_count": "2",
            "reference_1_role": "CHARACTER",
            "reference_2_role": "LOCATION",
            "framing_requirement": "MEDIUM",
            "identity_priority": "FACIAL_IDENTITY",
            "canonical_asset": "false",
        },
    )

    assert len(request.reference_assets) == 2

    assert (
        request.reference_assets[0].asset_type
        == "CHARACTER"
    )

    assert (
        request.reference_assets[1].asset_type
        == "LOCATION"
    )

    print(
        "TEST 6 — tighter identity request prepared → PASSED"
    )

    # ============================================================
    # ARTIFACT STORE
    # ============================================================

    artifact_root = (
        Path("data")
        / "generated"
        / "gemini"
        / "character_location_identity_smoke"
    )

    artifact_store = GenerationArtifactStore(
        base_path=str(artifact_root)
    )

    # ============================================================
    # PROVIDER
    # ============================================================

    provider = GeminiGenerationProvider(
        artifact_store=artifact_store,
        model="gemini-3.1-flash-image",
        api_key_env="GEMINI_API_KEY",
        network_enabled=True,
    )

    # ============================================================
    # TEST 7 — CAPABILITY GATE
    # ============================================================

    capability_result = (
        provider.validate_request_capabilities(
            request
        )
    )

    if not capability_result.compatible:
        raise RuntimeError(
            "Character/location identity request is incompatible "
            "with Gemini provider capabilities: "
            + "; ".join(
                capability_result.issues
            )
        )

    print(
        "TEST 7 — provider accepts identity request → PASSED"
    )

    # ============================================================
    # EXACTLY ONE REAL ATTEMPT
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini tighter-identity generation..."
    )
    print()

    attempt = provider.generate(
        request=request,
        attempt_number=1,
    )

    # ============================================================
    # TEST 8 — GENERATION SUCCESS
    # ============================================================

    if (
        attempt.status
        != GenerationStatus.SUCCEEDED
    ):

        print(
            "REAL CHARACTER/LOCATION IDENTITY GENERATION → FAILED"
        )

        if attempt.error is not None:

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

        raise SystemExit(1)

    print(
        "TEST 8 — tighter identity generation succeeded → PASSED"
    )

    # ============================================================
    # TEST 9 — EXACTLY ONE OUTPUT
    # ============================================================

    if len(attempt.outputs) != 1:
        raise AssertionError(
            "Expected exactly one generated output."
        )

    output = attempt.outputs[0]

    print(
        "TEST 9 — exactly one output returned → PASSED"
    )

    # ============================================================
    # TEST 10 — PHYSICAL ARTIFACT
    # ============================================================

    output_path = Path(
        output.output_path
    )

    if (
        not output_path.exists()
        or
        not output_path.is_file()
    ):
        raise AssertionError(
            "Gemini reported success but the tighter identity "
            "artifact does not exist."
        )

    if output_path.stat().st_size <= 0:
        raise AssertionError(
            "Generated tighter identity artifact is empty."
        )

    print(
        "TEST 10 — identity artifact materialized → PASSED"
    )

    # ============================================================
    # TEST 11 — LINEAGE
    # ============================================================

    expected_attempt_id = (
        f"{request_id}_ATTEMPT_001"
    )

    expected_output_id = (
        f"{request_id}_ATTEMPT_001_OUTPUT_001"
    )

    assert (
        attempt.attempt_id
        == expected_attempt_id
    )

    assert (
        output.output_id
        == expected_output_id
    )

    print(
        "TEST 11 — identity lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "TIGHTER CHARACTER + LOCATION IMAGE GENERATED"
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
        "Technical execution alone does NOT pass Batch 13F.2-D."
    )

    print()

    print(
        "Visual review must compare the generated image "
        "directly against BOTH reference images."
    )

    print()

    print(
        "Review criteria:"
    )

    print(
        "- face is large and detailed enough for comparison"
    )

    print(
        "- facial identity resembles the character reference"
    )

    print(
        "- apparent age and facial structure remain coherent"
    )

    print(
        "- fedora, coat, suit, shirt, and tie remain coherent"
    )

    print(
        "- warehouse identity remains recognizable"
    )

    print(
        "- character is naturally integrated into warehouse lighting"
    )

    print(
        "- office environment does not leak into the result"
    )

    print(
        "- result is a new composition rather than a copied reference"
    )

    print()

    print(
        "========================================"
    )
    print(
        "BATCH 13F.2-D TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL IDENTITY REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()