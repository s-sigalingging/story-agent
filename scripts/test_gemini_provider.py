import base64
import tempfile
from pathlib import Path
from types import SimpleNamespace

from app.generation import (
    GeminiGenerationProvider,
    GenerationArtifactStore,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationRequest,
    GenerationStatus,
    GenerationType,
)


class FakeInteractions:

    def __init__(
        self,
        image_bytes: bytes,
    ):

        self.image_bytes = (
            image_bytes
        )

        self.calls = []

    def create(
        self,
        model,
        input,
    ):

        self.calls.append({
            "model": model,
            "input": input,
        })

        encoded = (
            base64.b64encode(
                self.image_bytes
            )
            .decode(
                "ascii"
            )
        )

        return (
            SimpleNamespace(
                output_image=(
                    SimpleNamespace(
                        data=(
                            encoded
                        )
                    )
                )
            )
        )


class FakeGeminiClient:

    def __init__(
        self,
        image_bytes: bytes,
    ):

        self.interactions = (
            FakeInteractions(
                image_bytes=(
                    image_bytes
                )
            )
        )


class FailingInteractions:

    def create(
        self,
        model,
        input,
    ):

        raise RuntimeError(
            "503 service unavailable"
        )


class FailingGeminiClient:

    def __init__(
        self,
    ):

        self.interactions = (
            FailingInteractions()
        )


def make_request():

    return (
        GenerationRequest(
            request_id=(
                "GEN_REQ_GEMINI_PROVIDER"
            ),
            episode_id=(
                "EP_GEMINI_PROVIDER"
            ),
            shot_id=(
                "EP_GEMINI_PROVIDER-S01-SHOT01"
            ),
            generation_type=(
                GenerationType.KEYFRAME
            ),
            prompt=(
                "Create a cinematic detective portrait."
            ),
            negative_prompt=(
                "Avoid text and distorted anatomy."
            ),
            output=(
                GenerationOutputSpec(
                    width=1080,
                    height=1920,
                    aspect_ratio="9:16",
                    output_format="png",
                )
            ),
        )
    )


def main():

    print()
    print(
        "BATCH 13D.2 — GEMINI PROVIDER"
    )
    print(
        "========================================"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        artifact_store = (
            GenerationArtifactStore(
                base_path=temp_dir
            )
        )

        request = (
            make_request()
        )

        # ============================================================
        # TEST 1 — NETWORK DISABLED BY DEFAULT
        # ============================================================

        provider = (
            GeminiGenerationProvider(
                artifact_store=(
                    artifact_store
                )
            )
        )

        result = (
            provider.generate(
                request=request,
                attempt_number=1,
            )
        )

        assert (
            result.status
            ==
            GenerationStatus.FAILED
        )

        assert (
            result.error
            is not None
        )

        assert (
            result.error.code
            ==
            "GEMINI_NETWORK_DISABLED"
        )

        print(
            "TEST 1 — network disabled by default → PASSED"
        )

        # ============================================================
        # TEST 2 — INJECTED CLIENT CAN EXECUTE OFFLINE
        # ============================================================

        expected_bytes = (
            b"offline-gemini-image"
        )

        fake_client = (
            FakeGeminiClient(
                image_bytes=(
                    expected_bytes
                )
            )
        )

        provider = (
            GeminiGenerationProvider(
                artifact_store=(
                    artifact_store
                ),
                client=(
                    fake_client
                ),
            )
        )

        result = (
            provider.generate(
                request=request,
                attempt_number=2,
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

        print(
            "TEST 2 — injected client executes offline → PASSED"
        )

        # ============================================================
        # TEST 3 — RESPONSE MATERIALIZED
        # ============================================================

        output = (
            result.outputs[0]
        )

        physical_path = Path(
            output.output_path
        )

        assert (
            physical_path.is_file()
        )

        assert (
            physical_path.read_bytes()
            ==
            expected_bytes
        )

        print(
            "TEST 3 — Gemini response materialized → PASSED"
        )

        # ============================================================
        # TEST 4 — SDK CALL CONTRACT
        # ============================================================

        calls = (
            fake_client
            .interactions
            .calls
        )

        assert (
            len(calls)
            == 1
        )

        call = (
            calls[0]
        )

        assert (
            call["model"]
            ==
            "gemini-3.1-flash-image"
        )

        assert isinstance(
            call["input"],
            str,
        )

        print(
            "TEST 4 — SDK interaction contract mapped → PASSED"
        )

        # ============================================================
        # TEST 5 — NEGATIVE CONSTRAINT REACHES SDK INPUT
        # ============================================================

        assert (
            "Visual constraints:"
            in call[
                "input"
            ]
        )

        assert (
            "Avoid text and distorted anatomy."
            in call[
                "input"
            ]
        )

        print(
            "TEST 5 — negative constraints reach Gemini → PASSED"
        )

        # ============================================================
        # TEST 6 — ASPECT RATIO INSTRUCTION PRESERVED
        # ============================================================

        assert (
            "Aspect ratio: 9:16"
            in call[
                "input"
            ]
        )

        print(
            "TEST 6 — output ratio reaches execution prompt → PASSED"
        )

        # ============================================================
        # TEST 7 — OUTPUT LINEAGE
        # ============================================================

        assert (
            result.attempt_id
            ==
            "GEN_REQ_GEMINI_PROVIDER"
            "_ATTEMPT_002"
        )

        assert (
            output.output_id
            ==
            "GEN_REQ_GEMINI_PROVIDER"
            "_ATTEMPT_002_OUTPUT_001"
        )

        print(
            "TEST 7 — Gemini lineage preserved → PASSED"
        )

        # ============================================================
        # TEST 8 — PROVIDER METADATA
        # ============================================================

        assert (
            output.metadata[
                "provider"
            ]
            ==
            "GOOGLE_GEMINI"
        )

        assert (
            output.metadata[
                "artifact_materialized"
            ]
            ==
            "true"
        )

        print(
            "TEST 8 — provider metadata preserved → PASSED"
        )

        # ============================================================
        # TEST 9 — RETRYABLE SERVICE ERROR NORMALIZED
        # ============================================================

        failing_provider = (
            GeminiGenerationProvider(
                artifact_store=(
                    artifact_store
                ),
                client=(
                    FailingGeminiClient()
                ),
            )
        )

        failed_result = (
            failing_provider.generate(
                request=(
                    request
                ),
                attempt_number=3,
            )
        )

        assert (
            failed_result.status
            ==
            GenerationStatus.FAILED
        )

        assert (
            failed_result.error
            is not None
        )

        assert (
            failed_result.error.code
            ==
            "GEMINI_PROVIDER_ERROR"
        )

        assert (
            failed_result.error.retryable
            is True
        )

        print(
            "TEST 9 — transient Gemini error normalized → PASSED"
        )

        # ============================================================
        # TEST 10 — NO ARTIFACT ON PROVIDER FAILURE
        # ============================================================

        assert (
            failed_result.outputs
            == []
        )

        failed_output_path = (
            artifact_store.build_path(
                episode_id=(
                    request.episode_id
                ),
                shot_id=(
                    request.shot_id
                ),
                output_id=(
                    request.request_id
                    +
                    "_ATTEMPT_003_OUTPUT_001"
                ),
                output_format=(
                    request.output
                    .output_format
                ),
            )
        )

        assert (
            failed_output_path.exists()
            is False
        )

        print(
            "TEST 10 — provider failure creates no artifact → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13D.2 GEMINI PROVIDER PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()