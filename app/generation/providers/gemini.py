import base64
import os
from typing import Any, Optional

from app.generation.artifact_store import (
    GenerationArtifactStore,
)

from app.generation.providers.base import (
    GenerationProvider,
)

from app.generation.providers.gemini_mapper import (
    GeminiRequestMapper,
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


class GeminiGenerationProvider(
    GenerationProvider
):
    """
    Google Gemini image generation provider adapter.

    Important safety rule:

    Network execution is disabled by default.

    Unit/regression tests therefore cannot accidentally consume API
    credits unless network_enabled=True is explicitly supplied.

    A client may also be injected for deterministic offline testing.
    """

    def __init__(
        self,
        artifact_store: GenerationArtifactStore,
        model: str = "gemini-3.1-flash-image",
        api_key_env: str = "GEMINI_API_KEY",
        network_enabled: bool = False,
        client: Optional[Any] = None,
    ):

        cleaned_model = (
            model.strip()
        )

        if not cleaned_model:

            raise ValueError(
                "Gemini model cannot be empty."
            )

        cleaned_api_key_env = (
            api_key_env.strip()
        )

        if not cleaned_api_key_env:

            raise ValueError(
                "Gemini API key environment "
                "variable cannot be empty."
            )

        self.artifact_store = (
            artifact_store
        )

        self.model = (
            cleaned_model
        )

        self.api_key_env = (
            cleaned_api_key_env
        )

        self.network_enabled = (
            network_enabled
        )

        self._client = (
            client
        )

        self.mapper = (
            GeminiRequestMapper(
                model=self.model
            )
        )

    # ================================================================
    # PROVIDER IDENTITY
    # ================================================================

    @property
    def name(
        self,
    ) -> str:

        return (
            "GOOGLE_GEMINI"
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
                max_reference_images=10,
                supports_negative_prompt=True,
                supported_output_formats=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp",
                ],
                supported_aspect_ratios=[
                    "1:1",
                    "9:16",
                    "16:9",
                    "3:4",
                    "4:3",
                ],
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

        # ------------------------------------------------------------
        # CAPABILITY GATE
        # ------------------------------------------------------------

        capability_result = (
            self.validate_request_capabilities(
                request
            )
        )

        if (
            not capability_result.compatible
        ):

            return (
                self._failure(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "GEMINI_CAPABILITY_MISMATCH"
                    ),
                    message=(
                        "; ".join(
                            capability_result.issues
                        )
                    ),
                    retryable=False,
                )
            )

        # ------------------------------------------------------------
        # NETWORK SAFETY GATE
        # ------------------------------------------------------------

        if (
            not self.network_enabled
            and
            self._client
            is None
        ):

            return (
                self._failure(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "GEMINI_NETWORK_DISABLED"
                    ),
                    message=(
                        "Gemini network execution is disabled."
                    ),
                    retryable=False,
                )
            )

        # ------------------------------------------------------------
        # MAP GENERIC REQUEST
        # ------------------------------------------------------------

        try:

            plan = (
                self.mapper.map(
                    request
                )
            )

        except Exception as exc:

            return (
                self._failure(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "GEMINI_REQUEST_MAPPING_FAILED"
                    ),
                    message=str(
                        exc
                    ),
                    retryable=False,
                )
            )

        # ------------------------------------------------------------
        # EXECUTE
        # ------------------------------------------------------------

        try:

            client = (
                self._get_client()
            )

            sdk_input = (
                self._build_sdk_input(
                    plan
                )
            )

            interaction = (
                client.interactions.create(
                    model=(
                        plan.model
                    ),
                    input=(
                        sdk_input
                    ),
                )
            )

            artifact_bytes = (
                self._extract_output_bytes(
                    interaction
                )
            )

            return (
                self._materialize_success(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    artifact_bytes=(
                        artifact_bytes
                    ),
                )
            )

        except Exception as exc:

            return (
                self._failure(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                    code=(
                        "GEMINI_PROVIDER_ERROR"
                    ),
                    message=str(
                        exc
                    ),
                    retryable=(
                        self._is_retryable_error(
                            exc
                        )
                    ),
                )
            )

    # ================================================================
    # SDK CLIENT
    # ================================================================

    def _get_client(
        self,
    ):

        if (
            self._client
            is not None
        ):

            return (
                self._client
            )

        if (
            not self.network_enabled
        ):

            raise RuntimeError(
                "Gemini network execution "
                "is disabled."
            )

        api_key = (
            os.getenv(
                self.api_key_env
            )
        )

        if (
            api_key is None
            or
            not api_key.strip()
        ):

            raise RuntimeError(
                "Gemini API key was not found "
                f"in environment variable "
                f"{self.api_key_env}."
            )

        # ------------------------------------------------------------
        # LAZY IMPORT
        #
        # The SDK is imported only when actual network execution is
        # requested. Offline regression tests therefore do not require
        # google-genai to be installed.
        # ------------------------------------------------------------

        try:

            from google import genai

        except ImportError as exc:

            raise RuntimeError(
                "google-genai is not installed. "
                "Install it before enabling "
                "Gemini network execution."
            ) from exc

        self._client = (
            genai.Client(
                api_key=(
                    api_key
                )
            )
        )

        return (
            self._client
        )

    # ================================================================
    # SDK INPUT
    # ================================================================

    def _build_sdk_input(
        self,
        plan,
    ):

        prompt_text = (
            self._build_execution_prompt(
                plan
            )
        )

        if (
            not plan.input_images
        ):

            return (
                prompt_text
            )

        sdk_input = [
            {
                "type": "text",
                "text": (
                    prompt_text
                ),
            }
        ]

        for image in (
            plan.input_images
        ):

            sdk_input.append({
                "type": "image",
                "data": (
                    image.data_base64
                ),
                "mime_type": (
                    image.mime_type
                ),
            })

        return (
            sdk_input
        )

    def _build_execution_prompt(
        self,
        plan,
    ) -> str:
        """
        Aspect ratio is represented as an explicit textual instruction
        until the exact native SDK configuration field is verified.

        We intentionally do not invent undocumented SDK arguments.
        """

        return (
            f"{plan.prompt_text}\n\n"
            "Output requirements:\n"
            f"- Aspect ratio: {plan.aspect_ratio}\n"
            f"- Output format: {plan.output_format}"
        )

    # ================================================================
    # OUTPUT EXTRACTION
    # ================================================================

    def _extract_output_bytes(
        self,
        interaction,
    ) -> bytes:
        """
        Extract image data using the interaction.output_image.data
        contract shown by the Gemini example we are integrating
        against.
        """

        output_image = getattr(
            interaction,
            "output_image",
            None,
        )

        if (
            output_image
            is None
        ):

            raise ValueError(
                "Gemini response did not contain "
                "output_image."
            )

        data = getattr(
            output_image,
            "data",
            None,
        )

        if (
            data is None
        ):

            raise ValueError(
                "Gemini output_image did not "
                "contain data."
            )

        if isinstance(
            data,
            str,
        ):

            encoded = (
                data.encode(
                    "ascii"
                )
            )

        elif isinstance(
            data,
            bytes,
        ):

            encoded = (
                data
            )

        else:

            raise TypeError(
                "Gemini output_image.data must "
                "be base64 text or bytes."
            )

        try:

            decoded = (
                base64.b64decode(
                    encoded,
                    validate=True,
                )
            )

        except Exception as exc:

            raise ValueError(
                "Gemini output image data "
                "is not valid base64."
            ) from exc

        if (
            not decoded
        ):

            raise ValueError(
                "Gemini returned an empty "
                "image artifact."
            )

        return (
            decoded
        )

    # ================================================================
    # SUCCESS
    # ================================================================

    def _materialize_success(
        self,
        request: GenerationRequest,
        attempt_number: int,
        artifact_bytes: bytes,
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
                    request.output
                    .output_format
                ),
                content=(
                    artifact_bytes
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
                "Gemini artifact was not "
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
                    "model": (
                        self.model
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
                    "model": (
                        self.model
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
                    "model": (
                        self.model
                    ),
                },
            )
        )

    # ================================================================
    # ERROR CLASSIFICATION
    # ================================================================

    def _is_retryable_error(
        self,
        exc: Exception,
    ) -> bool:
        """
        Conservative preliminary classifier.

        Precise Gemini SDK exception mapping will be hardened in
        Batch 13H after we have observed the real SDK behavior.
        """

        text = (
            f"{exc.__class__.__name__} "
            f"{str(exc)}"
        ).lower()

        retryable_markers = [
            "timeout",
            "temporarily",
            "temporary",
            "rate limit",
            "rate_limit",
            "429",
            "503",
            "unavailable",
            "connection",
        ]

        return any(
            marker
            in text
            for marker
            in retryable_markers
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