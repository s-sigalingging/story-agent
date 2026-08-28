import re


class EntityIdGenerator:

    @staticmethod
    def normalize(value: str) -> str:

        value = value.upper()

        value = re.sub(
            r"[^A-Z0-9]+",
            "_",
            value
        )

        value = value.strip("_")

        return value

    @classmethod
    def character_id(cls, name: str) -> str:

        return f"CHAR_{cls.normalize(name)}"

    @classmethod
    def location_id(cls, name: str) -> str:

        return f"LOC_{cls.normalize(name)}"

    @classmethod
    def prop_id(cls, name: str) -> str:

        return f"PROP_{cls.normalize(name)}"