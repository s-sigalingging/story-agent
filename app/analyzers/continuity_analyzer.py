from copy import deepcopy
from typing import Dict, List, Optional

from app.analyzers.scene_analyzer import (
    SceneAnalyzer,
)
from app.models.continuity import (
    CharacterContinuityState,
    EpisodeContinuity,
    LocationContinuityState,
    PropContinuityState,
    SceneContinuity,
)
from app.models.episode import (
    Episode,
    Scene,
)
from app.models.scene_analysis import (
    SceneAnalysis,
)
from app.world.registry import (
    WorldRegistry,
)


class ContinuityAnalyzer:
    """
    Generic continuity analyzer.

    Responsibilities
    ----------------
    - inherit known state across scenes
    - update state only from explicit scene information
    - track characters, locations, and props by stable entity ID
    - preserve UNKNOWN when information is not established

    This analyzer must never contain knowledge about a specific
    character, location, prop, episode, or story world.
    """

    def __init__(
        self,
    ):

        self.scene_analyzer = (
            SceneAnalyzer()
        )

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze(
        self,
        episode: Episode,
        registry: Optional[
            WorldRegistry
        ] = None,
    ) -> EpisodeContinuity:

        scene_analysis_result = (
            self.scene_analyzer.analyze(
                episode=episode,
                registry=registry,
            )
        )

        scene_analysis_map = {
            item.scene_number: item
            for item in (
                scene_analysis_result.scenes
            )
        }

        character_states: Dict[
            str,
            CharacterContinuityState
        ] = {}

        location_states: Dict[
            str,
            LocationContinuityState
        ] = {}

        prop_states: Dict[
            str,
            PropContinuityState
        ] = {}

        scene_results: List[
            SceneContinuity
        ] = []

        for scene in episode.scenes:

            analysis = (
                scene_analysis_map.get(
                    scene.scene_number
                )
            )

            if analysis is None:
                continue

            scene_result = (
                self._analyze_scene(
                    scene=scene,
                    analysis=analysis,
                    character_states=(
                        character_states
                    ),
                    location_states=(
                        location_states
                    ),
                    prop_states=(
                        prop_states
                    ),
                )
            )

            scene_results.append(
                scene_result
            )

        return EpisodeContinuity(
            status="PASSED",
            episode_id=(
                episode.episode_id
            ),
            scenes=scene_results,
            final_character_states=(
                deepcopy(
                    character_states
                )
            ),
            final_location_states=(
                deepcopy(
                    location_states
                )
            ),
            final_prop_states=(
                deepcopy(
                    prop_states
                )
            ),
        )

    # ================================================================
    # SCENE
    # ================================================================

    def _analyze_scene(
        self,
        scene: Scene,
        analysis: SceneAnalysis,
        character_states: Dict[
            str,
            CharacterContinuityState
        ],
        location_states: Dict[
            str,
            LocationContinuityState
        ],
        prop_states: Dict[
            str,
            PropContinuityState
        ],
    ) -> SceneContinuity:

        inherited = False

        current_character_states: List[
            CharacterContinuityState
        ] = []

        current_prop_states: List[
            PropContinuityState
        ] = []

        # ============================================================
        # CHARACTERS
        # ============================================================

        for index, entity_id in enumerate(
            analysis.character_ids
        ):

            name = ""

            if index < len(
                analysis.characters
            ):
                name = (
                    analysis.characters[
                        index
                    ]
                )

            previous = (
                character_states.get(
                    entity_id
                )
            )

            if previous:
                state = deepcopy(
                    previous
                )
                inherited = True

            else:
                state = (
                    CharacterContinuityState(
                        entity_id=(
                            entity_id
                        ),
                        name=name,
                    )
                )

            if name:
                state.name = name

            if (
                analysis.emotional_state
                and
                analysis.emotional_state
                != "UNKNOWN"
            ):
                state.emotional_state = (
                    analysis.emotional_state
                )

            state.notes = (
                self._merge_notes(
                    state.notes,
                    self._scene_notes(
                        scene
                    ),
                )
            )

            character_states[
                entity_id
            ] = deepcopy(
                state
            )

            current_character_states.append(
                deepcopy(
                    state
                )
            )

        # ============================================================
        # LOCATION
        # ============================================================

        current_location_state = None

        if analysis.location_id:

            previous_location = (
                location_states.get(
                    analysis.location_id
                )
            )

            if previous_location:
                location_state = (
                    deepcopy(
                        previous_location
                    )
                )
                inherited = True

            else:
                location_state = (
                    LocationContinuityState(
                        entity_id=(
                            analysis.location_id
                        ),
                        name=(
                            analysis.location
                        ),
                    )
                )

            if analysis.location:
                location_state.name = (
                    analysis.location
                )

            environment = (
                analysis.environment
            )

            location_state.time_of_day = (
                self._prefer_known(
                    new_value=(
                        environment.time_of_day
                    ),
                    previous_value=(
                        location_state.time_of_day
                    ),
                )
            )

            location_state.weather = (
                self._prefer_known(
                    new_value=(
                        environment.weather
                    ),
                    previous_value=(
                        location_state.weather
                    ),
                )
            )

            location_state.lighting = (
                self._prefer_known(
                    new_value=(
                        environment.lighting
                    ),
                    previous_value=(
                        location_state.lighting
                    ),
                )
            )

            location_state.atmosphere = (
                self._prefer_known(
                    new_value=(
                        environment.atmosphere
                    ),
                    previous_value=(
                        location_state.atmosphere
                    ),
                )
            )

            location_state.notes = (
                self._merge_notes(
                    location_state.notes,
                    self._scene_notes(
                        scene
                    ),
                )
            )

            location_states[
                analysis.location_id
            ] = deepcopy(
                location_state
            )

            current_location_state = (
                deepcopy(
                    location_state
                )
            )

        # ============================================================
        # PROPS
        # ============================================================

        for index, entity_id in enumerate(
            analysis.prop_ids
        ):

            name = ""

            if index < len(
                analysis.props
            ):
                name = (
                    analysis.props[
                        index
                    ]
                )

            previous_prop = (
                prop_states.get(
                    entity_id
                )
            )

            if previous_prop:
                prop_state = (
                    deepcopy(
                        previous_prop
                    )
                )
                inherited = True

            else:
                prop_state = (
                    PropContinuityState(
                        entity_id=(
                            entity_id
                        ),
                        name=name,
                    )
                )

            if name:
                prop_state.name = name

            prop_state.notes = (
                self._merge_notes(
                    prop_state.notes,
                    self._scene_notes(
                        scene
                    ),
                )
            )

            prop_states[
                entity_id
            ] = deepcopy(
                prop_state
            )

            current_prop_states.append(
                deepcopy(
                    prop_state
                )
            )

        return SceneContinuity(
            scene_number=(
                scene.scene_number
            ),
            inherited_from_previous_scene=(
                inherited
            ),
            character_states=(
                current_character_states
            ),
            location_state=(
                current_location_state
            ),
            prop_states=(
                current_prop_states
            ),
            continuity_notes=(
                self._scene_notes(
                    scene
                )
            ),
        )

    # ================================================================
    # NOTES
    # ================================================================

    def _scene_notes(
        self,
        scene: Scene,
    ) -> List[str]:

        notes = []

        continuity_note = (
            scene.continuity_notes
            .strip()
        )

        if continuity_note:
            notes.append(
                continuity_note
            )

        return notes

    # ================================================================
    # STATE MERGING
    # ================================================================

    def _prefer_known(
        self,
        new_value: str,
        previous_value: str,
    ) -> str:
        """
        Prefer newly established information.

        UNKNOWN must never overwrite a previously known state.
        """

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