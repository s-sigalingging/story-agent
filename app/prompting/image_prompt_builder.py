from typing import List

from app.models.prompt import (
    PromptAssetReference,
    PromptCharacterPerformance,
    PromptPropPerformance,
    ShotPromptContext,
)


class ImagePromptBuilder:
    """
    Provider-agnostic image prompt builder.

    The builder compiles a still/keyframe prompt from structured
    ShotPromptContext.

    It must not contain story-specific names, episode IDs,
    genres, or visual styles.
    """

    # ================================================================
    # PUBLIC API
    # ================================================================

    def build(
        self,
        context: ShotPromptContext,
    ) -> str:

        sections: List[str] = []

        style_section = (
            self._build_style_section(
                context
            )
        )

        if style_section:
            sections.append(
                style_section
            )

        purpose_section = (
            self._build_purpose_section(
                context
            )
        )

        if purpose_section:
            sections.append(
                purpose_section
            )

        environment_section = (
            self._build_environment_section(
                context
            )
        )

        if environment_section:
            sections.append(
                environment_section
            )

        subject_section = (
            self._build_subject_section(
                context
            )
        )

        if subject_section:
            sections.append(
                subject_section
            )

        performance_section = (
            self._build_performance_section(
                context
            )
        )

        if performance_section:
            sections.append(
                performance_section
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

        continuity_section = (
            self._build_continuity_section(
                context
            )
        )

        if continuity_section:
            sections.append(
                continuity_section
            )

        asset_section = (
            self._build_asset_section(
                context
            )
        )

        if asset_section:
            sections.append(
                asset_section
            )

        sections.append(
            self._build_stability_section()
        )

        return self._join_sections(
            sections
        )

    # ================================================================
    # STYLE
    # ================================================================

    def _build_style_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        parts: List[str] = []

        tone = (
            context.style
            .tone
            .strip()
        )

        visual_style = (
            context.style
            .visual_style
            .strip()
        )

        if visual_style:
            parts.append(
                f"Visual style: {visual_style}."
            )

        if tone:
            parts.append(
                f"Tone: {tone}."
            )

        for note in (
            context.style
            .additional_style_notes
        ):

            cleaned = note.strip()

            if cleaned:
                parts.append(
                    cleaned
                    if cleaned.endswith(".")
                    else f"{cleaned}."
                )

        return " ".join(
            parts
        )

    # ================================================================
    # PURPOSE
    # ================================================================

    def _build_purpose_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        purpose = (
            context.purpose
            .strip()
        )

        if not purpose:
            return ""

        return (
            "Shot purpose: "
            f"{purpose.rstrip('.')}."
        )

    # ================================================================
    # ENVIRONMENT
    # ================================================================

    def _build_environment_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        environment = (
            context.environment
        )

        parts: List[str] = []

        if environment.location_name.strip():
            parts.append(
                f"Location: "
                f"{environment.location_name.strip()}."
            )

        known_environment = []

        if (
            environment.time_of_day
            and
            environment.time_of_day
            != "UNKNOWN"
        ):

            known_environment.append(
                self._humanize(
                    environment.time_of_day
                )
            )

        if (
            environment.weather
            and
            environment.weather
            != "UNKNOWN"
        ):

            known_environment.append(
                self._humanize(
                    environment.weather
                )
            )

        if (
            environment.lighting
            and
            environment.lighting
            != "UNKNOWN"
        ):

            known_environment.append(
                self._humanize(
                    environment.lighting
                )
            )

        if (
            environment.atmosphere
            and
            environment.atmosphere
            != "UNKNOWN"
        ):

            known_environment.append(
                self._humanize(
                    environment.atmosphere
                )
            )

        if known_environment:

            parts.append(
                "Environment: "
                + ", ".join(
                    known_environment
                )
                + "."
            )

        return " ".join(
            parts
        )

    # ================================================================
    # SUBJECTS
    # ================================================================

    def _build_subject_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        parts: List[str] = []

        character_names = [
            character.name.strip()
            for character
            in context.characters
            if character.name.strip()
        ]

        prop_names = [
            prop.name.strip()
            for prop
            in context.props
            if prop.name.strip()
        ]

        if character_names:

            parts.append(
                "Characters visible: "
                + ", ".join(
                    character_names
                )
                + "."
            )

        if prop_names:

            parts.append(
                "Props visible: "
                + ", ".join(
                    prop_names
                )
                + "."
            )

        return " ".join(
            parts
        )

    # ================================================================
    # PERFORMANCE
    # ================================================================

    def _build_performance_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        character_descriptions = []

        for character in (
            context.characters
        ):

            description = (
                self._describe_character(
                    character
                )
            )

            if description:
                character_descriptions.append(
                    description
                )

        prop_descriptions = []

        for prop in (
            context.props
        ):

            description = (
                self._describe_prop(
                    prop
                )
            )

            if description:
                prop_descriptions.append(
                    description
                )

        parts = []

        if character_descriptions:

            parts.append(
                "Character performance: "
                + "; ".join(
                    character_descriptions
                )
                + "."
            )

        if prop_descriptions:

            parts.append(
                "Prop behavior: "
                + "; ".join(
                    prop_descriptions
                )
                + "."
            )

        return " ".join(
            parts
        )

    def _describe_character(
        self,
        character: PromptCharacterPerformance,
    ) -> str:

        name = (
            character.name.strip()
            or character.entity_id
        )

        elements = []

        if character.action.strip():
            elements.append(
                self._humanize(
                    character.action
                )
            )

        if character.gesture.strip():
            elements.append(
                "gesture: "
                + self._humanize(
                    character.gesture
                )
            )

        if character.facial_movement.strip():
            elements.append(
                "facial expression: "
                + self._humanize(
                    character.facial_movement
                )
            )

        if not elements:
            return name

        return (
            f"{name} — "
            + ", ".join(
                elements
            )
        )

    def _describe_prop(
        self,
        prop: PromptPropPerformance,
    ) -> str:

        name = (
            prop.name.strip()
            or prop.entity_id
        )

        if not prop.action.strip():
            return name

        return (
            f"{name} — "
            f"{self._humanize(prop.action)}"
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

        if (
            camera.shot_type
            and
            camera.shot_type
            != "UNSPECIFIED"
        ):

            parts.append(
                "shot type: "
                + self._humanize(
                    camera.shot_type
                )
            )

        if (
            camera.framing
            and
            camera.framing
            != "UNSPECIFIED"
        ):

            parts.append(
                "framing: "
                + self._humanize(
                    camera.framing
                )
            )

        if (
            camera.camera_movement
            and
            camera.camera_movement
            != "UNSPECIFIED"
        ):

            parts.append(
                "camera movement intent: "
                + self._humanize(
                    camera.camera_movement
                )
            )

        composition = (
            camera.composition
            .strip()
        )

        if composition:
            parts.append(
                "composition: "
                + composition.rstrip(".")
            )

        if not parts:
            return ""

        return (
            "Camera and composition: "
            + "; ".join(
                parts
            )
            + "."
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
    # ASSETS
    # ================================================================

    def _build_asset_section(
        self,
        context: ShotPromptContext,
    ) -> str:

        assets = (
            context.assets
        )

        if not assets:
            return ""

        descriptions = []

        for asset in assets:

            descriptions.append(
                self._describe_asset(
                    asset
                )
            )

        return (
            "Reference assets: "
            + "; ".join(
                descriptions
            )
            + "."
        )

    def _describe_asset(
        self,
        asset: PromptAssetReference,
    ) -> str:

        parts = [
            asset.name
        ]

        if asset.purpose:
            parts.append(
                f"purpose: {asset.purpose}"
            )

        if (
            asset.master_reference_required
        ):
            parts.append(
                "preserve master reference identity"
            )

        if asset.reference_path:
            parts.append(
                "reference image supplied"
            )

        if asset.required:
            parts.append(
                "required"
            )

        return (
            " (".join(
                [
                    parts[0],
                    ", ".join(
                        parts[1:]
                    )
                    + ")"
                ]
            )
            if len(parts) > 1
            else parts[0]
        )

    # ================================================================
    # STABILITY
    # ================================================================

    def _build_stability_section(
        self,
    ) -> str:

        return (
            "Create one stable cinematic frame representing a single "
            "moment in time. Preserve believable anatomy, coherent "
            "spatial relationships, consistent identity, and natural "
            "poses. Do not depict a transition between multiple states."
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

        cleaned = (
            value.strip()
            .replace("_", " ")
            .lower()
        )

        return cleaned

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