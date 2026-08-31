import tempfile

from app.generation import (
    FakeGenerationProvider,
    GenerationRunner,
    GenerationStore,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationRequest,
    GenerationStatus,
    GenerationType,
)


def make_request(
    request_id: str,
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
        "BATCH 12F — FAILURE AND RETRY HANDLING"
    )
    print(
        "========================================"
    )

    # ============================================================
    # TEST 1 — SUCCESS FIRST ATTEMPT
    # ============================================================

    request = (
        make_request(
            "GEN_REQ_RETRY_001"
        )
    )

    runner = (
        GenerationRunner(
            provider=(
                FakeGenerationProvider()
            ),
            max_attempts=3,
        )
    )

    result = (
        runner.run(
            request
        )
    )

    assert (
        result.status
        ==
        GenerationStatus.SUCCEEDED
    )

    assert (
        len(result.attempts)
        == 1
    )

    print(
        "TEST 1 — success stops immediately → PASSED"
    )

    # ============================================================
    # TEST 2 — RETRY THEN SUCCESS
    # ============================================================

    request = (
        make_request(
            "GEN_REQ_RETRY_002"
        )
    )

    runner = (
        GenerationRunner(
            provider=(
                FakeGenerationProvider(
                    mode=(
                        "FAIL_THEN_SUCCESS"
                    ),
                    fail_attempts=2,
                )
            ),
            max_attempts=4,
        )
    )

    result = (
        runner.run(
            request
        )
    )

    assert (
        result.status
        ==
        GenerationStatus.SUCCEEDED
    )

    assert (
        len(result.attempts)
        == 3
    )

    assert (
        result.attempts[0]
        .status
        ==
        GenerationStatus.FAILED
    )

    assert (
        result.attempts[1]
        .status
        ==
        GenerationStatus.FAILED
    )

    assert (
        result.attempts[2]
        .status
        ==
        GenerationStatus.SUCCEEDED
    )

    print(
        "TEST 2 — retryable failures eventually succeed → PASSED"
    )

    # ============================================================
    # TEST 3 — MAX ATTEMPTS
    # ============================================================

    request = (
        make_request(
            "GEN_REQ_RETRY_003"
        )
    )

    runner = (
        GenerationRunner(
            provider=(
                FakeGenerationProvider(
                    mode=(
                        "RETRYABLE_FAILURE"
                    )
                )
            ),
            max_attempts=3,
        )
    )

    result = (
        runner.run(
            request
        )
    )

    assert (
        result.status
        ==
        GenerationStatus.FAILED
    )

    assert (
        len(result.attempts)
        == 3
    )

    assert all(
        attempt.error
        is not None
        and
        attempt.error.retryable
        for attempt
        in result.attempts
    )

    print(
        "TEST 3 — retry stops at max attempts → PASSED"
    )

    # ============================================================
    # TEST 4 — PERMANENT FAILURE STOPS
    # ============================================================

    request = (
        make_request(
            "GEN_REQ_RETRY_004"
        )
    )

    runner = (
        GenerationRunner(
            provider=(
                FakeGenerationProvider(
                    mode=(
                        "PERMANENT_FAILURE"
                    )
                )
            ),
            max_attempts=5,
        )
    )

    result = (
        runner.run(
            request
        )
    )

    assert (
        result.status
        ==
        GenerationStatus.FAILED
    )

    assert (
        len(result.attempts)
        == 1
    )

    assert (
        result.attempts[0]
        .error
        .retryable
        is False
    )

    print(
        "TEST 4 — permanent failure stops immediately → PASSED"
    )

    # ============================================================
    # TEST 5 — ATTEMPT NUMBERING
    # ============================================================

    request = (
        make_request(
            "GEN_REQ_RETRY_005"
        )
    )

    runner = (
        GenerationRunner(
            provider=(
                FakeGenerationProvider(
                    mode=(
                        "FAIL_THEN_SUCCESS"
                    ),
                    fail_attempts=2,
                )
            ),
            max_attempts=3,
        )
    )

    result = (
        runner.run(
            request
        )
    )

    attempt_numbers = [
        attempt.attempt_number
        for attempt
        in result.attempts
    ]

    assert (
        attempt_numbers
        == [1, 2, 3]
    )

    assert (
        result.attempts[0]
        .attempt_id
        .endswith(
            "ATTEMPT_001"
        )
    )

    assert (
        result.attempts[2]
        .attempt_id
        .endswith(
            "ATTEMPT_003"
        )
    )

    print(
        "TEST 5 — attempt lineage numbering preserved → PASSED"
    )

    # ============================================================
    # TEST 6 — OUTPUTS ONLY FROM SUCCESS
    # ============================================================

    assert (
        result.attempts[0]
        .outputs
        == []
    )

    assert (
        result.attempts[1]
        .outputs
        == []
    )

    assert (
        len(
            result.outputs
        )
        == 1
    )

    assert (
        result.outputs[0]
        .output_id
        ==
        result.attempts[2]
        .outputs[0]
        .output_id
    )

    print(
        "TEST 6 — successful outputs aggregated correctly → PASSED"
    )

    # ============================================================
    # TEST 7 — PERSIST COMPLETE LINEAGE
    # ============================================================

    with tempfile.TemporaryDirectory() as temp_dir:

        store = (
            GenerationStore(
                base_path=temp_dir
            )
        )

        request = (
            make_request(
                "GEN_REQ_RETRY_006"
            )
        )

        runner = (
            GenerationRunner(
                provider=(
                    FakeGenerationProvider(
                        mode=(
                            "FAIL_THEN_SUCCESS"
                        ),
                        fail_attempts=2,
                    )
                ),
                max_attempts=4,
                store=store,
            )
        )

        result = (
            runner.run(
                request
            )
        )

        loaded = (
            store.load(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
        )

        assert (
            loaded
            is not None
        )

        assert (
            loaded.result
            is not None
        )

        assert (
            len(
                loaded.result.attempts
            )
            == 3
        )

        assert (
            loaded.result.status
            ==
            GenerationStatus.SUCCEEDED
        )

        print(
            "TEST 7 — retry lineage persisted → PASSED"
        )

    # ============================================================
    # TEST 8 — INVALID MAX ATTEMPTS
    # ============================================================

    failed = False

    try:

        GenerationRunner(
            provider=(
                FakeGenerationProvider()
            ),
            max_attempts=0,
        )

    except ValueError:

        failed = True

    assert failed

    print(
        "TEST 8 — invalid retry policy rejected → PASSED"
    )

    # ============================================================
    # TEST 9 — METADATA RECORDS ATTEMPTS
    # ============================================================

    assert (
        result.metadata[
            "attempt_count"
        ]
        == "3"
    )

    assert (
        result.metadata[
            "max_attempts"
        ]
        == "4"
    )

    print(
        "TEST 9 — retry metadata recorded → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12F FAILURE AND RETRY HANDLING PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()