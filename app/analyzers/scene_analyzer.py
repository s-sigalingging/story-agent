from typing import Dict, List, Optional

from app.analyzers.entity_analyzer import (
    EntityAnalyzer,
)
from app.models.episode import (
    Episode,
    Scene,
)
from app.models.scene_analysis import (
    CameraAnalysis,
    EnvironmentAnalysis,
    EpisodeSceneAnalysis,
    SceneAnalysis,
)
from app.models.world import (
    SceneEntityAnalysis,
)
from app.world.registry import (
    WorldRegistry,
)


class SceneAnalyzer:
    """
    Generic scene analyzer.

    Responsibilities
    ----------------
    1. Interpret the narrative and visual meaning of scenes.
    2. Preserve human-readable story entity names.
    3. Attach stable entity IDs resolved by EntityAnalyzer.
    4. Produce provider-agnostic production intent.

    The analyzer must never contain knowledge about:
    - a specific episode
    - a specific character
    - a specific location
    - a specific prop
    - a specific story world
    """

    def __init__(
        self,
    ):

        self.entity_analyzer = (
            EntityAnalyzer()
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
    ) -> EpisodeSceneAnalysis:
        """
        Analyze every scene in an episode.

        Entity resolution is performed once for the entire episode
        and reused by every scene analysis.
        """

        entity_analysis = (
            self.entity_analyzer.analyze(
                episode=episode,
                registry=registry,
            )
        )

        entity_map: Dict[
            int,
            SceneEntityAnalysis
        ] = {
            item.scene_number: item
            for item in entity_analysis.scenes
        }

        analyses: List[
            SceneAnalysis
        ] = []

        for scene in episode.scenes:

            resolved_entities = (
                entity_map.get(
                    scene.scene_number
                )
            )

            analyses.append(
                self.analyze_scene(
                    scene=scene,
                    episode=episode,
                    resolved_entities=(
                        resolved_entities
                    ),
                )
            )

        return EpisodeSceneAnalysis(
            status="PASSED",
            episode_id=episode.episode_id,
            scenes=analyses,
        )

    def analyze_scene(
        self,
        scene: Scene,
        episode: Episode,
        resolved_entities: Optional[
            SceneEntityAnalysis
        ] = None,
    ) -> SceneAnalysis:
        """
        Analyze one scene.

        resolved_entities is optional so that components such as
        StoryStructureAnalyzer may still use this method without
        needing to run entity resolution themselves.
        """

        narrative_function = (
            self._infer_narrative_function(
                scene
            )
        )

        emotional_state = (
            self._infer_emotional_state(
                scene=scene,
                episode=episode,
            )
        )

        environment = (
            self._analyze_environment(
                scene
            )
        )

        camera = (
            self._analyze_camera(
                scene
            )
        )

        visual_intent = (
            self._build_visual_intent(
                scene
            )
        )

        character_actions = (
            self._build_character_actions(
                scene
            )
        )

        visual_constraints = (
            self._build_visual_constraints(
                scene
            )
        )

        primary_subject = (
            self._resolve_primary_subject(
                scene
            )
        )

        character_ids: List[str] = []

        location_id: Optional[str] = None

        prop_ids: List[str] = []

        if resolved_entities:

            character_ids = list(
                resolved_entities.character_ids
            )

            location_id = (
                resolved_entities.location_id
            )

            prop_ids = list(
                resolved_entities.prop_ids
            )

        primary_subject_id = (
            self._resolve_primary_subject_id(
                scene=scene,
                primary_subject=(
                    primary_subject
                ),
                resolved_entities=(
                    resolved_entities
                ),
            )
        )

        return SceneAnalysis(
            scene_number=scene.scene_number,
            narrative_function=(
                narrative_function
            ),
            visual_intent=(
                visual_intent
            ),
            emotional_state=(
                emotional_state
            ),
            character_actions=(
                character_actions
            ),
            characters=list(
                scene.characters
            ),
            location=scene.location,
            props=list(
                scene.props
            ),
            primary_subject=(
                primary_subject
            ),
            character_ids=(
                character_ids
            ),
            location_id=(
                location_id
            ),
            prop_ids=(
                prop_ids
            ),
            primary_subject_id=(
                primary_subject_id
            ),
            environment=(
                environment
            ),
            camera=(
                camera
            ),
            visual_constraints=(
                visual_constraints
            ),
        )

    # ================================================================
    # NARRATIVE FUNCTION
    # ================================================================

    def _infer_narrative_function(
        self,
        scene: Scene,
    ) -> str:

        text = self._scene_text(
            scene
        )

        keyword_groups = {
            "DISCOVERY": (
                "discover",
                "discovers",
                "find",
                "finds",
                "found",
                "clue",
                "realize",
                "realizes",
                "recognize",
                "recognizes",
                "uncover",
                "uncovers",
            ),
            "REVELATION": (
                "reveal",
                "reveals",
                "revealed",
                "truth",
                "expose",
                "exposes",
                "confession",
                "identity",
            ),
            "CONFRONTATION": (
                "confront",
                "confronts",
                "argument",
                "fight",
                "challenge",
                "accuse",
                "accuses",
                "threaten",
                "threatens",
            ),
            "ESCALATION": (
                "escalate",
                "escalates",
                "danger",
                "threat",
                "worse",
                "increasing",
                "suspicion",
                "tension",
                "complication",
            ),
            "RESOLUTION": (
                "resolve",
                "resolves",
                "resolution",
                "conclude",
                "concludes",
                "closure",
                "finally",
            ),
            "TRANSITION": (
                "transition",
                "move to",
                "moves to",
                "later",
                "meanwhile",
                "afterward",
            ),
            "SETUP": (
                "introduce",
                "introduces",
                "establish",
                "establishes",
                "opening",
                "begin",
                "begins",
            ),
        }

        for (
            function_name,
            keywords,
        ) in keyword_groups.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                return function_name

        return "DEVELOPMENT"

    # ================================================================
    # VISUAL INTENT
    # ================================================================

    def _build_visual_intent(
        self,
        scene: Scene,
    ) -> str:

        if (
            scene.visual_description
            .strip()
        ):
            return (
                scene.visual_description
                .strip()
            )

        if (
            scene.narrative_purpose
            .strip()
        ):
            return (
                "Visually support the "
                "narrative purpose: "
                f"{scene.narrative_purpose.strip()}"
            )

        if scene.characters:
            return (
                "Maintain visual focus "
                "on the characters and "
                "their interaction within "
                "the scene."
            )

        return (
            "Establish and maintain "
            "the scene environment while "
            "advancing the story."
        )

    # ================================================================
    # EMOTIONAL STATE
    # ================================================================

    def _infer_emotional_state(
        self,
        scene: Scene,
        episode: Episode,
    ) -> str:

        text = " ".join(
            [
                self._scene_text(
                    scene
                ),
                episode.tone.lower(),
            ]
        )

        emotional_keywords = {
            "FEARFUL": (
                "fear",
                "afraid",
                "terrified",
                "panic",
                "horror",
            ),
            "TENSE": (
                "tense",
                "tension",
                "danger",
                "threat",
                "suspense",
                "uneasy",
                "foreboding",
            ),
            "SUSPICIOUS": (
                "suspicious",
                "suspicion",
                "doubt",
                "uncertain",
                "mystery",
                "investigat",
            ),
            "SAD": (
                "sad",
                "tragic",
                "grief",
                "mourning",
                "somber",
            ),
            "ANGRY": (
                "angry",
                "anger",
                "furious",
                "rage",
                "confront",
            ),
            "HOPEFUL": (
                "hope",
                "hopeful",
                "optimistic",
            ),
            "JOYFUL": (
                "joy",
                "happy",
                "celebrat",
                "excited",
            ),
            "ROMANTIC": (
                "romantic",
                "romance",
                "intimate",
                "affection",
            ),
        }

        for (
            state,
            keywords,
        ) in emotional_keywords.items():

            if any(
                keyword in text
                for keyword in keywords
            ):
                return state

        return "NEUTRAL"

    # ================================================================
    # CHARACTER ACTIONS
    # ================================================================

    def _build_character_actions(
        self,
        scene: Scene,
    ) -> List[str]:

        actions: List[str] = []

        if (
            scene.visual_description
            .strip()
        ):
            actions.append(
                scene.visual_description
                .strip()
            )

        if scene.dialogue.strip():

            if scene.characters:
                actions.append(
                    "Characters perform the "
                    "scene while delivering "
                    "the supplied dialogue."
                )

            else:
                actions.append(
                    "Deliver the supplied "
                    "dialogue as established "
                    "by the story."
                )

        return self._deduplicate(
            actions
        )

    # ================================================================
    # PRIMARY SUBJECT
    # ================================================================

    def _resolve_primary_subject(
        self,
        scene: Scene,
    ) -> Optional[str]:

        if len(
            scene.characters
        ) == 1:
            return (
                scene.characters[0]
            )

        return None

    def _resolve_primary_subject_id(
        self,
        scene: Scene,
        primary_subject: Optional[
            str
        ],
        resolved_entities: Optional[
            SceneEntityAnalysis
        ],
    ) -> Optional[str]:
        """
        Resolve primary subject ID without guessing.

        Currently, a character becomes the primary subject only when
        the scene contains exactly one character.

        Multi-character subject priority will later come from semantic
        analysis / production intent instead of assumptions.
        """

        if not primary_subject:
            return None

        if not resolved_entities:
            return None

        if (
            len(scene.characters) !=
            len(
                resolved_entities
                .character_ids
            )
        ):
            return None

        try:
            index = (
                scene.characters.index(
                    primary_subject
                )
            )

        except ValueError:
            return None

        if index >= len(
            resolved_entities
            .character_ids
        ):
            return None

        return (
            resolved_entities
            .character_ids[index]
        )

    # ================================================================
    # ENVIRONMENT
    # ================================================================

    def _analyze_environment(
        self,
        scene: Scene,
    ) -> EnvironmentAnalysis:

        text = self._scene_text(
            scene
        )

        return EnvironmentAnalysis(
            time_of_day=(
                self._infer_time_of_day(
                    text
                )
            ),
            weather=(
                self._infer_weather(
                    text
                )
            ),
            lighting=(
                self._infer_lighting(
                    text
                )
            ),
            atmosphere=(
                self._infer_atmosphere(
                    text
                )
            ),
        )

    def _infer_time_of_day(
        self,
        text: str,
    ) -> str:

        patterns = [
            (
                "PRE_DAWN",
                (
                    "pre-dawn",
                    "before dawn",
                    "before sunrise",
                ),
            ),
            (
                "DAWN",
                (
                    "dawn",
                    "sunrise",
                ),
            ),
            (
                "MORNING",
                (
                    "morning",
                ),
            ),
            (
                "AFTERNOON",
                (
                    "afternoon",
                ),
            ),
            (
                "EVENING",
                (
                    "evening",
                    "sunset",
                    "dusk",
                ),
            ),
            (
                "NIGHT",
                (
                    "night",
                    "midnight",
                ),
            ),
        ]

        return self._match_group(
            text=text,
            groups=patterns,
            default="UNKNOWN",
        )

    def _infer_weather(
        self,
        text: str,
    ) -> str:

        patterns = [
            (
                "RAIN",
                (
                    "rain",
                    "rainy",
                    "raining",
                ),
            ),
            (
                "SNOW",
                (
                    "snow",
                    "snowing",
                ),
            ),
            (
                "FOG",
                (
                    "fog",
                    "foggy",
                    "mist",
                    "misty",
                ),
            ),
            (
                "STORM",
                (
                    "storm",
                    "stormy",
                    "thunder",
                ),
            ),
            (
                "CLEAR",
                (
                    "clear sky",
                    "clear weather",
                ),
            ),
            (
                "DAMP",
                (
                    "damp",
                    "wet",
                ),
            ),
        ]

        return self._match_group(
            text=text,
            groups=patterns,
            default="UNKNOWN",
        )

    def _infer_lighting(
        self,
        text: str,
    ) -> str:

        patterns = [
            (
                "LOW_LIGHT",
                (
                    "dark",
                    "dim",
                    "low light",
                    "low-light",
                ),
            ),
            (
                "PRACTICAL_LIGHT",
                (
                    "lamp",
                    "candle",
                    "practical lighting",
                ),
            ),
            (
                "BRIGHT",
                (
                    "bright",
                    "well-lit",
                ),
            ),
            (
                "NATURAL_LIGHT",
                (
                    "natural light",
                    "sunlight",
                ),
            ),
        ]

        return self._match_group(
            text=text,
            groups=patterns,
            default="UNKNOWN",
        )

    def _infer_atmosphere(
        self,
        text: str,
    ) -> str:

        patterns = [
            (
                "TENSE",
                (
                    "tense",
                    "tension",
                    "uneasy",
                    "suspense",
                ),
            ),
            (
                "SOMBER",
                (
                    "somber",
                    "tragic",
                    "grief",
                ),
            ),
            (
                "ISOLATED",
                (
                    "isolated",
                    "alone",
                    "lonely",
                ),
            ),
            (
                "CHAOTIC",
                (
                    "chaotic",
                    "chaos",
                    "frantic",
                ),
            ),
            (
                "CALM",
                (
                    "calm",
                    "peaceful",
                    "quiet",
                ),
            ),
        ]

        return self._match_group(
            text=text,
            groups=patterns,
            default="NEUTRAL",
        )

    # ================================================================
    # CAMERA
    # ================================================================

    def _analyze_camera(
        self,
        scene: Scene,
    ) -> CameraAnalysis:

        direction = (
            scene.camera_direction
            .strip()
        )

        text = direction.lower()

        framing = "UNSPECIFIED"

        framing_patterns = [
            (
                "EXTREME_CLOSE_UP",
                "extreme close",
            ),
            (
                "CLOSE_UP",
                "close-up",
            ),
            (
                "CLOSE_UP",
                "close up",
            ),
            (
                "MEDIUM_CLOSE_UP",
                "medium close",
            ),
            (
                "MEDIUM",
                "medium",
            ),
            (
                "WIDE",
                "wide",
            ),
            (
                "ESTABLISHING",
                "establishing",
            ),
        ]

        for (
            value,
            keyword,
        ) in framing_patterns:

            if keyword in text:
                framing = value
                break

        movement = "STATIC"

        movement_patterns = [
            (
                "SLOW_PUSH_IN",
                (
                    "push in",
                    "push-in",
                    "push toward",
                ),
            ),
            (
                "PULL_BACK",
                (
                    "pull back",
                    "pull-back",
                ),
            ),
            (
                "PAN",
                (
                    "pan ",
                    "panning",
                ),
            ),
            (
                "TILT",
                (
                    "tilt ",
                    "tilting",
                ),
            ),
            (
                "TRACK",
                (
                    "track ",
                    "tracking",
                ),
            ),
            (
                "DOLLY",
                (
                    "dolly",
                ),
            ),
            (
                "LATERAL",
                (
                    "lateral",
                ),
            ),
            (
                "HANDHELD",
                (
                    "handheld",
                ),
            ),
            (
                "STATIC",
                (
                    "static",
                ),
            ),
        ]

        for (
            value,
            keywords,
        ) in movement_patterns:

            if any(
                keyword in text
                for keyword in keywords
            ):
                movement = value
                break

        focus = "SCENE"

        if len(
            scene.characters
        ) == 1:
            focus = (
                scene.characters[0]
            )

        elif len(
            scene.characters
        ) > 1:
            focus = "CHARACTERS"

        elif scene.location:
            focus = scene.location

        return CameraAnalysis(
            framing=framing,
            movement=movement,
            focus=focus,
        )

    # ================================================================
    # CONTINUITY / CONSTRAINTS
    # ================================================================

    def _build_visual_constraints(
        self,
        scene: Scene,
    ) -> List[str]:

        constraints: List[
            str
        ] = []

        if (
            scene.continuity_notes
            .strip()
        ):
            constraints.append(
                scene.continuity_notes
                .strip()
            )

        if scene.characters:
            constraints.append(
                "Preserve established "
                "character identity "
                "throughout the scene."
            )

        if scene.location:
            constraints.append(
                "Preserve the established "
                "location and environment "
                "throughout the scene."
            )

        if scene.props:
            constraints.append(
                "Preserve established prop "
                "identity and appearance "
                "throughout the scene."
            )

        return self._deduplicate(
            constraints
        )

    # ================================================================
    # UTILITIES
    # ================================================================

    def _scene_text(
        self,
        scene: Scene,
    ) -> str:

        return " ".join(
            [
                scene.dialogue,
                scene.visual_description,
                scene.narrative_purpose,
                scene.camera_direction,
                scene.continuity_notes,
            ]
        ).lower()

    def _match_group(
        self,
        text: str,
        groups,
        default: str,
    ) -> str:

        for (
            value,
            keywords,
        ) in groups:

            if any(
                keyword in text
                for keyword in keywords
            ):
                return value

        return default

    def _deduplicate(
        self,
        values: List[str],
    ) -> List[str]:

        seen = set()

        result = []

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