from typing import List

from app.models.prompt import (
    ShotPromptContext,
)


class NegativePromptBuilder:
    """
    Provider-agnostic, context-aware negative prompt builder.

    Negative constraints are only added when they are relevant
    to the current shot.

    The builder contains no story-specific knowledge.
    """

    # ================================================================
    # PUBLIC API
    # ================================================================

    def build(
        self,
        context: ShotPromptContext,
    ) -> str:

        exclusions: List[str] = []

        # ============================================================
        # UNIVERSAL QUALITY / STABILITY
        # ============================================================

        exclusions.extend(
            self._base_exclusions()
        )

        # ============================================================
        # CHARACTER-SPECIFIC
        # ============================================================

        if context.characters:

            exclusions.extend(
                self._character_exclusions()
            )

        # ============================================================
        # PROP-SPECIFIC
        # ============================================================

        if context.props:

            exclusions.extend(
                self._prop_exclusions()
            )

        # ============================================================
        # ENVIRONMENT-SPECIFIC
        # ============================================================

        if (
            context.environment.location_id
            or
            context.environment.location_name
        ):

            exclusions.extend(
                self._environment_exclusions(
                    context
                )
            )

        # ============================================================
        # CAMERA-SPECIFIC
        # ============================================================

        exclusions.extend(
            self._camera_exclusions(
                context
            )
        )

        # ============================================================
        # TEXT / DOCUMENT-SPECIFIC
        # ============================================================

        if self._shot_has_text_sensitive_content(
            context
        ):

            exclusions.extend(
                self._text_exclusions()
            )

        # ============================================================
        # TRANSITION / MOTION STABILITY
        # ============================================================

        exclusions.extend(
            self._transition_exclusions()
        )

        return ", ".join(
            self._deduplicate(
                exclusions
            )
        )

    # ================================================================
    # BASE
    # ================================================================

    def _base_exclusions(
        self,
    ) -> List[str]:

        return [
            "visual glitches",
            "flickering",
            "unstable details",
            "warped geometry",
            "distorted anatomy",
            "inconsistent proportions",
            "unmotivated visual changes",
        ]

    # ================================================================
    # CHARACTERS
    # ================================================================

    def _character_exclusions(
        self,
    ) -> List[str]:

        return [
            "extra characters",
            "duplicate characters",
            "character identity drift",
            "facial identity changes",
            "different hairstyle",
            "incorrect wardrobe",
            "incorrect accessories",
            "body deformation",
            "extra limbs",
            "extra fingers",
            "unnecessary head movement",
            "exaggerated facial expressions",
            "exaggerated acting",
            "unnatural gestures",
        ]

    # ================================================================
    # PROPS
    # ================================================================

    def _prop_exclusions(
        self,
    ) -> List[str]:

        return [
            "extra props",
            "unrelated objects",
            "prop identity changes",
            "object morphing",
            "object transformation",
            "unmotivated prop movement",
        ]

    # ================================================================
    # ENVIRONMENT
    # ================================================================

    def _environment_exclusions(
        self,
        context: ShotPromptContext,
    ) -> List[str]:

        exclusions = [
            "environment redesign",
            "unexpected location changes",
            "lighting changes",
        ]

        environment = (
            context.environment
        )

        if (
            environment.weather
            and
            environment.weather
            != "UNKNOWN"
        ):

            exclusions.append(
                "unexpected weather changes"
            )

        if (
            environment.time_of_day
            and
            environment.time_of_day
            != "UNKNOWN"
        ):

            exclusions.append(
                "time of day changes"
            )

        if (
            environment.atmosphere
            and
            environment.atmosphere
            != "UNKNOWN"
        ):

            exclusions.append(
                "atmosphere changes"
            )

        return exclusions

    # ================================================================
    # CAMERA
    # ================================================================

    def _camera_exclusions(
        self,
        context: ShotPromptContext,
    ) -> List[str]:

        movement = (
            context.camera
            .camera_movement
            .strip()
            .upper()
        )

        # STATIC means the camera should not invent movement.
        if movement == "STATIC":

            return [
                "camera shake",
                "camera spin",
                "camera rotation",
                "sudden zoom",
                "rapid reframing",
                "unwanted camera movement",
            ]

        # A moving camera is allowed to move, but should still avoid
        # unstable or excessive motion.
        return [
            "random camera shake",
            "camera spin",
            "unmotivated camera rotation",
            "sudden zoom",
            "excessive zoom",
            "rapid reframing",
            "camera movement beyond the planned motion",
        ]

    # ================================================================
    # TEXT
    # ================================================================

    def _shot_has_text_sensitive_content(
        self,
        context: ShotPromptContext,
    ) -> bool:
        """
        Detect whether the shot should protect readable text.

        This remains generic and relies on structured context instead
        of story-specific keywords.
        """

        metadata = {
            key.lower(): value.lower()
            for key, value
            in context.metadata.items()
        }

        if (
            metadata.get(
                "text_sensitive"
            )
            == "true"
        ):

            return True

        if (
            metadata.get(
                "contains_readable_text"
            )
            == "true"
        ):

            return True

        return False

    def _text_exclusions(
        self,
    ) -> List[str]:

        return [
            "changing text",
            "random typography",
            "unrelated text",
            "random letters",
            "random numbers",
            "text distortion",
            "text morphing",
        ]

    # ================================================================
    # TRANSITIONS
    # ================================================================

    def _transition_exclusions(
        self,
    ) -> List[str]:

        return [
            "artificial transitions",
            "scene transitions",
            "crossfades",
            "object transitions",
            "state morphing",
        ]

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