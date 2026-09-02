import base64
from pathlib import Path

from app.models.generation import (
    GenerationRequest,
    GenerationType,
)

from app.generation.providers.gemini_contract import (
    GeminiGenerationPlan,
    GeminiInputImage,
)


class GeminiRequestMapper:
    """
    Translate provider-agnostic GenerationRequest objects into a
    Gemini-specific generation plan.

    Responsibilities:
    - preserve prompt meaning
    - translate negative_prompt into textual constraints
    - load resolved physical reference images
    - preserve reference ordering
    - encode reference bytes as base64
    - detect supported reference MIME types
    - preserve requested aspect ratio and output format

    This mapper performs no network calls.
    """

    def __init__(
        self,
        model: str,
    ):

        cleaned_model = (
            model.strip()
        )

        if not cleaned_model:

            raise ValueError(
                "Gemini model cannot be empty."
            )

        self.model = (
            cleaned_model
        )

    # ================================================================
    # MAP
    # ================================================================

    def map(
        self,
        request: GenerationRequest,
    ) -> GeminiGenerationPlan:

        self._validate_request(
            request
        )

        prompt_text = (
            self._build_prompt_text(
                request
            )
        )

        input_images = [
            self._map_reference(
                reference
            )
            for reference
            in request.reference_assets
        ]

        return (
            GeminiGenerationPlan(
                model=(
                    self.model
                ),
                prompt_text=(
                    prompt_text
                ),
                input_images=(
                    input_images
                ),
                aspect_ratio=(
                    request.output
                    .aspect_ratio
                    .strip()
                ),
                output_format=(
                    request.output
                    .output_format
                    .strip()
                    .lower()
                ),
            )
        )

    # ================================================================
    # VALIDATION
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
                "GeminiRequestMapper currently "
                "supports KEYFRAME generation only."
            )

        if (
            not request.prompt.strip()
        ):

            raise ValueError(
                "Generation prompt cannot be empty."
            )

        if (
            not request.output
            .aspect_ratio
            .strip()
        ):

            raise ValueError(
                "Generation aspect ratio cannot be empty."
            )

        if (
            not request.output
            .output_format
            .strip()
        ):

            raise ValueError(
                "Generation output format cannot be empty."
            )

    # ================================================================
    # PROMPT TRANSLATION
    # ================================================================

    def _build_prompt_text(
        self,
        request: GenerationRequest,
    ) -> str:
        """
        Gemini does not use the provider-agnostic negative_prompt
        field as a dedicated API parameter.

        Instead, negative constraints are translated into explicit
        natural-language instructions.
        """

        base_prompt = (
            request.prompt.strip()
        )

        negative_prompt = (
            request.negative_prompt
        )

        if (
            negative_prompt is None
            or
            not negative_prompt.strip()
        ):

            return base_prompt

        constraints = (
            negative_prompt.strip()
        )

        return (
            f"{base_prompt}\n\n"
            "Visual constraints:\n"
            f"{constraints}"
        )

    # ================================================================
    # REFERENCE IMAGE
    # ================================================================

    def _map_reference(
        self,
        reference,
    ) -> GeminiInputImage:

        reference_path = Path(
            reference.reference_path
        )

        if (
            not reference_path.exists()
            or
            not reference_path.is_file()
        ):

            raise FileNotFoundError(
                "Gemini reference image was not found: "
                f"{reference_path}"
            )

        raw_bytes = (
            reference_path
            .read_bytes()
        )

        if not raw_bytes:

            raise ValueError(
                "Gemini reference image cannot be empty: "
                f"{reference_path}"
            )

        mime_type = (
            self._mime_type(
                reference_path
            )
        )

        encoded = (
            base64.b64encode(
                raw_bytes
            )
            .decode(
                "ascii"
            )
        )

        return (
            GeminiInputImage(
                asset_id=(
                    reference.asset_id
                ),
                entity_id=(
                    reference.entity_id
                ),
                mime_type=(
                    mime_type
                ),
                data_base64=(
                    encoded
                ),
            )
        )

    # ================================================================
    # MIME TYPE
    # ================================================================

    def _mime_type(
        self,
        path: Path,
    ) -> str:

        suffix = (
            path.suffix
            .strip()
            .lower()
        )

        mapping = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }

        mime_type = (
            mapping.get(
                suffix
            )
        )

        if mime_type is None:

            raise ValueError(
                "Unsupported Gemini reference "
                "image format: "
                f"{suffix or '<none>'}"
            )

        return mime_type