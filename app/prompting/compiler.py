from typing import Dict, List, Optional

from app.models.asset import (
    AssetPlan,
    AssetReference,
)

from app.models.episode import (
    Episode,
)

from app.models.prompt import (
    EpisodeProductionPrompts,
    ProductionPrompt,
    PromptAssetReference,
    PromptCameraContext,
    PromptCharacterPerformance,
    PromptEnvironmentContext,
    PromptPropPerformance,
    PromptStyleContext,
    SceneProductionPrompts,
    ShotPromptContext,
)

from app.models.scene_analysis import (
    EpisodeSceneAnalysis,
    SceneAnalysis,
)

from app.models.state import (
    EpisodeState,
    SceneState,
)

from app.prompting.image_prompt_builder import (
    ImagePromptBuilder,
)

from app.prompting.video_prompt_builder import (
    VideoPromptBuilder,
)

from app.prompting.negative_prompt_builder import (
    NegativePromptBuilder,
)


class PromptCompiler:
    """
    Compiles provider-agnostic production prompts.

    Responsibilities
    ----------------
    - assemble ShotPromptContext
    - resolve human-readable entity names
    - resolve environment continuity state
    - resolve shot-level assets
    - call image/video/negative builders
    - return EpisodeProductionPrompts

    The compiler performs no story-specific creative reasoning.
    """

    def __init__(
        self,
        image_builder: Optional[
            ImagePromptBuilder
        ] = None,
        video_builder: Optional[
            VideoPromptBuilder
        ] = None,
        negative_builder: Optional[
            NegativePromptBuilder
        ] = None,
    ):

        self.image_builder = (
            image_builder
            or ImagePromptBuilder()
        )

        self.video_builder = (
            video_builder
            or VideoPromptBuilder()
        )

        self.negative_builder = (
            negative_builder
            or NegativePromptBuilder()
        )

    # ================================================================
    # PUBLIC API
    # ================================================================

    def compile(
        self,
        episode: Episode,
        scene_analysis: EpisodeSceneAnalysis,
        episode_state: EpisodeState,
        production_execution: dict,
        asset_plan: AssetPlan,
    ) -> EpisodeProductionPrompts:

        analysis_map: Dict[
            int,
            SceneAnalysis
        ] = {
            item.scene_number: item
            for item in (
                scene_analysis.scenes
            )
        }

        scene_prompt_packages: List[
            SceneProductionPrompts
        ] = []

        total_shots = 0

        execution_scenes = (
            production_execution.get(
                "scenes",
                []
            )
        )

        for execution_scene in (
            execution_scenes
        ):

            scene_number = (
                execution_scene.get(
                    "scene_number"
                )
            )

            if scene_number is None:
                continue

            analysis = (
                analysis_map.get(
                    scene_number
                )
            )

            scene_state = (
                episode_state
                .scene_states
                .get(
                    scene_number
                )
            )

            prompts = []

            for shot in (
                execution_scene.get(
                    "shots",
                    []
                )
            ):

                context = (
                    self._build_context(
                        episode=episode,
                        shot=shot,
                        analysis=analysis,
                        scene_state=(
                            scene_state
                        ),
                        asset_plan=(
                            asset_plan
                        ),
                    )
                )

                production_prompt = (
                    ProductionPrompt(
                        shot_id=(
                            context.shot_id
                        ),
                        scene_number=(
                            context
                            .scene_number
                        ),
                        duration_seconds=(
                            context
                            .duration_seconds
                        ),
                        image_prompt=(
                            self.image_builder
                            .build(
                                context
                            )
                        ),
                        video_prompt=(
                            self.video_builder
                            .build(
                                context
                            )
                        ),
                        negative_prompt=(
                            self.negative_builder
                            .build(
                                context
                            )
                        ),
                        assets=(
                            context.assets
                        ),
                        dialogue=(
                            context.dialogue
                        ),
                    )
                )

                prompts.append(
                    production_prompt
                )

                total_shots += 1

            scene_prompt_packages.append(
                SceneProductionPrompts(
                    scene_number=(
                        scene_number
                    ),
                    prompts=(
                        prompts
                    ),
                )
            )

        return EpisodeProductionPrompts(
            episode_id=(
                episode.episode_id
            ),
            title=(
                episode.title
            ),
            target_duration_seconds=(
                episode
                .target_duration_seconds
            ),
            scenes=(
                scene_prompt_packages
            ),
            total_shots=(
                total_shots
            ),
        )

    # ================================================================
    # CONTEXT BUILDING
    # ================================================================

    def _build_context(
        self,
        episode: Episode,
        shot: dict,
        analysis: Optional[
            SceneAnalysis
        ],
        scene_state: Optional[
            SceneState
        ],
        asset_plan: AssetPlan,
    ) -> ShotPromptContext:

        shot_id = (
            shot.get(
                "shot_id",
                ""
            )
        )

        scene_number = (
            shot.get(
                "scene_number",
                0
            )
        )

        duration_seconds = (
            shot.get(
                "duration_seconds",
                0
            )
        )

        purpose = (
            shot.get(
                "purpose",
                ""
            )
        )

        style = (
            PromptStyleContext(
                tone=(
                    episode.tone
                ),
                visual_style=(
                    episode
                    .visual_style
                ),
            )
        )

        camera = (
            self._build_camera_context(
                shot
            )
        )

        environment = (
            self._build_environment_context(
                analysis=analysis,
                scene_state=scene_state,
            )
        )

        characters = (
            self._build_character_context(
                shot=shot,
                scene_state=scene_state,
            )
        )

        props = (
            self._build_prop_context(
                shot=shot,
                scene_state=scene_state,
            )
        )

        assets = (
            self._build_asset_context(
                shot_id=shot_id,
                shot=shot,
                asset_plan=asset_plan,
            )
        )

        continuity_constraints = (
            list(
                shot.get(
                    "visual_constraints",
                    []
                )
            )
        )

        dialogue = (
            shot.get(
                "dialogue"
            )
        )

        metadata = (
            self._build_metadata(
                shot=shot,
                analysis=analysis,
            )
        )

        return ShotPromptContext(
            shot_id=(
                shot_id
            ),
            scene_number=(
                scene_number
            ),
            duration_seconds=(
                duration_seconds
            ),
            purpose=(
                purpose
            ),
            style=(
                style
            ),
            camera=(
                camera
            ),
            environment=(
                environment
            ),
            characters=(
                characters
            ),
            props=(
                props
            ),
            continuity_constraints=(
                continuity_constraints
            ),
            assets=(
                assets
            ),
            dialogue=(
                dialogue
            ),
            metadata=(
                metadata
            ),
        )

    # ================================================================
    # CAMERA
    # ================================================================

    def _build_camera_context(
        self,
        shot: dict,
    ) -> PromptCameraContext:

        camera = (
            shot.get(
                "camera",
                {}
            )
            or {}
        )

        return PromptCameraContext(
            shot_type=(
                camera.get(
                    "shot_type",
                    "UNSPECIFIED"
                )
            ),
            camera_movement=(
                camera.get(
                    "camera_movement",
                    "STATIC"
                )
            ),
            framing=(
                camera.get(
                    "framing",
                    "UNSPECIFIED"
                )
            ),
            composition=(
                camera.get(
                    "composition",
                    ""
                )
            ),
        )

    # ================================================================
    # ENVIRONMENT
    # ================================================================

    def _build_environment_context(
        self,
        analysis: Optional[
            SceneAnalysis
        ],
        scene_state: Optional[
            SceneState
        ],
    ) -> PromptEnvironmentContext:

        location_id = None
        location_name = ""

        time_of_day = "UNKNOWN"
        weather = "UNKNOWN"
        lighting = "UNKNOWN"
        atmosphere = "UNKNOWN"

        if (
            scene_state
            and
            scene_state.location
        ):

            location = (
                scene_state.location
            )

            location_id = (
                location.entity_id
            )

            location_name = (
                location.name
            )

            time_of_day = (
                location.time_of_day
            )

            weather = (
                location.weather
            )

            lighting = (
                location.lighting
            )

            atmosphere = (
                location.atmosphere
            )

        elif analysis:

            location_id = (
                analysis.location_id
            )

            location_name = (
                analysis.location
            )

            time_of_day = (
                analysis
                .environment
                .time_of_day
            )

            weather = (
                analysis
                .environment
                .weather
            )

            lighting = (
                analysis
                .environment
                .lighting
            )

            atmosphere = (
                analysis
                .environment
                .atmosphere
            )

        return PromptEnvironmentContext(
            location_id=(
                location_id
            ),
            location_name=(
                location_name
            ),
            time_of_day=(
                time_of_day
            ),
            weather=(
                weather
            ),
            lighting=(
                lighting
            ),
            atmosphere=(
                atmosphere
            ),
        )

    # ================================================================
    # CHARACTERS
    # ================================================================

    def _build_character_context(
        self,
        shot: dict,
        scene_state: Optional[
            SceneState
        ],
    ) -> List[
        PromptCharacterPerformance
    ]:

        actions = {
            item.get(
                "entity_id"
            ): item
            for item
            in (
                shot.get(
                    "character_actions",
                    []
                )
            )
            if item.get(
                "entity_id"
            )
        }

        result = []

        for entity_id in (
            shot.get(
                "characters",
                []
            )
        ):

            action = (
                actions.get(
                    entity_id,
                    {}
                )
            )

            name = (
                self._character_name(
                    entity_id=entity_id,
                    scene_state=scene_state,
                )
            )

            result.append(
                PromptCharacterPerformance(
                    entity_id=(
                        entity_id
                    ),
                    name=(
                        name
                    ),
                    action=(
                        action.get(
                            "action",
                            ""
                        )
                    ),
                    gesture=(
                        action.get(
                            "gesture",
                            ""
                        )
                    ),
                    facial_movement=(
                        action.get(
                            "facial_movement",
                            ""
                        )
                    ),
                )
            )

        return result

    def _character_name(
        self,
        entity_id: str,
        scene_state: Optional[
            SceneState
        ],
    ) -> str:

        if not scene_state:
            return ""

        state = (
            scene_state
            .characters
            .get(
                entity_id
            )
        )

        if not state:
            return ""

        return (
            state.name
        )

    # ================================================================
    # PROPS
    # ================================================================

    def _build_prop_context(
        self,
        shot: dict,
        scene_state: Optional[
            SceneState
        ],
    ) -> List[
        PromptPropPerformance
    ]:

        actions = {
            item.get(
                "entity_id"
            ): item
            for item
            in (
                shot.get(
                    "prop_actions",
                    []
                )
            )
            if item.get(
                "entity_id"
            )
        }

        result = []

        for entity_id in (
            shot.get(
                "props",
                []
            )
        ):

            action = (
                actions.get(
                    entity_id,
                    {}
                )
            )

            name = (
                self._prop_name(
                    entity_id=entity_id,
                    scene_state=scene_state,
                )
            )

            result.append(
                PromptPropPerformance(
                    entity_id=(
                        entity_id
                    ),
                    name=(
                        name
                    ),
                    action=(
                        action.get(
                            "action",
                            ""
                        )
                    ),
                )
            )

        return result

    def _prop_name(
        self,
        entity_id: str,
        scene_state: Optional[
            SceneState
        ],
    ) -> str:

        if not scene_state:
            return ""

        state = (
            scene_state
            .props
            .get(
                entity_id
            )
        )

        if not state:
            return ""

        return (
            state.name
        )

    # ================================================================
    # ASSETS
    # ================================================================

    def _build_asset_context(
        self,
        shot_id: str,
        shot: dict,
        asset_plan: AssetPlan,
    ) -> List[
        PromptAssetReference
    ]:

        shot_asset_ids = {
            asset.get(
                "asset_id"
            )
            for asset
            in (
                shot.get(
                    "assets",
                    []
                )
            )
            if asset.get(
                "asset_id"
            )
        }

        references = []

        for asset in (
            asset_plan.assets
        ):

            if (
                shot_asset_ids
                and
                asset.asset_id
                not in shot_asset_ids
            ):
                continue

            if (
                not shot_asset_ids
                and
                not self._asset_is_relevant_to_shot(
                    asset=asset,
                    shot=shot,
                )
            ):
                continue

            references.append(
                self._convert_asset(
                    asset
                )
            )

        return references

    def _asset_is_relevant_to_shot(
        self,
        asset: AssetReference,
        shot: dict,
    ) -> bool:

        entity_ids = set(
            shot.get(
                "characters",
                []
            )
            + shot.get(
                "props",
                []
            )
        )

        location_id = (
            shot.get(
                "location_id"
            )
        )

        if location_id:
            entity_ids.add(
                location_id
            )

        return (
            asset.entity_id
            in entity_ids
        )

    def _convert_asset(
        self,
        asset: AssetReference,
    ) -> PromptAssetReference:

        return PromptAssetReference(
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
            purpose=(
                asset.purpose
            ),
            reference_path=(
                asset.reference_path
            ),
            required=(
                asset.required
            ),
            master_reference_required=(
                asset
                .master_reference_required
            ),
        )

    # ================================================================
    # METADATA
    # ================================================================

    def _build_metadata(
        self,
        shot: dict,
        analysis: Optional[
            SceneAnalysis
        ],
    ) -> Dict[str, str]:

        metadata = {}

        if analysis:

            metadata[
                "narrative_function"
            ] = (
                analysis
                .narrative_function
            )

            metadata[
                "emotional_state"
            ] = (
                analysis
                .emotional_state
            )

        # Text-sensitive content should eventually be supplied
        # explicitly by upstream semantic analysis.
        # Do not infer it from story-specific keywords here.

        return metadata