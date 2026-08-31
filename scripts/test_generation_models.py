from pydantic import ValidationError

from app.models.generation import (
    GenerationAttempt,
    GenerationError,
    GenerationOutput,
    GenerationOutputSpec,
    GenerationReferenceAsset,
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
    GenerationType,
)


def main():

    print()
    print(
        "BATCH 12B — GENERATION DOMAIN MODEL"
    )
    print(
        "========================================"
    )

    # ============================================================
    # TEST 1 — GENERATION REQUEST
    # ============================================================

    reference = (
        GenerationReferenceAsset(
            asset_id="ASSET_CHAR_TEST_MASTER",
            entity_id="CHAR_TEST",
            asset_type="CHARACTER",
            name="Test Character",
            reference_path=(
                "assets/characters/"
                "CHAR_TEST/master_v2.png"
            ),
            purpose="Identity reference",
            required=True,
            master_reference_required=True,
        )
    )

    request = (
        GenerationRequest(
            request_id=(
                "GEN_REQ_TEST_001"
            ),
            episode_id=(
                "EP_TEST"
            ),
            shot_id=(
                "EP_TEST-S01-SHOT01"
            ),
            generation_type=(
                GenerationType.KEYFRAME
            ),
            prompt=(
                "Create one stable cinematic frame."
            ),
            negative_prompt=(
                "No distorted anatomy."
            ),
            reference_assets=[
                reference
            ],
            output=(
                GenerationOutputSpec(
                    width=1024,
                    height=1024,
                    aspect_ratio="1:1",
                    output_format="png",
                )
            ),
            metadata={
                "scene_number": "1",
            },
        )
    )

    assert (
        request.generation_type
        ==
        GenerationType.KEYFRAME
    )

    assert (
        len(
            request.reference_assets
        )
        == 1
    )

    assert (
        request.reference_assets[
            0
        ].reference_path
        ==
        "assets/characters/"
        "CHAR_TEST/master_v2.png"
    )

    print(
        "TEST 1 — generation request → PASSED"
    )

    # ============================================================
    # TEST 2 — OUTPUT SPEC DEFAULTS
    # ============================================================

    default_output = (
        GenerationOutputSpec()
    )

    assert (
        default_output.width
        == 1024
    )

    assert (
        default_output.height
        == 1024
    )

    assert (
        default_output.aspect_ratio
        == "1:1"
    )

    assert (
        default_output.output_format
        == "png"
    )

    print(
        "TEST 2 — output defaults → PASSED"
    )

    # ============================================================
    # TEST 3 — INVALID OUTPUT DIMENSION
    # ============================================================

    validation_failed = False

    try:

        GenerationOutputSpec(
            width=0,
            height=1024,
        )

    except ValidationError:

        validation_failed = True

    assert validation_failed

    print(
        "TEST 3 — invalid dimensions rejected → PASSED"
    )

    # ============================================================
    # TEST 4 — FAILED ATTEMPT
    # ============================================================

    failed_attempt = (
        GenerationAttempt(
            attempt_id=(
                "GEN_ATTEMPT_TEST_001"
            ),
            request_id=(
                request.request_id
            ),
            attempt_number=1,
            provider=(
                "FAKE_PROVIDER"
            ),
            status=(
                GenerationStatus.FAILED
            ),
            error=(
                GenerationError(
                    code=(
                        "TEMPORARY_FAILURE"
                    ),
                    message=(
                        "Temporary provider failure."
                    ),
                    retryable=True,
                )
            ),
        )
    )

    assert (
        failed_attempt.status
        ==
        GenerationStatus.FAILED
    )

    assert (
        failed_attempt.error
        is not None
    )

    assert (
        failed_attempt.error.retryable
        is True
    )

    print(
        "TEST 4 — failed attempt lineage → PASSED"
    )

    # ============================================================
    # TEST 5 — SUCCESSFUL ATTEMPT
    # ============================================================

    output = (
        GenerationOutput(
            output_id=(
                "GEN_OUTPUT_TEST_001"
            ),
            output_path=(
                "generated/"
                "EP_TEST/"
                "S01/"
                "SHOT01/"
                "keyframe_001.png"
            ),
            width=1024,
            height=1024,
        )
    )

    successful_attempt = (
        GenerationAttempt(
            attempt_id=(
                "GEN_ATTEMPT_TEST_002"
            ),
            request_id=(
                request.request_id
            ),
            attempt_number=2,
            provider=(
                "FAKE_PROVIDER"
            ),
            status=(
                GenerationStatus.SUCCEEDED
            ),
            outputs=[
                output
            ],
        )
    )

    assert (
        successful_attempt.status
        ==
        GenerationStatus.SUCCEEDED
    )

    assert (
        len(
            successful_attempt.outputs
        )
        == 1
    )

    print(
        "TEST 5 — successful attempt lineage → PASSED"
    )

    # ============================================================
    # TEST 6 — AGGREGATE RESULT
    # ============================================================

    result = (
        GenerationResult(
            request_id=(
                request.request_id
            ),
            episode_id=(
                request.episode_id
            ),
            shot_id=(
                request.shot_id
            ),
            generation_type=(
                request.generation_type
            ),
            status=(
                GenerationStatus.SUCCEEDED
            ),
            attempts=[
                failed_attempt,
                successful_attempt,
            ],
            outputs=[
                output
            ],
            selected_output_id=(
                output.output_id
            ),
        )
    )

    assert (
        len(
            result.attempts
        )
        == 2
    )

    assert (
        result.attempts[
            0
        ].attempt_number
        == 1
    )

    assert (
        result.attempts[
            1
        ].attempt_number
        == 2
    )

    assert (
        result.selected_output_id
        ==
        "GEN_OUTPUT_TEST_001"
    )

    print(
        "TEST 6 — aggregate result lineage → PASSED"
    )

    # ============================================================
    # TEST 7 — NO CREATIVE APPROVAL STATE
    # ============================================================

    status_values = {
        item.value
        for item
        in GenerationStatus
    }

    assert (
        "APPROVED"
        not in status_values
    )

    assert (
        "REJECTED"
        not in status_values
    )

    print(
        "TEST 7 — approval separated from generation → PASSED"
    )

    # ============================================================
    # TEST 8 — PROVIDER-AGNOSTIC REQUEST
    # ============================================================

    request_fields = set(
        GenerationRequest
        .model_fields
        .keys()
    )

    forbidden_fields = {
        "provider",
        "model",
        "openai_model",
        "digen_model",
        "cfg_scale",
        "sampler",
    }

    assert (
        request_fields
        .isdisjoint(
            forbidden_fields
        )
    )

    print(
        "TEST 8 — request remains provider-agnostic → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12B GENERATION DOMAIN MODEL PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()