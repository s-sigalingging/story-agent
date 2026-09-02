from typing import List

from pydantic import BaseModel, Field


class GeminiInputImage(
    BaseModel
):
    """
    One physical reference image prepared for Gemini.

    This model belongs to the Gemini adapter boundary and must not
    leak into provider-agnostic generation models.
    """

    asset_id: str

    entity_id: str

    mime_type: str

    data_base64: str


class GeminiGenerationPlan(
    BaseModel
):
    """
    Provider-specific execution plan for Gemini image generation.

    This is NOT the Google SDK payload itself.

    The real Gemini provider adapter will translate this plan into
    the currently supported SDK/API request format.
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