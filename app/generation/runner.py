from typing import Optional

from app.generation.providers.base import (
    GenerationProvider,
)

from app.generation.store import (
    GenerationStore,
)

from app.models.generation import (
    GenerationAttempt,
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
    GenerationType,
)


class GenerationRunner:
    """
    Retry-aware execution coordinator.

    The runner owns technical retry policy.

    It does not perform creative review or output approval.
    """

    def __init__(
        self,
        provider: GenerationProvider,
        max_attempts: int = 3,
        store: Optional[
            GenerationStore
        ] = None,
    ):

        if (
            max_attempts
            < 1
        ):

            raise ValueError(
                "max_attempts must be at least 1."
            )

        self.provider = provider

        self.max_attempts = (
            max_attempts
        )

        self.store = store

    # ================================================================
    # RUN
    # ================================================================

    def run(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:

        self._validate_request(
            request
        )

        self._ensure_persisted(
            request
        )

        attempts = []
        outputs = []

        final_status = (
            GenerationStatus.FAILED
        )

        for attempt_number in range(
            1,
            self.max_attempts + 1,
        ):

            attempt = (
                self.provider.generate(
                    request=request,
                    attempt_number=(
                        attempt_number
                    ),
                )
            )

            self._validate_attempt(
                request=request,
                attempt=attempt,
                expected_attempt_number=(
                    attempt_number
                ),
            )

            attempts.append(
                attempt
            )

            # ========================================================
            # SUCCESS
            # ========================================================

            if (
                attempt.status
                == GenerationStatus.SUCCEEDED
            ):

                outputs.extend(
                    attempt.outputs
                )

                final_status = (
                    GenerationStatus.SUCCEEDED
                )

                break

            # ========================================================
            # FAILURE
            # ========================================================

            error = (
                attempt.error
            )

            if (
                error is None
            ):

                break

            if (
                not error.retryable
            ):

                break

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
                    final_status
                ),
                attempts=(
                    attempts
                ),
                outputs=(
                    outputs
                ),
                selected_output_id=None,
                metadata={
                    "provider": (
                        self.provider.name
                    ),
                    "attempt_count": (
                        str(
                            len(attempts)
                        )
                    ),
                    "max_attempts": (
                        str(
                            self.max_attempts
                        )
                    ),
                },
            )
        )

        self._persist_result(
            result
        )

        return result

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
                "GenerationRunner currently "
                "supports KEYFRAME requests only."
            )

        if (
            not request.request_id.strip()
        ):

            raise ValueError(
                "request_id cannot be empty."
            )

        if (
            not request.episode_id.strip()
        ):

            raise ValueError(
                "episode_id cannot be empty."
            )

        if (
            not request.shot_id.strip()
        ):

            raise ValueError(
                "shot_id cannot be empty."
            )

        if (
            not request.prompt.strip()
        ):

            raise ValueError(
                "Generation prompt cannot be empty."
            )

    # ================================================================
    # ATTEMPT VALIDATION
    # ================================================================

    def _validate_attempt(
        self,
        request: GenerationRequest,
        attempt: GenerationAttempt,
        expected_attempt_number: int,
    ) -> None:

        if (
            attempt.request_id
            != request.request_id
        ):

            raise ValueError(
                "Provider returned attempt "
                "for a different request."
            )

        if (
            attempt.attempt_number
            != expected_attempt_number
        ):

            raise ValueError(
                "Provider returned incorrect "
                "attempt number."
            )

        if (
            attempt.status
            == GenerationStatus.SUCCEEDED
        ):

            if (
                not attempt.outputs
            ):

                raise ValueError(
                    "Successful attempt must "
                    "contain output."
                )

            return

        if (
            attempt.status
            == GenerationStatus.FAILED
        ):

            if (
                attempt.error
                is None
            ):

                raise ValueError(
                    "Failed attempt must contain "
                    "structured error information."
                )

            return

        raise ValueError(
            "Provider returned non-terminal "
            "generation status."
        )

    # ================================================================
    # PERSISTENCE
    # ================================================================

    def _ensure_persisted(
        self,
        request: GenerationRequest,
    ) -> None:

        if (
            self.store
            is None
        ):

            return

        exists = (
            self.store.exists(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
        )

        if not exists:

            self.store.create(
                request
            )

    def _persist_result(
        self,
        result: GenerationResult,
    ) -> None:

        if (
            self.store
            is None
        ):

            return

        self.store.save_result(
            result
        )