import base64
from pathlib import Path

from app.models.generation import (
    GenerationReferenceAsset,
    GenerationReferenceRole,
    GenerationReferenceTransformation,
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
    - attach generation-time semantic reference roles
    - preserve identity-vs-transformation semantics
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
        reference: GenerationReferenceAsset,
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

        role = (
            self._reference_role(
                reference
            )
        )

        preserve_attributes = (
            reference.preserve_attributes
            or
            self._default_preserve_attributes(
                role
            )
        )

        allowed_transformations = (
            reference.allowed_transformations
            or
            self._default_allowed_transformations(
                role
            )
        )

        usage_instruction = (
            reference.usage_instruction
            or
            self._default_usage_instruction(
                role
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
                reference_role=(
                    role.value
                ),
                preserve_attributes=[
                    value.strip()
                    for value
                    in preserve_attributes
                    if value.strip()
                ],
                allowed_transformations=[
                    transformation.value
                    for transformation
                    in allowed_transformations
                ],
                usage_instruction=(
                    usage_instruction.strip()
                ),
            )
        )

    # ================================================================
    # REFERENCE ROLE
    # ================================================================

    def _reference_role(
        self,
        reference: GenerationReferenceAsset,
    ) -> GenerationReferenceRole:

        if (
            reference.reference_role
            is not None
        ):

            return (
                reference.reference_role
            )

        asset_type = (
            reference.asset_type
            .strip()
            .upper()
        )

        mapping = {
            "CHARACTER": (
                GenerationReferenceRole.CHARACTER
            ),
            "LOCATION": (
                GenerationReferenceRole.LOCATION
            ),
            "PROP": (
                GenerationReferenceRole.PROP
            ),
            "STYLE": (
                GenerationReferenceRole.STYLE
            ),
        }

        return (
            mapping.get(
                asset_type,
                GenerationReferenceRole.GENERIC,
            )
        )

    # ================================================================
    # DEFAULT PRESERVATION SEMANTICS
    # ================================================================

    def _default_preserve_attributes(
        self,
        role: GenerationReferenceRole,
    ):

        mapping = {
            GenerationReferenceRole.CHARACTER: [
                "facial identity",
                "apparent age",
                "hairstyle",
                "facial proportions",
                "body identity",
                "canonical wardrobe identity",
            ],

            GenerationReferenceRole.LOCATION: [
                "architectural identity",
                "materials",
                "recognizable landmarks",
                "environmental design language",
                "spatial character",
            ],

            GenerationReferenceRole.PROP: [
                "object identity",
                "material",
                "color",
                "shape",
                "construction",
                "recognizable design features",
            ],

            GenerationReferenceRole.STYLE: [
                "rendering language",
                "texture treatment",
                "edge treatment",
                "tonal language",
                "cinematic visual style",
            ],

            GenerationReferenceRole.GENERIC: [
                "recognizable visual identity",
            ],
        }

        return list(
            mapping[
                role
            ]
        )

    # ================================================================
    # DEFAULT TRANSFORMATION PERMISSIONS
    # ================================================================

    def _default_allowed_transformations(
        self,
        role: GenerationReferenceRole,
    ):

        mapping = {
            GenerationReferenceRole.CHARACTER: [
                GenerationReferenceTransformation.CHANGE_POSE,
                GenerationReferenceTransformation.CHANGE_EXPRESSION,
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
            ],

            GenerationReferenceRole.LOCATION: [
                GenerationReferenceTransformation.CHANGE_VIEWPOINT,
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
            ],

            GenerationReferenceRole.PROP: [
                GenerationReferenceTransformation.ROTATE,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.OPEN_CLOSE,
                GenerationReferenceTransformation.ADAPT_TO_INTERACTION,
            ],

            GenerationReferenceRole.STYLE: [
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
            ],

            GenerationReferenceRole.GENERIC: [
                GenerationReferenceTransformation.REFRAME,
                GenerationReferenceTransformation.RELIGHT,
                GenerationReferenceTransformation.CHANGE_PERSPECTIVE,
            ],
        }

        return list(
            mapping[
                role
            ]
        )

    # ================================================================
    # DEFAULT ROLE INSTRUCTION
    # ================================================================

    def _default_usage_instruction(
        self,
        role: GenerationReferenceRole,
    ) -> str:

        mapping = {
            GenerationReferenceRole.CHARACTER: (
                "Use this image as a character identity reference. "
                "Preserve identity-defining characteristics, but do "
                "not treat the exact pose, facial expression, camera "
                "angle, lighting, or framing as immutable."
            ),

            GenerationReferenceRole.LOCATION: (
                "Use this image as a location identity reference. "
                "Preserve recognizable environmental identity and "
                "design language, but allow camera viewpoint, "
                "perspective, framing, and lighting to adapt to "
                "the requested shot."
            ),

            GenerationReferenceRole.PROP: (
                "Use this image as a prop identity reference. "
                "Preserve the object's recognizable physical identity, "
                "but allow orientation, rotation, perspective, visible "
                "side, open or closed state, and hand interaction to "
                "change naturally according to the requested action. "
                "Do not force the camera-facing orientation of the "
                "reference image into the generated scene."
            ),

            GenerationReferenceRole.STYLE: (
                "Use this image only as a visual style reference. "
                "Transfer rendering language and visual treatment, "
                "not the depicted objects, environment, composition, "
                "or camera viewpoint."
            ),

            GenerationReferenceRole.GENERIC: (
                "Use this image as a visual reference while preserving "
                "its relevant identity without copying its exact "
                "composition."
            ),
        }

        return (
            mapping[
                role
            ]
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