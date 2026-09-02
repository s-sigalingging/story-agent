import base64
import tempfile
from pathlib import Path

from app.generation import (
    GeminiRequestMapper,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationReferenceAsset,
    GenerationRequest,
    GenerationType,
)


def make_reference(
    asset_id: str,
    entity_id: str,
    path: str,
) -> GenerationReferenceAsset:

    return (
        GenerationReferenceAsset(
            asset_id=(
                asset_id
            ),
            entity_id=(
                entity_id
            ),
            asset_type=(
                "CHARACTER"
            ),
            name=(
                asset_id
            ),
            reference_path=(
                path
            ),
        )
    )


def make_request(
    references=None,
    negative_prompt=(
        "Avoid text and distorted anatomy."
    ),
) -> GenerationRequest:

    if references is None:

        references = []

    return (
        GenerationRequest(
            request_id=(
                "GEN_REQ_GEMINI_TEST"
            ),
            episode_id=(
                "EP_GEMINI_TEST"
            ),
            shot_id=(
                "EP_GEMINI_TEST-S01-SHOT01"
            ),
            generation_type=(
                GenerationType.KEYFRAME
            ),
            prompt=(
                "Create a cinematic portrait "
                "of the subject in the supplied environment."
            ),
            negative_prompt=(
                negative_prompt
            ),
            reference_assets=(
                references
            ),
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
        )
    )


