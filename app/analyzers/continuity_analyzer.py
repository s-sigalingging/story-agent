from app.models.episode import Episode

from app.models.continuity import (
    EpisodeContinuity,
    SceneContinuity,
    CharacterState,
    LocationState,
    PropState
)


class ContinuityAnalyzer:

    def analyze(
        self,
        episode: Episode
    ) -> EpisodeContinuity:

        scenes = []

        previous_characters = {}
        previous_location = None
        previous_props = {}

        for index, scene in enumerate(episode.scenes):

            continuity = self.analyze_scene(
                scene=scene,
                previous_characters=previous_characters,
                previous_location=previous_location,
                previous_props=previous_props,
                is_first_scene=(index == 0)
            )

            scenes.append(continuity)

            # Update state after analyzing scene
            previous_characters = {
                character.name: character
                for character in continuity.characters
            }

            previous_location = continuity.location

            previous_props = {
                prop.name: prop
                for prop in continuity.props
            }

        return EpisodeContinuity(
            status="PASSED",
            scenes=scenes
        )

    def analyze_scene(
        self,
        scene,
        previous_characters,
        previous_location,
        previous_props,
        is_first_scene
    ):

        characters = []

        for character_name in scene.characters:

            character = self.build_character_state(
                character_name=character_name,
                scene_number=scene.scene_number,
                previous_character=(
                    previous_characters.get(character_name)
                )
            )

            characters.append(character)

        location = self.build_location_state(
            scene.location,
            scene.scene_number,
            previous_location
        )

        props = self.build_prop_states(
            scene.scene_number,
            previous_props
        )

        continuity_requirements = (
            self.build_continuity_requirements(
                scene,
                previous_characters,
                previous_location,
                previous_props
            )
        )

        changes = self.detect_changes(
            scene,
            previous_characters,
            previous_location,
            previous_props
        )

        return SceneContinuity(
            scene_number=scene.scene_number,

            inherited_from_previous_scene=(
                not is_first_scene
            ),

            characters=characters,

            location=location,

            props=props,

            continuity_requirements=continuity_requirements,

            changes_from_previous_scene=changes
        )

    # ================================================================
    # CHARACTER STATE
    # ================================================================

    def build_character_state(
        self,
        character_name,
        scene_number,
        previous_character
    ):

        # If character already existed,
        # preserve the previous state.
        if previous_character:

            return CharacterState(
                name=previous_character.name,
                appearance=previous_character.appearance,
                wardrobe=previous_character.wardrobe,
                emotional_state=(
                    self.update_emotional_state(
                        character_name,
                        scene_number,
                        previous_character.emotional_state
                    )
                ),
                physical_condition=(
                    previous_character.physical_condition
                )
            )

        # Initial character state
        return CharacterState(
            name=character_name,

            appearance=(
                f"Established appearance of {character_name}."
            ),

            wardrobe=(
                f"Established wardrobe of {character_name}."
            ),

            emotional_state=(
                self.initial_emotional_state(
                    character_name,
                    scene_number
                )
            ),

            physical_condition="Normal"
        )

    def initial_emotional_state(
        self,
        character_name,
        scene_number
    ):

        if character_name == "Sam Bell":
            return "UNEASY"

        if character_name == "Sterling":
            return "CALM"

        if character_name == "Julian":
            return "FOCUSED"

        if character_name == "Ren":
            return "ALERT"

        return "NEUTRAL"

    def update_emotional_state(
        self,
        character_name,
        scene_number,
        previous_state
    ):

        if character_name == "Julian":
            return "SUSPICIOUS"

        if character_name == "Ren":
            return "ALERT"

        return previous_state

    # ================================================================
    # LOCATION STATE
    # ================================================================

    def build_location_state(
        self,
        location_name,
        scene_number,
        previous_location
    ):

        # Preserve environment if the location remains the same.

        if (
            previous_location
            and previous_location.name == location_name
        ):

            return LocationState(
                name=previous_location.name,
                time_of_day=previous_location.time_of_day,
                weather=previous_location.weather,
                lighting=previous_location.lighting,
                atmosphere=previous_location.atmosphere
            )

        # Initial environment

        if location_name == "The Old Docks":

            return LocationState(
                name=location_name,
                time_of_day="Pre-dawn",
                weather="Cold and damp",
                lighting="Dim natural light",
                atmosphere="Quiet and uneasy"
            )

        if location_name == "Dock Edge":

            return LocationState(
                name=location_name,
                time_of_day="Early morning",
                weather="Cold and damp",
                lighting="Low natural light",
                atmosphere="Quiet and foreboding"
            )

        if location_name == "Julian's Office":

            return LocationState(
                name=location_name,
                time_of_day="Night",
                weather="Cold and dry",
                lighting="Low desk-lamp lighting",
                atmosphere="Dark and investigative"
            )

        return LocationState(
            name=location_name,
            time_of_day="Unspecified",
            weather="Unspecified",
            lighting="Unspecified",
            atmosphere="Unspecified"
        )

    # ================================================================
    # PROP STATE
    # ================================================================

    def build_prop_states(
        self,
        scene_number,
        previous_props
    ):

        props = []

        if scene_number == 4:

            catalog_document = PropState(
                name="Catalog document",
                appearance=(
                    "Aged paper document with "
                    "subtle handwritten and printed markings."
                ),
                state="Active investigation"
            )

            props.append(catalog_document)

            case_records = PropState(
                name="Case records",
                appearance="Old investigative records.",
                state="Active investigation"
            )

            props.append(case_records)

            desk = PropState(
                name="Desk",
                appearance="Established office desk.",
                state="Existing"
            )

            props.append(desk)

        else:

            for prop in previous_props.values():
                props.append(prop)

        return props

    # ================================================================
    # CONTINUITY REQUIREMENTS
    # ================================================================

    def build_continuity_requirements(
        self,
        scene,
        previous_characters,
        previous_location,
        previous_props
    ):

        requirements = []

        # Character continuity

        for character in scene.characters:

            if character in previous_characters:

                requirements.append(
                    f"Maintain visual identity of {character}."
                )

                requirements.append(
                    f"Maintain wardrobe continuity for {character}."
                )

        # Location continuity

        if previous_location:

            if previous_location.name == scene.location:

                requirements.append(
                    "Preserve the established environment "
                    "of the previous scene."
                )

                requirements.append(
                    "Do not arbitrarily change lighting or weather."
                )

        # Scene-specific continuity

        if scene.scene_number == 4:

            requirements.append(
                "Maintain continuity of the catalog document."
            )

            requirements.append(
                "Do not reveal document details before "
                "the intended close-up."
            )

            requirements.append(
                "Avoid unnecessary character movement."
            )

        return requirements

    # ================================================================
    # CHANGE DETECTION
    # ================================================================

    def detect_changes(
        self,
        scene,
        previous_characters,
        previous_location,
        previous_props
    ):

        changes = []

        # New characters

        for character in scene.characters:

            if character not in previous_characters:

                changes.append(
                    f"{character} enters the story state."
                )

        # Location change

        if (
            previous_location
            and previous_location.name != scene.location
        ):

            changes.append(
                f"Location changes from "
                f"{previous_location.name} "
                f"to {scene.location}."
            )

        # First scene

        if not previous_location:

            changes.append(
                "Initial scene establishes the episode state."
            )

        return changes