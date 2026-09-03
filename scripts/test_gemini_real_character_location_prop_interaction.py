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
    GenerationReferenceRole,
    GenerationReferenceTransformation,
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
            "character, location, and prop references while "
            "explicitly validating natural prop interaction "
            "orientation."
        )
    )

    parser.add_argument(
        "--character-reference",
        required=True,
        help=(
            "Path to the approved character identity fixture."
        ),
    )

    parser.add_argument(
        "--location-reference",
        required=True,
        help=(
            "Path to the approved location identity fixture."
        ),
    )

    parser.add_argument(
        "--prop-reference",
        required=True,
        help=(
            "Path to the approved Revision 4 prop fixture."
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
        "BATCH 13F.3-D — PROP INTERACTION ORIENTATION"
    )
    print(
        "REAL VALIDATION"
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
    # TEST 3 — PROP REFERENCE
    # ============================================================

    prop_path = (
        validate_reference(
            path_value=(
                args.prop_reference
            ),
            label=(
                "Prop"
            ),
        )
    )

    print(
        "TEST 3 — physical prop reference found → PASSED"
    )

    print(
        "         prop:",
        prop_path,
    )

    # ============================================================
    # TEST 4 — DISTINCT REFERENCES
    # ============================================================

    unique_paths = {
        character_path,
        location_path,
        prop_path,
    }

    if (
        len(
            unique_paths
        )
        != 3
    ):

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

    if (
        not args.execute
    ):

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
            "This batch validates the real visual effect of "
            "the reference usage contract introduced in 13F.3-C."
        )

        print()

        print(
            "Expected prop behavior:"
        )

        print(
            "- preserve folder identity"
        )

        print(
            "- preserve brown kraft/manila material"
        )

        print(
            "- preserve loose off-white documents"
        )

        print(
            "- allow folder rotation"
        )

        print(
            "- allow perspective change"
        )

        print(
            "- allow open/close adaptation"
        )

        print(
            "- adapt naturally to character interaction"
        )

        print(
            "- document surfaces should primarily face the reader"
        )

        print(
            "- camera may see the back, edge, or oblique side"
        )

        print()

        print(
            "To execute exactly ONE billable Gemini request:"
        )

        print()

        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_character_location_prop_interaction.py "
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
        "GEN_REQ_REAL_GEMINI_PROP_INTERACTION_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_PROP_INTERACTION"
    )

    shot_id = (
        "EP_REAL_GEMINI_PROP_INTERACTION-S01-SHOT01"
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
                str(
                    character_path
                )
            ),
            reference_role=(
                GenerationReferenceRole.CHARACTER
            ),
            preserve_attributes=[
                "facial identity",
                "apparent age",
                "hairstyle",
                "facial proportions",
                "dark fedora",
                "long dark overcoat",
                "formal suit",
                "white shirt",
                "dark tie",
                "body identity",
                "overall noir detective identity",
            ],
            allowed_transformations=[
                GenerationReferenceTransformation.CHANGE_POSE,
                GenerationReferenceTransformation.CHANGE_EXPRESSION,
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
            ],
            usage_instruction=(
                "Preserve this man's identity and wardrobe. "
                "He may change pose naturally so he can hold "
                "and read the supplied prop. His face must remain "
                "clearly recognizable and should not be copied "
                "from the exact pose or framing of the reference."
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
                str(
                    location_path
                )
            ),
            reference_role=(
                GenerationReferenceRole.LOCATION
            ),
            preserve_attributes=[
                "aged heavy timber architecture",
                "industrial windows",
                "weathered wooden surfaces",
                "dock-side atmosphere",
                "cargo-storage language",
                "muted mystery palette",
                "illustrated noir environment identity",
            ],
            allowed_transformations=[
                GenerationReferenceTransformation.CHANGE_VIEWPOINT,
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
            ],
            usage_instruction=(
                "Preserve the recognizable identity of this dock "
                "warehouse, but compose a new medium cinematic shot. "
                "Do not copy the exact camera position or object "
                "placement from the location reference."
            ),
        )
    )

    # ============================================================
    # REFERENCE 3 — PROP
    #
    # THIS IS THE CORE OF BATCH 13F.3-D.
    #
    # Identity is invariant.
    #
    # Exact orientation is NOT invariant.
    #
    # The prop must adapt to its physical interaction with the
    # character.
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
                str(
                    prop_path
                )
            ),
            reference_role=(
                GenerationReferenceRole.PROP
            ),
            preserve_attributes=[
                "brown administrative folder identity",
                "kraft or manila paper material",
                "thin flexible folder construction",
                "simple utilitarian shape",
                "worn paper edges",
                "loose off-white administrative documents",
                "non-ornamental archival appearance",
                "illustrated rendering language",
            ],
            allowed_transformations=[
                GenerationReferenceTransformation.ROTATE,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.OPEN_CLOSE,
                GenerationReferenceTransformation.ADAPT_TO_INTERACTION,
            ],
            usage_instruction=(
                "This folder is being actively held and read by "
                "the character. Preserve the recognizable physical "
                "identity of the folder and its loose documents, "
                "but DO NOT preserve the exact camera-facing "
                "orientation shown in the reference image. "

                "Rotate and orient the folder naturally according "
                "to human reading posture. "

                "The open document surfaces should primarily face "
                "the character who is reading them, NOT the camera. "

                "From the camera viewpoint, it is physically valid "
                "to see the back cover, outer folder surface, "
                "paper edges, side profile, or an oblique partial "
                "view of the documents. "

                "Do not rotate the folder unnaturally simply to "
                "show the same front-facing document view as the "
                "master reference. "

                "Physical interaction takes priority over copying "
                "the master reference viewpoint."
            ),
        )
    )

    # ============================================================
    # TEST 7 — REFERENCE USAGE CONTRACT
    # ============================================================

    assert (
        prop_reference.reference_role
        ==
        GenerationReferenceRole.PROP
    )

    assert (
        GenerationReferenceTransformation.ROTATE
        in
        prop_reference.allowed_transformations
    )

    assert (
        GenerationReferenceTransformation.CHANGE_PERSPECTIVE
        in
        prop_reference.allowed_transformations
    )

    assert (
        GenerationReferenceTransformation.OPEN_CLOSE
        in
        prop_reference.allowed_transformations
    )

    assert (
        GenerationReferenceTransformation.ADAPT_TO_INTERACTION
        in
        prop_reference.allowed_transformations
    )

    print(
        "TEST 7 — prop transformation contract active → PASSED"
    )

    # ============================================================
    # TEST 8 — GENERATION REQUEST
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
                "Create one coherent cinematic illustrated mystery "
                "film frame using the three supplied visual references. "

                "The character from the CHARACTER reference is "
                "standing inside the warehouse from the LOCATION "
                "reference. "

                "He is carefully reading and examining the brown "
                "administrative folder from the PROP reference. "

                "Use a MEDIUM cinematic composition, approximately "
                "waist-up. "

                "The character holds the folder naturally with both "
                "hands around upper-waist or lower-chest level. "

                "The folder is partially open and contains several "
                "loose off-white administrative documents. "

                "IMPORTANT PHYSICAL INTERACTION: "
                "the document surfaces must be oriented primarily "
                "toward the character's eyes because HE is reading "
                "them. "

                "Do not orient the papers toward the camera merely "
                "to reproduce the reference image. "

                "The camera should see a physically plausible view "
                "of the folder from the opposite side or from an "
                "oblique angle. "

                "It is acceptable and desirable for the camera to "
                "see the back or outer side of the brown folder, "
                "the folder edge, and only partial document surfaces "
                "when physically appropriate. "

                "His hands should support the folder naturally. "
                "The wrists, fingers, elbows, folder angle, and "
                "eye-line must all agree with the action of reading. "

                "His gaze should clearly fall downward toward the "
                "documents. "

                "The character's face must remain recognizable and "
                "detailed. Preserve the same apparent age, facial "
                "structure, fedora, overcoat, suit, shirt, and tie. "

                "The dock warehouse must remain recognizable behind "
                "him through its aged timber structure, industrial "
                "windows, wooden surfaces, and dock-side visual "
                "language. "

                "Preserve the shared realistic-stylized illustrated "
                "noir aesthetic. "

                "The scene must feel physically coherent, not like "
                "three reference images pasted together. "

                "Identity preservation and physical interaction are "
                "different requirements: preserve WHO the character "
                "is, preserve WHERE the scene is, and preserve WHAT "
                "the folder is, while allowing pose, viewpoint, "
                "perspective, and prop orientation to adapt naturally "
                "to the shot."
            ),
            negative_prompt=(
                "Do not replace the character with a different man. "
                "Do not redesign his face. "
                "Do not significantly alter his apparent age. "
                "Do not remove his fedora, overcoat, suit, white "
                "shirt, or dark tie. "

                "Do not obscure his face. "
                "Do not make his gaze unrelated to the document. "

                "Do not reproduce the office from the character "
                "reference. "
                "No office desk. "
                "No green desk lamp. "
                "No telephone. "
                "No bookshelves. "

                "Do not create a railway station. "

                "Do not replace the warehouse with a generic modern "
                "interior. "
                "Do not replace timber construction with concrete "
                "or futuristic architecture. "

                "Do not replace the brown folder with a book. "
                "No bound ledger. "
                "No leather cover. "
                "No medieval tome. "
                "No fantasy artifact. "
                "No brass corners. "
                "No metal clasp. "
                "No seal. "
                "No crest. "
                "No emblem. "

                "Do not force the front face of the prop reference "
                "toward the camera. "

                "Do not make the character hold the folder backwards. "

                "Do not orient readable document surfaces toward "
                "the camera while the character is supposedly "
                "reading the opposite side. "

                "Do not create physically contradictory hand, "
                "eye-line, and folder orientation. "

                "Do not paste the reference folder flat onto the "
                "character's hands. "

                "Do not make the folder float. "
                "Do not merge the folder into the hands. "

                "Avoid extra hands, extra fingers, fused fingers, "
                "broken wrists, malformed arms, distorted anatomy, "
                "warped folder geometry, duplicate objects, "
                "readable text, readable names, readable dates, "
                "readable numbers, logos, watermarks, bright daylight, "
                "highly saturated colors, photorealistic product "
                "photography, collage composition, and split screens."
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
                    "REAL_PROP_INTERACTION_ORIENTATION_VALIDATION"
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
                "prop_interaction": (
                    "READING"
                ),
                "prop_orientation_requirement": (
                    "DOCUMENTS_FACE_CHARACTER"
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

    print(
        "TEST 8 — interaction-aware generation request prepared → PASSED"
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
        "prop_interaction_smoke"
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
    # TEST 9 — CAPABILITY GATE
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
            "Interaction-aware request is incompatible "
            "with Gemini provider capabilities: "
            +
            "; ".join(
                capability_result.issues
            )
        )

    print(
        "TEST 9 — provider accepts interaction-aware request → PASSED"
    )

    # ============================================================
    # TEST 10 — MAPPED REFERENCE SEMANTICS
    #
    # Validate immediately before the billable execution that the
    # semantics introduced by 13F.3-C actually survive mapping.
    # ============================================================

    mapped_plan = (
        provider.mapper.map(
            request
        )
    )

    if (
        len(
            mapped_plan.input_images
        )
        != 3
    ):

        raise AssertionError(
            "Expected exactly three mapped Gemini references."
        )

    mapped_prop = (
        mapped_plan.input_images[
            2
        ]
    )

    assert (
        mapped_prop.reference_role
        ==
        "PROP"
    )

    assert (
        "ROTATE"
        in
        mapped_prop.allowed_transformations
    )

    assert (
        "CHANGE_PERSPECTIVE"
        in
        mapped_prop.allowed_transformations
    )

    assert (
        "OPEN_CLOSE"
        in
        mapped_prop.allowed_transformations
    )

    assert (
        "ADAPT_TO_INTERACTION"
        in
        mapped_prop.allowed_transformations
    )

    assert (
        "document surfaces should primarily face"
        in
        mapped_prop
        .usage_instruction
        .lower()
    )

    print(
        "TEST 10 — prop semantics survive Gemini mapping → PASSED"
    )

    # ============================================================
    # TEST 11 — SDK INPUT ROLE BINDING
    # ============================================================

    sdk_input = (
        provider._build_sdk_input(
            mapped_plan
        )
    )

    if (
        not isinstance(
            sdk_input,
            list,
        )
    ):

        raise AssertionError(
            "Expected role-aware Gemini SDK input list."
        )

    if (
        len(
            sdk_input
        )
        != 7
    ):

        raise AssertionError(
            "Expected global text plus three "
            "role-text/image pairs."
        )

    prop_role_text = (
        sdk_input[
            5
        ][
            "text"
        ]
    )

    assert (
        "ROLE: PROP"
        in
        prop_role_text
    )

    assert (
        "ADAPT_TO_INTERACTION"
        in
        prop_role_text
    )

    assert (
        "document surfaces should primarily face"
        in
        prop_role_text.lower()
    )

    print(
        "TEST 11 — interaction semantics reach SDK input → PASSED"
    )

    # ============================================================
    # EXACTLY ONE REAL ATTEMPT
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini prop-interaction "
        "validation generation..."
    )
    print()

    attempt = (
        provider.generate(
            request=request,
            attempt_number=1,
        )
    )

    # ============================================================
    # TEST 12 — GENERATION SUCCESS
    # ============================================================

    if (
        attempt.status
        != GenerationStatus.SUCCEEDED
    ):

        print(
            "REAL PROP INTERACTION GENERATION → FAILED"
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
        "TEST 12 — real interaction generation succeeded → PASSED"
    )

    # ============================================================
    # TEST 13 — EXACTLY ONE OUTPUT
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
        "TEST 13 — exactly one output returned → PASSED"
    )

    # ============================================================
    # TEST 14 — PHYSICAL ARTIFACT
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
            "Gemini reported success but the prop-interaction "
            "artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated prop-interaction artifact is empty."
        )

    print(
        "TEST 14 — interaction artifact materialized → PASSED"
    )

    # ============================================================
    # TEST 15 — LINEAGE
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
        "TEST 15 — interaction lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "PROP INTERACTION IMAGE GENERATED"
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
        "Technical execution does NOT prove that the "
        "orientation problem is fixed."
    )

    print()

    print(
        "Visual review must specifically determine:"
    )

    print(
        "- character identity remains consistent"
    )

    print(
        "- location identity remains consistent"
    )

    print(
        "- brown folder identity remains consistent"
    )

    print(
        "- loose document identity remains consistent"
    )

    print(
        "- prop orientation changed naturally from its master view"
    )

    print(
        "- open document surfaces primarily face the character"
    )

    print(
        "- camera sees a physically plausible back / edge / "
        "oblique view of the folder"
    )

    print(
        "- eye-line agrees with document position"
    )

    print(
        "- hands and wrists agree with folder orientation"
    )

    print(
        "- folder is not held backwards"
    )

    print(
        "- provider did not simply copy the prop master viewpoint"
    )

    print()

    print(
        "========================================"
    )
    print(
        "BATCH 13F.3-D TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL PROP INTERACTION REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()