def main():

    print()
    print(
        "BATCH 13D.1 — GEMINI REQUEST MAPPER"
    )
    print(
        "========================================"
    )

    mapper = (
        GeminiRequestMapper(
            model=(
                "gemini-3.1-flash-image"
            )
        )
    )

    # ============================================================
    # TEST 1 — TEXT-ONLY REQUEST
    # ============================================================

    request = (
        make_request(
            references=[]
        )
    )

    plan = (
        mapper.map(
            request
        )
    )

    assert (
        plan.model
        ==
        "gemini-3.1-flash-image"
    )

    assert (
        plan.input_images
        == []
    )

    print(
        "TEST 1 — text-only request mapped → PASSED"
    )

    # ============================================================
    # TEST 2 — NEGATIVE PROMPT TRANSLATION
    # ============================================================

    assert (
        "Visual constraints:"
        in plan.prompt_text
    )

    assert (
        "Avoid text and distorted anatomy."
        in plan.prompt_text
    )

    assert (
        request.prompt
        in plan.prompt_text
    )

    print(
        "TEST 2 — negative prompt translated into text → PASSED"
    )

    # ============================================================
    # TEST 3 — EMPTY NEGATIVE PROMPT
    # ============================================================

    request_without_negative = (
        make_request(
            references=[],
            negative_prompt=None,
        )
    )

    plan_without_negative = (
        mapper.map(
            request_without_negative
        )
    )

    assert (
        plan_without_negative.prompt_text
        ==
        request_without_negative.prompt
    )

    assert (
        "Visual constraints:"
        not in plan_without_negative
        .prompt_text
    )

    print(
        "TEST 3 — absent negative prompt does not add constraints → PASSED"
    )

    # ============================================================
    # TEMPORARY REFERENCE IMAGES
    # ============================================================

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_root = Path(
            temp_dir
        )

        character_path = (
            temp_root
            /
            "character.png"
        )

        location_path = (
            temp_root
            /
            "location.jpg"
        )

        prop_path = (
            temp_root
            /
            "prop.webp"
        )

        character_bytes = (
            b"character-reference-bytes"
        )

        location_bytes = (
            b"location-reference-bytes"
        )

        prop_bytes = (
            b"prop-reference-bytes"
        )

        character_path.write_bytes(
            character_bytes
        )

        location_path.write_bytes(
            location_bytes
        )

        prop_path.write_bytes(
            prop_bytes
        )

        references = [
            make_reference(
                asset_id=(
                    "ASSET_CHARACTER"
                ),
                entity_id=(
                    "CHARACTER_TEST"
                ),
                path=str(
                    character_path
                ),
            ),
            make_reference(
                asset_id=(
                    "ASSET_LOCATION"
                ),
                entity_id=(
                    "LOCATION_TEST"
                ),
                path=str(
                    location_path
                ),
            ),
            make_reference(
                asset_id=(
                    "ASSET_PROP"
                ),
                entity_id=(
                    "PROP_TEST"
                ),
                path=str(
                    prop_path
                ),
            ),
        ]

        request = (
            make_request(
                references=(
                    references
                )
            )
        )

        plan = (
            mapper.map(
                request
            )
        )

        # ========================================================
        # TEST 4 — MULTIPLE REFERENCES
        # ========================================================

        assert (
            len(
                plan.input_images
            )
            == 3
        )

        print(
            "TEST 4 — multiple references mapped → PASSED"
        )

        # ========================================================
        # TEST 5 — REFERENCE ORDER PRESERVED
        # ========================================================

        assert [
            image.asset_id
            for image
            in plan.input_images
        ] == [
            "ASSET_CHARACTER",
            "ASSET_LOCATION",
            "ASSET_PROP",
        ]

        print(
            "TEST 5 — reference ordering preserved → PASSED"
        )

        # ========================================================
        # TEST 6 — MIME DETECTION
        # ========================================================

        assert (
            plan.input_images[
                0
            ].mime_type
            ==
            "image/png"
        )

        assert (
            plan.input_images[
                1
            ].mime_type
            ==
            "image/jpeg"
        )

        assert (
            plan.input_images[
                2
            ].mime_type
            ==
            "image/webp"
        )

        print(
            "TEST 6 — reference MIME types detected → PASSED"
        )

        # ========================================================
        # TEST 7 — BASE64 CONTENT
        # ========================================================

        decoded_character = (
            base64.b64decode(
                plan.input_images[
                    0
                ].data_base64
            )
        )

        decoded_location = (
            base64.b64decode(
                plan.input_images[
                    1
                ].data_base64
            )
        )

        decoded_prop = (
            base64.b64decode(
                plan.input_images[
                    2
                ].data_base64
            )
        )

        assert (
            decoded_character
            ==
            character_bytes
        )

        assert (
            decoded_location
            ==
            location_bytes
        )

        assert (
            decoded_prop
            ==
            prop_bytes
        )

        print(
            "TEST 7 — reference bytes encoded losslessly → PASSED"
        )

        # ========================================================
        # TEST 8 — 9:16 PRESERVED
        # ========================================================

        assert (
            plan.aspect_ratio
            ==
            "9:16"
        )

        assert (
            plan.output_format
            ==
            "png"
        )

        print(
            "TEST 8 — output requirements preserved → PASSED"
        )

        # ========================================================
        # TEST 9 — MISSING REFERENCE REJECTED
        # ========================================================

        missing_reference = (
            make_reference(
                asset_id=(
                    "ASSET_MISSING"
                ),
                entity_id=(
                    "ENTITY_MISSING"
                ),
                path=str(
                    temp_root
                    /
                    "does_not_exist.png"
                ),
            )
        )

        failed = False

        try:

            mapper.map(
                make_request(
                    references=[
                        missing_reference
                    ]
                )
            )

        except FileNotFoundError:

            failed = True

        assert failed

        print(
            "TEST 9 — missing physical reference rejected → PASSED"
        )

        # ========================================================
        # TEST 10 — UNSUPPORTED REFERENCE FORMAT
        # ========================================================

        unsupported_path = (
            temp_root
            /
            "reference.gif"
        )

        unsupported_path.write_bytes(
            b"unsupported-image"
        )

        unsupported_reference = (
            make_reference(
                asset_id=(
                    "ASSET_UNSUPPORTED"
                ),
                entity_id=(
                    "ENTITY_UNSUPPORTED"
                ),
                path=str(
                    unsupported_path
                ),
            )
        )

        failed = False

        try:

            mapper.map(
                make_request(
                    references=[
                        unsupported_reference
                    ]
                )
            )

        except ValueError:

            failed = True

        assert failed

        print(
            "TEST 10 — unsupported reference format rejected → PASSED"
        )

    # ============================================================
    # TEST 11 — MODEL CONFIGURATION IS PROVIDER-SPECIFIC
    # ============================================================

    request_fields = set(
        GenerationRequest
        .model_fields
        .keys()
    )

    assert (
        "gemini_model"
        not in request_fields
    )

    assert (
        "google_model"
        not in request_fields
    )

    assert (
        "api_key"
        not in request_fields
    )

    print(
        "TEST 11 — Gemini configuration does not leak into domain → PASSED"
    )

    # ============================================================
    # TEST 12 — EMPTY MODEL REJECTED
    # ============================================================

    failed = False

    try:

        GeminiRequestMapper(
            model="   "
        )

    except ValueError:

        failed = True

    assert failed

    print(
        "TEST 12 — empty Gemini model rejected → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13D.1 GEMINI REQUEST MAPPER PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()