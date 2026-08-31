from app.generation.providers.base import (
    GenerationProvider,
)

from app.models.generation import (
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
    GenerationType,
)


class KeyframeGenerator:
    """
    Provider-agnostic execution engine for keyframe generation.

    The generator coordinates one GenerationRequest with one
    GenerationProvider.

    Batch 12D intentionally performs a single attempt only.

    Retry policy and exception recovery belong to a later generation
    orchestration layer.
    """

    def __init__(
        self,
        provider: GenerationProvider,
    ):

        self.provider = provider

    # ================================================================
    # GENERATE
    # ================================================================

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Execute one keyframe generation attempt.

        The provider returns a GenerationAttempt.

        The generator converts that attempt into the aggregate
        GenerationResult contract used by downstream systems.
        """

        self._validate_request(
            request
        )

        attempt = (
            self.provider.generate(
                request=request,
                attempt_number=1,
            )
        )

        self._validate_attempt(
            request=request,
            attempt=attempt,
        )

        if (
            attempt.status
            == GenerationStatus.SUCCEEDED
        ):

            outputs = list(
                attempt.outputs
            )

            return (
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
                        attempt
                    ],
                    outputs=(
                        outputs
                    ),
                    selected_output_id=None,
                    metadata={
                        "provider": (
                            self.provider.name
                        ),
                        "attempt_count": "1",
                    },
                )
            )

        return (
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
                    GenerationStatus.FAILED
                ),
                attempts=[
                    attempt
                ],
                outputs=[],
                selected_output_id=None,
                metadata={
                    "provider": (
                        self.provider.name
                    ),
                    "attempt_count": "1",
                },
            )
        )

    # ================================================================
    # REQUEST VALIDATION
    # ================================================================

    def _validate_request(
        self,
        request: GenerationRequest,
    ) -> None:

        if (
            request.generation_type
            != GenerationType.KEYFRAME
        ):

            raise ValueError(
                "KeyframeGenerator only supports "
                "KEYFRAME generation requests."
            )

        if (
            not request.request_id.strip()
        ):

            raise ValueError(
                "Generation request_id "
                "cannot be empty."
            )

        if (
            not request.episode_id.strip()
        ):

            raise ValueError(
                "Generation episode_id "
                "cannot be empty."
            )

        if (
            not request.shot_id.strip()
        ):

            raise ValueError(
                "Generation shot_id "
                "cannot be empty."
            )

        if (
            not request.prompt.strip()
        ):

            raise ValueError(
                "Keyframe generation prompt "
                "cannot be empty."
            )

    # ================================================================
    # ATTEMPT VALIDATION
    # ================================================================

    def _validate_attempt(
        self,
        request: GenerationRequest,
        attempt,
    ) -> None:
        """
        Protect the core pipeline from malformed provider adapters.

        Provider implementations must preserve request lineage.
        """

        if (
            attempt.request_id
            != request.request_id
        ):

            raise ValueError(
                "Provider returned an attempt "
                "for a different request_id."
            )

        if (
            attempt.attempt_number
            != 1
        ):

            raise ValueError(
                "Provider returned an unexpected "
                "attempt number."
            )

        if (
            attempt.status
            == GenerationStatus.SUCCEEDED
            and
            not attempt.outputs
        ):

            raise ValueError(
                "Successful generation attempt "
                "must contain at least one output."
            )

        if (
            attempt.status
            == GenerationStatus.FAILED
            and
            attempt.error
            is None
        ):

            raise ValueError(
                "Failed generation attempt "
                "must contain structured error "
                "information."
            )

        if (
            attempt.status
            not in {
                GenerationStatus.SUCCEEDED,
                GenerationStatus.FAILED,
            }
        ):

            raise ValueError(
                "Provider returned a non-terminal "
                "generation attempt status."
            )