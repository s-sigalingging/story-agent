from app.generation.artifact_store import (
    GenerationArtifactStore,
)

from app.generation.providers.base import (
    GenerationProvider,
)

from app.models.generation import (
    GenerationAttempt,
    GenerationError,
    GenerationOutput,
    GenerationRequest,
    GenerationStatus,
)

from app.models.generation_provider import (
    ProviderCapabilities,
)


class ArtifactFakeGenerationProvider(
    GenerationProvider
):
    """
    Deterministic artifact-backed provider used to test the boundary
    between generation providers and physical artifact storage.

    Unlike FakeGenerationProvider, this provider actually materializes
    output bytes through GenerationArtifactStore.

    It performs no network calls and consumes no external API credits.
    """

    def __init__(
        self,
        artifact_store: GenerationArtifactStore,
        mode: str = "SUCCESS",
        content: bytes = b"fake-generated-image-bytes",
    ):

        self.artifact_store = (
            artifact_store
        )

        self.mode = (
            mode.strip().upper()
        )

        self.content = (
            content
        )

        if not isinstance(
            self.content,
            bytes,
        ):

            raise TypeError(
                "content must be bytes."
            )

        if not self.content:

            raise ValueError(
                "content cannot be empty."
            )

    # ================================================================
    # NAME
    # ================================================================

    @property
    def name(
        self,
    ) -> str:

        return (
            "ARTIFACT_FAKE_PROVIDER"
        )

    # ================================================================
    # CAPABILITIES
    # ================================================================

    @property
    def capabilities(
        self,
    ) -> ProviderCapabilities:

        return (
            ProviderCapabilities(
                supports_keyframe=True,
                supports_reference_images=True,
                max_reference_images=None,
                supports_negative_prompt=True,
                supported_output_formats=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                ],
                supported_aspect_ratios=[],
                supported_media_types=[
                    "IMAGE"
                ],
            )
        )

    # ================================================================
    # GENERATE
    # ================================================================

    def generate(
        self,
        request: GenerationRequest,
        attempt_number: int,
    ) -> GenerationAttempt:

        if (
            attempt_number
            < 1
        ):

            raise ValueError(
                "attempt_number must be at least 1."
            )

        if (
            self.mode
            == "PERMANENT_FAILURE"
        ):

            return (
                self._failure(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "ARTIFACT_FAKE_PERMANENT_FAILURE"
                    ),
                    message=(
                        "Simulated permanent artifact "
                        "provider failure."
                    ),
                    retryable=False,
                )
            )

        if (
            self.mode
            == "RETRYABLE_FAILURE"
        ):

            return (
                self._failure(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "ARTIFACT_FAKE_RETRYABLE_FAILURE"
                    ),
                    message=(
                        "Simulated retryable artifact "
                        "provider failure."
                    ),
                    retryable=True,
                )
            )

        if (
            self.mode
            != "SUCCESS"
        ):

            raise ValueError(
                "Unsupported artifact fake provider mode: "
                f"{self.mode}"
            )

        return (
            self._success(
                request=request,
                attempt_number=(
                    attempt_number
                ),
            )
        )

    # ================================================================
    # SUCCESS
    # ================================================================

    def _success(
        self,
        request: GenerationRequest,
        attempt_number: int,
    ) -> GenerationAttempt:

        output_id = (
            f"{request.request_id}"
            f"_ATTEMPT_{attempt_number:03d}"
            f"_OUTPUT_001"
        )

        output_path = (
            self.artifact_store.write(
                episode_id=(
                    request.episode_id
                ),
                shot_id=(
                    request.shot_id
                ),
                output_id=(
                    output_id
                ),
                output_format=(
                    request.output.output_format
                ),
                content=(
                    self.content
                ),
            )
        )

        if (
            not self.artifact_store
            .verify_path(
                output_path
            )
        ):

            raise IOError(
                "Provider artifact was not "
                "materialized successfully."
            )

        output = (
            GenerationOutput(
                output_id=(
                    output_id
                ),
                output_path=(
                    output_path
                ),
                media_type="IMAGE",
                mime_type=(
                    self._mime_type(
                        request.output
                        .output_format
                    )
                ),
                width=(
                    request.output.width
                ),
                height=(
                    request.output.height
                ),
                metadata={
                    "provider": (
                        self.name
                    ),
                    "artifact_materialized": (
                        "true"
                    ),
                },
            )
        )

        return (
            GenerationAttempt(
                attempt_id=(
                    f"{request.request_id}"
                    f"_ATTEMPT_{attempt_number:03d}"
                ),
                request_id=(
                    request.request_id
                ),
                attempt_number=(
                    attempt_number
                ),
                provider=(
                    self.name
                ),
                status=(
                    GenerationStatus.SUCCEEDED
                ),
                outputs=[
                    output
                ],
                metadata={
                    "mode": (
                        self.mode
                    ),
                },
            )
        )

    # ================================================================
    # FAILURE
    # ================================================================

    def _failure(
        self,
        request: GenerationRequest,
        attempt_number: int,
        code: str,
        message: str,
        retryable: bool,
    ) -> GenerationAttempt:

        return (
            GenerationAttempt(
                attempt_id=(
                    f"{request.request_id}"
                    f"_ATTEMPT_{attempt_number:03d}"
                ),
                request_id=(
                    request.request_id
                ),
                attempt_number=(
                    attempt_number
                ),
                provider=(
                    self.name
                ),
                status=(
                    GenerationStatus.FAILED
                ),
                outputs=[],
                error=(
                    GenerationError(
                        code=code,
                        message=message,
                        retryable=(
                            retryable
                        ),
                    )
                ),
                metadata={
                    "mode": (
                        self.mode
                    ),
                },
            )
        )

    # ================================================================
    # MIME
    # ================================================================

    def _mime_type(
        self,
        output_format: str,
    ) -> str:

        normalized = (
            output_format
            .strip()
            .lower()
        )

        mapping = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }

        return (
            mapping.get(
                normalized,
                "application/octet-stream",
            )
        )