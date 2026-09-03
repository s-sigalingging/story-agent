from typing import List

from pydantic import BaseModel, Field


class GeminiInputImage(
    BaseModel
):
    """
    One physical reference prepared for Gemini.

    Beside the image bytes, this contract carries provider-facing
    semantic instructions describing how the image should influence
    generation.

    It is still not the actual Google SDK payload.
    """

    asset_id: str

    entity_id: str

    mime_type: str

    data_base64: str

    reference_role: str = (
        "GENERIC"
    )

    preserve_attributes: List[
        str
    ] = Field(
        default_factory=list
    )

    allowed_transformations: List[
        str
    ] = Field(
        default_factory=list
    )

    usage_instruction: str = ""


class GeminiGenerationPlan(
    BaseModel
):
    """
    Provider-specific execution plan for Gemini image generation.

    This is NOT the Google SDK payload itself.

    GeminiGenerationProvider translates this plan into the runtime
    SDK request.
    """

    model: str

    prompt_text: str

    input_images: List[
        GeminiInputImage
    ] = Field(
        default_factory=list
    )

    aspect_ratio: str

    output_format: str