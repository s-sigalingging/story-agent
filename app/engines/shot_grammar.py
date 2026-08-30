from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ShotGrammarBeat:
    """
    Deterministic cinematic treatment for one production beat.

    This object defines HOW a beat is generally filmed.

    Character-specific semantic performance is resolved later by
    ShotPlanner.

    This object must never contain:
    - story-specific character names
    - story-specific locations
    - story-specific props
    - episode IDs
    """

    beat_type: str

    shot_type: str

    camera_movement: str

    framing: str

    character_action: str

    gesture: str

    facial_movement: str

    use_primary_subject: bool = True

    use_supporting_subjects: bool = False

    use_important_props: bool = True


class ShotGrammar:
    """
    Generic cinematic grammar.

    ProductionIntent decides WHAT dramatic beat exists.

    ShotGrammar decides HOW that beat should generally be filmed.

    Scene-level semantic interactions may override generic character
    performance later inside ShotPlanner.
    """

    def __init__(
        self,
    ):

        self._beats: Dict[
            str,
            ShotGrammarBeat
        ] = {

            # ========================================================
            # ESTABLISH
            # ========================================================

            "ESTABLISH": ShotGrammarBeat(
                beat_type="ESTABLISH",
                shot_type="MEDIUM_WIDE",
                camera_movement=(
                    "STATIC_OR_SUBTLE_PUSH"
                ),
                framing=(
                    "CHARACTER_AND_ENVIRONMENT"
                ),
                character_action=(
                    "PERFORM_SCENE_ACTION"
                ),
                gesture=(
                    "SUBTLE_NATURAL_GESTURE"
                ),
                facial_movement=(
                    "CONTROLLED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),

            # ========================================================
            # PRIMARY ACTION
            # ========================================================

            "PRIMARY_ACTION": ShotGrammarBeat(
                beat_type="PRIMARY_ACTION",
                shot_type="MEDIUM",
                camera_movement=(
                    "STATIC_OR_SUBTLE_PUSH"
                ),
                framing=(
                    "CHARACTER_FOCUSED"
                ),
                character_action=(
                    "PERFORM_SCENE_ACTION"
                ),
                gesture=(
                    "SUBTLE_NATURAL_GESTURE"
                ),
                facial_movement=(
                    "CONTROLLED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),

            # ========================================================
            # INVESTIGATION
            # ========================================================

            "INVESTIGATION": ShotGrammarBeat(
                beat_type="INVESTIGATION",
                shot_type="MEDIUM",
                camera_movement=(
                    "STATIC_OR_SUBTLE_PUSH"
                ),
                framing=(
                    "SUBJECT_AND_CONTEXT"
                ),
                character_action=(
                    "INVESTIGATE"
                ),
                gesture=(
                    "CONTROLLED_INSPECTION"
                ),
                facial_movement=(
                    "FOCUSED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),

            # ========================================================
            # PROP REVEAL
            # ========================================================

            "PROP_REVEAL": ShotGrammarBeat(
                beat_type="PROP_REVEAL",
                shot_type="CLOSE_UP",
                camera_movement="STATIC",
                framing="PROP_FOCUSED",
                character_action="OBSERVE",
                gesture="MINIMAL_MOVEMENT",
                facial_movement=(
                    "CONTROLLED_EXPRESSION"
                ),
                use_primary_subject=False,
                use_supporting_subjects=False,
                use_important_props=True,
            ),

            # ========================================================
            # REVEAL
            # ========================================================

            "REVEAL": ShotGrammarBeat(
                beat_type="REVEAL",
                shot_type="MEDIUM",
                camera_movement=(
                    "STATIC_OR_SUBTLE_PUSH"
                ),
                framing=(
                    "NARRATIVE_FOCUSED"
                ),
                character_action=(
                    "PRESENT_OR_RECEIVE_INFORMATION"
                ),
                gesture=(
                    "MINIMAL_CONTROLLED_GESTURE"
                ),
                facial_movement=(
                    "FOCUSED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),

            # ========================================================
            # REACTION
            # ========================================================

            "REACTION": ShotGrammarBeat(
                beat_type="REACTION",
                shot_type="MEDIUM_CLOSE",
                camera_movement=(
                    "SUBTLE_PUSH_IN"
                ),
                framing=(
                    "SUBJECT_FOCUSED"
                ),
                character_action="REACT",
                gesture="MINIMAL_REACTION",
                facial_movement=(
                    "CONTROLLED_REALIZATION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=False,
                use_important_props=False,
            ),

            # ========================================================
            # PRESSURE
            # ========================================================

            "PRESSURE": ShotGrammarBeat(
                beat_type="PRESSURE",
                shot_type="MEDIUM",
                camera_movement="STATIC",
                framing=(
                    "CHARACTER_INTERACTION"
                ),
                character_action=(
                    "RESPOND_TO_PRESSURE"
                ),
                gesture=(
                    "CONTROLLED_MOVEMENT"
                ),
                facial_movement=(
                    "TENSE_CONTROLLED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),

            # ========================================================
            # INTENSIFY
            # ========================================================

            "INTENSIFY": ShotGrammarBeat(
                beat_type="INTENSIFY",
                shot_type="MEDIUM_CLOSE",
                camera_movement=(
                    "SUBTLE_PUSH_IN"
                ),
                framing=(
                    "SUBJECT_FOCUSED"
                ),
                character_action=(
                    "REACT_TO_ESCALATION"
                ),
                gesture="MINIMAL_REACTION",
                facial_movement=(
                    "HEIGHTENED_CONTROLLED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=False,
                use_important_props=True,
            ),

            # ========================================================
            # ENGAGE
            # ========================================================

            "ENGAGE": ShotGrammarBeat(
                beat_type="ENGAGE",
                shot_type="MEDIUM_TWO_SHOT",
                camera_movement="STATIC",
                framing=(
                    "CHARACTER_INTERACTION"
                ),
                character_action=(
                    "ENGAGE_IN_CONFLICT"
                ),
                gesture=(
                    "CONTROLLED_GESTURE"
                ),
                facial_movement=(
                    "TENSE_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),

            # ========================================================
            # RESOLVE
            # ========================================================

            "RESOLVE": ShotGrammarBeat(
                beat_type="RESOLVE",
                shot_type="MEDIUM",
                camera_movement="STATIC",
                framing=(
                    "CHARACTER_AND_ENVIRONMENT"
                ),
                character_action=(
                    "COMPLETE_SCENE_ACTION"
                ),
                gesture=(
                    "SUBTLE_NATURAL_GESTURE"
                ),
                facial_movement=(
                    "CONTROLLED_SETTLED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),

            # ========================================================
            # TRANSITION
            # ========================================================

            "TRANSITION": ShotGrammarBeat(
                beat_type="TRANSITION",
                shot_type="WIDE",
                camera_movement=(
                    "STATIC_OR_SUBTLE_MOVE"
                ),
                framing=(
                    "ENVIRONMENT_AND_SUBJECT"
                ),
                character_action=(
                    "PERFORM_TRANSITION_ACTION"
                ),
                gesture=(
                    "SUBTLE_NATURAL_GESTURE"
                ),
                facial_movement=(
                    "CONTROLLED_EXPRESSION"
                ),
                use_primary_subject=True,
                use_supporting_subjects=True,
                use_important_props=True,
            ),
        }

    # ================================================================
    # PUBLIC API
    # ================================================================

    def get_beat(
        self,
        beat_type: str,
    ) -> ShotGrammarBeat:

        normalized = (
            beat_type
            .strip()
            .upper()
        )

        return (
            self._beats.get(
                normalized,
                self._beats[
                    "PRIMARY_ACTION"
                ],
            )
        )