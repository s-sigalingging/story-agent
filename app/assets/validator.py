from pathlib import Path
from typing import List

from app.assets.registry import (
    AssetRegistry,
)

from app.models.asset import (
    AssetReference,
)

from app.models.asset_registry import (
    AssetResolutionReport,
    AssetResolutionResult,
    AssetRole,
    AssetStatus,
    AssetValidationCode,
    AssetValidationReport,
    AssetValidationResult,
    RegistryAssetType,
)


class AssetValidator:
    """
    Validate whether resolved production assets are ready
    for downstream media generation.
    """

    def __init__(
        self,
        registry: AssetRegistry,
        project_root: Path | None = None,
    ):

        self.registry = registry

        if project_root is None:
            project_root = Path.cwd()

        self.project_root = (
            Path(project_root)
            .resolve()
        )

    # ================================================================
    # SINGLE REQUIREMENT
    # ================================================================

    def validate_requirement(
        self,
        requirement: AssetReference,
        resolution: AssetResolutionResult,
    ) -> AssetValidationResult:

        base = {
            "requirement_asset_id": (
                requirement.asset_id
            ),
            "entity_id": (
                requirement.entity_id
            ),
            "required": (
                requirement.required
            ),
            "resolved_asset_id": (
                resolution.resolved_asset_id
            ),
        }

        if (
            not resolution.resolved
            or
            not resolution.resolved_asset_id
        ):

            return AssetValidationResult(
                **base,
                reference_path=(
                    resolution.reference_path
                ),
                ready=False,
                code=(
                    AssetValidationCode
                    .MISSING_RESOLUTION
                ),
                reason=(
                    "Requirement has no "
                    "resolved asset."
                ),
            )

        record = (
            self.registry.get(
                resolution.resolved_asset_id
            )
        )

        if record is None:

            return AssetValidationResult(
                **base,
                reference_path=(
                    resolution.reference_path
                ),
                ready=False,
                code=(
                    AssetValidationCode
                    .REGISTRY_RECORD_NOT_FOUND
                ),
                reason=(
                    "Resolved asset no longer "
                    "exists in the registry."
                ),
            )

        if (
            record.entity_id
            != requirement.entity_id
        ):

            return AssetValidationResult(
                **base,
                reference_path=(
                    record.reference_path
                ),
                ready=False,
                code=(
                    AssetValidationCode
                    .ENTITY_MISMATCH
                ),
                reason=(
                    "Resolved registry asset "
                    "belongs to a different entity."
                ),
            )

        expected_type = (
            self._registry_asset_type(
                requirement.asset_type
            )
        )

        if (
            record.asset_type
            != expected_type
        ):

            return AssetValidationResult(
                **base,
                reference_path=(
                    record.reference_path
                ),
                ready=False,
                code=(
                    AssetValidationCode
                    .TYPE_MISMATCH
                ),
                reason=(
                    "Resolved registry asset "
                    "has the wrong asset type."
                ),
            )

        if (
            record.role
            != resolution.role
        ):

            return AssetValidationResult(
                **base,
                reference_path=(
                    record.reference_path
                ),
                ready=False,
                code=(
                    AssetValidationCode
                    .ROLE_MISMATCH
                ),
                reason=(
                    "Resolved registry asset "
                    "has the wrong asset role."
                ),
            )

        if (
            record.status
            != AssetStatus.APPROVED
        ):

            return AssetValidationResult(
                **base,
                reference_path=(
                    record.reference_path
                ),
                ready=False,
                code=(
                    AssetValidationCode
                    .NOT_APPROVED
                ),
                reason=(
                    "Resolved asset is not "
                    "currently approved."
                ),
            )

        reference_path = (
            record.reference_path
        )

        if (
            reference_path is None
            or
            not reference_path.strip()
        ):

            return AssetValidationResult(
                **base,
                reference_path=None,
                ready=False,
                code=(
                    AssetValidationCode
                    .MISSING_REFERENCE_PATH
                ),
                reason=(
                    "Resolved asset has no "
                    "reference path."
                ),
            )

        physical_path = (
            self._physical_path(
                reference_path
            )
        )

        if not physical_path.is_file():

            return AssetValidationResult(
                **base,
                reference_path=(
                    reference_path
                ),
                ready=False,
                code=(
                    AssetValidationCode
                    .REFERENCE_NOT_FOUND
                ),
                reason=(
                    "Reference file does not "
                    "exist on disk."
                ),
            )

        return AssetValidationResult(
            **base,
            reference_path=(
                reference_path
            ),
            ready=True,
            code=(
                AssetValidationCode.READY
            ),
            reason=(
                "Asset is production-ready."
            ),
        )

    # ================================================================
    # REPORT
    # ================================================================

    def validate_report(
        self,
        episode_id: str,
        requirements: List[
            AssetReference
        ],
        resolution_report: (
            AssetResolutionReport
        ),
    ) -> AssetValidationReport:

        resolution_map = {
            item.requirement_asset_id: item
            for item
            in resolution_report.resolutions
        }

        results = []
        blocked = False

        for requirement in requirements:

            resolution = (
                resolution_map.get(
                    requirement.asset_id
                )
            )

            if resolution is None:

                resolution = (
                    self._missing_resolution(
                        requirement
                    )
                )

            result = (
                self.validate_requirement(
                    requirement,
                    resolution,
                )
            )

            results.append(
                result
            )

            if (
                requirement.required
                and
                not result.ready
            ):

                blocked = True

        return AssetValidationReport(
            episode_id=episode_id,
            status=(
                "BLOCKED"
                if blocked
                else "PRODUCTION_READY"
            ),
            results=results,
        )

    # ================================================================
    # HELPERS
    # ================================================================

    def _missing_resolution(
        self,
        requirement: AssetReference,
    ) -> AssetResolutionResult:

        return AssetResolutionResult(
            requirement_asset_id=(
                requirement.asset_id
            ),
            entity_id=(
                requirement.entity_id
            ),
            asset_type=(
                self._registry_asset_type(
                    requirement.asset_type
                )
            ),
            role=(
                AssetRole.MASTER_REFERENCE
            ),
            resolved=False,
            reason=(
                "Resolution result missing."
            ),
        )

    def _registry_asset_type(
        self,
        value: str,
    ) -> RegistryAssetType:

        normalized = (
            value
            or ""
        ).strip().upper()

        mapping = {
            "CHARACTER": (
                RegistryAssetType.CHARACTER
            ),
            "LOCATION": (
                RegistryAssetType.LOCATION
            ),
            "PROP": (
                RegistryAssetType.PROP
            ),
        }

        resolved = (
            mapping.get(
                normalized
            )
        )

        if resolved is None:

            raise ValueError(
                "Unsupported production "
                "asset type: "
                f"{value!r}"
            )

        return resolved

    def _physical_path(
        self,
        reference_path: str,
    ) -> Path:

        path = Path(
            reference_path
        )

        if path.is_absolute():
            return path

        return (
            self.project_root
            /
            path
        )