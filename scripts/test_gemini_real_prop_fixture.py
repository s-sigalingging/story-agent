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
            "Generate exactly one style-normalized prop fixture "
            "using one object reference and one visual-style reference."
        )
    )

    parser.add_argument(
        "--object-reference",
        required=True,
        help=(
            "Path to the Revision 3 brown-folder reference."
        ),
    )

    parser.add_argument(
        "--style-reference",
        required=True,
        help=(
            "Path to the approved illustrated visual-style reference."
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
# REFERENCE VALIDATION
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
        "BATCH 13F.3-A — PROP FIXTURE REVISION 4"
    )
    print(
        "STYLE NORMALIZATION"
    )
    print(
        "========================================"
    )

    args = parse_arguments()

    # ============================================================
    # TEST 1 — OBJECT REFERENCE
    # ============================================================

    object_path = (
        validate_reference(
            path_value=(
                args.object_reference
            ),
            label=(
                "Object"
            ),
        )
    )

    print(
        "TEST 1 — physical object reference found → PASSED"
    )

    print(
        "         object:",
        object_path,
    )

    # ============================================================
    # TEST 2 — STYLE REFERENCE
    # ============================================================

    style_path = (
        validate_reference(
            path_value=(
                args.style_reference
            ),
            label=(
                "Style"
            ),
        )
    )

    print(
        "TEST 2 — physical style reference found → PASSED"
    )

    print(
        "         style:",
        style_path,
    )

    # ============================================================
    # TEST 3 — DISTINCT REFERENCES
    # ============================================================

    if (
        object_path
        ==
        style_path
    ):

        raise ValueError(
            "Object and style references must be "
            "different physical files."
        )

    print(
        "TEST 3 — object and style references are distinct → PASSED"
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
            "Reference roles:"
        )

        print(
            "REFERENCE 1 → object form / semantics"
        )

        print(
            "REFERENCE 2 → illustrated visual style only"
        )

        print()
        print(
            "To execute exactly ONE billable Gemini request:"
        )

        print()

        print(
            "PYTHONPATH=. python3 "
            "scripts/test_gemini_real_prop_fixture.py "
            f'--object-reference "{object_path}" '
            f'--style-reference "{style_path}" '
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
        "GEN_REQ_REAL_GEMINI_PROP_FIXTURE_R4_"
        f"{timestamp}"
    )

    episode_id = (
        "EP_REAL_GEMINI_PROP_FIXTURE_R4"
    )

    shot_id = (
        "EP_REAL_GEMINI_PROP_FIXTURE_R4-S01-SHOT01"
    )

    # ============================================================
    # REFERENCE 1 — OBJECT SEMANTICS
    # ============================================================

    object_reference = (
        GenerationReferenceAsset(
            asset_id=(
                "ASSET_PROP_OBJECT_REFERENCE"
            ),
            entity_id=(
                "PROP_OBJECT_REFERENCE"
            ),
            asset_type=(
                "PROP"
            ),
            name=(
                "Brown Administrative Folder Object Reference"
            ),
            reference_path=(
                str(
                    object_path
                )
            ),
        )
    )

    # ============================================================
    # REFERENCE 2 — STYLE SOURCE
    #
    # We deliberately do not introduce a new STYLE domain type yet.
    #
    # This remains a test-only semantic role communicated through
    # the prompt. The provider still receives an ordinary resolved
    # physical image reference.
    # ============================================================

    style_reference = (
        GenerationReferenceAsset(
            asset_id=(
                "ASSET_VISUAL_STYLE_REFERENCE"
            ),
            entity_id=(
                "VISUAL_STYLE_REFERENCE"
            ),
            asset_type=(
                "LOCATION"
            ),
            name=(
                "Illustrated Mystery Visual Style Reference"
            ),
            reference_path=(
                str(
                    style_path
                )
            ),
        )
    )

    # ============================================================
    # TEST 6 — STYLE NORMALIZATION REQUEST
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
                "Two visual references are supplied. "

                "REFERENCE 1 is the OBJECT FORM reference. "
                "Preserve the essential physical identity of the "
                "administrative prop shown there: a simple thin "
                "brown manila or kraft-paper archival folder, "
                "partially open, containing several loose off-white "
                "administrative paper documents. "

                "Preserve the ordinary utilitarian construction, "
                "thin paper/cardstock profile, slightly worn edges, "
                "simple shape, and visible loose documents. "

                "Do NOT turn the prop back into a book, ledger, "
                "leather-bound object, antique tome, or decorative "
                "artifact. "

                "REFERENCE 2 is provided ONLY as the VISUAL STYLE "
                "and RENDERING LANGUAGE reference. "

                "Do NOT reproduce the warehouse architecture, crates, "
                "dock, windows, machinery, ship, structural beams, "
                "or environmental composition from REFERENCE 2. "

                "Instead, study only the visual rendering language "
                "of REFERENCE 2: the realistic-stylized illustrated "
                "film treatment, subtle graphic edge definition, "
                "painted texture, muted dark mystery palette, "
                "controlled cinematic contrast, restrained detail, "
                "and slightly animated-film / illustrated appearance. "

                "Generate a NEW clean PROP REFERENCE IMAGE combining "
                "the OBJECT IDENTITY from REFERENCE 1 with the "
                "ILLUSTRATED VISUAL LANGUAGE from REFERENCE 2. "

                "Show the brown administrative folder resting "
                "partially open on a simple dark wooden surface. "

                "Several loose off-white documents should remain "
                "clearly visible inside the folder. "

                "The documents may contain only faint generic form "
                "lines, small blocks, or abstract administrative "
                "layout marks. Nothing should be clearly readable. "

                "Use a clean three-quarter prop-reference composition. "

                "The entire folder and enough of the visible papers "
                "must remain easy to recognize. "

                "Use controlled noir-style cinematic lighting that "
                "belongs to the same illustrated world as "
                "REFERENCE 2. "

                "The final result must look like an illustrated "
                "cinematic prop asset from the same fictional film "
                "world as REFERENCE 2, NOT like a photograph of a "
                "real office folder. "

                "Priority order: "
                "first preserve the simple administrative folder "
                "identity from REFERENCE 1; "
                "second match the illustrated rendering style of "
                "REFERENCE 2; "
                "third keep the presentation clean and useful as "
                "a reusable master prop reference."
            ),
            negative_prompt=(
                "Do not reproduce the warehouse scene. "
                "No warehouse beams. "
                "No dock. "
                "No ship. "
                "No cargo crates. "
                "No warehouse machinery. "

                "No people. "
                "No human figures. "
                "No hands. "
                "No arms. "
                "No detective. "

                "No book. "
                "No bound ledger. "
                "No hardcover book. "
                "No leather book. "
                "No medieval tome. "
                "No grimoire. "
                "No ancient manuscript. "

                "No leather cover. "
                "No brass corners. "
                "No metal corners. "
                "No clasp. "
                "No lock. "
                "No buckle. "
                "No chain. "
                "No crest. "
                "No seal. "
                "No emblem. "
                "No ornamentation. "

                "No fantasy visual language. "
                "No medieval visual language. "
                "No mystical object design. "

                "Do not make the image photorealistic. "
                "Do not render it as commercial product photography. "
                "Do not use photographic lens bokeh. "
                "Do not use shallow photographic depth of field. "
                "Do not make it look like a real DSLR or smartphone "
                "photograph. "
                "Do not use hyper-real skin, material, or lens rendering. "

                "No readable text. "
                "No readable dates. "
                "No readable names. "
                "No readable numbers. "
                "No readable codes. "
                "No A-1930 marking. "

                "Do not make the folder thick. "
                "Do not make it luxurious. "
                "Do not make it rigid like a book. "

                "No plastic binder. "
                "No ring binder. "
                "No glossy stationery. "
                "No bright saturated colors. "

                "Avoid logos, watermarks, excessive clutter, "
                "extreme perspective, and bright daylight."
            ),
            reference_assets=[
                object_reference,
                style_reference,
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
                    "TEST_PROP_FIXTURE_REVISION_4_STYLE_NORMALIZATION"
                ),
                "canonical_asset": (
                    "false"
                ),
                "fixture_type": (
                    "PROP"
                ),
                "reference_count": (
                    "2"
                ),
                "reference_1_role": (
                    "OBJECT_SEMANTICS"
                ),
                "reference_2_role": (
                    "VISUAL_STYLE"
                ),
                "fixture_identity": (
                    "ILLUSTRATED_BROWN_ADMINISTRATIVE_FOLDER"
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

    print(
        "TEST 6 — object + style request prepared → PASSED"
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
        "prop_revision_4"
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
            "Style-normalized prop request is incompatible "
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
    # EXACTLY ONE REAL NETWORK CALL
    # ============================================================

    print()
    print(
        "Executing exactly ONE Gemini prop style-normalization "
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
            "REAL PROP STYLE NORMALIZATION → FAILED"
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
        "TEST 8 — style-normalized prop generation succeeded → PASSED"
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
        attempt.outputs[0]
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
            "Gemini reported success but style-normalized "
            "prop artifact does not exist."
        )

    if (
        output_path.stat().st_size
        <= 0
    ):

        raise AssertionError(
            "Generated style-normalized prop artifact is empty."
        )

    print(
        "TEST 10 — style-normalized prop artifact materialized → PASSED"
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
        "TEST 11 — style-normalization lineage preserved → PASSED"
    )

    # ============================================================
    # REPORT
    # ============================================================

    print()
    print(
        "STYLE-NORMALIZED PROP FIXTURE GENERATED"
    )
    print(
        "----------------------------------------"
    )

    print(
        "Provider:",
        attempt.provider,
    )

    print(
        "Object reference:",
        object_path,
    )

    print(
        "Style reference:",
        style_path,
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
        "Technical success alone does NOT pass Revision 4."
    )

    print()

    print(
        "Visual review must confirm:"
    )

    print(
        "- object still reads as a simple brown administrative folder"
    )

    print(
        "- loose documents remain visible"
    )

    print(
        "- object did not turn back into a book"
    )

    print(
        "- warehouse environment itself did not leak into the image"
    )

    print(
        "- rendering is visibly illustrated rather than photographic"
    )

    print(
        "- texture / edge / lighting language is compatible "
        "with the character and warehouse fixtures"
    )

    print(
        "- no readable text"
    )

    print(
        "- no decorative medieval/fantasy elements"
    )

    print()

    print(
        "========================================"
    )
    print(
        "BATCH 13F.3-A REVISION 4 TECHNICAL EXECUTION PASSED"
    )
    print(
        "VISUAL STYLE NORMALIZATION REVIEW REQUIRED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()