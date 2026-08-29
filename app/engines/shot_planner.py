from typing import Dict, List, Optional

from app.engines.shot_grammar import (
    ShotGrammar,
    ShotGrammarBeat,
)

from app.models.analysis import (
    ProductionBeatIntent,
    SceneProductionIntent,
)

from app.models.episode import (
    Scene,
)

from app.models.production import (
    CameraPlan,
    CharacterAction,
    PropAction,
    ShotPlan,
)

from app.models.scene_analysis import (
    SceneAnalysis,
)

from app.models.state import (
    SceneState,
)


class ShotPlanner:
    """
    Generic deterministic shot planner.

    ProductionIntent decides WHAT should happen.

    ShotGrammar decides HOW each beat is generally filmed.

    ShotPlanner combines both with:
    - scene duration
    - scene state
    - camera intent
    - dialogue

    The planner contains no story-specific knowledge.
    """

    def __init__(
        self,
        grammar: ShotGrammar | None = None,
    ):

        self.grammar = (
            grammar
            or ShotGrammar()
        )

    # ================================================================
    # PUBLIC API
    # ================================================================

    def create_shots(
        self,
        episode_id: str,
        scene: Scene,
        analysis: SceneAnalysis,
        intent: SceneProductionIntent,
        scene_state: SceneState,
    ) -> List[ShotPlan]:

        beats = list(
            intent.beats
        )

        if not beats:

            beats = [
                ProductionBeatIntent(
                    beat_type="PRIMARY_ACTION",
                    purpose=(
                        "Present the primary "
                        "narrative action."
                    ),
                    primary_subject_id=(
                        intent.primary_subject_id
                    ),
                    supporting_subject_ids=(
                        intent.supporting_subject_ids
                    ),
                    important_prop_ids=(
                        intent.important_prop_ids
                    ),
                )
            ]

        beats = (
            self._limit_beats_for_duration(
                beats=beats,
                total_duration=(
                    scene.duration_seconds
                ),
            )
        )

        durations = (
            self._allocate_durations(
                total_duration=(
                    scene.duration_seconds
                ),
                beats=beats,
            )
        )

        dialogue_map = (
            self._allocate_scene_dialogue(
                dialogue=(
                    scene.dialogue
                ),
                beats=(
                    beats
                ),
            )
        )

        shots: List[
            ShotPlan
        ] = []

        for index, beat_intent in enumerate(
            beats,
            start=1,
        ):

            grammar_beat = (
                self.grammar.get_beat(
                    beat_intent.beat_type
                )
            )

            characters = (
                self._select_characters(
                    beat_intent=(
                        beat_intent
                    ),
                    grammar_beat=(
                        grammar_beat
                    ),
                    scene_state=(
                        scene_state
                    ),
                )
            )

            props = (
                self._select_props(
                    beat_intent=(
                        beat_intent
                    ),
                    grammar_beat=(
                        grammar_beat
                    ),
                    scene_state=(
                        scene_state
                    ),
                )
            )

            shot = ShotPlan(
                shot_id=self._shot_id(
                    episode_id=(
                        episode_id
                    ),
                    scene_number=(
                        scene.scene_number
                    ),
                    shot_number=(
                        index
                    ),
                ),
                scene_number=(
                    scene.scene_number
                ),
                duration_seconds=(
                    durations[
                        index - 1
                    ]
                ),
                purpose=(
                    beat_intent.purpose
                ),
                characters=(
                    characters
                ),
                props=(
                    props
                ),
                camera=(
                    self._build_camera(
                        grammar_beat=(
                            grammar_beat
                        ),
                        analysis=(
                            analysis
                        ),
                        beat_intent=(
                            beat_intent
                        ),
                    )
                ),
                character_actions=(
                    self._build_character_actions(
                        character_ids=(
                            characters
                        ),
                        grammar_beat=(
                            grammar_beat
                        ),
                        beat_intent=(
                            beat_intent
                        ),
                    )
                ),
                prop_actions=(
                    self._build_prop_actions(
                        prop_ids=(
                            props
                        ),
                        beat_intent=(
                            beat_intent
                        ),
                    )
                ),
                visual_constraints=(
                    self._build_constraints(
                        analysis=(
                            analysis
                        ),
                        scene_state=(
                            scene_state
                        ),
                    )
                ),
                dialogue=(
                    dialogue_map.get(
                        index
                    )
                ),
            )

            shots.append(
                shot
            )

        return shots

    # ================================================================
    # BEAT LIMITING
    # ================================================================

    def _limit_beats_for_duration(
        self,
        beats: List[
            ProductionBeatIntent
        ],
        total_duration: int,
    ) -> List[
        ProductionBeatIntent
    ]:

        if total_duration <= 6:

            return [
                beats[0]
            ]

        if (
            total_duration <= 10
            and
            len(beats) > 2
        ):

            return [
                beats[0],
                beats[-1],
            ]

        return beats

    # ================================================================
    # CHARACTER SELECTION
    # ================================================================

    def _select_characters(
        self,
        beat_intent: ProductionBeatIntent,
        grammar_beat: ShotGrammarBeat,
        scene_state: SceneState,
    ) -> List[str]:

        selected = []

        active = set(
            scene_state.active_characters
        )

        if (
            grammar_beat.use_primary_subject
            and
            beat_intent.primary_subject_id
            and
            beat_intent.primary_subject_id
            in active
        ):

            selected.append(
                beat_intent.primary_subject_id
            )

        if (
            grammar_beat
            .use_supporting_subjects
        ):

            for entity_id in (
                beat_intent
                .supporting_subject_ids
            ):

                if (
                    entity_id in active
                    and
                    entity_id not in selected
                ):

                    selected.append(
                        entity_id
                    )

        if (
            not selected
            and
            (
                grammar_beat
                .use_primary_subject
                or
                grammar_beat
                .use_supporting_subjects
            )
        ):

            selected = list(
                scene_state
                .active_characters
            )

        return selected

    # ================================================================
    # PROP SELECTION
    # ================================================================

    def _select_props(
        self,
        beat_intent: ProductionBeatIntent,
        grammar_beat: ShotGrammarBeat,
        scene_state: SceneState,
    ) -> List[str]:

        if (
            not grammar_beat
            .use_important_props
        ):

            return []

        active = set(
            scene_state.active_props
        )

        return [
            entity_id
            for entity_id
            in (
                beat_intent
                .important_prop_ids
            )
            if entity_id in active
        ]

    # ================================================================
    # CAMERA
    # ================================================================

    def _build_camera(
        self,
        grammar_beat: ShotGrammarBeat,
        analysis: SceneAnalysis,
        beat_intent: ProductionBeatIntent,
    ) -> CameraPlan:

        movement = (
            grammar_beat
            .camera_movement
        )

        if (
            analysis.camera.movement
            and
            analysis.camera.movement
            not in {
                "STATIC",
                "UNSPECIFIED",
            }
        ):

            movement = (
                analysis.camera
                .movement
            )

        framing = (
            grammar_beat
            .framing
        )

        if (
            analysis.camera.framing
            and
            analysis.camera.framing
            != "UNSPECIFIED"
            and
            beat_intent.beat_type
            not in {
                "PROP_REVEAL",
                "REACTION",
            }
        ):

            framing = (
                analysis.camera
                .framing
            )

        return CameraPlan(
            shot_type=(
                grammar_beat
                .shot_type
            ),
            camera_movement=(
                movement
            ),
            framing=(
                framing
            ),
            composition=(
                self._build_composition(
                    beat_intent=(
                        beat_intent
                    ),
                    analysis=(
                        analysis
                    ),
                )
            ),
        )

    def _build_composition(
        self,
        beat_intent: ProductionBeatIntent,
        analysis: SceneAnalysis,
    ) -> str:

        beat_type = (
            beat_intent
            .beat_type
            .upper()
        )

        if (
            beat_type
            == "PROP_REVEAL"
            and
            beat_intent
            .important_prop_ids
        ):

            return (
                "Keep the important prop clearly readable "
                "while preserving enough surrounding context."
            )

        if (
            beat_type
            == "REACTION"
            and
            beat_intent
            .primary_subject_id
        ):

            return (
                "Keep the primary subject visually dominant "
                "while preserving continuity with the previous beat."
            )

        if (
            beat_intent
            .primary_subject_id
        ):

            return (
                "Keep the primary subject visually clear "
                "while preserving relevant scene context."
            )

        if (
            len(
                beat_intent
                .supporting_subject_ids
            )
            > 1
        ):

            return (
                "Maintain a clear spatial relationship "
                "between the active characters."
            )

        if analysis.character_ids:

            return (
                "Keep the active characters visually readable "
                "within the established environment."
            )

        if (
            beat_intent
            .important_prop_ids
        ):

            return (
                "Keep the important prop visually clear "
                "within the established environment."
            )

        return (
            "Maintain a clear view of the primary "
            "narrative action and environment."
        )

    # ================================================================
    # CHARACTER ACTIONS
    # ================================================================

    def _build_character_actions(
        self,
        character_ids: List[str],
        grammar_beat: ShotGrammarBeat,
        beat_intent: ProductionBeatIntent,
    ) -> List[
        CharacterAction
    ]:

        actions = []

        for entity_id in character_ids:

            action = (
                grammar_beat
                .character_action
            )

            if (
                beat_intent
                .beat_type
                .upper()
                == "REACTION"
            ):

                action = (
                    "REACT_TO_"
                    + self._reaction_context(
                        beat_intent
                    )
                )

            actions.append(
                CharacterAction(
                    entity_id=(
                        entity_id
                    ),
                    action=(
                        action
                    ),
                    gesture=(
                        grammar_beat
                        .gesture
                    ),
                    facial_movement=(
                        grammar_beat
                        .facial_movement
                    ),
                )
            )

        return actions

    def _reaction_context(
        self,
        beat_intent: ProductionBeatIntent,
    ) -> str:

        purpose = (
            beat_intent
            .purpose
            .lower()
        )

        if "discovery" in purpose:
            return "DISCOVERY"

        if "revelation" in purpose:
            return "REVELATION"

        if "conflict" in purpose:
            return "CONFLICT"

        return "EVENT"

    # ================================================================
    # PROP ACTIONS
    # ================================================================

    def _build_prop_actions(
        self,
        prop_ids: List[str],
        beat_intent: ProductionBeatIntent,
    ) -> List[
        PropAction
    ]:

        actions = []

        for entity_id in prop_ids:

            if (
                beat_intent
                .beat_type
                .upper()
                == "PROP_REVEAL"
            ):

                action = (
                    "PRESENT_IMPORTANT_PROP"
                )

            else:

                action = (
                    "MAINTAIN_ESTABLISHED_STATE"
                )

            actions.append(
                PropAction(
                    entity_id=(
                        entity_id
                    ),
                    action=(
                        action
                    ),
                )
            )

        return actions

    # ================================================================
    # DIALOGUE
    # ================================================================

    def _allocate_scene_dialogue(
        self,
        dialogue: str,
        beats: List[
            ProductionBeatIntent
        ],
    ) -> Dict[
        int,
        Optional[str]
    ]:
        """
        Allocate scene dialogue to exactly one shot.

        Dialogue is never duplicated automatically.

        Actual sentence-level timing and speaker attribution can later
        replace this conservative allocation strategy.
        """

        allocation: Dict[
            int,
            Optional[str]
        ] = {
            index: None
            for index in range(
                1,
                len(beats) + 1
            )
        }

        cleaned = (
            dialogue.strip()
        )

        if not cleaned:
            return allocation

        preferred_types = [
            "REVEAL",
            "PRIMARY_ACTION",
            "PRESSURE",
            "ENGAGE",
            "ESTABLISH",
            "INVESTIGATION",
        ]

        for preferred_type in (
            preferred_types
        ):

            for index, beat in enumerate(
                beats,
                start=1,
            ):

                if (
                    beat.beat_type
                    .strip()
                    .upper()
                    == preferred_type
                ):

                    allocation[
                        index
                    ] = cleaned

                    return allocation

        if beats:

            allocation[
                len(beats)
            ] = cleaned

        return allocation

    # ================================================================
    # DURATIONS
    # ================================================================

    def _allocate_durations(
        self,
        total_duration: int,
        beats: List[
            ProductionBeatIntent
        ],
    ) -> List[int]:

        count = len(
            beats
        )

        if count <= 0:
            return []

        if count == 1:

            return [
                total_duration
            ]

        weights = []

        for beat in beats:

            emphasis = (
                beat.emphasis
                .strip()
                .upper()
            )

            if emphasis == "HIGH":

                weights.append(
                    2
                )

            else:

                weights.append(
                    1
                )

        weight_total = sum(
            weights
        )

        durations = []

        allocated = 0

        for weight in weights:

            value = max(
                1,
                int(
                    total_duration
                    * weight
                    / weight_total
                ),
            )

            durations.append(
                value
            )

            allocated += value

        difference = (
            total_duration
            - allocated
        )

        index = (
            len(durations)
            - 1
        )

        while difference != 0:

            if difference > 0:

                durations[
                    index
                ] += 1

                difference -= 1

            else:

                if (
                    durations[
                        index
                    ]
                    > 1
                ):

                    durations[
                        index
                    ] -= 1

                    difference += 1

            index -= 1

            if index < 0:

                index = (
                    len(durations)
                    - 1
                )

        return durations

    # ================================================================
    # CONSTRAINTS
    # ================================================================

    def _build_constraints(
        self,
        analysis: SceneAnalysis,
        scene_state: SceneState,
    ) -> List[str]:

        constraints = list(
            analysis
            .visual_constraints
        )

        if (
            scene_state
            .active_characters
        ):

            constraints.extend([
                (
                    "Preserve established character "
                    "identity and proportions."
                ),
                (
                    "Preserve established wardrobe "
                    "and physical condition."
                ),
                (
                    "Avoid unnecessary character movement."
                ),
            ])

        if scene_state.location:

            constraints.extend([
                (
                    "Preserve the established environment."
                ),
                (
                    "Do not arbitrarily change lighting, "
                    "weather, or time of day."
                ),
            ])

        if (
            scene_state
            .active_props
        ):

            constraints.extend([
                (
                    "Preserve established prop identity "
                    "and appearance."
                ),
                (
                    "Do not introduce unrelated props."
                ),
            ])

        constraints.extend([
            (
                "Do not introduce unrelated characters."
            ),
            (
                "Avoid unnecessary camera movement."
            ),
            (
                "Do not create artificial transitions "
                "inside the shot."
            ),
        ])

        return self._deduplicate(
            constraints
        )

    # ================================================================
    # SHOT ID
    # ================================================================

    def _shot_id(
        self,
        episode_id: str,
        scene_number: int,
        shot_number: int,
    ) -> str:

        normalized_episode_id = (
            episode_id
            .strip()
            .upper()
        )

        return (
            f"{normalized_episode_id}-"
            f"S{scene_number:02d}-"
            f"SHOT{shot_number:02d}"
        )

    # ================================================================
    # UTILITIES
    # ================================================================

    def _deduplicate(
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

            seen.add(
                key
            )

            result.append(
                cleaned
            )

        return result