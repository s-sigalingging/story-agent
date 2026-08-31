from abc import ABC, abstractmethod

from app.models.generation import (
    GenerationAttempt,
    GenerationRequest,
)


class GenerationProvider(
    ABC
):
    """
    Provider-agnostic contract for media generation backends.

    Core generation code must depend on this interface rather
    than on any provider SDK directly.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Stable provider identifier.
        """

        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        request: GenerationRequest,
        attempt_number: int,
    ) -> GenerationAttempt:
        """
        Execute one technical generation attempt.

        The provider returns a GenerationAttempt rather than a raw
        SDK response.

        Provider-specific payloads must not leak through this
        boundary.
        """

        raise NotImplementedError