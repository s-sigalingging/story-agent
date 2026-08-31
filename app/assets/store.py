import json
import re
from pathlib import Path
from typing import Optional

from app.models.asset_registry import (
    AssetRegistrySnapshot,
)


class AssetStore:
    """
    Filesystem persistence for asset registry snapshots.

    The store does not implement asset lifecycle or lookup logic.
    Those responsibilities belong to AssetRegistry.
    """

    def __init__(
        self,
        base_path: str = (
            "data/asset_registry"
        ),
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
        registry_id: str,
    ) -> Optional[
        AssetRegistrySnapshot
    ]:

        path = self._path_for(
            registry_id
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

        return (
            AssetRegistrySnapshot(
                **data
            )
        )

    # ================================================================
    # SAVE
    # ================================================================

    def save(
        self,
        registry_id: str,
        snapshot: (
            AssetRegistrySnapshot
        ),
    ) -> Path:

        path = self._path_for(
            registry_id
        )

        temporary_path = (
            path.with_suffix(
                ".tmp"
            )
        )

        payload = (
            snapshot.model_dump(
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
        registry_id: str,
    ) -> bool:

        path = self._path_for(
            registry_id
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
        registry_id: str,
    ) -> bool:

        return (
            self._path_for(
                registry_id
            ).exists()
        )

    # ================================================================
    # PATH
    # ================================================================

    def _path_for(
        self,
        registry_id: str,
    ) -> Path:

        safe_registry_id = (
            self._safe_identifier(
                registry_id
            )
        )

        return (
            self.base_path
            /
            f"{safe_registry_id}.json"
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
                "registry_id cannot be empty."
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
                "registry_id contains "
                "no usable characters."
            )

        return cleaned