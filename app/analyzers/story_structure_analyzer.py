from typing import List

from app.analyzers.scene_analyzer import SceneAnalyzer
from app.models.episode import Episode, Scene
from app.models.story_structure import (
    SceneStructure,
    StoryStructure,
)


class StoryStructureAnalyzer:
    """
    Generic story structure analyzer.

    Story structure is derived from scene content rather than
    episode-specific rules or scene numbers.
    """

    def __init__(self):

        self.scene_analyzer = SceneAnalyzer()

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze(
        self,
        episode: Episode,
    ) -> StoryStructure:

        if not episode.scenes:
            return StoryStructure(
                status="FAILED",
                overall_arc="EMPTY",
                scenes=[],
            )

        structures: List[SceneStructure] = []

        narrative_functions: List[str] = []

        for index, scene in enumerate(
            episode.scenes
        ):

            scene_analysis = (
                self.scene_analyzer.analyze_scene(
                    scene=scene,
                    episode=episode,
                )
            )

            narrative_function = (
                scene_analysis.narrative_function
            )

            narrative_functions.append(
                narrative_function
            )

            structure = SceneStructure(
                scene_number=scene.scene_number,
                narrative_function=narrative_function,
                dramatic_role=self._dramatic_role(
                    narrative_function
                ),
                purpose=self._purpose(
                    scene
                ),
                information_revealed=(
                    self._information_revealed(
                        scene
                    )
                ),
                open_questions=(
                    self._open_questions(
                        scene
                    )
                ),
                tension_level=(
                    self._estimate_tension(
                        episode=episode,
                        scene=scene,
                        scene_index=index,
                    )
                ),
            )

            structures.append(
                structure
            )

        return StoryStructure(
            status="PASSED",
            overall_arc=self._overall_arc(
                narrative_functions
            ),
            scenes=structures,
        )

    # ================================================================
    # DRAMATIC ROLE
    # ================================================================

    def _dramatic_role(
        self,
        narrative_function: str,
    ) -> str:

        roles = {
            "SETUP": "ESTABLISH",
            "ESCALATION": "INTENSIFY",
            "DISCOVERY": "UNCOVER_INFORMATION",
            "REVELATION": "REVEAL_INFORMATION",
            "CONFRONTATION": "CREATE_CONFLICT",
            "RESOLUTION": "RESOLVE_CONFLICT",
            "TRANSITION": "CONNECT_STORY_BEATS",
            "DEVELOPMENT": "ADVANCE_STORY",
        }

        return roles.get(
            narrative_function,
            "ADVANCE_STORY",
        )

    # ================================================================
    # PURPOSE
    # ================================================================

    def _purpose(
        self,
        scene: Scene,
    ) -> str:

        if scene.narrative_purpose.strip():
            return scene.narrative_purpose.strip()

        if scene.visual_description.strip():
            return (
                "Advance the story through the "
                "events depicted in the scene."
            )

        if scene.dialogue.strip():
            return (
                "Advance the story through dialogue."
            )

        return "Advance the narrative."

    # ================================================================
    # INFORMATION
    # ================================================================

    def _information_revealed(
        self,
        scene: Scene,
    ) -> List[str]:
        """
        Do not fabricate story facts.

        Until a semantic/LLM analysis provider is introduced,
        the deterministic analyzer only reports explicit
        story material supplied by the episode.
        """

        information: List[str] = []

        purpose = scene.narrative_purpose.strip()

        if purpose:
            information.append(
                purpose
            )

        return information

    # ================================================================
    # OPEN QUESTIONS
    # ================================================================

    def _open_questions(
        self,
        scene: Scene,
    ) -> List[str]:
        """
        Question inference is intentionally conservative.

        A deterministic engine should not invent unresolved
        mysteries that are not explicitly represented in
        story data.
        """

        text = " ".join(
            [
                scene.dialogue,
                scene.narrative_purpose,
            ]
        )

        questions = []

        parts = text.split("?")

        if len(parts) > 1:

            for part in parts[:-1]:

                candidate = (
                    part.strip()
                    .split(".")[-1]
                    .strip()
                )

                if candidate:
                    questions.append(
                        candidate + "?"
                    )

        return self._deduplicate(
            questions
        )

    # ================================================================
    # TENSION
    # ================================================================

    def _estimate_tension(
        self,
        episode: Episode,
        scene: Scene,
        scene_index: int,
    ) -> int:

        text = " ".join(
            [
                scene.dialogue,
                scene.visual_description,
                scene.narrative_purpose,
                episode.tone,
            ]
        ).lower()

        score = 2

        tension_terms = (
            "danger",
            "threat",
            "fear",
            "tense",
            "tension",
            "suspense",
            "mystery",
            "death",
            "dead",
            "fight",
            "confront",
            "discover",
            "reveal",
            "secret",
            "chase",
            "escape",
            "panic",
        )

        intense_terms = (
            "kill",
            "attack",
            "explosion",
            "terrified",
            "violent",
            "critical",
            "emergency",
        )

        for term in tension_terms:
            if term in text:
                score += 1

        for term in intense_terms:
            if term in text:
                score += 2

        scene_count = max(
            len(episode.scenes),
            1,
        )

        story_progress = (
            scene_index / scene_count
        )

        if story_progress >= 0.75:
            score += 1

        return max(
            0,
            min(score, 10),
        )

    # ================================================================
    # OVERALL ARC
    # ================================================================

    def _overall_arc(
        self,
        functions: List[str],
    ) -> str:

        if not functions:
            return "EMPTY"

        meaningful_functions = []

        for function in functions:

            if (
                not meaningful_functions
                or meaningful_functions[-1] != function
            ):
                meaningful_functions.append(
                    function
                )

        if len(meaningful_functions) == 1:
            return meaningful_functions[0]

        return "_TO_".join(
            meaningful_functions
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

            cleaned = value.strip()

            if not cleaned:
                continue

            key = cleaned.lower()

            if key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result