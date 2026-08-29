from typing import Dict, Optional

from app.analyzers.production_intent_analyzer import (
    ProductionIntentAnalyzer,
)

from app.analyzers.scene_analyzer import (
    SceneAnalyzer,
)

from app.engines.shot_planner import (
    ShotPlanner,
)

from app.models.analysis import (
    EpisodeProductionIntent,
    SceneProductionIntent,
)

from app.models.episode import (
    Episode,
)

from app.models.production import (
    ProductionPlan,
    SceneProductionPlan,
)

from app.models.scene_analysis import (
    EpisodeSceneAnalysis,
    SceneAnalysis,
)

from app.models.state import (
    EpisodeState,
)


class ProductionPlanner:
    """
    Generic production planner.

    Responsibilities
    ----------------
    - receive scene analysis
    - receive production intent
    - pass both to ShotPlanner
    - assemble SceneProductionPlan and ProductionPlan

    This class performs no story-specific shot design.
    """

    def __init__(
        self,
    ):

        self.scene_analyzer = (
            SceneAnalyzer()
        )

        self.production_intent_analyzer = (
            ProductionIntentAnalyzer()
        )

        self.shot_planner = (
            ShotPlanner()
        )

    # ================================================================
    # PUBLIC API
    # ================================================================

    def create_plan(
        self,
        episode: Episode,
        state: EpisodeState,
        scene_analysis: Optional[
            EpisodeSceneAnalysis
        ] = None,
        production_intent: Optional[
            EpisodeProductionIntent
        ] = None,
    ) -> ProductionPlan:

        # ============================================================
        # SCENE ANALYSIS
        # ============================================================

        if scene_analysis is None:

            scene_analysis = (
                self.scene_analyzer
                .analyze(
                    episode
                )
            )

        # ============================================================
        # PRODUCTION INTENT
        # ============================================================

        if production_intent is None:

            production_intent = (
                self.production_intent_analyzer
                .analyze(
                    episode=(
                        episode
                    ),
                    scene_analysis=(
                        scene_analysis
                    ),
                )
            )

        analysis_map: Dict[
            int,
            SceneAnalysis
        ] = {
            item.scene_number: item
            for item in (
                scene_analysis.scenes
            )
        }

        intent_map: Dict[
            int,
            SceneProductionIntent
        ] = {
            item.scene_number: item
            for item in (
                production_intent.scenes
            )
        }

        scenes = []

        # ============================================================
        # SCENE PLANNING
        # ============================================================

        for scene in episode.scenes:

            scene_state = (
                state.scene_states.get(
                    scene.scene_number
                )
            )

            if scene_state is None:
                raise ValueError(
                    "Scene state not found for "
                    f"scene {scene.scene_number}."
                )

            analysis = (
                analysis_map.get(
                    scene.scene_number
                )
            )

            if analysis is None:
                raise ValueError(
                    "Scene analysis not found for "
                    f"scene {scene.scene_number}."
                )

            intent = (
                intent_map.get(
                    scene.scene_number
                )
            )

            if intent is None:
                raise ValueError(
                    "Production intent not found for "
                    f"scene {scene.scene_number}."
                )

            shots = (
                self.shot_planner
                .create_shots(
                    episode_id=(
                        episode.episode_id
                    ),
                    scene=(
                        scene
                    ),
                    analysis=(
                        analysis
                    ),
                    intent=(
                        intent
                    ),
                    scene_state=(
                        scene_state
                    ),
                )
            )

            location_id = None

            if scene_state.location:

                location_id = (
                    scene_state
                    .location
                    .entity_id
                )

            scene_plan = (
                SceneProductionPlan(
                    scene_number=(
                        scene.scene_number
                    ),
                    duration_seconds=(
                        scene.duration_seconds
                    ),
                    location_id=(
                        location_id
                    ),
                    shot_count=(
                        len(shots)
                    ),
                    shots=(
                        shots
                    ),
                )
            )

            scenes.append(
                scene_plan
            )

        # ============================================================
        # FINAL PLAN
        # ============================================================

        return ProductionPlan(
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
                scenes
            ),
        )