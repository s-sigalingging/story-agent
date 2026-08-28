from app.models.episode import Episode

from app.models.state import EpisodeState

from app.models.production import (
    ProductionPlan,
    SceneProductionPlan,
    ShotPlan,
    CameraPlan,
    CharacterAction,
    PropAction
)


class ProductionPlanner:

    def create_plan(
        self,
        episode: Episode,
        state: EpisodeState
    ) -> ProductionPlan:

        scenes = []

        for scene in episode.scenes:

            scene_state = state.scene_states[
                scene.scene_number
            ]

            shots = self.create_shots(
                scene,
                scene_state
            )

            scene_plan = SceneProductionPlan(
                scene_number=scene.scene_number,

                duration_seconds=scene.duration_seconds,

                location_id=scene_state.location.entity_id,

                shot_count=len(shots),

                shots=shots
            )

            scenes.append(scene_plan)

        return ProductionPlan(
            episode_id=episode.episode_id,

            title=episode.title,

            target_duration_seconds=(
                episode.target_duration_seconds
            ),

            scenes=scenes
        )

    # ================================================================
    # SHOT PLANNING
    # ================================================================

    def create_shots(
        self,
        scene,
        scene_state
    ):

        scene_number = scene.scene_number

        # ------------------------------------------------------------
        # Scene 1
        # ------------------------------------------------------------

        if scene_number == 1:

            return self.create_scene_1_shots(
                scene,
                scene_state
            )

        # ------------------------------------------------------------
        # Scene 2
        # ------------------------------------------------------------

        if scene_number == 2:

            return self.create_scene_2_shots(
                scene,
                scene_state
            )

        # ------------------------------------------------------------
        # Scene 3
        # ------------------------------------------------------------

        if scene_number == 3:

            return self.create_scene_3_shots(
                scene,
                scene_state
            )

        # ------------------------------------------------------------
        # Scene 4
        # ------------------------------------------------------------

        if scene_number == 4:

            return self.create_scene_4_shots(
                scene,
                scene_state
            )

        # ------------------------------------------------------------
        # Generic fallback
        # ------------------------------------------------------------

        return self.create_generic_shots(
            scene,
            scene_state
        )

    # ================================================================
    # SCENE 1
    # ================================================================

    def create_scene_1_shots(
        self,
        scene,
        scene_state
    ):

        character_id = (
            scene_state.active_characters[0]
        )

        return [

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    1
                ),

                scene_number=scene.scene_number,

                duration_seconds=scene.duration_seconds,

                purpose=(
                    "Establish Sam Bell and "
                    "the old docks."
                ),

                characters=[
                    character_id
                ],

                props=scene_state.active_props,

                camera=CameraPlan(
                    shot_type="MEDIUM_WIDE",

                    camera_movement="VERY_SLOW_PUSH_IN",

                    framing="CHARACTER_AND_ENVIRONMENT",

                    composition=(
                        "Sam Bell remains the primary "
                        "subject while the old docks "
                        "remain clearly visible."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=character_id,

                        action=(
                            "WORK_AT_DOCK"
                        ),

                        gesture=(
                            "SUBTLE_WORKING_GESTURE"
                        ),

                        facial_movement=(
                            "UNEASY_CONTROLLED_EXPRESSION"
                        )
                    )
                ],

                prop_actions=[],

                visual_constraints=[
                    "Preserve Sam Bell's established appearance.",
                    "Preserve Sam Bell's established wardrobe.",
                    "Keep the docks visually quiet.",
                    "Maintain cold and damp pre-dawn conditions.",
                    "Avoid unnecessary character movement.",
                    "Do not introduce additional characters.",
                    "Do not introduce unrelated props.",
                    "Avoid dramatic camera movement."
                ],

                dialogue=scene.dialogue
            )

        ]

    # ================================================================
    # SCENE 2
    # ================================================================

    def create_scene_2_shots(
        self,
        scene,
        scene_state
    ):

        character_id = (
            scene_state.active_characters[0]
        )

        first_duration = 4

        second_duration = (
            scene.duration_seconds -
            first_duration
        )

        return [

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    1
                ),

                scene_number=scene.scene_number,

                duration_seconds=first_duration,

                purpose=(
                    "Continue Sam Bell's work "
                    "at the dock edge."
                ),

                characters=[
                    character_id
                ],

                props=scene_state.active_props,

                camera=CameraPlan(
                    shot_type="MEDIUM",

                    camera_movement="STATIC",

                    framing="CHARACTER_FOCUSED",

                    composition=(
                        "Sam Bell remains centered "
                        "with the dock edge visible."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=character_id,

                        action="CONTINUE_WORKING",

                        gesture="SUBTLE_NATURAL_GESTURE",

                        facial_movement=(
                            "UNEASY_CONTROLLED_EXPRESSION"
                        )
                    )
                ],

                prop_actions=[],

                visual_constraints=[
                    "Maintain wardrobe continuity.",
                    "Maintain cold and damp weather.",
                    "Maintain early morning lighting.",
                    "Do not introduce new characters.",
                    "Avoid unnecessary head movement."
                ],

                dialogue=None
            ),

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    2
                ),

                scene_number=scene.scene_number,

                duration_seconds=second_duration,

                purpose=(
                    "Emphasize Sam Bell's awareness "
                    "that something is wrong."
                ),

                characters=[
                    character_id
                ],

                props=scene_state.active_props,

                camera=CameraPlan(
                    shot_type="MEDIUM_CLOSE",

                    camera_movement="SUBTLE_PUSH_IN",

                    framing="CHARACTER_FOCUSED",

                    composition=(
                        "Sam Bell dominates the frame "
                        "while the dock remains recognizable."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=character_id,

                        action="OBSERVE_DOCK_AREA",

                        gesture="MINIMAL_MOVEMENT",

                        facial_movement=(
                            "UNEASY_LOOK"
                        )
                    )
                ],

                prop_actions=[],

                visual_constraints=[
                    "Do not turn Sam fully toward camera.",
                    "Avoid exaggerated acting.",
                    "Maintain visual continuity with Shot 01.",
                    "Keep environment subdued.",
                    "Do not introduce additional workers."
                ],

                dialogue=scene.dialogue
            )

        ]

    # ================================================================
    # SCENE 3
    # ================================================================

    def create_scene_3_shots(
        self,
        scene,
        scene_state
    ):

        character_id = (
            scene_state.active_characters[0]
        )

        first_duration = 6

        second_duration = (
            scene.duration_seconds -
            first_duration
        )

        return [

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    1
                ),

                scene_number=scene.scene_number,

                duration_seconds=first_duration,

                purpose=(
                    "Establish Sterling examining "
                    "the case at the old docks."
                ),

                characters=[
                    character_id
                ],

                props=scene_state.active_props,

                camera=CameraPlan(
                    shot_type="MEDIUM",

                    camera_movement="STATIC",

                    framing="CHARACTER_FOCUSED",

                    composition=(
                        "Sterling is framed against "
                        "the quiet old docks."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=character_id,

                        action="EXAMINE_CASE",

                        gesture="CONTROLLED_INSPECTION",

                        facial_movement=(
                            "CALM_NEUTRAL_EXPRESSION"
                        )
                    )
                ],

                prop_actions=[],

                visual_constraints=[
                    "Maintain Sterling's established appearance.",
                    "Maintain Sterling's established wardrobe.",
                    "Maintain cold damp pre-dawn conditions.",
                    "Avoid exaggerated acting.",
                    "Keep the scene subdued."
                ],

                dialogue=None
            ),

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    2
                ),

                scene_number=scene.scene_number,

                duration_seconds=second_duration,

                purpose=(
                    "Deliver the apparent conclusion "
                    "that Samuel Bell's case is closed."
                ),

                characters=[
                    character_id
                ],

                props=scene_state.active_props,

                camera=CameraPlan(
                    shot_type="MEDIUM_CLOSE",

                    camera_movement="SUBTLE_SLOW_PUSH_IN",

                    framing="CHARACTER_FOCUSED",

                    composition=(
                        "Sterling remains the sole "
                        "visual focus."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=character_id,

                        action="DELIVER_CASE_CONCLUSION",

                        gesture="MINIMAL_HAND_MOVEMENT",

                        facial_movement=(
                            "CALM_CONTROLLED_EXPRESSION"
                        )
                    )
                ],

                prop_actions=[],

                visual_constraints=[
                    "Do not introduce Julian yet.",
                    "Do not introduce Ren yet.",
                    "Avoid melodramatic performance.",
                    "Maintain muted lighting.",
                    "Keep the old docks visually consistent."
                ],

                dialogue=scene.dialogue
            )

        ]

    # ================================================================
    # SCENE 4
    # ================================================================

    def create_scene_4_shots(
        self,
        scene,
        scene_state
    ):

        julian_id = self.find_character(
            scene_state,
            "Julian"
        )

        ren_id = self.find_character(
            scene_state,
            "Ren"
        )

        document_id = self.find_prop(
            scene_state,
            "Catalog document"
        )

        case_records_id = self.find_prop(
            scene_state,
            "Case records"
        )

        desk_id = self.find_prop(
            scene_state,
            "Desk"
        )

        return [

            # --------------------------------------------------------
            # SHOT 01 — ESTABLISH JULIAN
            # --------------------------------------------------------

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    1
                ),

                scene_number=scene.scene_number,

                duration_seconds=5,

                purpose=(
                    "Establish Julian investigating "
                    "the case in his office."
                ),

                characters=[
                    julian_id
                ],

                props=[
                    desk_id,
                    case_records_id
                ],

                camera=CameraPlan(
                    shot_type="MEDIUM",

                    camera_movement="STATIC",

                    framing="CHARACTER_FOCUSED",

                    composition=(
                        "Julian remains the primary "
                        "subject at his desk."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=julian_id,

                        action="STUDY_CASE_RECORDS",

                        gesture="MINIMAL_HAND_MOVEMENT",

                        facial_movement=(
                            "FOCUSED_EXPRESSION"
                        )
                    )
                ],

                prop_actions=[],

                visual_constraints=[
                    "Camera remains on Julian.",
                    "Do not reveal document details yet.",
                    "Maintain low desk-lamp lighting.",
                    "Maintain dark investigative atmosphere.",
                    "Avoid unnecessary head turns.",
                    "Do not introduce rain.",
                    "Preserve established office environment."
                ],

                dialogue=None
            ),

            # --------------------------------------------------------
            # SHOT 02 — DOCUMENT INVESTIGATION
            # --------------------------------------------------------

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    2
                ),

                scene_number=scene.scene_number,

                duration_seconds=5,

                purpose=(
                    "Show Julian beginning to examine "
                    "the suspicious catalog document."
                ),

                characters=[
                    julian_id
                ],

                props=[
                    document_id,
                    desk_id
                ],

                camera=CameraPlan(
                    shot_type="MEDIUM",

                    camera_movement="SUBTLE_CONTROLLED_PUSH",

                    framing="OVER_SHOULDER",

                    composition=(
                        "Julian remains visible while "
                        "the document becomes partially visible."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=julian_id,

                        action="EXAMINE_DOCUMENT",

                        gesture="CAREFULLY_HANDLING_DOCUMENT",

                        facial_movement=(
                            "FOCUSED_SUSPICIOUS_EXPRESSION"
                        )
                    )
                ],

                prop_actions=[
                    PropAction(
                        entity_id=document_id,

                        action="REMAINS_ON_DESK"
                    )
                ],

                visual_constraints=[
                    "Do not reveal the key catalog code yet.",
                    "Do not zoom excessively close.",
                    "Document must remain visually consistent.",
                    "Avoid document flipping animation.",
                    "Keep Julian's movement subtle.",
                    "Maintain low desk-lamp lighting."
                ],

                dialogue=None
            ),

            # --------------------------------------------------------
            # SHOT 03 — CATALOG CODE REVEAL
            # --------------------------------------------------------

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    3
                ),

                scene_number=scene.scene_number,

                duration_seconds=5,

                purpose=(
                    "Reveal the catalog code that "
                    "changes Julian's understanding."
                ),

                characters=[],

                props=[
                    document_id
                ],

                camera=CameraPlan(
                    shot_type="CLOSE_UP",

                    camera_movement="STATIC",

                    framing="DOCUMENT_FOCUSED",

                    composition=(
                        "The catalog document fills "
                        "most of the frame while preserving "
                        "enough surrounding context."
                    )
                ),

                character_actions=[],

                prop_actions=[
                    PropAction(
                        entity_id=document_id,

                        action="DISPLAY_CATALOG_CODE"
                    )
                ],

                visual_constraints=[
                    "Reveal the catalog code clearly.",
                    "Do not introduce unrelated text.",
                    "Preserve document appearance.",
                    "Do not animate page flipping.",
                    "Keep the document physically stable.",
                    "Maintain the established lighting."
                ],

                dialogue=None
            ),

            # --------------------------------------------------------
            # SHOT 04 — REACTION
            # --------------------------------------------------------

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    4
                ),

                scene_number=scene.scene_number,

                duration_seconds=5,

                purpose=(
                    "Show Julian recognizing the significance "
                    "of the catalog code while Ren remains alert."
                ),

                characters=[
                    julian_id,
                    ren_id
                ],

                props=[
                    document_id,
                    desk_id
                ],

                camera=CameraPlan(
                    shot_type="MEDIUM_TWO_SHOT",

                    camera_movement="SUBTLE_PUSH_IN",

                    framing="CHARACTER_INTERACTION",

                    composition=(
                        "Julian remains visually dominant "
                        "with Ren positioned nearby."
                    )
                ),

                character_actions=[
                    CharacterAction(
                        entity_id=julian_id,

                        action="RECOGNIZE_CLUE",

                        gesture="MINIMAL_REACTION",

                        facial_movement=(
                            "SUSPICIOUS_REALIZATION"
                        )
                    ),

                    CharacterAction(
                        entity_id=ren_id,

                        action="WATCH_JULIAN",

                        gesture="STILL_ALERT_POSTURE",

                        facial_movement=(
                            "CONTROLLED_ALERT_EXPRESSION"
                        )
                    )
                ],

                prop_actions=[],

                visual_constraints=[
                    "Maintain both character identities.",
                    "Maintain wardrobe continuity.",
                    "Preserve spatial relationship.",
                    "Avoid unnecessary head turns.",
                    "Keep reactions subtle.",
                    "Do not introduce new characters.",
                    "Maintain dark investigative atmosphere."
                ],

                dialogue=scene.dialogue
            )

        ]

    # ================================================================
    # GENERIC SCENE
    # ================================================================

    def create_generic_shots(
        self,
        scene,
        scene_state
    ):

        characters = scene_state.active_characters

        props = scene_state.active_props

        character_actions = [

            CharacterAction(
                entity_id=character_id,

                action="PERFORM_NARRATIVE_ACTION",

                gesture="SUBTLE_NATURAL_GESTURE",

                facial_movement=(
                    "CONTROLLED_EXPRESSION"
                )
            )

            for character_id in characters
        ]

        return [

            ShotPlan(
                shot_id=self.shot_id(
                    scene.scene_number,
                    1
                ),

                scene_number=scene.scene_number,

                duration_seconds=scene.duration_seconds,

                purpose="Primary narrative shot",

                characters=characters,

                props=props,

                camera=CameraPlan(
                    shot_type="MEDIUM",

                    camera_movement="STATIC_OR_SUBTLE_PUSH",

                    framing="CHARACTER_FOCUSED",

                    composition=(
                        "Maintain clear focus on "
                        "the primary narrative action."
                    )
                ),

                character_actions=character_actions,

                prop_actions=[],

                visual_constraints=[
                    "Preserve character identity.",
                    "Preserve wardrobe continuity.",
                    "Maintain environment continuity.",
                    "Avoid unnecessary movement.",
                    "Do not introduce unrelated characters."
                ],

                dialogue=scene.dialogue
            )

        ]

    # ================================================================
    # HELPERS
    # ================================================================

    def shot_id(
        self,
        scene_number: int,
        shot_number: int
    ) -> str:

        return (
            f"EP001-"
            f"S{scene_number:02d}-"
            f"SHOT{shot_number:02d}"
        )

    def find_character(
        self,
        scene_state,
        name: str
    ):

        for entity_id in scene_state.active_characters:

            character = (
                scene_state.characters[entity_id]
            )

            if character.name == name:

                return entity_id

        raise ValueError(
            f"Character '{name}' "
            f"not found in scene state."
        )

    def find_prop(
        self,
        scene_state,
        name: str
    ):

        for entity_id in scene_state.active_props:

            prop = (
                scene_state.props[entity_id]
            )

            if prop.name == name:

                return entity_id

        raise ValueError(
            f"Prop '{name}' "
            f"not found in scene state."
        )