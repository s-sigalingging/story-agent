from enum import Enum
from typing import Dict, List, Optional

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


# ================================================================
# ASSET TYPE
# ================================================================


class RegistryAssetType(
    str,
    Enum,
):
    """
    Canonical entity-facing asset categories.
    """

    CHARACTER = "CHARACTER"
    LOCATION = "LOCATION"
    PROP = "PROP"


# ================================================================
# ASSET ROLE
# ================================================================


class AssetRole(
    str,
    Enum,
):
    """
    Describes how an asset is intended to be used.
    """

    MASTER_REFERENCE = (
        "MASTER_REFERENCE"
    )

    SUPPORTING_REFERENCE = (
        "SUPPORTING_REFERENCE"
    )


# ================================================================
# ASSET STATUS
# ================================================================


class AssetStatus(
    str,
    Enum,
):
    """
    Lifecycle state of an asset record.
    """

    DRAFT = "DRAFT"

    REVIEW_REQUIRED = (
        "REVIEW_REQUIRED"
    )

    APPROVED = "APPROVED"

    REJECTED = "REJECTED"

    SUPERSEDED = "SUPERSEDED"


# ================================================================
# ASSET SOURCE
# ================================================================


class AssetSource(
    str,
    Enum,
):
    """
    Describes where the asset originated.
    """

    MANUAL = "MANUAL"
    GENERATED = "GENERATED"
    IMPORTED = "IMPORTED"


# ================================================================
# ASSET VALIDATION CODE
# ================================================================


class AssetValidationCode(
    str,
    Enum,
):
    """
    Machine-readable production validation result.
    """

    READY = "READY"

    MISSING_RESOLUTION = (
        "MISSING_RESOLUTION"
    )

    REGISTRY_RECORD_NOT_FOUND = (
        "REGISTRY_RECORD_NOT_FOUND"
    )

    NOT_APPROVED = (
        "NOT_APPROVED"
    )

    MISSING_REFERENCE_PATH = (
        "MISSING_REFERENCE_PATH"
    )

    REFERENCE_NOT_FOUND = (
        "REFERENCE_NOT_FOUND"
    )

    ENTITY_MISMATCH = (
        "ENTITY_MISMATCH"
    )

    TYPE_MISMATCH = (
        "TYPE_MISMATCH"
    )

    ROLE_MISMATCH = (
        "ROLE_MISMATCH"
    )


# ================================================================
# ASSET RECORD
# ================================================================


class AssetRecord(BaseModel):
    """
    Canonical registry record for one physical media asset.

    AssetRecord answers:

        "What actual asset exists?"

    It is intentionally separate from AssetReference, which answers:

        "What asset does production require?"
    """

    asset_id: str

    entity_id: str

    asset_type: RegistryAssetType

    role: AssetRole = (
        AssetRole.MASTER_REFERENCE
    )

    version: int = Field(
        default=1,
        ge=1,
    )

    status: AssetStatus = (
        AssetStatus.DRAFT
    )

    reference_path: Optional[
        str
    ] = None

    source: AssetSource = (
        AssetSource.MANUAL
    )

    supersedes_asset_id: Optional[
        str
    ] = None

    metadata: Dict[
        str,
        str,
    ] = Field(
        default_factory=dict
    )

    @model_validator(
        mode="after"
    )
    def validate_record(
        self,
    ):
        """
        Enforce invariants that are true for every registry backend.
        """

        if not self.asset_id.strip():

            raise ValueError(
                "asset_id cannot be empty."
            )

        if not self.entity_id.strip():

            raise ValueError(
                "entity_id cannot be empty."
            )

        if (
            self.status
            == AssetStatus.APPROVED
        ):

            if (
                self.reference_path
                is None
                or
                not self.reference_path.strip()
            ):

                raise ValueError(
                    "Approved assets require "
                    "a reference_path."
                )

        if (
            self.supersedes_asset_id
            and
            self.supersedes_asset_id
            == self.asset_id
        ):

            raise ValueError(
                "An asset cannot supersede itself."
            )

        return self


# ================================================================
# REGISTRY SNAPSHOT
# ================================================================


class AssetRegistrySnapshot(
    BaseModel
):
    """
    Serializable snapshot of all known asset records.
    """

    records: Dict[
        str,
        AssetRecord,
    ] = Field(
        default_factory=dict
    )


# ================================================================
# RESOLUTION RESULT
# ================================================================


class AssetResolutionResult(
    BaseModel
):
    """
    Result of resolving one production asset requirement.
    """

    requirement_asset_id: str

    entity_id: str

    asset_type: RegistryAssetType

    role: AssetRole

    resolved: bool = False

    resolved_asset_id: Optional[
        str
    ] = None

    reference_path: Optional[
        str
    ] = None

    version: Optional[
        int
    ] = None

    status: Optional[
        AssetStatus
    ] = None

    reason: str = ""


# ================================================================
# EPISODE RESOLUTION
# ================================================================


class AssetResolutionReport(
    BaseModel
):
    """
    Aggregate result for all asset requirements of one episode.
    """

    episode_id: str

    status: str

    resolutions: List[
        AssetResolutionResult
    ] = Field(
        default_factory=list
    )


# ================================================================
# VALIDATION RESULT
# ================================================================


class AssetValidationResult(
    BaseModel
):
    """
    Production-readiness result for one asset requirement.
    """

    requirement_asset_id: str

    entity_id: str

    required: bool

    ready: bool = False

    code: AssetValidationCode

    resolved_asset_id: Optional[
        str
    ] = None

    reference_path: Optional[
        str
    ] = None

    reason: str = ""


# ================================================================
# VALIDATION REPORT
# ================================================================


class AssetValidationReport(
    BaseModel
):
    """
    Aggregate production gate for one episode.
    """

    episode_id: str

    status: str

    results: List[
        AssetValidationResult
    ] = Field(
        default_factory=list
    )