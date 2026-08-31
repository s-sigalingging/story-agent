from typing import List, Optional

from app.models.asset_registry import (
    AssetRecord,
    AssetRegistrySnapshot,
    AssetRole,
    AssetStatus,
    RegistryAssetType,
)


class AssetRegistry:
    """
    Canonical registry for production media assets.

    The registry manages asset records and lifecycle state.

    It does not perform filesystem persistence.
    Persistence belongs to AssetStore.
    """

    def __init__(
        self,
        snapshot: Optional[
            AssetRegistrySnapshot
        ] = None,
    ):

        if snapshot is None:

            snapshot = (
                AssetRegistrySnapshot()
            )

        self.records = dict(
            snapshot.records
        )

    # ================================================================
    # REGISTER
    # ================================================================

    def register(
        self,
        record: AssetRecord,
    ) -> AssetRecord:
        """
        Register a new asset record.

        Asset IDs are immutable identifiers and may not be silently
        overwritten.
        """

        if (
            record.asset_id
            in self.records
        ):

            raise ValueError(
                "Asset already exists: "
                f"{record.asset_id}"
            )

        self._validate_version_uniqueness(
            record
        )

        self.records[
            record.asset_id
        ] = record

        return record

    # ================================================================
    # GET
    # ================================================================

    def get(
        self,
        asset_id: str,
    ) -> Optional[
        AssetRecord
    ]:

        return (
            self.records.get(
                asset_id
            )
        )

    # ================================================================
    # UPDATE
    # ================================================================

    def update(
        self,
        record: AssetRecord,
    ) -> AssetRecord:
        """
        Replace an existing asset record.

        The asset_id must already exist.
        """

        if (
            record.asset_id
            not in self.records
        ):

            raise ValueError(
                "Cannot update unknown asset: "
                f"{record.asset_id}"
            )

        self._validate_version_uniqueness(
            record,
            exclude_asset_id=(
                record.asset_id
            ),
        )

        self.records[
            record.asset_id
        ] = record

        return record

    # ================================================================
    # REMOVE
    # ================================================================

    def remove(
        self,
        asset_id: str,
    ) -> bool:

        if (
            asset_id
            not in self.records
        ):

            return False

        del self.records[
            asset_id
        ]

        return True

    # ================================================================
    # ENTITY LOOKUP
    # ================================================================

    def list_for_entity(
        self,
        entity_id: str,
    ) -> List[
        AssetRecord
    ]:

        result = [
            record
            for record
            in self.records.values()
            if (
                record.entity_id
                == entity_id
            )
        ]

        return self._sort_records(
            result
        )

    # ================================================================
    # FILTERED LOOKUP
    # ================================================================

    def find(
        self,
        entity_id: Optional[
            str
        ] = None,
        asset_type: Optional[
            RegistryAssetType
        ] = None,
        role: Optional[
            AssetRole
        ] = None,
        status: Optional[
            AssetStatus
        ] = None,
    ) -> List[
        AssetRecord
    ]:

        result = []

        for record in (
            self.records.values()
        ):

            if (
                entity_id is not None
                and
                record.entity_id
                != entity_id
            ):

                continue

            if (
                asset_type is not None
                and
                record.asset_type
                != asset_type
            ):

                continue

            if (
                role is not None
                and
                record.role
                != role
            ):

                continue

            if (
                status is not None
                and
                record.status
                != status
            ):

                continue

            result.append(
                record
            )

        return self._sort_records(
            result
        )

    # ================================================================
    # APPROVED LOOKUP
    # ================================================================

    def approved_for_entity(
        self,
        entity_id: str,
        asset_type: Optional[
            RegistryAssetType
        ] = None,
        role: Optional[
            AssetRole
        ] = None,
    ) -> List[
        AssetRecord
    ]:
        """
        Return only production-eligible APPROVED assets.
        """

        return self.find(
            entity_id=entity_id,
            asset_type=asset_type,
            role=role,
            status=(
                AssetStatus.APPROVED
            ),
        )

    # ================================================================
    # SNAPSHOT
    # ================================================================

    def snapshot(
        self,
    ) -> AssetRegistrySnapshot:

        return (
            AssetRegistrySnapshot(
                records=dict(
                    self.records
                )
            )
        )

    # ================================================================
    # VERSION VALIDATION
    # ================================================================

    def _validate_version_uniqueness(
        self,
        record: AssetRecord,
        exclude_asset_id: Optional[
            str
        ] = None,
    ) -> None:
        """
        Prevent duplicate version numbers for the same logical asset
        family.

        A logical asset family is:

            entity_id
            + asset_type
            + role
        """

        for existing in (
            self.records.values()
        ):

            if (
                exclude_asset_id
                and
                existing.asset_id
                == exclude_asset_id
            ):

                continue

            same_family = (
                existing.entity_id
                == record.entity_id
                and
                existing.asset_type
                == record.asset_type
                and
                existing.role
                == record.role
            )

            if not same_family:

                continue

            if (
                existing.version
                == record.version
            ):

                raise ValueError(
                    "Duplicate asset version "
                    "for logical asset family: "
                    f"{record.entity_id} / "
                    f"{record.asset_type.value} / "
                    f"{record.role.value} / "
                    f"version {record.version}"
                )

    # ================================================================
    # SORTING
    # ================================================================

    def _sort_records(
        self,
        records: List[
            AssetRecord
        ],
    ) -> List[
        AssetRecord
    ]:

        return sorted(
            records,
            key=lambda item: (
                item.entity_id,
                item.asset_type.value,
                item.role.value,
                item.version,
                item.asset_id,
            ),
        )