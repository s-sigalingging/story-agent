from copy import deepcopy
from typing import Dict, List, Optional

from app.models.continuity import (
    CharacterContinuityState,
    EpisodeContinuity,
    LocationContinuityState,
    PropContinuityState,
)
from app.models.episode import Episode
from app.models.state import (
    CharacterState,
    EpisodeState,
    LocationState,
    PropState,
    SceneState,
    WorldStateSnapshot,
)


class StateManager:
    """
    Converts continuity analysis into production state.

    Responsibilities
    ----------------
    - accept optional persistent world state from a previous episode
    - inherit known entity state
    - apply current episode continuity state
    - build per-scene production state
    - produce a new final world state

    This manager contains no story-specific knowledge.
    """

    # ================================================================
    # PUBLIC API
    # ================================================================

    def build_episode_state(
        self,
        episode: Episode,
        continuity: EpisodeContinuity,
        initial_world_state: Optional[
            WorldStateSnapshot
        ] = None,
    ) -> EpisodeState:

        inherited_world_state = (
            initial_world_state is not None
        )

        source_episode_id = None

        if initial_world_state:
            source_episode_id = (
                initial_world_state
                .last_episode_id
            )

        # ============================================================
        # START FROM EXISTING WORLD STATE
        # ============================================================

        characters: Dict[
            str,
            CharacterState
        ] = {}

        locations: Dict[
            str,
            LocationState
        ] = {}

        props: Dict[
            str,
            PropState
        ] = {}

        if initial_world_state:

            characters = deepcopy(
                initial_world_state.characters
            )

            locations = deepcopy(
                initial_world_state.locations
            )

            props = deepcopy(
                initial_world_state.props
            )

        scene_states: Dict[
            int,
            SceneState
        ] = {}

        # ============================================================
        # PROCESS SCENES
        # ============================================================

        for continuity_scene in (
            continuity.scenes
        ):

            scene_characters: Dict[
                str,
                CharacterState
            ] = {}

            scene_props: Dict[
                str,
                PropState
            ] = {}

            # ========================================================
            # CHARACTERS
            # ========================================================

            for continuity_character in (
                continuity_scene
                .character_states
            ):

                entity_id = (
                    continuity_character
                    .entity_id
                )

                previous = (
                    characters.get(
                        entity_id
                    )
                )

                character_state = (
                    self._build_character_state(
                        continuity_state=(
                            continuity_character
                        ),
                        previous_state=(
                            previous
                        ),
                    )
                )

                characters[
                    entity_id
                ] = deepcopy(
                    character_state
                )

                scene_characters[
                    entity_id
                ] = deepcopy(
                    character_state
                )

            # ========================================================
            # LOCATION
            # ========================================================

            scene_location = None

            if (
                continuity_scene
                .location_state
                is not None
            ):

                continuity_location = (
                    continuity_scene
                    .location_state
                )

                entity_id = (
                    continuity_location
                    .entity_id
                )

                previous_location = (
                    locations.get(
                        entity_id
                    )
                )

                location_state = (
                    self._build_location_state(
                        continuity_state=(
                            continuity_location
                        ),
                        previous_state=(
                            previous_location
                        ),
                    )
                )

                locations[
                    entity_id
                ] = deepcopy(
                    location_state
                )

                scene_location = deepcopy(
                    location_state
                )

            # ========================================================
            # PROPS
            # ========================================================

            for continuity_prop in (
                continuity_scene
                .prop_states
            ):

                entity_id = (
                    continuity_prop
                    .entity_id
                )

                previous_prop = (
                    props.get(
                        entity_id
                    )
                )

                prop_state = (
                    self._build_prop_state(
                        continuity_state=(
                            continuity_prop
                        ),
                        previous_state=(
                            previous_prop
                        ),
                    )
                )

                props[
                    entity_id
                ] = deepcopy(
                    prop_state
                )

                scene_props[
                    entity_id
                ] = deepcopy(
                    prop_state
                )

            # ========================================================
            # SCENE STATE
            # ========================================================

            scene_state = SceneState(
                scene_number=(
                    continuity_scene
                    .scene_number
                ),
                characters=(
                    scene_characters
                ),
                location=(
                    scene_location
                ),
                props=(
                    scene_props
                ),
                active_characters=list(
                    scene_characters.keys()
                ),
                active_props=list(
                    scene_props.keys()
                ),
            )

            scene_states[
                continuity_scene
                .scene_number
            ] = scene_state

        # ============================================================
        # CURRENT SCENE
        # ============================================================

        current_scene = 0

        if episode.scenes:
            current_scene = (
                episode.scenes[-1]
                .scene_number
            )

        # ============================================================
        # FINAL WORLD STATE
        # ============================================================

        final_world_state = (
            WorldStateSnapshot(
                version=1,
                last_episode_id=(
                    episode.episode_id
                ),
                characters=deepcopy(
                    characters
                ),
                locations=deepcopy(
                    locations
                ),
                props=deepcopy(
                    props
                ),
            )
        )

        # ============================================================
        # EPISODE STATE
        # ============================================================

        return EpisodeState(
            episode_id=(
                episode.episode_id
            ),
            title=(
                episode.title
            ),
            current_scene=(
                current_scene
            ),
            characters=(
                characters
            ),
            locations=(
                locations
            ),
            props=(
                props
            ),
            scene_states=(
                scene_states
            ),
            inherited_world_state=(
                inherited_world_state
            ),
            source_episode_id=(
                source_episode_id
            ),
            final_world_state=(
                final_world_state
            ),
        )

    # ================================================================
    # CHARACTER STATE
    # ================================================================

    def _build_character_state(
        self,
        continuity_state:
        CharacterContinuityState,
        previous_state: Optional[
            CharacterState
        ],
    ) -> CharacterState:

        if previous_state:

            result = deepcopy(
                previous_state
            )

        else:

            result = CharacterState(
                entity_id=(
                    continuity_state.entity_id
                ),
                name=(
                    continuity_state.name
                ),
            )

        result.entity_id = (
            continuity_state.entity_id
        )

        if continuity_state.name:
            result.name = (
                continuity_state.name
            )

        result.appearance = (
            self._prefer_known(
                continuity_state.appearance,
                result.appearance,
            )
        )

        result.wardrobe = (
            self._prefer_known(
                continuity_state.wardrobe,
                result.wardrobe,
            )
        )

        result.emotional_state = (
            self._prefer_known(
                continuity_state
                .emotional_state,
                result.emotional_state,
            )
        )

        result.physical_condition = (
            self._prefer_known(
                continuity_state
                .physical_condition,
                result.physical_condition,
            )
        )

        result.position = (
            self._prefer_known(
                continuity_state.position,
                result.position,
            )
        )

        result.notes = (
            self._merge_notes(
                result.notes,
                continuity_state.notes,
            )
        )

        return result

    # ================================================================
    # LOCATION STATE
    # ================================================================

    def _build_location_state(
        self,
        continuity_state:
        LocationContinuityState,
        previous_state: Optional[
            LocationState
        ],
    ) -> LocationState:

        if previous_state:

            result = deepcopy(
                previous_state
            )

        else:

            result = LocationState(
                entity_id=(
                    continuity_state.entity_id
                ),
                name=(
                    continuity_state.name
                ),
            )

        result.entity_id = (
            continuity_state.entity_id
        )

        if continuity_state.name:
            result.name = (
                continuity_state.name
            )

        result.time_of_day = (
            self._prefer_known(
                continuity_state.time_of_day,
                result.time_of_day,
            )
        )

        result.weather = (
            self._prefer_known(
                continuity_state.weather,
                result.weather,
            )
        )

        result.lighting = (
            self._prefer_known(
                continuity_state.lighting,
                result.lighting,
            )
        )

        result.atmosphere = (
            self._prefer_known(
                continuity_state.atmosphere,
                result.atmosphere,
            )
        )

        result.notes = (
            self._merge_notes(
                result.notes,
                continuity_state.notes,
            )
        )

        return result

    # ================================================================
    # PROP STATE
    # ================================================================

    def _build_prop_state(
        self,
        continuity_state:
        PropContinuityState,
        previous_state: Optional[
            PropState
        ],
    ) -> PropState:

        if previous_state:

            result = deepcopy(
                previous_state
            )

        else:

            result = PropState(
                entity_id=(
                    continuity_state.entity_id
                ),
                name=(
                    continuity_state.name
                ),
            )

        result.entity_id = (
            continuity_state.entity_id
        )

        if continuity_state.name:
            result.name = (
                continuity_state.name
            )

        result.appearance = (
            self._prefer_known(
                continuity_state.appearance,
                result.appearance,
            )
        )

        result.state = (
            self._prefer_known(
                continuity_state.condition,
                result.state,
            )
        )

        result.position = (
            self._prefer_known(
                continuity_state.position,
                result.position,
            )
        )

        if (
            continuity_state.holder_id
            is not None
        ):
            result.holder_id = (
                continuity_state.holder_id
            )

        result.notes = (
            self._merge_notes(
                result.notes,
                continuity_state.notes,
            )
        )

        return result

    # ================================================================
    # UTILITIES
    # ================================================================

    def _prefer_known(
        self,
        new_value: str,
        previous_value: str,
    ) -> str:

        if (
            new_value
            and
            new_value != "UNKNOWN"
        ):
            return new_value

        if previous_value:
            return previous_value

        return "UNKNOWN"

    def _merge_notes(
        self,
        existing: List[str],
        incoming: List[str],
    ) -> List[str]:

        result = []

        seen = set()

        for value in (
            list(existing)
            + list(incoming)
        ):

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

            seen.add(
                key
            )

            result.append(
                cleaned
            )

        return result