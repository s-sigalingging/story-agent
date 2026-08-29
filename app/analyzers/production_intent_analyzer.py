from typing import List, Optional

from app.models.analysis import (
    EpisodeProductionIntent,
    ProductionBeatIntent,
    SceneProductionIntent,
)
from app.models.episode import Episode, Scene
from app.models.scene_analysis import (
    EpisodeSceneAnalysis,
    SceneAnalysis,
)


class ProductionIntentAnalyzer:
    """
    Generic production-intent analyzer.

    Responsibilities
    ----------------
    - identify primary/supporting subjects
    - identify important props
    - convert narrative function into dramatic production beats
    - provide structured creative intent to ShotPlanner

    This analyzer must not contain story-specific names or episode IDs.
    """

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze(
        self,
        episode: Episode,
        scene_analysis: EpisodeSceneAnalysis,
    ) -> EpisodeProductionIntent:

        analysis_map = {
            item.scene_number: item
            for item in scene_analysis.scenes
        }

        results = []

        for scene in episode.scenes:

            analysis = analysis_map.get(
                scene.scene_number
            )

            if analysis is None:
                continue

            results.append(
                self._analyze_scene(
                    scene=scene,
                    analysis=analysis,
                )
            )

        return EpisodeProductionIntent(
            status="PASSED",
            episode_id=episode.episode_id,
            scenes=results,
        )

    # ================================================================
    # SCENE
    # ================================================================

    def _analyze_scene(
        self,
        scene: Scene,
        analysis: SceneAnalysis,
    ) -> SceneProductionIntent:

        primary_subject_id = (
            self._resolve_primary_subject(
                analysis
            )
        )

        supporting_subject_ids = (
            self._resolve_supporting_subjects(
                analysis=analysis,
                primary_subject_id=(
                    primary_subject_id
                ),
            )
        )

        important_prop_ids = (
            self._resolve_important_props(
                analysis
            )
        )

        visual_priority = (
            self._resolve_visual_priority(
                analysis=analysis,
                important_prop_ids=(
                    important_prop_ids
                ),
            )
        )

        pacing = (
            self._resolve_pacing(
                scene=scene,
                analysis=analysis,
            )
        )

        beats = (
            self._build_beats(
                analysis=analysis,
                primary_subject_id=(
                    primary_subject_id
                ),
                supporting_subject_ids=(
                    supporting_subject_ids
                ),
                important_prop_ids=(
                    important_prop_ids
                ),
            )
        )

        return SceneProductionIntent(
            scene_number=(
                scene.scene_number
            ),
            narrative_function=(
                analysis.narrative_function
            ),
            primary_subject_id=(
                primary_subject_id
            ),
            supporting_subject_ids=(
                supporting_subject_ids
            ),
            important_prop_ids=(
                important_prop_ids
            ),
            dialogue_present=(
                bool(
                    scene.dialogue.strip()
                )
            ),
            visual_priority=(
                visual_priority
            ),
            pacing=(
                pacing
            ),
            beats=(
                beats
            ),
        )

    # ================================================================
    # SUBJECT RESOLUTION
    # ================================================================

    def _resolve_primary_subject(
        self,
        analysis: SceneAnalysis,
    ) -> Optional[str]:

        if (
            analysis.primary_subject_id
            is not None
        ):
            return (
                analysis.primary_subject_id
            )

        if len(
            analysis.character_ids
        ) == 1:
            return (
                analysis.character_ids[0]
            )

        # Conservative fallback:
        # do not guess primary subject in multi-character scenes.
        return None

    def _resolve_supporting_subjects(
        self,
        analysis: SceneAnalysis,
        primary_subject_id: Optional[str],
    ) -> List[str]:

        if not analysis.character_ids:
            return []

        if primary_subject_id is None:
            return list(
                analysis.character_ids
            )

        return [
            entity_id
            for entity_id
            in analysis.character_ids
            if entity_id
            != primary_subject_id
        ]

    # ================================================================
    # PROP RESOLUTION
    # ================================================================

    def _resolve_important_props(
        self,
        analysis: SceneAnalysis,
    ) -> List[str]:
        """
        For now, every explicitly declared prop is considered important.

        This is conservative and deterministic.

        Later, semantic scoring can distinguish:
        - background prop
        - handled prop
        - clue prop
        - hero prop
        """

        return list(
            analysis.prop_ids
        )

    # ================================================================
    # VISUAL PRIORITY
    # ================================================================

    def _resolve_visual_priority(
        self,
        analysis: SceneAnalysis,
        important_prop_ids: List[str],
    ) -> str:

        if (
            important_prop_ids
            and
            not analysis.character_ids
        ):
            return "PROP"

        if (
            important_prop_ids
            and
            analysis.character_ids
        ):
            return "CHARACTER_AND_PROP"

        if analysis.character_ids:
            return "CHARACTER"

        return "ENVIRONMENT"

    # ================================================================
    # PACING
    # ================================================================

    def _resolve_pacing(
        self,
        scene: Scene,
        analysis: SceneAnalysis,
    ) -> str:

        function = (
            analysis.narrative_function
            .strip()
            .upper()
        )

        if function in {
            "CONFRONTATION",
            "ESCALATION",
        }:
            return "TIGHT"

        if function in {
            "DISCOVERY",
            "REVELATION",
        }:
            return "CONTROLLED"

        if function in {
            "SETUP",
            "TRANSITION",
        }:
            return "SLOW"

        if (
            scene.duration_seconds
            <= 6
        ):
            return "TIGHT"

        return "MODERATE"

    # ================================================================
    # BEATS
    # ================================================================

    def _build_beats(
        self,
        analysis: SceneAnalysis,
        primary_subject_id: Optional[str],
        supporting_subject_ids: List[str],
        important_prop_ids: List[str],
    ) -> List[
        ProductionBeatIntent
    ]:

        function = (
            analysis.narrative_function
            .strip()
            .upper()
        )

        if function == "SETUP":

            return [
                ProductionBeatIntent(
                    beat_type="ESTABLISH",
                    purpose=(
                        "Establish the active subject "
                        "and environment."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="NORMAL",
                )
            ]

        if function == "DISCOVERY":

            beats = [
                ProductionBeatIntent(
                    beat_type="INVESTIGATION",
                    purpose=(
                        "Show the subject examining "
                        "or encountering new information."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="NORMAL",
                )
            ]

            if important_prop_ids:

                beats.append(
                    ProductionBeatIntent(
                        beat_type="PROP_REVEAL",
                        purpose=(
                            "Emphasize the important "
                            "prop or information."
                        ),
                        primary_subject_id=None,
                        supporting_subject_ids=[],
                        important_prop_ids=(
                            important_prop_ids
                        ),
                        emphasis="HIGH",
                    )
                )

            beats.append(
                ProductionBeatIntent(
                    beat_type="REACTION",
                    purpose=(
                        "Show the dramatic response "
                        "to the discovery."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="HIGH",
                )
            )

            return beats

        if function == "REVELATION":

            return [
                ProductionBeatIntent(
                    beat_type="REVEAL",
                    purpose=(
                        "Present the information "
                        "that changes understanding."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="HIGH",
                ),
                ProductionBeatIntent(
                    beat_type="REACTION",
                    purpose=(
                        "Hold on the consequence "
                        "of the revelation."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="HIGH",
                ),
            ]

        if function == "ESCALATION":

            return [
                ProductionBeatIntent(
                    beat_type="PRESSURE",
                    purpose=(
                        "Establish the rising pressure "
                        "or complication."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="NORMAL",
                ),
                ProductionBeatIntent(
                    beat_type="INTENSIFY",
                    purpose=(
                        "Increase the dramatic pressure."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="HIGH",
                ),
            ]

        if function == "CONFRONTATION":

            return [
                ProductionBeatIntent(
                    beat_type="ENGAGE",
                    purpose=(
                        "Establish the participants "
                        "and conflict."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="NORMAL",
                ),
                ProductionBeatIntent(
                    beat_type="REACTION",
                    purpose=(
                        "Emphasize the strongest "
                        "conflict response."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="HIGH",
                ),
            ]

        if function == "RESOLUTION":

            return [
                ProductionBeatIntent(
                    beat_type="RESOLVE",
                    purpose=(
                        "Present the resolved "
                        "narrative state."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="NORMAL",
                )
            ]

        if function == "TRANSITION":

            return [
                ProductionBeatIntent(
                    beat_type="TRANSITION",
                    purpose=(
                        "Connect the current state "
                        "to the next narrative beat."
                    ),
                    primary_subject_id=(
                        primary_subject_id
                    ),
                    supporting_subject_ids=(
                        supporting_subject_ids
                    ),
                    important_prop_ids=(
                        important_prop_ids
                    ),
                    emphasis="LOW",
                )
            ]

        return [
            ProductionBeatIntent(
                beat_type="PRIMARY_ACTION",
                purpose=(
                    "Present the primary "
                    "narrative action."
                ),
                primary_subject_id=(
                    primary_subject_id
                ),
                supporting_subject_ids=(
                    supporting_subject_ids
                ),
                important_prop_ids=(
                    important_prop_ids
                ),
                emphasis="NORMAL",
            )
        ]