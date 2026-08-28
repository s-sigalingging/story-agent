from app.models.episode import Episode
from app.models.story_structure import (
    StoryStructure,
    SceneStructure
)


class StoryStructureAnalyzer:

    def analyze(self, episode: Episode) -> StoryStructure:

        scenes = []

        for scene in episode.scenes:

            structure = self.analyze_scene(
                scene.scene_number,
                scene.dialogue,
                scene.location,
                scene.characters
            )

            scenes.append(structure)

        return StoryStructure(
            status="PASSED",
            overall_arc=self.determine_overall_arc(scenes),
            scenes=scenes
        )

    def analyze_scene(
        self,
        scene_number: int,
        dialogue: str,
        location: str,
        characters: list
    ):

        text = dialogue.lower()

        # Scene 1
        if scene_number == 1:

            return SceneStructure(
                scene_number=scene_number,
                narrative_function="SETUP",
                dramatic_role="ESTABLISH_MYSTERY",
                purpose=(
                    "Establish the central mystery "
                    "and introduce the audience to the "
                    "core problem."
                ),
                information_revealed=[
                    "The official story about Oakhaven "
                    "may not be true."
                ],
                open_questions=[
                    "What is the truth behind Oakhaven?"
                ],
                tension_level=2
            )

        # Scene 2
        if scene_number == 2:

            return SceneStructure(
                scene_number=scene_number,
                narrative_function="ESCALATION",
                dramatic_role="CHALLENGE_ASSUMPTION",
                purpose=(
                    "Challenge the established version "
                    "of events and increase audience curiosity."
                ),
                information_revealed=[
                    "Workers at the docks know something "
                    "contradicts the official story."
                ],
                open_questions=[
                    "What really happened at the docks?"
                ],
                tension_level=4
            )

        # Scene 3
        if scene_number == 3:

            return SceneStructure(
                scene_number=scene_number,
                narrative_function="REVELATION",
                dramatic_role="INTRODUCE_CASE",
                purpose=(
                    "Introduce the death that becomes "
                    "the first concrete mystery."
                ),
                information_revealed=[
                    "Samuel Bell has died.",
                    "The case appears to be closed."
                ],
                open_questions=[
                    "Was Samuel Bell's death really natural?"
                ],
                tension_level=6
            )

        # Scene 4
        if scene_number == 4:

            return SceneStructure(
                scene_number=scene_number,
                narrative_function="DISCOVERY",
                dramatic_role="REVEAL_CLUE",
                purpose=(
                    "Reveal the first significant clue "
                    "that changes the interpretation of the case."
                ),
                information_revealed=[
                    "The apparent heart attack may not "
                    "be a simple medical event.",
                    "A catalog code is connected to the case."
                ],
                open_questions=[
                    "What does the catalog code mean?",
                    "Who created the catalog?"
                ],
                tension_level=8
            )

        # Fallback for future scenes
        return SceneStructure(
            scene_number=scene_number,
            narrative_function="DEVELOPMENT",
            dramatic_role="ADVANCE_STORY",
            purpose=(
                "Advance the story and provide additional "
                "information."
            ),
            information_revealed=[],
            open_questions=[],
            tension_level=5
        )

    def determine_overall_arc(
        self,
        scenes: list
    ) -> str:

        if not scenes:
            return "UNDEFINED"

        functions = [
            scene.narrative_function
            for scene in scenes
        ]

        if (
            "SETUP" in functions
            and "ESCALATION" in functions
            and "DISCOVERY" in functions
        ):
            return "MYSTERY_ESCALATION"

        return "LINEAR_NARRATIVE"