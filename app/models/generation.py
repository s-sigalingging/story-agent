from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ================================================================
# GENERATION TYPE
# ================================================================


class GenerationType(
    str,
    Enum,
):
    """
    Type of media generation requested by the production pipeline.
    """

    KEYFRAME = "KEYFRAME"


# ================================================================
# GENERATION STATUS
# ================================================================


class GenerationStatus(
    str,
    Enum,
):
    """
    Technical lifecycle state of one generation attempt/result.

    Creative approval is intentionally not part of this enum.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


# ================================================================
# REFERENCE ASSET
# ================================================================


class GenerationReferenceAsset(
    BaseModel
):
    """
    Physical reference asset supplied to a generation provider.
    """

    asset_id: str

    entity_id: str

    asset_type: str

    name: str

    reference_path: str

    purpose: Optional[
        str
    ] = None

    required: bool = True

    master_reference_required: bool = False


# ================================================================
# OUTPUT SPECIFICATION
# ================================================================


class GenerationOutputSpec(
    BaseModel
):
    """
    Provider-agnostic output requirements.
    """

    width: int = Field(
        default=1024,
        gt=0,
    )

    height: int = Field(
        default=1024,
        gt=0,
    )

    aspect_ratio: str = "1:1"

    output_format: str = "png"


# ================================================================
# GENERATION REQUEST
# ================================================================


class GenerationRequest(
    BaseModel
):
    """
    Provider-agnostic request for one media generation operation.
    """

    request_id: str

    episode_id: str

    shot_id: str

    generation_type: GenerationType

    prompt: str

    negative_prompt: Optional[
        str
    ] = None

    reference_assets: List[
        GenerationReferenceAsset
    ] = Field(
        default_factory=list
    )

    output: GenerationOutputSpec = Field(
        default_factory=(
            GenerationOutputSpec
        )
    )

    metadata: Dict[
        str,
        str,
    ] = Field(
        default_factory=dict
    )


# ================================================================
# GENERATION ERROR
# ================================================================


class GenerationError(
    BaseModel
):
    """
    Structured technical failure information.
    """

    code: str

    message: str

    retryable: bool = False


# ================================================================
# GENERATION OUTPUT
# ================================================================


class GenerationOutput(
    BaseModel
):
    """
    One physical artifact produced by a generation attempt.
    """

    output_id: str

    output_path: str

    media_type: str = "IMAGE"

    mime_type: str = "image/png"

    width: Optional[
        int
    ] = None

    height: Optional[
        int
    ] = None

    metadata: Dict[
        str,
        str,
    ] = Field(
        default_factory=dict
    )


# ================================================================
# GENERATION ATTEMPT
# ================================================================


class GenerationAttempt(
    BaseModel
):
    """
    Technical record for one provider invocation.
    """

    attempt_id: str

    request_id: str

    attempt_number: int = Field(
        ge=1
    )

    provider: str

    status: GenerationStatus

    outputs: List[
        GenerationOutput
    ] = Field(
        default_factory=list
    )

    error: Optional[
        GenerationError
    ] = None

    metadata: Dict[
        str,
        str,
    ] = Field(
        default_factory=dict
    )


# ================================================================
# GENERATION RESULT
# ================================================================


class GenerationResult(
    BaseModel
):
    """
    Aggregate technical result for one GenerationRequest.

    selected_output_id identifies a chosen technical output,
    but does not represent creative approval.
    """

    request_id: str

    episode_id: str

    shot_id: str

    generation_type: GenerationType

    status: GenerationStatus

    attempts: List[
        GenerationAttempt
    ] = Field(
        default_factory=list
    )

    outputs: List[
        GenerationOutput
    ] = Field(
        default_factory=list
    )

    selected_output_id: Optional[
        str
    ] = None

    metadata: Dict[
        str,
        str,
    ] = Field(
        default_factory=dict
    )


# ================================================================
# GENERATION RECORD
# ================================================================


class GenerationRecord(
    BaseModel
):
    """
    Persistent lineage record for one generation request.

    This record groups the immutable request with its latest
    aggregate technical result.

    Persistence does not imply creative approval.
    """

    request: GenerationRequest

    result: Optional[
        GenerationResult
    ] = None


# ================================================================
# GENERATION STORE SNAPSHOT
# ================================================================


class GenerationStoreSnapshot(
    BaseModel
):
    """
    Serializable collection of generation records.

    The store implementation may persist individual records or
    aggregate snapshots. This model provides the canonical
    persistence contract.
    """

    records: Dict[
        str,
        GenerationRecord,
    ] = Field(
        default_factory=dict
    )