from app.models.episode import Episode

from app.models.continuity import EpisodeContinuity

from app.models.state import (
    EpisodeState,
    SceneState,
    CharacterState,
    LocationState,
    PropState
)

from app.engines.entity_id import (
    EntityIdGenerator
)


class StateManager:

    def build_episode_state(
        self,
        episode: Episode,
        continuity: EpisodeContinuity
    ) -> EpisodeState:

        characters = {}

        locations = {}

        props = {}

        scene_states = {}

        # ============================================================
        # PROCESS EACH SCENE
        # ============================================================

        for continuity_scene in continuity.scenes:

            # --------------------------------------------------------
            # Characters
            # --------------------------------------------------------

            scene_characters = {}

            for character in continuity_scene.characters:

                entity_id = (
                    EntityIdGenerator.character_id(
                        character.name
                    )
                )

                character_state = CharacterState(
                    entity_id=entity_id,

                    name=character.name,

                    appearance=character.appearance,

                    wardrobe=character.wardrobe,

                    emotional_state=character.emotional_state,

                    physical_condition=character.physical_condition,

                    reference_required=True,

                    master_character_required=True
                )

                scene_characters[
                    entity_id
                ] = character_state

                # ----------------------------------------------------
                # Update global episode state
                # ----------------------------------------------------

                characters[
                    entity_id
                ] = character_state

            # --------------------------------------------------------
            # Location
            # --------------------------------------------------------

            location_entity_id = (
                EntityIdGenerator.location_id(
                    continuity_scene.location.name
                )
            )

            location = LocationState(
                entity_id=location_entity_id,

                name=continuity_scene.location.name,

                time_of_day=continuity_scene.location.time_of_day,

                weather=continuity_scene.location.weather,

                lighting=continuity_scene.location.lighting,

                atmosphere=continuity_scene.location.atmosphere,

                reference_required=True
            )

            locations[
                location_entity_id
            ] = location

            # --------------------------------------------------------
            # Props
            # --------------------------------------------------------

            scene_props = {}

            for prop in continuity_scene.props:

                prop_entity_id = (
                    EntityIdGenerator.prop_id(
                        prop.name
                    )
                )

                prop_state = PropState(
                    entity_id=prop_entity_id,

                    name=prop.name,

                    appearance=prop.appearance,

                    state=prop.state,

                    reference_required=True
                )

                scene_props[
                    prop_entity_id
                ] = prop_state

                # ----------------------------------------------------
                # Update global episode state
                # ----------------------------------------------------

                props[
                    prop_entity_id
                ] = prop_state

            # --------------------------------------------------------
            # Scene State
            # --------------------------------------------------------

            scene_state = SceneState(
                scene_number=continuity_scene.scene_number,

                characters=scene_characters,

                location=location,

                props=scene_props,

                active_characters=list(
                    scene_characters.keys()
                ),

                active_props=list(
                    scene_props.keys()
                )
            )

            scene_states[
                continuity_scene.scene_number
            ] = scene_state

        # ============================================================
        # BUILD EPISODE STATE
        # ============================================================

        current_scene = 0

        if episode.scenes:

            current_scene = (
                episode.scenes[-1].scene_number
            )

        return EpisodeState(
            episode_id=episode.episode_id,

            title=episode.title,

            current_scene=current_scene,

            characters=characters,

            locations=locations,

            props=props,

            scene_states=scene_states
        )