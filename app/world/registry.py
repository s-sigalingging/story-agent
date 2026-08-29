from typing import Optional

from app.engines.entity_id import (
    EntityIdGenerator,
)
from app.models.episode import Episode
from app.models.world import (
    CharacterDefinition,
    LocationDefinition,
    PropDefinition,
    WorldRegistrySnapshot,
)


class WorldRegistry:
    """
    Canonical registry for story-world entities.

    The registry knows how to register and resolve entities,
    but it does not know anything about a specific story,
    character, location, or episode.

    Story knowledge must always be supplied as data.
    """

    def __init__(
        self,
        snapshot: Optional[
            WorldRegistrySnapshot
        ] = None,
    ):

        if snapshot is None:
            snapshot = (
                WorldRegistrySnapshot()
            )

        self.characters = dict(
            snapshot.characters
        )

        self.locations = dict(
            snapshot.locations
        )

        self.props = dict(
            snapshot.props
        )

    # ================================================================
    # CHARACTER
    # ================================================================

    def register_character(
        self,
        name: str,
    ) -> CharacterDefinition:

        cleaned_name = (
            self._clean_name(name)
        )

        entity_id = (
            EntityIdGenerator.character_id(
                cleaned_name
            )
        )

        existing = self.characters.get(
            entity_id
        )

        if existing:
            self._add_alias(
                aliases=existing.aliases,
                value=cleaned_name,
                canonical_name=existing.name,
            )

            return existing

        entity = CharacterDefinition(
            entity_id=entity_id,
            name=cleaned_name,
        )

        self.characters[
            entity_id
        ] = entity

        return entity

    def resolve_character(
        self,
        name: str,
    ) -> Optional[
        CharacterDefinition
    ]:

        return self._resolve_by_name(
            name=name,
            entities=self.characters,
        )

    # ================================================================
    # LOCATION
    # ================================================================

    def register_location(
        self,
        name: str,
    ) -> LocationDefinition:

        cleaned_name = (
            self._clean_name(name)
        )

        entity_id = (
            EntityIdGenerator.location_id(
                cleaned_name
            )
        )

        existing = self.locations.get(
            entity_id
        )

        if existing:
            self._add_alias(
                aliases=existing.aliases,
                value=cleaned_name,
                canonical_name=existing.name,
            )

            return existing

        entity = LocationDefinition(
            entity_id=entity_id,
            name=cleaned_name,
        )

        self.locations[
            entity_id
        ] = entity

        return entity

    def resolve_location(
        self,
        name: str,
    ) -> Optional[
        LocationDefinition
    ]:

        return self._resolve_by_name(
            name=name,
            entities=self.locations,
        )

    # ================================================================
    # PROP
    # ================================================================

    def register_prop(
        self,
        name: str,
    ) -> PropDefinition:

        cleaned_name = (
            self._clean_name(name)
        )

        entity_id = (
            EntityIdGenerator.prop_id(
                cleaned_name
            )
        )

        existing = self.props.get(
            entity_id
        )

        if existing:
            self._add_alias(
                aliases=existing.aliases,
                value=cleaned_name,
                canonical_name=existing.name,
            )

            return existing

        entity = PropDefinition(
            entity_id=entity_id,
            name=cleaned_name,
        )

        self.props[
            entity_id
        ] = entity

        return entity

    def resolve_prop(
        self,
        name: str,
    ) -> Optional[
        PropDefinition
    ]:

        return self._resolve_by_name(
            name=name,
            entities=self.props,
        )

    # ================================================================
    # EPISODE INGESTION
    # ================================================================

    def ingest_episode(
        self,
        episode: Episode,
    ) -> None:
        """
        Register every explicit entity contained in an episode.

        This function does NOT attempt NLP entity extraction.

        Only entities explicitly declared in structured Episode data
        are registered.
        """

        for scene in episode.scenes:

            for character_name in (
                scene.characters
            ):
                if character_name.strip():
                    self.register_character(
                        character_name
                    )

            if scene.location.strip():
                self.register_location(
                    scene.location
                )

            for prop_name in scene.props:

                if prop_name.strip():
                    self.register_prop(
                        prop_name
                    )

    # ================================================================
    # SNAPSHOT
    # ================================================================

    def snapshot(
        self,
    ) -> WorldRegistrySnapshot:

        return WorldRegistrySnapshot(
            characters=dict(
                self.characters
            ),
            locations=dict(
                self.locations
            ),
            props=dict(
                self.props
            ),
        )

    # ================================================================
    # UTILITIES
    # ================================================================

    def _clean_name(
        self,
        value: str,
    ) -> str:

        cleaned = " ".join(
            value.strip().split()
        )

        if not cleaned:
            raise ValueError(
                "Entity name cannot be empty."
            )

        return cleaned

    def _resolve_by_name(
        self,
        name: str,
        entities: dict,
    ):

        if not name:
            return None

        normalized_query = (
            EntityIdGenerator.normalize(
                name
            )
        )

        for entity in entities.values():

            canonical_normalized = (
                EntityIdGenerator.normalize(
                    entity.name
                )
            )

            if (
                canonical_normalized
                == normalized_query
            ):
                return entity

            for alias in entity.aliases:

                alias_normalized = (
                    EntityIdGenerator.normalize(
                        alias
                    )
                )

                if (
                    alias_normalized
                    == normalized_query
                ):
                    return entity

        return None

    def _add_alias(
        self,
        aliases: list,
        value: str,
        canonical_name: str,
    ) -> None:

        normalized_value = (
            EntityIdGenerator.normalize(
                value
            )
        )

        normalized_canonical = (
            EntityIdGenerator.normalize(
                canonical_name
            )
        )

        if (
            normalized_value
            == normalized_canonical
        ):
            return

        existing_normalized = {
            EntityIdGenerator.normalize(
                alias
            )
            for alias in aliases
        }

        if (
            normalized_value
            not in existing_normalized
        ):
            aliases.append(
                value
            )