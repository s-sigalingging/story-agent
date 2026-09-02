from pathlib import Path
from typing import Optional

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


class FakeGenerationProvider(
    GenerationProvider
):
    """
    Deterministic test provider.

    Supported modes:

    SUCCESS
        Every attempt succeeds.

    RETRYABLE_FAILURE
        Every attempt fails with retryable=True.

    PERMANENT_FAILURE
        Every attempt fails with retryable=False.

    FAIL_THEN_SUCCESS
        The first N attempts fail retryably, then generation succeeds.
    """

    def __init__(
        self,
        mode: str = "SUCCESS",
        output_root: Optional[
            str
        ] = None,
        output_count: int = 1,
        fail_attempts: int = 1,
        capabilities: Optional[
            ProviderCapabilities
        ] = None,
    ):

        self.mode = (
            mode.strip().upper()
        )

        self.output_count = (
            output_count
        )

        self.fail_attempts = (
            fail_attempts
        )

        if (
            self.output_count
            < 1
        ):

            raise ValueError(
                "output_count must be at least 1."
            )

        if (
            self.fail_attempts
            < 0
        ):

            raise ValueError(
                "fail_attempts cannot be negative."
            )

        if output_root is None:

            output_root = (
                "data/generated/fake"
            )

        self.output_root = Path(
            output_root
        )

        if capabilities is None:

            capabilities = (
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

        self._capabilities = (
            capabilities
        )

    # ================================================================
    # PROVIDER NAME
    # ================================================================

    @property
    def name(
        self,
    ) -> str:

        return "FAKE_PROVIDER"

    # ================================================================
    # PROVIDER CAPABILITIES
    # ================================================================

    @property
    def capabilities(
        self,
    ) -> ProviderCapabilities:

        return (
            self._capabilities
            .model_copy(
                deep=True
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
            == "RETRYABLE_FAILURE"
        ):

            return (
                self._failed_attempt(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "FAKE_RETRYABLE_FAILURE"
                    ),
                    message=(
                        "Simulated retryable "
                        "provider failure."
                    ),
                    retryable=True,
                )
            )

        if (
            self.mode
            == "PERMANENT_FAILURE"
        ):

            return (
                self._failed_attempt(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "FAKE_PERMANENT_FAILURE"
                    ),
                    message=(
                        "Simulated permanent "
                        "provider failure."
                    ),
                    retryable=False,
                )
            )

        if (
            self.mode
            == "FAIL_THEN_SUCCESS"
        ):

            if (
                attempt_number
                <= self.fail_attempts
            ):

                return (
                    self._failed_attempt(
                        request=request,
                        attempt_number=(
                            attempt_number
                        ),
                        code=(
                            "FAKE_TRANSIENT_FAILURE"
                        ),
                        message=(
                            "Simulated transient "
                            "provider failure."
                        ),
                        retryable=True,
                    )
                )

            return (
                self._successful_attempt(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                )
            )

        if (
            self.mode
            == "SUCCESS"
        ):

            return (
                self._successful_attempt(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                )
            )

        raise ValueError(
            "Unsupported fake provider mode: "
            f"{self.mode}"
        )

    # ================================================================
    # SUCCESS
    # ================================================================

    def _successful_attempt(
        self,
        request: GenerationRequest,
        attempt_number: int,
    ) -> GenerationAttempt:

        outputs = []

        for output_index in range(
            1,
            self.output_count + 1,
        ):

            output_id = (
                f"{request.request_id}"
                f"_ATTEMPT_{attempt_number:03d}"
                f"_OUTPUT_{output_index:03d}"
            )

            output_path = (
                self.output_root
                /
                request.episode_id
                /
                request.shot_id
                /
                (
                    f"{output_id}."
                    f"{request.output.output_format}"
                )
            )

            outputs.append(
                GenerationOutput(
                    output_id=(
                        output_id
                    ),
                    output_path=(
                        str(
                            output_path
                        )
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
                        "fake": "true",
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
                outputs=outputs,
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

    def _failed_attempt(
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