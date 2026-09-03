from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, Optional

from app.assets.registry import AssetRegistry
from app.assets.store import AssetStore

from app.models.asset_registry import (
    AssetRecord,
    AssetRole,
    AssetSource,
    AssetStatus,
    RegistryAssetType,
)


class AssetPromotionService:
    """
    Promote a reviewed physical artifact into the canonical
    production asset library.

    Responsibilities:

    - validate the candidate artifact
    - determine the next logical asset version
    - copy the artifact into canonical storage
    - preserve the original candidate artifact
    - create an APPROVED AssetRecord
    - supersede the previous APPROVED record
    - persist the updated AssetRegistry snapshot

    The service is provider-agnostic.

    Gemini/FAL/etc. information may be supplied through metadata,
    but the promotion workflow itself has no provider dependency.
    """

    def __init__(
        self,
        registry: AssetRegistry,
        store: AssetStore,
        registry_id: str,
        canonical_root: str = (
            "data/assets/canonical"
        ),
    ):
        if not registry_id.strip():
            raise ValueError(
                "registry_id cannot be empty."
            )

        self.registry = registry
        self.store = store
        self.registry_id = (
            registry_id.strip()
        )

        self.canonical_root = Path(
            canonical_root
        )

    # ============================================================
    # PUBLIC API
    # ============================================================

    def promote(
        self,
        *,
        candidate_path: str,
        entity_id: str,
        asset_type: RegistryAssetType,
        role: AssetRole = (
            AssetRole.MASTER_REFERENCE
        ),
        source: AssetSource = (
            AssetSource.GENERATED
        ),
        metadata: Optional[
            Dict[str, str]
        ] = None,
    ) -> AssetRecord:
        """
        Promote one reviewed candidate artifact.

        A successful promotion creates exactly one new APPROVED
        canonical record.

        If an APPROVED asset already exists in the same logical
        family, that previous record becomes SUPERSEDED.
        """

        normalized_entity_id = (
            entity_id.strip()
        )

        if not normalized_entity_id:
            raise ValueError(
                "entity_id cannot be empty."
            )

        source_path = Path(
            candidate_path
        )

        self._validate_candidate(
            source_path
        )

        family = self.registry.find(
            entity_id=(
                normalized_entity_id
            ),
            asset_type=asset_type,
            role=role,
        )

        next_version = (
            self._next_version(
                family
            )
        )

        previous_approved = [
            record
            for record
            in family
            if (
                record.status
                == AssetStatus.APPROVED
            )
        ]

        previous_active = (
            previous_approved[-1]
            if previous_approved
            else None
        )

        destination_path = (
            self._canonical_path(
                entity_id=(
                    normalized_entity_id
                ),
                asset_type=asset_type,
                role=role,
                version=next_version,
                source_path=source_path,
            )
        )

        if destination_path.exists():
            raise FileExistsError(
                "Canonical promotion destination "
                "already exists: "
                f"{destination_path}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # Copy first.
        #
        # The original candidate remains untouched so generation
        # lineage can still point to the original artifact.
        # --------------------------------------------------------

        shutil.copy2(
            source_path,
            destination_path,
        )

        asset_id = (
            self._build_asset_id(
                entity_id=(
                    normalized_entity_id
                ),
                role=role,
                version=next_version,
            )
        )

        record_metadata = dict(
            metadata or {}
        )

        record_metadata.setdefault(
            "source_artifact_path",
            str(source_path),
        )

        new_record = AssetRecord(
            asset_id=asset_id,
            entity_id=(
                normalized_entity_id
            ),
            asset_type=asset_type,
            role=role,
            version=next_version,
            status=(
                AssetStatus.APPROVED
            ),
            reference_path=(
                str(destination_path)
            ),
            source=source,
            supersedes_asset_id=(
                previous_active.asset_id
                if previous_active
                is not None
                else None
            ),
            metadata=(
                record_metadata
            ),
        )

        # --------------------------------------------------------
        # Mutate registry only after the physical copy succeeded.
        # --------------------------------------------------------

        try:

            self.registry.register(
                new_record
            )

            if (
                previous_active
                is not None
            ):

                superseded_record = (
                    previous_active.model_copy(
                        update={
                            "status": (
                                AssetStatus
                                .SUPERSEDED
                            ),
                        }
                    )
                )

                self.registry.update(
                    superseded_record
                )

            self.store.save(
                registry_id=(
                    self.registry_id
                ),
                snapshot=(
                    self.registry.snapshot()
                ),
            )

        except Exception:

            # ----------------------------------------------------
            # Best-effort rollback of the canonical physical copy.
            #
            # Registry rollback is handled explicitly below.
            # ----------------------------------------------------

            if destination_path.exists():
                destination_path.unlink()

            # Remove the newly registered record if registration
            # succeeded before a later operation failed.
            if (
                self.registry.get(
                    asset_id
                )
                is not None
            ):

                self.registry.remove(
                    asset_id
                )

            # Restore previous active status if we already changed it.
            if (
                previous_active
                is not None
                and
                self.registry.get(
                    previous_active.asset_id
                )
                is not None
            ):

                current_previous = (
                    self.registry.get(
                        previous_active.asset_id
                    )
                )

                if (
                    current_previous.status
                    != previous_active.status
                ):

                    self.registry.update(
                        previous_active
                    )

            raise

        return new_record

    # ============================================================
    # CANDIDATE VALIDATION
    # ============================================================

    @staticmethod
    def _validate_candidate(
        path: Path,
    ) -> None:

        if not path.exists():
            raise FileNotFoundError(
                "Candidate artifact does not exist: "
                f"{path}"
            )

        if not path.is_file():
            raise ValueError(
                "Candidate artifact must be a file: "
                f"{path}"
            )

        if path.stat().st_size <= 0:
            raise ValueError(
                "Candidate artifact cannot be empty: "
                f"{path}"
            )

    # ============================================================
    # VERSIONING
    # ============================================================

    @staticmethod
    def _next_version(
        family: list[
            AssetRecord
        ],
    ) -> int:

        if not family:
            return 1

        return (
            max(
                record.version
                for record
                in family
            )
            + 1
        )

    # ============================================================
    # CANONICAL PATH
    # ============================================================

    def _canonical_path(
        self,
        *,
        entity_id: str,
        asset_type: RegistryAssetType,
        role: AssetRole,
        version: int,
        source_path: Path,
    ) -> Path:

        type_directory = (
            self._type_directory(
                asset_type
            )
        )

        role_name = (
            role.value
            .lower()
        )

        extension = (
            source_path.suffix
            .lower()
        )

        if not extension:
            extension = ".bin"

        filename = (
            f"{role_name}_"
            f"v{version:03d}"
            f"{extension}"
        )

        return (
            self.canonical_root
            /
            type_directory
            /
            entity_id
            /
            filename
        )

    # ============================================================
    # ASSET ID
    # ============================================================

    @staticmethod
    def _build_asset_id(
        *,
        entity_id: str,
        role: AssetRole,
        version: int,
    ) -> str:

        return (
            f"ASSET_"
            f"{entity_id}_"
            f"{role.value}_"
            f"V{version:03d}"
        )

    # ============================================================
    # TYPE DIRECTORY
    # ============================================================

    @staticmethod
    def _type_directory(
        asset_type: RegistryAssetType,
    ) -> str:

        mapping = {
            RegistryAssetType.CHARACTER: (
                "characters"
            ),
            RegistryAssetType.LOCATION: (
                "locations"
            ),
            RegistryAssetType.PROP: (
                "props"
            ),
        }

        if asset_type not in mapping:
            raise ValueError(
                "Unsupported canonical asset type: "
                f"{asset_type}"
            )

        return mapping[
            asset_type
        ]