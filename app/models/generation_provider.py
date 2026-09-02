from typing import List, Optional

from pydantic import BaseModel, Field


class ProviderCapabilities(
    BaseModel
):
    """
    Provider capability declaration.

    This model is provider-agnostic.

    It describes what a provider CAN do, not how the provider
    implements the operation internally.
    """

    supports_keyframe: bool = True

    supports_reference_images: bool = False

    max_reference_images: Optional[
        int
    ] = None

    supports_negative_prompt: bool = True

    supported_output_formats: List[
        str
    ] = Field(
        default_factory=lambda: [
            "png"
        ]
    )

    supported_aspect_ratios: List[
        str
    ] = Field(
        default_factory=list
    )

    supported_media_types: List[
        str
    ] = Field(
        default_factory=lambda: [
            "IMAGE"
        ]
    )


class CapabilityValidationResult(
    BaseModel
):
    """
    Result of validating one GenerationRequest against provider
    capabilities.

    This is a technical compatibility result only.
    """

    compatible: bool

    issues: List[
        str
    ] = Field(
        default_factory=list
    )