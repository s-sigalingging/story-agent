from app.generation.providers import (
    FakeGenerationProvider,
    GenerationProvider,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationRequest,
    GenerationStatus,
    GenerationType,
)


def make_request(
    request_id: str = (
        "GEN_REQ_TEST_PROVIDER"
    ),
) -> GenerationRequest:

    return GenerationRequest(
        request_id=request_id,
        episode_id="EP_TEST",
        shot_id="EP_TEST-S01-SHOT01",
        generation_type=(
            GenerationType.KEYFRAME
        ),
        prompt=(
            "Create one stable cinematic frame."
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


def main():

    print()
    print(
        "BATCH 12C — GENERATION PROVIDER CONTRACT"
    )
    print(
        "========================================"
    )

    request = (
        make_request()
    )

    # ============================================================
    # TEST 1 — CONTRACT
    # ============================================================

    provider = (
        FakeGenerationProvider()
    )

    assert isinstance(
        provider,
        GenerationProvider,
    )

    assert (
        provider.name
        == "FAKE_PROVIDER"
    )

    print(
        "TEST 1 — provider contract → PASSED"
    )

    # ============================================================
    # TEST 2 — SUCCESS
    # ============================================================

    attempt = (
        provider.generate(
            request=request,
            attempt_number=1,
        )
    )

    assert (
        attempt.status
        ==
        GenerationStatus.SUCCEEDED
    )

    assert (
        attempt.attempt_number
        == 1
    )

    assert (
        attempt.provider
        == "FAKE_PROVIDER"
    )

    assert (
        len(
            attempt.outputs
        )
        == 1
    )

    print(
        "TEST 2 — successful generation → PASSED"
    )

    # ============================================================
    # TEST 3 — OUTPUT CONTRACT
    # ============================================================

    output = (
        attempt.outputs[0]
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

    assert (
        request.shot_id
        in output.output_path
    )

    print(
        "TEST 3 — output contract → PASSED"
    )

    # ============================================================
    # TEST 4 — MULTIPLE OUTPUTS
    # ============================================================

    multi_provider = (
        FakeGenerationProvider(
            output_count=3
        )
    )

    multi_attempt = (
        multi_provider.generate(
            request=request,
            attempt_number=1,
        )
    )

    assert (
        len(
            multi_attempt.outputs
        )
        == 3
    )

    output_ids = {
        item.output_id
        for item
        in multi_attempt.outputs
    }

    assert (
        len(output_ids)
        == 3
    )

    print(
        "TEST 4 — multiple outputs → PASSED"
    )

    # ============================================================
    # TEST 5 — RETRYABLE FAILURE
    # ============================================================

    retry_provider = (
        FakeGenerationProvider(
            mode=(
                "RETRYABLE_FAILURE"
            )
        )
    )

    retry_attempt = (
        retry_provider.generate(
            request=request,
            attempt_number=2,
        )
    )

    assert (
        retry_attempt.status
        ==
        GenerationStatus.FAILED
    )

    assert (
        retry_attempt.error
        is not None
    )

    assert (
        retry_attempt.error.retryable
        is True
    )

    assert (
        retry_attempt.attempt_number
        == 2
    )

    print(
        "TEST 5 — retryable failure → PASSED"
    )

    # ============================================================
    # TEST 6 — PERMANENT FAILURE
    # ============================================================

    permanent_provider = (
        FakeGenerationProvider(
            mode=(
                "PERMANENT_FAILURE"
            )
        )
    )

    permanent_attempt = (
        permanent_provider.generate(
            request=request,
            attempt_number=3,
        )
    )

    assert (
        permanent_attempt.status
        ==
        GenerationStatus.FAILED
    )

    assert (
        permanent_attempt.error
        is not None
    )

    assert (
        permanent_attempt
        .error
        .retryable
        is False
    )

    print(
        "TEST 6 — permanent failure → PASSED"
    )

    # ============================================================
    # TEST 7 — DETERMINISTIC ATTEMPT IDs
    # ============================================================

    attempt_2 = (
        provider.generate(
            request=request,
            attempt_number=2,
        )
    )

    assert (
        attempt.attempt_id
        ==
        "GEN_REQ_TEST_PROVIDER_ATTEMPT_001"
    )

    assert (
        attempt_2.attempt_id
        ==
        "GEN_REQ_TEST_PROVIDER_ATTEMPT_002"
    )

    print(
        "TEST 7 — deterministic lineage IDs → PASSED"
    )

    # ============================================================
    # TEST 8 — INVALID ATTEMPT NUMBER
    # ============================================================

    failed = False

    try:

        provider.generate(
            request=request,
            attempt_number=0,
        )

    except ValueError:

        failed = True

    assert failed

    print(
        "TEST 8 — invalid attempt rejected → PASSED"
    )

    # ============================================================
    # TEST 9 — UNKNOWN FAKE MODE
    # ============================================================

    unknown_provider = (
        FakeGenerationProvider(
            mode="UNKNOWN_MODE"
        )
    )

    failed = False

    try:

        unknown_provider.generate(
            request=request,
            attempt_number=1,
        )

    except ValueError:

        failed = True

    assert failed

    print(
        "TEST 9 — unsupported mode rejected → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12C GENERATION PROVIDER CONTRACT PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()