from typing import List

from app.models.prompt import (
    PromptCharacterPerformance,
    PromptPropPerformance,
    ShotPromptContext,
)


class VideoPromptBuilder:
    """
    Provider-agnostic video prompt builder.

    The builder assumes that an approved keyframe already exists.

    Its responsibility is to describe motion only:
    - camera movement
    - character movement
    - prop movement
    - continuity preservation

    It must not redesign the approved keyframe.
    """

    # ================================================================
    # PUBLIC API
    # ================================================================

    def build(
        self,
        context: ShotPromptContext,
    ) -> str:

        sections: List[str] = []

        sections.append(
            self._build_opening_section(
                context
            )
        )

        camera_section = (
            self._build_camera_section(
                context
            )
        )

        if camera_section:
            sections.append(
                camera_section
            )

        character_section = (
            self._build_character_motion_section(
                context
            )
        )

        if character_section:
            sections.append(
                character_section
            )

        prop_section = (
            self._build_prop_motion_section(
                context
            )
        )

        if prop_section:
            sections.append(
                prop_section
            )

        continuity_section = (
            self._build_continuity_section(
                context
            )
        )

        if continuity_section:
            sections.append(
                continuity_section
            )

        sections.append(
            self._build_motion_policy_section()
        )

        return self._join_sections(
            sections
        )

    # ================================================================
    # OPENING
    # ================================================================

    def _build_opening_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        return (
            f"Animate the approved keyframe for "
            f"{context.duration_seconds} seconds. "
            "Treat the approved keyframe as the fixed visual source "
            "for character identity, wardrobe, environment, props, "
            "lighting, composition, and visual style."
        )

    # ================================================================
    # CAMERA
    # ================================================================

    def _build_camera_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        camera = (
            context.camera
        )

        parts = []

        movement = (
            camera.camera_movement
            .strip()
        )

        if (
            movement
            and
            movement != "UNSPECIFIED"
        ):
            parts.append(
                "camera movement: "
                + self._humanize(
                    movement
                )
            )

        framing = (
            camera.framing
            .strip()
        )

        if (
            framing
            and
            framing != "UNSPECIFIED"
        ):
            parts.append(
                "preserve framing: "
                + self._humanize(
                    framing
                )
            )

        composition = (
            camera.composition
            .strip()
        )

        if composition:
            parts.append(
                "preserve composition: "
                + composition.rstrip(".")
            )

        if not parts:
            return ""

        return (
            "Camera motion: "
            + "; ".join(
                parts
            )
            + "."
        )

    # ================================================================
    # CHARACTER MOTION
    # ================================================================

    def _build_character_motion_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        descriptions = []

        for character in (
            context.characters
        ):

            description = (
                self._describe_character_motion(
                    character
                )
            )

            if description:
                descriptions.append(
                    description
                )

        if not descriptions:
            return ""

        return (
            "Character motion: "
            + "; ".join(
                descriptions
            )
            + "."
        )

    def _describe_character_motion(
        self,
        character: PromptCharacterPerformance,
    ) -> str:

        name = (
            character.name.strip()
            or character.entity_id
        )

        parts = []

        action = (
            character.action
            .strip()
        )

        if action:
            parts.append(
                "action: "
                + self._humanize(
                    action
                )
            )

        gesture = (
            character.gesture
            .strip()
        )

        if gesture:
            parts.append(
                "gesture: "
                + self._humanize(
                    gesture
                )
            )

        facial = (
            character.facial_movement
            .strip()
        )

        if facial:
            parts.append(
                "facial movement: "
                + self._humanize(
                    facial
                )
            )

        if not parts:
            return (
                f"{name} remains visually stable "
                "with only subtle natural motion"
            )

        return (
            f"{name} — "
            + ", ".join(
                parts
            )
        )

    # ================================================================
    # PROP MOTION
    # ================================================================

    def _build_prop_motion_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        descriptions = []

        for prop in (
            context.props
        ):

            description = (
                self._describe_prop_motion(
                    prop
                )
            )

            if description:
                descriptions.append(
                    description
                )

        if not descriptions:
            return ""

        return (
            "Prop motion: "
            + "; ".join(
                descriptions
            )
            + "."
        )

    def _describe_prop_motion(
        self,
        prop: PromptPropPerformance,
    ) -> str:

        name = (
            prop.name.strip()
            or prop.entity_id
        )

        action = (
            prop.action.strip()
        )

        if not action:

            return (
                f"{name} remains visually stable"
            )

        humanized_action = (
            self._humanize(
                action
            )
        )

        if (
            humanized_action
            == "maintain established state"
        ):

            return (
                f"{name} remains visually stable "
                "and preserves its established state"
            )

        return (
            f"{name} — "
            f"{humanized_action}"
        )

    # ================================================================
    # CONTINUITY
    # ================================================================

    def _build_continuity_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        constraints = (
            self._deduplicate(
                context
                .continuity_constraints
            )
        )

        if not constraints:
            return ""

        normalized = []

        for constraint in constraints:

            cleaned = (
                constraint.strip()
            )

            if not cleaned:
                continue

            normalized.append(
                cleaned
                if cleaned.endswith(".")
                else f"{cleaned}."
            )

        if not normalized:
            return ""

        return (
            "Continuity requirements: "
            + " ".join(
                normalized
            )
        )

    # ================================================================
    # MOTION POLICY
    # ================================================================

    def _build_motion_policy_section(
        self,
    ) -> str:

        return (
            "Keep all motion restrained, natural, and physically "
            "believable. Preserve character identity, facial structure, "
            "hairstyle, wardrobe, body proportions, accessories, "
            "environment design, lighting, weather, atmosphere, prop "
            "appearance, and spatial relationships throughout the shot. "
            "Do not redesign or reinterpret the approved keyframe. "
            "Do not introduce new characters, unrelated objects, or "
            "environmental changes. Do not create artificial transitions "
            "inside the shot."
        )

    # ================================================================
    # UTILITIES
    # ================================================================

    def _join_sections(
        self,
        sections: List[str],
    ) -> str:

        cleaned = [
            section.strip()
            for section
            in sections
            if section.strip()
        ]

        return " ".join(
            cleaned
        )

    def _humanize(
        self,
        value: str,
    ) -> str:

        return (
            value.strip()
            .replace("_", " ")
            .lower()
        )

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