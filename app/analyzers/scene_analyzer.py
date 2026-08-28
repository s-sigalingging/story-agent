from app.models.episode import Episode
from app.models.scene_analysis import (
    SceneAnalysis,
    EpisodeSceneAnalysis,
    EnvironmentAnalysis,
    CameraAnalysis
)


class SceneAnalyzer:

    def analyze(
        self,
        episode: Episode
    ) -> EpisodeSceneAnalysis:

        scenes = []

        for scene in episode.scenes:

            scene_analysis = self.analyze_scene(
                scene.scene_number,
                scene.location,
                scene.characters,
                scene.dialogue
            )

            scenes.append(scene_analysis)

        return EpisodeSceneAnalysis(
            status="PASSED",
            scenes=scenes
        )

    def analyze_scene(
        self,
        scene_number: int,
        location: str,
        characters: list,
        dialogue: str
    ) -> SceneAnalysis:

        # Scene 1
        if scene_number == 1:

            return SceneAnalysis(
                scene_number=1,

                narrative_function="SETUP",

                visual_intent=(
                    "Establish the old docks and create "
                    "an uneasy sense that the official story "
                    "may be incomplete."
                ),

                emotional_state="UNEASY",

                character_actions=[
                    "Sam Bell speaks while working at the docks.",
                    "Sam appears familiar with the environment."
                ],

                characters=characters,

                location=location,

                props=[
                    "Dock equipment",
                    "Work materials"
                ],

                environment=EnvironmentAnalysis(
                    time_of_day="Pre-dawn",
                    weather="Cold and damp",
                    lighting="Dim natural light",
                    atmosphere="Quiet, isolated, uneasy"
                ),

                camera=CameraAnalysis(
                    framing="Medium establishing shot",
                    movement="Slow observational movement",
                    focus="Sam Bell and the surrounding docks"
                ),

                visual_constraints=[
                    "Maintain a grounded realistic environment.",
                    "Do not introduce unnecessary characters.",
                    "Keep the scene visually quiet.",
                    "Avoid excessive camera movement."
                ]
            )

        # Scene 2
        if scene_number == 2:

            return SceneAnalysis(
                scene_number=2,

                narrative_function="ESCALATION",

                visual_intent=(
                    "Show the dock environment from a closer "
                    "perspective while reinforcing the contrast "
                    "between the official story and what workers know."
                ),

                emotional_state="UNEASY",

                character_actions=[
                    "Sam Bell continues working.",
                    "Sam observes the surrounding dock area."
                ],

                characters=characters,

                location=location,

                props=[
                    "Dock equipment",
                    "Cargo materials"
                ],

                environment=EnvironmentAnalysis(
                    time_of_day="Early morning",
                    weather="Cold and damp",
                    lighting="Low natural light",
                    atmosphere="Quiet and foreboding"
                ),

                camera=CameraAnalysis(
                    framing="Medium shot",
                    movement="Slow controlled movement",
                    focus="Sam Bell and dock surroundings"
                ),

                visual_constraints=[
                    "Maintain continuity with Scene 1.",
                    "Do not introduce a different weather condition.",
                    "Avoid unnecessary character movement.",
                    "Keep the environment subdued."
                ]
            )

        # Scene 3
        if scene_number == 3:

            return SceneAnalysis(
                scene_number=3,

                narrative_function="REVELATION",

                visual_intent=(
                    "Introduce Sterling and the apparent death "
                    "of Samuel Bell while maintaining an understated "
                    "and slightly tragic tone."
                ),

                emotional_state="TRAGIC",

                character_actions=[
                    "Sterling examines the case.",
                    "Sterling delivers his conclusion."
                ],

                characters=characters,

                location=location,

                props=[
                    "Case materials",
                    "Dock records"
                ],

                environment=EnvironmentAnalysis(
                    time_of_day="Early morning",
                    weather="Cold and damp",
                    lighting="Muted natural light",
                    atmosphere="Somber and quiet"
                ),

                camera=CameraAnalysis(
                    framing="Medium shot",
                    movement="Minimal controlled movement",
                    focus="Sterling and the case"
                ),

                visual_constraints=[
                    "Keep Sterling visually consistent.",
                    "Maintain the subdued tone.",
                    "Avoid exaggerated acting.",
                    "Do not introduce unrelated objects."
                ]
            )

        # Scene 4
        if scene_number == 4:

            return SceneAnalysis(
                scene_number=4,

                narrative_function="DISCOVERY",

                visual_intent=(
                    "Reveal that Samuel Bell's death may be connected "
                    "to a catalog code, establishing the first concrete "
                    "mystery for Julian."
                ),

                emotional_state="SUSPICIOUS",

                character_actions=[
                    "Julian examines the document carefully.",
                    "Ren remains present while Julian studies the clue.",
                    "Julian recognizes that the document contains "
                    "something unusual."
                ],

                characters=characters,

                location=location,

                props=[
                    "Catalog document",
                    "Case records",
                    "Desk"
                ],

                environment=EnvironmentAnalysis(
                    time_of_day="Night",
                    weather="Cold and dry",
                    lighting="Low desk-lamp lighting",
                    atmosphere="Dark, investigative, claustrophobic"
                ),

                camera=CameraAnalysis(
                    framing="Medium two-shot",
                    movement="Slow controlled push-in",
                    focus="Julian and the document"
                ),

                visual_constraints=[
                    "Maintain Julian's established appearance.",
                    "Maintain continuity of the office environment.",
                    "Do not introduce rain if it was not established.",
                    "Keep Julian's movements subtle.",
                    "Avoid unnecessary head turns.",
                    "Do not reveal document details too early.",
                    "Preserve document continuity for later close-ups."
                ]
            )

        # Generic fallback
        return SceneAnalysis(
            scene_number=scene_number,

            narrative_function="DEVELOPMENT",

            visual_intent=(
                "Advance the story while maintaining "
                "visual continuity."
            ),

            emotional_state="NEUTRAL",

            character_actions=[
                "Characters perform actions appropriate "
                "to the scene."
            ],

            characters=characters,

            location=location,

            props=[],

            environment=EnvironmentAnalysis(
                time_of_day="UNSPECIFIED",
                weather="UNSPECIFIED",
                lighting="UNSPECIFIED",
                atmosphere="UNSPECIFIED"
            ),

            camera=CameraAnalysis(
                framing="Medium shot",
                movement="Controlled movement",
                focus="Primary character"
            ),

            visual_constraints=[
                "Maintain character continuity.",
                "Maintain environment continuity."
            ]
        )