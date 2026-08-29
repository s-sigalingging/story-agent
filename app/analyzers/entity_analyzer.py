from typing import Optional

from app.models.episode import Episode
from app.models.world import (
    EpisodeEntityAnalysis,
    SceneEntityAnalysis,
)
from app.world.registry import (
    WorldRegistry,
)


class EntityAnalyzer:
    """
    Resolves story-facing entity names into stable engine-facing IDs.

    Example:

        Alice Chen
            ->
        CHAR_ALICE_CHEN

    The analyzer contains no story-specific entity names.
    """

    def analyze(
        self,
        episode: Episode,
        registry: Optional[
            WorldRegistry
        ] = None,
    ) -> EpisodeEntityAnalysis:

        if registry is None:
            registry = WorldRegistry()

        registry.ingest_episode(
            episode
        )

        scene_results = []

        for scene in episode.scenes:

            character_ids = []

            for character_name in (
                scene.characters
            ):

                character = (
                    registry.resolve_character(
                        character_name
                    )
                )

                if character:
                    character_ids.append(
                        character.entity_id
                    )

            location_id = None

            if scene.location.strip():

                location = (
                    registry.resolve_location(
                        scene.location
                    )
                )

                if location:
                    location_id = (
                        location.entity_id
                    )

            prop_ids = []

            for prop_name in scene.props:

                prop = registry.resolve_prop(
                    prop_name
                )

                if prop:
                    prop_ids.append(
                        prop.entity_id
                    )

            scene_results.append(
                SceneEntityAnalysis(
                    scene_number=(
                        scene.scene_number
                    ),
                    character_ids=(
                        self._deduplicate(
                            character_ids
                        )
                    ),
                    location_id=(
                        location_id
                    ),
                    prop_ids=(
                        self._deduplicate(
                            prop_ids
                        )
                    ),
                )
            )

        return EpisodeEntityAnalysis(
            status="PASSED",
            episode_id=episode.episode_id,
            scenes=scene_results,
            registry=registry.snapshot(),
        )

    # ================================================================
    # UTILITIES
    # ================================================================

    def _deduplicate(
        self,
        values: list,
    ) -> list:

        result = []
        seen = set()

        for value in values:

            if value in seen:
                continue

            seen.add(value)
            result.append(value)

        return result