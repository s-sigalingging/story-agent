from typing import List

from app.models.generation import (
    GenerationOutputSpec,
    GenerationReferenceAsset,
    GenerationRequest,
    GenerationType,
)

from app.models.prompt import (
    EpisodeProductionPrompts,
    ProductionPrompt,
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
    - define provider-agnostic output requirements

    This compiler must not:

    - call generation providers
    - perform asset resolution
    - perform asset validation
    - implement retry behavior
    - make creative approval decisions
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
                )
            )

        return references

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