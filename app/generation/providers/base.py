from abc import ABC, abstractmethod

from app.models.generation import (
    GenerationAttempt,
    GenerationRequest,
)

from app.models.generation_provider import (
    CapabilityValidationResult,
    ProviderCapabilities,
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

    @property
    @abstractmethod
    def capabilities(
        self,
    ) -> ProviderCapabilities:
        """
        Provider capability declaration.

        This property must not perform a remote API call.
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

        Provider-specific payloads must not leak through this
        boundary.
        """

        raise NotImplementedError

    # ================================================================
    # CAPABILITY VALIDATION
    # ================================================================

    def validate_request_capabilities(
        self,
        request: GenerationRequest,
    ) -> CapabilityValidationResult:
        """
        Validate whether this provider can technically handle the
        supplied GenerationRequest.

        This check is local and deterministic.
        """

        issues = []

        capabilities = (
            self.capabilities
        )

        # ------------------------------------------------------------
        # KEYFRAME SUPPORT
        # ------------------------------------------------------------

        if (
            request.generation_type.value
            == "KEYFRAME"
            and
            not capabilities.supports_keyframe
        ):

            issues.append(
                "Provider does not support "
                "KEYFRAME generation."
            )

        # ------------------------------------------------------------
        # REFERENCE IMAGES
        # ------------------------------------------------------------

        reference_count = (
            len(
                request.reference_assets
            )
        )

        if (
            reference_count
            > 0
            and
            not capabilities
            .supports_reference_images
        ):

            issues.append(
                "Provider does not support "
                "reference images."
            )

        if (
            reference_count
            > 0
            and
            capabilities
            .supports_reference_images
            and
            capabilities
            .max_reference_images
            is not None
            and
            reference_count
            >
            capabilities
            .max_reference_images
        ):

            issues.append(
                "Generation request contains "
                f"{reference_count} reference images, "
                "but provider supports at most "
                f"{capabilities.max_reference_images}."
            )

        # ------------------------------------------------------------
        # NEGATIVE PROMPT
        # ------------------------------------------------------------

        if (
            request.negative_prompt
            is not None
            and
            request.negative_prompt.strip()
            and
            not capabilities
            .supports_negative_prompt
        ):

            issues.append(
                "Provider does not support "
                "negative prompts."
            )

        # ------------------------------------------------------------
        # OUTPUT FORMAT
        # ------------------------------------------------------------

        requested_format = (
            request.output
            .output_format
            .strip()
            .lower()
        )

        supported_formats = {
            item.strip().lower()
            for item
            in capabilities
            .supported_output_formats
        }

        if (
            requested_format
            not in supported_formats
        ):

            issues.append(
                "Unsupported output format: "
                f"{request.output.output_format}"
            )

        # ------------------------------------------------------------
        # ASPECT RATIO
        # ------------------------------------------------------------

        if (
            capabilities
            .supported_aspect_ratios
        ):

            supported_ratios = {
                item.strip()
                for item
                in capabilities
                .supported_aspect_ratios
            }

            if (
                request.output
                .aspect_ratio
                .strip()
                not in supported_ratios
            ):

                issues.append(
                    "Unsupported aspect ratio: "
                    f"{request.output.aspect_ratio}"
                )

        return (
            CapabilityValidationResult(
                compatible=(
                    len(issues)
                    == 0
                ),
                issues=issues,
            )
        )