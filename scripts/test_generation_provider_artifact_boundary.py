import tempfile
from pathlib import Path

from app.generation import (
    ArtifactFakeGenerationProvider,
    GenerationArtifactStore,
    GenerationRunner,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationRequest,
    GenerationStatus,
    GenerationType,
)


def make_request(
    request_id: str = (
        "GEN_REQ_ARTIFACT_BOUNDARY"
    ),
) -> GenerationRequest:

    return (
        GenerationRequest(
            request_id=(
                request_id
            ),
            episode_id=(
                "EP_ARTIFACT_TEST"
            ),
            shot_id=(
                "EP_ARTIFACT_TEST-S01-SHOT01"
            ),
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
    )


def main():

    print()
    print(
        "BATCH 13C.2 — PROVIDER ARTIFACT BOUNDARY"
    )
    print(
        "========================================"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        artifact_store = (
            GenerationArtifactStore(
                base_path=(
                    temp_dir
                )
            )
        )

        provider = (
            ArtifactFakeGenerationProvider(
                artifact_store=(
                    artifact_store
                ),
                content=(
                    b"deterministic-generated-image"
                ),
            )
        )

        request = (
            make_request()
        )

        # ============================================================
        # TEST 1 — CAPABILITY CONTRACT STILL WORKS
        # ============================================================

        capability_result = (
            provider
            .validate_request_capabilities(
                request
            )
        )

        assert (
            capability_result.compatible
            is True
        )

        print(
            "TEST 1 — artifact provider capability contract → PASSED"
        )

        # ============================================================
        # TEST 2 — PROVIDER MATERIALIZES ARTIFACT
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
            len(
                attempt.outputs
            )
            == 1
        )

        output = (
            attempt.outputs[0]
        )

        output_path = Path(
            output.output_path
        )

        assert (
            output_path.exists()
        )

        assert (
            output_path.is_file()
        )

        print(
            "TEST 2 — provider materializes physical artifact → PASSED"
        )

        # ============================================================
        # TEST 3 — PHYSICAL BYTES ARE REAL
        # ============================================================

        assert (
            output_path.read_bytes()
            ==
            b"deterministic-generated-image"
        )

        assert (
            output_path.stat().st_size
            > 0
        )

        print(
            "TEST 3 — physical artifact bytes preserved → PASSED"
        )

        # ============================================================
        # TEST 4 — OUTPUT PATH MATCHES ARTIFACT STORE
        # ============================================================

        expected_path = (
            artifact_store.build_path(
                episode_id=(
                    request.episode_id
                ),
                shot_id=(
                    request.shot_id
                ),
                output_id=(
                    output.output_id
                ),
                output_format=(
                    request.output.output_format
                ),
            )
        )

        assert (
            output_path
            ==
            expected_path
        )

        print(
            "TEST 4 — GenerationOutput points to artifact store path → PASSED"
        )

        # ============================================================
        # TEST 5 — ARTIFACT METADATA
        # ============================================================

        assert (
            output.metadata[
                "artifact_materialized"
            ]
            ==
            "true"
        )

        assert (
            output.metadata[
                "provider"
            ]
            ==
            "ARTIFACT_FAKE_PROVIDER"
        )

        print(
            "TEST 5 — materialization metadata recorded → PASSED"
        )

        # ============================================================
        # TEST 6 — GENERATION RUNNER REMAINS UNAWARE OF BYTES
        # ============================================================

        runner_request = (
            make_request(
                request_id=(
                    "GEN_REQ_ARTIFACT_RUNNER"
                )
            )
        )

        runner_provider = (
            ArtifactFakeGenerationProvider(
                artifact_store=(
                    artifact_store
                ),
                content=(
                    b"runner-artifact-bytes"
                ),
            )
        )

        runner = (
            GenerationRunner(
                provider=(
                    runner_provider
                ),
                max_attempts=3,
            )
        )

        result = (
            runner.run(
                runner_request
            )
        )

        assert (
            result.status
            ==
            GenerationStatus.SUCCEEDED
        )

        assert (
            len(
                result.outputs
            )
            == 1
        )

        runner_output = (
            result.outputs[0]
        )

        assert (
            Path(
                runner_output.output_path
            )
            .is_file()
        )

        assert (
            Path(
                runner_output.output_path
            )
            .read_bytes()
            ==
            b"runner-artifact-bytes"
        )

        print(
            "TEST 6 — runner receives materialized output transparently → PASSED"
        )

        # ============================================================
        # TEST 7 — FAILURE CREATES NO ARTIFACT
        # ============================================================

        failed_request = (
            make_request(
                request_id=(
                    "GEN_REQ_ARTIFACT_FAILURE"
                )
            )
        )

        failed_provider = (
            ArtifactFakeGenerationProvider(
                artifact_store=(
                    artifact_store
                ),
                mode=(
                    "PERMANENT_FAILURE"
                ),
            )
        )

        failed_attempt = (
            failed_provider.generate(
                request=(
                    failed_request
                ),
                attempt_number=1,
            )
        )

        assert (
            failed_attempt.status
            ==
            GenerationStatus.FAILED
        )

        assert (
            failed_attempt.outputs
            == []
        )

        expected_failed_output = (
            artifact_store.build_path(
                episode_id=(
                    failed_request.episode_id
                ),
                shot_id=(
                    failed_request.shot_id
                ),
                output_id=(
                    failed_request.request_id
                    +
                    "_ATTEMPT_001_OUTPUT_001"
                ),
                output_format=(
                    failed_request.output
                    .output_format
                ),
            )
        )

        assert (
            expected_failed_output.exists()
            is False
        )

        print(
            "TEST 7 — failed generation creates no artifact → PASSED"
        )

        # ============================================================
        # TEST 8 — RETRYABLE FAILURE CREATES NO ARTIFACT
        # ============================================================

        retry_request = (
            make_request(
                request_id=(
                    "GEN_REQ_ARTIFACT_RETRY"
                )
            )
        )

        retry_provider = (
            ArtifactFakeGenerationProvider(
                artifact_store=(
                    artifact_store
                ),
                mode=(
                    "RETRYABLE_FAILURE"
                ),
            )
        )

        retry_attempt = (
            retry_provider.generate(
                request=(
                    retry_request
                ),
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
            retry_attempt.outputs
            == []
        )

        print(
            "TEST 8 — retryable failure creates no artifact → PASSED"
        )

        # ============================================================
        # TEST 9 — OUTPUT LINEAGE REMAINS DETERMINISTIC
        # ============================================================

        assert (
            output.output_id
            ==
            "GEN_REQ_ARTIFACT_BOUNDARY"
            "_ATTEMPT_001_OUTPUT_001"
        )

        assert (
            attempt.attempt_id
            ==
            "GEN_REQ_ARTIFACT_BOUNDARY"
            "_ATTEMPT_001"
        )

        print(
            "TEST 9 — artifact lineage IDs remain deterministic → PASSED"
        )

        # ============================================================
        # TEST 10 — SUCCEEDED IMPLIES PHYSICAL ARTIFACT
        # ============================================================

        for generated_output in (
            result.outputs
        ):

            assert (
                artifact_store
                .verify_path(
                    generated_output
                    .output_path
                )
                is True
            )

        print(
            "TEST 10 — successful output always has physical artifact → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13C.2 PROVIDER ARTIFACT BOUNDARY PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()