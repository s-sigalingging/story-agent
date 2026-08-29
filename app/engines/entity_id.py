import re


class EntityIdGenerator:
    """
    Generates deterministic entity IDs.

    Entity IDs contain no knowledge about a specific story world.
    """

    @staticmethod
    def normalize(
        value: str,
    ) -> str:

        value = value.strip().upper()

        value = re.sub(
            r"[^A-Z0-9]+",
            "_",
            value,
        )

        value = value.strip("_")

        return value

    @classmethod
    def character_id(
        cls,
        name: str,
    ) -> str:

        normalized = cls.normalize(name)

        if not normalized:
            raise ValueError(
                "Cannot generate character ID from empty name."
            )

        return f"CHAR_{normalized}"

    @classmethod
    def location_id(
        cls,
        name: str,
    ) -> str:

        normalized = cls.normalize(name)

        if not normalized:
            raise ValueError(
                "Cannot generate location ID from empty name."
            )

        return f"LOC_{normalized}"

    @classmethod
    def prop_id(
        cls,
        name: str,
    ) -> str:

        normalized = cls.normalize(name)

        if not normalized:
            raise ValueError(
                "Cannot generate prop ID from empty name."
            )

        return f"PROP_{normalized}"