from copy import deepcopy
from typing import Dict

from app.models.character_role import (
    EpisodeCharacterRoleAnalysis,
    SceneCharacterRoleAnalysis,
)

from app.models.prop_content import (
    EpisodePropContentAnalysis,
    ScenePropContentAnalysis,
)

from app.models.scene_analysis import (
    EpisodeSceneAnalysis,
    SceneAnalysis,
    SceneCharacterRole,
    ScenePropContent,
)


class SceneSemanticEnricher:
    """
    Merge specialized semantic analyses into the canonical
    EpisodeSceneAnalysis contract.

    Responsibilities
    ----------------
    - preserve base SceneAnalysis
    - attach character semantic roles
    - promote authoritative primary subjects
    - attach resolved prop-content semantics
    - avoid re-analyzing story text
    - avoid hidden mutation

    This component contains no story-specific knowledge.
    """

    # ================================================================
    # CHARACTER ROLE ENRICHMENT
    # ================================================================

    def enrich_character_roles(
        self,
        scene_analysis: EpisodeSceneAnalysis,
        character_role_analysis: EpisodeCharacterRoleAnalysis,
    ) -> EpisodeSceneAnalysis:

        role_map: Dict[
            int,
            SceneCharacterRoleAnalysis,
        ] = {
            scene.scene_number: scene
            for scene
            in character_role_analysis.scenes
        }

        enriched_scenes = []

        for scene in scene_analysis.scenes:

            role_scene = (
                role_map.get(
                    scene.scene_number
                )
            )

            enriched_scenes.append(
                self._enrich_character_scene(
                    scene=scene,
                    role_scene=(
                        role_scene
                    ),
                )
            )

        return EpisodeSceneAnalysis(
            status=(
                scene_analysis.status
            ),
            episode_id=(
                scene_analysis.episode_id
            ),
            scenes=(
                enriched_scenes
            ),
        )

    def _enrich_character_scene(
        self,
        scene: SceneAnalysis,
        role_scene: SceneCharacterRoleAnalysis | None,
    ) -> SceneAnalysis:

        if role_scene is None:

            return deepcopy(
                scene
            )

        data = (
            scene.model_dump()
        )

        data[
            "character_roles"
        ] = [
            SceneCharacterRole(
                entity_id=(
                    role.entity_id
                ),
                name=(
                    role.name
                ),
                role=(
                    role.role
                ),
                interaction=(
                    role.interaction
                ),
                confidence=(
                    role.confidence
                ),
                primary_candidate=(
                    role.primary_candidate
                ),
                evidence=(
                    role.evidence
                ),
            ).model_dump()
            for role
            in role_scene.characters
        ]

        if (
            role_scene.primary_subject_id
            is not None
        ):

            data[
                "primary_subject_id"
            ] = (
                role_scene
                .primary_subject_id
            )

            data[
                "primary_subject"
            ] = (
                role_scene
                .primary_subject_name
            )

        return SceneAnalysis(
            **data
        )

    # ================================================================
    # PROP CONTENT ENRICHMENT
    # ================================================================

    def enrich_prop_content(
        self,
        scene_analysis: EpisodeSceneAnalysis,
        prop_content_analysis: EpisodePropContentAnalysis,
    ) -> EpisodeSceneAnalysis:
        """
        Attach prop-content semantics to canonical SceneAnalysis.

        No prop is discovered here.

        Only already-resolved prop entities may receive content
        semantics.
        """

        prop_map: Dict[
            int,
            ScenePropContentAnalysis,
        ] = {
            scene.scene_number: scene
            for scene
            in prop_content_analysis.scenes
        }

        enriched_scenes = []

        for scene in scene_analysis.scenes:

            prop_scene = (
                prop_map.get(
                    scene.scene_number
                )
            )

            enriched_scenes.append(
                self._enrich_prop_scene(
                    scene=scene,
                    prop_scene=(
                        prop_scene
                    ),
                )
            )

        return EpisodeSceneAnalysis(
            status=(
                scene_analysis.status
            ),
            episode_id=(
                scene_analysis.episode_id
            ),
            scenes=(
                enriched_scenes
            ),
        )

    def _enrich_prop_scene(
        self,
        scene: SceneAnalysis,
        prop_scene: ScenePropContentAnalysis | None,
    ) -> SceneAnalysis:

        if prop_scene is None:

            return deepcopy(
                scene
            )

        data = (
            scene.model_dump()
        )

        active_prop_ids = set(
            scene.prop_ids
        )

        data[
            "prop_content"
        ] = [
            ScenePropContent(
                entity_id=(
                    prop.entity_id
                ),
                name=(
                    prop.name
                ),
                content_modalities=(
                    list(
                        prop.content_modalities
                    )
                ),
                text_sensitive=(
                    prop.text_sensitive
                ),
                readability_required=(
                    prop.readability_required
                ),
                visual_detail_sensitive=(
                    prop.visual_detail_sensitive
                ),
                confidence=(
                    prop.confidence
                ),
                evidence=(
                    list(
                        prop.evidence
                    )
                ),
            ).model_dump()
            for prop
            in prop_scene.props
            if (
                prop.entity_id
                in active_prop_ids
            )
        ]

        return SceneAnalysis(
            **data
        )