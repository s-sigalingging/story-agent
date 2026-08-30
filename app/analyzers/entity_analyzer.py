from typing import Dict, List, Optional

from app.models.analysis import (
    EpisodePropAnalysis,
)

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

    Responsibilities
    ----------------
    1. Register and resolve explicitly declared episode entities.
    2. Accept resolved semantic prop analysis from PropAnalyzer.
    3. Register validated inferred props into WorldRegistry.
    4. Resolve every scene entity into stable engine-facing IDs.

        Example:

        A character name
        ->
        stable character entity ID

        A resolved prop name
        ->
        stable prop entity ID
    Important architectural rule
    ----------------------------
    EntityAnalyzer does NOT infer props itself.

    Prop inference belongs to PropAnalyzer.

    EntityAnalyzer only consumes already-resolved semantic prop results.
    This keeps entity identity separate from semantic interpretation.

    The analyzer contains no story-specific entity names.
    """

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze(
        self,
        episode: Episode,
        registry: Optional[
            WorldRegistry
        ] = None,
        prop_analysis: Optional[
            EpisodePropAnalysis
        ] = None,
    ) -> EpisodeEntityAnalysis:

        if registry is None:
            registry = WorldRegistry()

        # ============================================================
        # 1. REGISTER EXPLICIT EPISODE ENTITIES
        # ============================================================

        registry.ingest_episode(
            episode
        )

        # ============================================================
        # 2. BUILD RESOLVED PROP MAP
        # ============================================================

        resolved_prop_map = (
            self._build_resolved_prop_map(
                episode=episode,
                prop_analysis=prop_analysis,
            )
        )

        # ============================================================
        # 3. REGISTER RESOLVED PROPS
        # ============================================================

        self._register_resolved_props(
            registry=registry,
            resolved_prop_map=(
                resolved_prop_map
            ),
        )

        # ============================================================
        # 4. RESOLVE SCENE ENTITIES
        # ============================================================

        scene_results = []

        for scene in episode.scenes:

            # --------------------------------------------------------
            # CHARACTERS
            # --------------------------------------------------------

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

            # --------------------------------------------------------
            # LOCATION
            # --------------------------------------------------------

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

            # --------------------------------------------------------
            # PROPS
            # --------------------------------------------------------

            prop_ids = []

            resolved_prop_names = (
                resolved_prop_map.get(
                    scene.scene_number,
                    [],
                )
            )

            for prop_name in (
                resolved_prop_names
            ):

                prop = (
                    registry.resolve_prop(
                        prop_name
                    )
                )

                if prop:

                    prop_ids.append(
                        prop.entity_id
                    )

            # --------------------------------------------------------
            # RESULT
            # --------------------------------------------------------

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

        # ============================================================
        # 5. EPISODE RESULT
        # ============================================================

        return EpisodeEntityAnalysis(
            status="PASSED",
            episode_id=(
                episode.episode_id
            ),
            scenes=scene_results,
            registry=registry.snapshot(),
        )

    # ================================================================
    # PROP RESOLUTION
    # ================================================================

    def _build_resolved_prop_map(
        self,
        episode: Episode,
        prop_analysis: Optional[
            EpisodePropAnalysis
        ],
    ) -> Dict[
        int,
        List[str],
    ]:
        """
        Build the authoritative prop list for every scene.

        Without PropAnalyzer output:
            use explicit scene.props only.

        With PropAnalyzer output:
            use PropAnalyzer.resolved_props.

        Explicit props are always preserved as a safety invariant.

        This means EntityAnalyzer remains backward compatible with
        callers that have not yet integrated PropAnalyzer.
        """

        result: Dict[
            int,
            List[str],
        ] = {}

        prop_analysis_map = {}

        if prop_analysis is not None:

            prop_analysis_map = {
                item.scene_number: item
                for item
                in prop_analysis.scenes
            }

        for scene in episode.scenes:

            prop_names = list(
                scene.props
            )

            analyzed_scene = (
                prop_analysis_map.get(
                    scene.scene_number
                )
            )

            if analyzed_scene is not None:

                prop_names.extend(
                    analyzed_scene.resolved_props
                )

            result[
                scene.scene_number
            ] = self._deduplicate_names(
                prop_names
            )

        return result

    def _register_resolved_props(
        self,
        registry: WorldRegistry,
        resolved_prop_map: Dict[
            int,
            List[str],
        ],
    ) -> None:
        """
        Register validated resolved props into the canonical registry.

        WorldRegistry itself remains semantic-agnostic.

        It does not need to know whether a prop was:
        - explicitly authored
        - visually inferred
        - discovered by another future analyzer

        It simply receives an already-resolved entity name.
        """

        for prop_names in (
            resolved_prop_map.values()
        ):

            for prop_name in prop_names:

                if not prop_name.strip():
                    continue

                registry.register_prop(
                    prop_name
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

    def _deduplicate_names(
        self,
        values: List[str],
    ) -> List[str]:

        result = []

        seen = set()

        for value in values:

            cleaned = (
                value.strip()
            )

            if not cleaned:
                continue

            key = (
                cleaned.lower()
            )

            if key in seen:
                continue

            seen.add(key)

            result.append(
                cleaned
            )

        return result