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
            "character, location, and prop references."
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
        "--prop-reference",
        required=True,
        help="Path to the approved prop reference image.",
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
# REFERENCE VALIDATION
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

    if (
        path.stat().st_size
        <= 0
    ):

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
        "BATCH 13F.3-B — CHARACTER + LOCATION + PROP GROUNDING"
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
    # TEST 3 — PROP REFERENCE
    # ============================================================

    prop_path = validate_reference(
        path_value=args.prop_reference,
        label="Prop",
    )

    print(
        "TEST 3 — physical prop reference found → PASSED"
    )

    print(
        "         prop:",
        prop_path,
    )

    # ============================================================
    # TEST 4 — REFERENCES ARE DISTINCT
    # ============================================================

    unique_paths = {
        character_path,
        location_path,
        prop_path,
    }

    if len(unique_paths) != 3:

        raise ValueError(
            "Character, location, and prop references "
            "must be three distinct physical files."
        )

    print(
        "TEST 4 — all references are physically distinct → PASSED"
    )

    # ============================================================
    # TEST 5 — EXECUTION GUARD
    # ============================================================

    if not args.execute:

        print(
            "TEST 5 — execution guard active → PASSED"
        )

        print()
        print(
            "REAL GENERATION NOT EXECUTED"
        )
        print(
            "----------------------------------------"
        )

        print(
            "Reference roles:"
        )

        print(
            "REFERENCE 1 → CHARACTER / WHO"
        )

        print(
            "REFERENCE 2 → LOCATION / WHERE"
        )

        print(
            "REFERENCE 3 → PROP / WHAT"
        )

        print()
        print(
            "To execute exactly ONE billable Gemini request:"
        )

        print()
        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_character_location_prop.py "
            f'--character-reference "{character_path}" '
            f'--location-reference "{location_path}" '
            f'--prop-reference "{prop_path}" '
            "--execute"
        )

        print()

        return

    print(
        "TEST 5 — explicit execution permission → PASSED"
    )

    # ============================================================
    # TEST 6 — CREDENTIAL
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
        "TEST 6 — Gemini credential available → PASSED"
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
        "GEN_REQ_REAL_GEMINI_CHAR_LOC_PROP_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_CHAR_LOC_PROP"
    )

    shot_id = (
        "EP_REAL_GEMINI_CHAR_LOC_PROP-S01-SHOT01"
    )

    # ============================================================
    # REFERENCE 1 — CHARACTER
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
                str(character_path)
            ),
        )
    )

    # ============================================================
    # REFERENCE 2 — LOCATION
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
                str(location_path)
            ),
        )
    )

    # ============================================================
    # REFERENCE 3 — PROP
    # ============================================================

    prop_reference = (
        GenerationReferenceAsset(
            asset_id=(
                "ASSET_PROP_FIXTURE"
            ),
            entity_id=(
                "PROP_FIXTURE"
            ),
            asset_type=(
                "PROP"
            ),
            name=(
                "Administrative Folder Prop Fixture"
            ),
            reference_path=(
                str(prop_path)
            ),
        )
    )

    # ============================================================
    # TEST 7 — THREE-WAY GROUNDING REQUEST
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
                "Three visual reference images are supplied. "

                "REFERENCE 1 is the CHARACTER identity reference. "
                "Preserve the same man's recognizable facial identity, "
                "apparent age, hairstyle, facial proportions, "
                "dark fedora, long dark overcoat, formal suit, "
                "white shirt, dark tie, silhouette, and restrained "
                "noir detective appearance. "

                "REFERENCE 2 is the LOCATION identity reference. "
                "The scene must take place inside that same old dock "
                "warehouse. Preserve its aged timber construction, "
                "heavy wooden support beams, industrial windows, "
                "weathered floorboards, dock-side atmosphere, "
                "cargo-storage language, muted palette, deep shadows, "
                "and dim practical lighting. "

                "REFERENCE 3 is the PROP identity reference. "
                "Preserve the same simple brown administrative "
                "paper folder containing several loose off-white "
                "documents. Preserve its thin kraft/manila construction, "
                "ordinary office-archive appearance, worn edges, "
                "and visible loose paperwork. "

                "Create a NEW cinematic shot combining all three "
                "references naturally. "

                "Show the same man from REFERENCE 1 standing inside "
                "the warehouse from REFERENCE 2 while carefully "
                "examining the folder from REFERENCE 3. "

                "He holds the brown administrative folder naturally "
                "with both hands around lower-chest or upper-waist level. "

                "The folder is partially open. "
                "Several off-white paper documents remain visibly "
                "nested inside it. "

                "The prop must be large enough in frame that the viewer "
                "can clearly recognize it as the same type of brown "
                "administrative folder from REFERENCE 3. "

                "Use a MEDIUM cinematic composition, approximately "
                "waist-up or lower-chest-up. "

                "The man's face must remain clearly visible and detailed "
                "enough for identity comparison. "

                "The warehouse must also remain clearly recognizable "
                "behind him through timber beams, industrial windows, "
                "weathered wood, or other distinctive architecture. "

                "The character should appear physically integrated into "
                "the warehouse lighting. "

                "The folder should feel like a real physical object "
                "being held by the character, not pasted into the image. "

                "Do not make the prop visually magical or unusually "
                "important-looking. Its narrative importance comes "
                "from its contents, not decorative design. "

                "Use restrained body language and a serious, focused "
                "expression as he studies the documents. "

                "The result should feel like one coherent premium "
                "illustrated mystery-film frame. "

                "Priority order: "
                "first preserve CHARACTER FACIAL IDENTITY; "
                "second preserve LOCATION IDENTITY; "
                "third preserve PROP IDENTITY; "
                "fourth preserve the shared illustrated visual style; "
                "fifth create a natural interaction between character "
                "and prop."
            ),
            negative_prompt=(
                "Do not replace the character with a different man. "
                "Do not redesign his face. "
                "Do not significantly change his apparent age. "
                "Do not change his hairstyle or hairline. "
                "Do not obscure his face. "

                "Do not remove the fedora, overcoat, suit, white shirt, "
                "or dark tie. "

                "Do not reproduce the office from the character reference. "
                "No office desk. "
                "No green desk lamp. "
                "No office telephone. "
                "No office bookshelves. "

                "Do not create a railway platform. "

                "Do not replace the warehouse with a generic interior. "
                "Do not create a modern warehouse. "
                "Do not replace timber architecture with concrete "
                "or futuristic architecture. "

                "Do not replace the brown folder with a book. "
                "No bound book. "
                "No leather ledger. "
                "No ancient tome. "
                "No medieval manuscript. "
                "No fantasy grimoire. "

                "No metal corners. "
                "No clasp. "
                "No lock. "
                "No crest. "
                "No seal. "
                "No emblem. "
                "No decorative ornament. "

                "Do not turn the folder into a modern plastic binder. "
                "No ring binder. "
                "No glossy stationery. "

                "Do not make the folder disappear. "
                "Do not make the prop tiny or unreadable. "
                "Do not merge the folder unnaturally into the hands. "
                "Do not create extra hands or extra fingers. "

                "No readable text. "
                "No readable names. "
                "No readable dates. "
                "No readable numbers. "
                "No readable codes. "
                "No A-1930 marking. "

                "Do not create a collage or split-screen composition. "

                "Avoid distorted anatomy, extra limbs, malformed hands, "
                "logos, watermarks, bright daylight, highly saturated "
                "colors, photorealistic product-photography style, "
                "and excessive visual clutter."
            ),
            reference_assets=[
                character_reference,
                location_reference,
                prop_reference,
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
                    "REAL_GEMINI_CHARACTER_LOCATION_PROP_GROUNDING"
                ),
                "reference_count": (
                    "3"
                ),
                "reference_1_role": (
                    "CHARACTER"
                ),
                "reference_2_role": (
                    "LOCATION"
                ),
                "reference_3_role": (
                    "PROP"
                ),
                "framing_requirement": (
                    "MEDIUM"
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
        == 3
    )

    assert (
        request.reference_assets[0].asset_type
        == "CHARACTER"
    )

    assert (
        request.reference_assets[1].asset_type
        == "LOCATION"
    )

    assert (
        request.reference_assets[2].asset_type
        == "PROP"
    )

    print(
        "TEST 7 — three-role generation request prepared → PASSED"
    )

    # ============================================================
    # ARTIFACT STORE
    # ============================================================

    artifact_root = (
        Path("data")
        / "generated"
        / "gemini"
        / "character_location_prop_smoke"
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
    # TEST 8 — CAPABILITY GATE
    # ============================================================

    capability_result = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    if not capability_result.compatible:

        raise RuntimeError(
            "Character + location + prop request is incompatible "
            "with Gemini provider capabilities: "
            + "; ".join(
                capability_result.issues
            )
        )

    print(
        "TEST 8 — provider accepts three references → PASSED"
    )

    # ============================================================
    # EXACTLY ONE REAL ATTEMPT
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini character + location + prop "
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
    # TEST 9 — GENERATION SUCCESS
    # ============================================================

    if (
        attempt.status
        != GenerationStatus.SUCCEEDED
    ):

        print(
            "REAL CHARACTER + LOCATION + PROP GENERATION → FAILED"
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

        raise SystemExit(
            1
        )

    print(
        "TEST 9 — three-way generation succeeded → PASSED"
    )

    # ============================================================
    # TEST 10 — EXACTLY ONE OUTPUT
    # ============================================================

    if len(attempt.outputs) != 1:

        raise AssertionError(
            "Expected exactly one generated output."
        )

    output = (
        attempt.outputs[0]
    )

    print(
        "TEST 10 — exactly one output returned → PASSED"
    )

    # ============================================================
    # TEST 11 — PHYSICAL ARTIFACT
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
            "Gemini reported success but the three-way "
            "artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated three-way artifact is empty."
        )

    print(
        "TEST 11 — three-way artifact materialized → PASSED"
    )

    # ============================================================
    # TEST 12 — LINEAGE
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
        "TEST 12 — three-way lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "CHARACTER + LOCATION + PROP IMAGE GENERATED"
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
        "Prop reference:",
        prop_path,
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
        "Technical success alone does NOT pass Batch 13F.3-B."
    )

    print()
    print(
        "Visual review must confirm:"
    )

    print(
        "- face clearly resembles the character fixture"
    )

    print(
        "- wardrobe remains coherent"
    )

    print(
        "- warehouse remains recognizable"
    )

    print(
        "- brown folder remains recognizable"
    )

    print(
        "- loose off-white documents remain visible"
    )

    print(
        "- prop is naturally held by the character"
    )

    print(
        "- no book / medieval drift"
    )

    print(
        "- no office or railway environment leakage"
    )

    print(
        "- shared illustrated visual language remains coherent"
    )

    print(
        "- result is a genuinely new composition"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13F.3-B TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL THREE-WAY GROUNDING REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()