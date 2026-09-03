from typing import Dict, List

from app.models.generation import (
    GenerationOutputSpec,
    GenerationReferenceAsset,
    GenerationReferenceRole,
    GenerationReferenceTransformation,
    GenerationRequest,
    GenerationType,
)

from app.models.prompt import (
    EpisodeProductionPrompts,
    ProductionPrompt,
    PromptReferenceUsage,
)


class GenerationRequestCompiler:
    """
    Converts provider-agnostic production prompts into
    provider-agnostic generation requests.

    This compiler is the boundary between the prompt pipeline
    and the generation execution subsystem.

    Responsibilities:

    - create one KEYFRAME request per ProductionPrompt
    - preserve episode and shot lineage
    - forward image and negative prompts
    - forward resolved physical reference assets
    - apply shot-specific reference usage semantics
    - define provider-agnostic output requirements

    This compiler must not:

    - call generation providers
    - perform asset resolution
    - perform asset validation
    - implement retry behavior
    - make creative approval decisions
    - infer story-specific behavior from asset names
    """

    def __init__(
        self,
        default_width: int = 1024,
        default_height: int = 1024,
        default_aspect_ratio: str = "1:1",
        default_output_format: str = "png",
    ):

        if default_width < 1:

            raise ValueError(
                "default_width must be at least 1."
            )

        if default_height < 1:

            raise ValueError(
                "default_height must be at least 1."
            )

        if not default_aspect_ratio.strip():

            raise ValueError(
                "default_aspect_ratio cannot be empty."
            )

        if not default_output_format.strip():

            raise ValueError(
                "default_output_format cannot be empty."
            )

        self.output_spec = (
            GenerationOutputSpec(
                width=default_width,
                height=default_height,
                aspect_ratio=(
                    default_aspect_ratio
                ),
                output_format=(
                    default_output_format
                ),
            )
        )

    # ================================================================
    # COMPILE EPISODE
    # ================================================================

    def compile(
        self,
        prompts: EpisodeProductionPrompts,
    ) -> List[
        GenerationRequest
    ]:
        """
        Compile all shot prompts in one episode into KEYFRAME
        generation requests.
        """

        requests = []

        for scene in prompts.scenes:

            for prompt in scene.prompts:

                requests.append(
                    self.compile_prompt(
                        episode_id=(
                            prompts.episode_id
                        ),
                        prompt=prompt,
                    )
                )

        return requests

    # ================================================================
    # COMPILE ONE PROMPT
    # ================================================================

    def compile_prompt(
        self,
        episode_id: str,
        prompt: ProductionPrompt,
    ) -> GenerationRequest:

        if not episode_id.strip():

            raise ValueError(
                "episode_id cannot be empty."
            )

        if not prompt.shot_id.strip():

            raise ValueError(
                "ProductionPrompt shot_id "
                "cannot be empty."
            )

        if not prompt.image_prompt.strip():

            raise ValueError(
                "ProductionPrompt image_prompt "
                "cannot be empty."
            )

        reference_assets = (
            self._compile_reference_assets(
                prompt
            )
        )

        request_id = (
            self._request_id(
                episode_id=episode_id,
                shot_id=prompt.shot_id,
            )
        )

        return (
            GenerationRequest(
                request_id=request_id,
                episode_id=episode_id,
                shot_id=prompt.shot_id,
                generation_type=(
                    GenerationType.KEYFRAME
                ),
                prompt=(
                    prompt.image_prompt
                ),
                negative_prompt=(
                    prompt.negative_prompt
                ),
                reference_assets=(
                    reference_assets
                ),
                output=(
                    self.output_spec.model_copy(
                        deep=True
                    )
                ),
                metadata={
                    "scene_number": str(
                        prompt.scene_number
                    ),
                    "duration_seconds": str(
                        prompt.duration_seconds
                    ),
                    "source": (
                        "PRODUCTION_PROMPTS"
                    ),
                },
            )
        )

    # ================================================================
    # REFERENCE ASSETS
    # ================================================================

    def _compile_reference_assets(
        self,
        prompt: ProductionPrompt,
    ) -> List[
        GenerationReferenceAsset
    ]:

        references = []

        usage_map = (
            self._reference_usage_map(
                prompt
            )
        )

        for asset in prompt.assets:

            reference_path = (
                asset.reference_path
            )

            # --------------------------------------------------------
            # Generation providers can only consume physical
            # references.
            #
            # Logical unresolved assets remain an upstream concern
            # and must not be invented here.
            # --------------------------------------------------------

            if (
                reference_path is None
                or
                not reference_path.strip()
            ):

                continue

            usage = (
                usage_map.get(
                    asset.asset_id
                )
            )

            reference_kwargs = {}

            if usage is not None:

                reference_kwargs = (
                    self._compile_reference_usage(
                        usage=usage,
                        expected_entity_id=(
                            asset.entity_id
                        ),
                    )
                )

            references.append(
                GenerationReferenceAsset(
                    asset_id=(
                        asset.asset_id
                    ),
                    entity_id=(
                        asset.entity_id
                    ),
                    asset_type=(
                        asset.asset_type
                    ),
                    name=(
                        asset.name
                    ),
                    reference_path=(
                        reference_path
                    ),
                    purpose=(
                        asset.purpose
                    ),
                    required=(
                        asset.required
                    ),
                    master_reference_required=(
                        asset.master_reference_required
                    ),
                    **reference_kwargs,
                )
            )

        return references

    # ================================================================
    # REFERENCE USAGE
    # ================================================================

    def _reference_usage_map(
        self,
        prompt: ProductionPrompt,
    ) -> Dict[
        str,
        PromptReferenceUsage
    ]:
        """
        Build a deterministic asset_id -> usage map.

        Duplicate usage declarations are rejected because two
        contradictory semantic policies for the same physical
        reference would make generation behavior ambiguous.
        """

        usage_map = {}

        for usage in (
            prompt.reference_usages
        ):

            if (
                usage.asset_id
                in usage_map
            ):

                raise ValueError(
                    "Duplicate reference usage for asset_id "
                    f"'{usage.asset_id}'."
                )

            usage_map[
                usage.asset_id
            ] = usage

        return usage_map

    def _compile_reference_usage(
        self,
        usage: PromptReferenceUsage,
        expected_entity_id: str,
    ) -> dict:
        """
        Convert provider-agnostic prompt-layer reference semantics
        into the canonical generation-domain contract.

        No provider-specific behavior is introduced here.
        """

        if (
            usage.entity_id
            != expected_entity_id
        ):

            raise ValueError(
                "Reference usage entity mismatch for asset_id "
                f"'{usage.asset_id}'. "
                f"Expected entity_id '{expected_entity_id}', "
                f"received '{usage.entity_id}'."
            )

        role = (
            self._parse_reference_role(
                usage.reference_role
            )
        )

        transformations = [
            self._parse_reference_transformation(
                value
            )
            for value in (
                usage.allowed_transformations
            )
        ]

        return {
            "reference_role": (
                role
            ),
            "preserve_attributes": (
                list(
                    usage.preserve_attributes
                )
            ),
            "allowed_transformations": (
                transformations
            ),
            "usage_instruction": (
                usage.usage_instruction
            ),
        }

    def _parse_reference_role(
        self,
        value: str,
    ) -> GenerationReferenceRole:
        """
        Parse a prompt-layer role into the generation-domain enum.
        """

        normalized = (
            value
            .strip()
            .upper()
        )

        if not normalized:

            raise ValueError(
                "reference_role cannot be empty."
            )

        try:

            return (
                GenerationReferenceRole(
                    normalized
                )
            )

        except ValueError as exc:

            raise ValueError(
                "Unsupported reference_role "
                f"'{value}'."
            ) from exc

    def _parse_reference_transformation(
        self,
        value: str,
    ) -> GenerationReferenceTransformation:
        """
        Parse a prompt-layer transformation into the canonical
        generation-domain enum.
        """

        normalized = (
            value
            .strip()
            .upper()
        )

        if not normalized:

            raise ValueError(
                "Reference transformation cannot be empty."
            )

        try:

            return (
                GenerationReferenceTransformation(
                    normalized
                )
            )

        except ValueError as exc:

            raise ValueError(
                "Unsupported reference transformation "
                f"'{value}'."
            ) from exc

    # ================================================================
    # REQUEST ID
    # ================================================================

    def _request_id(
        self,
        episode_id: str,
        shot_id: str,
    ) -> str:
        """
        Build a deterministic request ID.

        Recompiling the same episode/shot therefore produces the
        same logical generation request identifier.
        """

        return (
            f"GEN_REQ_"
            f"{episode_id}_"
            f"{shot_id}"
        )