import json
import re
from pathlib import Path
from typing import Optional

from app.models.state import (
    WorldStateSnapshot,
)


class WorldStateStore:
    """
    Persistent storage for canonical world state.

    Storage is filesystem-based for now, but the interface is kept
    simple so it can later be replaced by a database, object storage,
    or another persistence backend.

    The store contains no knowledge about a specific story world.
    """

    def __init__(
        self,
        base_path: str = "data/world_state",
    ):

        self.base_path = Path(
            base_path
        )

        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ================================================================
    # LOAD
    # ================================================================

    def load(
        self,
        world_id: str,
    ) -> Optional[
        WorldStateSnapshot
    ]:

        path = self._path_for(
            world_id
        )

        if not path.exists():
            return None

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        return WorldStateSnapshot(
            **data
        )

    # ================================================================
    # SAVE
    # ================================================================

    def save(
        self,
        world_id: str,
        state: WorldStateSnapshot,
    ) -> Path:

        path = self._path_for(
            world_id
        )

        temporary_path = (
            path.with_suffix(
                ".tmp"
            )
        )

        payload = (
            state.model_dump(
                mode="json"
            )
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                indent=2,
                ensure_ascii=False,
            )

        temporary_path.replace(
            path
        )

        return path

    # ================================================================
    # DELETE
    # ================================================================

    def delete(
        self,
        world_id: str,
    ) -> bool:

        path = self._path_for(
            world_id
        )

        if not path.exists():
            return False

        path.unlink()

        return True

    # ================================================================
    # EXISTS
    # ================================================================

    def exists(
        self,
        world_id: str,
    ) -> bool:

        return (
            self._path_for(
                world_id
            ).exists()
        )

    # ================================================================
    # PATH
    # ================================================================

    def _path_for(
        self,
        world_id: str,
    ) -> Path:

        safe_world_id = (
            self._safe_identifier(
                world_id
            )
        )

        return (
            self.base_path
            / f"{safe_world_id}.json"
        )

    def _safe_identifier(
        self,
        value: str,
    ) -> str:

        cleaned = (
            value.strip()
        )

        if not cleaned:
            raise ValueError(
                "world_id cannot be empty."
            )

        cleaned = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            cleaned,
        )

        cleaned = (
            cleaned.strip("_")
        )

        if not cleaned:
            raise ValueError(
                "world_id contains no usable characters."
            )

        return cleaned