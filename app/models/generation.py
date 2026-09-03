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
# REFERENCE ROLE
# ================================================================


class GenerationReferenceRole(
    str,
    Enum,
):
    """
    Semantic role played by one physical reference during generation.

    This is deliberately separate from the permanent asset registry.

    The same physical asset may be used with different generation
    semantics in different shots.
    """

    CHARACTER = "CHARACTER"
    LOCATION = "LOCATION"
    PROP = "PROP"
    STYLE = "STYLE"
    GENERIC = "GENERIC"


# ================================================================
# REFERENCE TRANSFORMATION
# ================================================================


class GenerationReferenceTransformation(
    str,
    Enum,
):
    """
    Transformations that a provider may apply while preserving the
    semantic identity of a reference.

    These describe permission, not a mandatory action.
    """

    ROTATE = "ROTATE"
    CHANGE_PERSPECTIVE = "CHANGE_PERSPECTIVE"
    CHANGE_VIEWPOINT = "CHANGE_VIEWPOINT"

    REFRAME = "REFRAME"
    RELIGHT = "RELIGHT"

    CHANGE_POSE = "CHANGE_POSE"
    CHANGE_EXPRESSION = "CHANGE_EXPRESSION"

    OPEN_CLOSE = "OPEN_CLOSE"

    ADAPT_TO_INTERACTION = (
        "ADAPT_TO_INTERACTION"
    )


# ================================================================
# REFERENCE ASSET
# ================================================================


class GenerationReferenceAsset(
    BaseModel
):
    """
    Physical reference asset supplied to a generation provider.

    The asset identifies WHAT visual source is available.

    reference_role / preserve_attributes / allowed_transformations /
    usage_instruction describe HOW that source should influence this
    specific generation request.

    This distinction prevents providers from treating the exact pose,
    camera-facing side, or perspective of a master reference as an
    invariant when only its identity should remain invariant.
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

    # ------------------------------------------------------------
    # Generation-time usage semantics
    # ------------------------------------------------------------

    reference_role: Optional[
        GenerationReferenceRole
    ] = None

    preserve_attributes: List[
        str
    ] = Field(
        default_factory=list
    )

    allowed_transformations: List[
        GenerationReferenceTransformation
    ] = Field(
        default_factory=list
    )

    usage_instruction: Optional[
        str
    ] = None


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