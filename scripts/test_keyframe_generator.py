from app.generation import (
    FakeGenerationProvider,
    KeyframeGenerator,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationRequest,
    GenerationStatus,
    GenerationType,
)


def make_request(
    request_id: str = (
        "GEN_REQ_KEYFRAME_TEST"
    ),
) -> GenerationRequest:

    return (
        GenerationRequest(
            request_id=request_id,
            episode_id="EP_TEST",
            shot_id=(
                "EP_TEST-S01-SHOT01"
            ),
            generation_type=(
                GenerationType.KEYFRAME
            ),
            prompt=(
                "Create one stable "
                "cinematic frame."
            ),
            negative_prompt=(
                "Avoid distorted anatomy."
            ),
            output=(
                GenerationOutputSpec(
                    width=1280,
                    height=720,
                    aspect_ratio="16:9",
                    output_format="png",
                )
            ),
        )
    )


def main():

    print()
    print(
        "BATCH 12D — KEYFRAME GENERATOR"
    )
    print(
        "========================================"
    )

    request = make_request()

    # ============================================================
    # TEST 1 — SUCCESS
    # ============================================================

    provider = (
        FakeGenerationProvider()
    )

    generator = (
        KeyframeGenerator(
            provider=provider
        )
    )

    result = (
        generator.generate(
            request
        )
    )

    assert (
        result.status
        ==
        GenerationStatus.SUCCEEDED
    )

    assert (
        result.request_id
        ==
        request.request_id
    )

    assert (
        result.episode_id
        ==
        request.episode_id
    )

    assert (
        result.shot_id
        ==
        request.shot_id
    )

    print(
        "TEST 1 — successful generation → PASSED"
    )

    # ============================================================
    # TEST 2 — SINGLE ATTEMPT
    # ============================================================

    assert (
        len(
            result.attempts
        )
        == 1
    )

    assert (
        result.attempts[
            0
        ].attempt_number
        == 1
    )

    assert (
        result.metadata[
            "attempt_count"
        ]
        == "1"
    )

    print(
        "TEST 2 — single attempt execution → PASSED"
    )

    # ============================================================
    # TEST 3 — OUTPUTS PROPAGATE
    # ============================================================

    assert (
        len(
            result.outputs
        )
        == 1
    )

    output = (
        result.outputs[0]
    )

    assert (
        output.width
        == 1280
    )

    assert (
        output.height
        == 720
    )

    assert (
        output.mime_type
        == "image/png"
    )

    print(
        "TEST 3 — provider outputs propagated → PASSED"
    )

    # ============================================================
    # TEST 4 — NO AUTOMATIC CREATIVE SELECTION
    # ============================================================

    assert (
        result.selected_output_id
        is None
    )

    print(
        "TEST 4 — no automatic output selection → PASSED"
    )

    # ============================================================
    # TEST 5 — MULTIPLE OUTPUTS
    # ============================================================

    multi_provider = (
        FakeGenerationProvider(
            output_count=3
        )
    )

    multi_generator = (
        KeyframeGenerator(
            provider=(
                multi_provider
            )
        )
    )

    multi_result = (
        multi_generator.generate(
            request
        )
    )

    assert (
        multi_result.status
        ==
        GenerationStatus.SUCCEEDED
    )

    assert (
        len(
            multi_result.outputs
        )
        == 3
    )

    assert (
        multi_result.selected_output_id
        is None
    )

    print(
        "TEST 5 — multiple outputs preserved → PASSED"
    )

    # ============================================================
    # TEST 6 — RETRYABLE FAILURE REMAINS FAILED
    #
    # Retry does not belong to Batch 12D.
    # ============================================================

    retry_provider = (
        FakeGenerationProvider(
            mode=(
                "RETRYABLE_FAILURE"
            )
        )
    )

    retry_generator = (
        KeyframeGenerator(
            provider=(
                retry_provider
            )
        )
    )

    retry_result = (
        retry_generator.generate(
            request
        )
    )

    assert (
        retry_result.status
        ==
        GenerationStatus.FAILED
    )

    assert (
        len(
            retry_result.attempts
        )
        == 1
    )

    assert (
        retry_result
        .attempts[0]
        .error
        is not None
    )

    assert (
        retry_result
        .attempts[0]
        .error
        .retryable
        is True
    )

    print(
        "TEST 6 — retryable failure "
        "does not auto-retry → PASSED"
    )

    # ============================================================
    # TEST 7 — PERMANENT FAILURE
    # ============================================================

    permanent_provider = (
        FakeGenerationProvider(
            mode=(
                "PERMANENT_FAILURE"
            )
        )
    )

    permanent_generator = (
        KeyframeGenerator(
            provider=(
                permanent_provider
            )
        )
    )

    permanent_result = (
        permanent_generator.generate(
            request
        )
    )

    assert (
        permanent_result.status
        ==
        GenerationStatus.FAILED
    )

    assert (
        permanent_result.outputs
        == []
    )

    assert (
        permanent_result
        .attempts[0]
        .error
        .retryable
        is False
    )

    print(
        "TEST 7 — permanent failure → PASSED"
    )

    # ============================================================
    # TEST 8 — PROVIDER METADATA
    # ============================================================

    assert (
        result.metadata[
            "provider"
        ]
        ==
        "FAKE_PROVIDER"
    )

    print(
        "TEST 8 — provider metadata recorded → PASSED"
    )

    # ============================================================
    # TEST 9 — EMPTY PROMPT REJECTED
    # ============================================================

    empty_prompt_request = (
        request.model_copy(
            update={
                "prompt": "   "
            }
        )
    )

    failed = False

    try:

        generator.generate(
            empty_prompt_request
        )

    except ValueError:

        failed = True

    assert failed

    print(
        "TEST 9 — empty prompt rejected → PASSED"
    )

    # ============================================================
    # TEST 10 — REQUEST LINEAGE PRESERVED
    # ============================================================

    attempt = (
        result.attempts[0]
    )

    assert (
        attempt.request_id
        ==
        request.request_id
    )

    assert (
        attempt.attempt_id
        ==
        request.request_id
        + "_ATTEMPT_001"
    )

    for generated_output in (
        result.outputs
    ):

        assert (
            request.request_id
            in generated_output.output_id
        )

    print(
        "TEST 10 — generation lineage preserved → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12D KEYFRAME GENERATOR PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()