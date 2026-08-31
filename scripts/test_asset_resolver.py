from app.assets.registry import (
    AssetRegistry,
)

from app.assets.resolver import (
    AssetResolver,
)

from app.models.asset import (
    AssetReference,
)

from app.models.asset_registry import (
    AssetRecord,
    AssetRole,
    AssetSource,
    AssetStatus,
    RegistryAssetType,
)


def make_requirement(
    asset_id: str,
    entity_id: str,
    asset_type: str,
    required: bool = True,
) -> AssetReference:

    return AssetReference(
        asset_id=asset_id,
        entity_id=entity_id,
        asset_type=asset_type,
        name=entity_id,
        purpose="Master reference",
        required=required,
        master_reference_required=True,
    )


registry = AssetRegistry()


# ================================================================
# CHARACTER MASTER FAMILY
# ================================================================

registry.register(
    AssetRecord(
        asset_id=(
            "ASSET_CHAR_TEST_MASTER_V1"
        ),
        entity_id="CHAR_TEST",
        asset_type=(
            RegistryAssetType.CHARACTER
        ),
        role=(
            AssetRole.MASTER_REFERENCE
        ),
        version=1,
        status=(
            AssetStatus.APPROVED
        ),
        reference_path=(
            "assets/characters/"
            "CHAR_TEST/master_v1.png"
        ),
        source=(
            AssetSource.MANUAL
        ),
    )
)


registry.register(
    AssetRecord(
        asset_id=(
            "ASSET_CHAR_TEST_MASTER_V2"
        ),
        entity_id="CHAR_TEST",
        asset_type=(
            RegistryAssetType.CHARACTER
        ),
        role=(
            AssetRole.MASTER_REFERENCE
        ),
        version=2,
        status=(
            AssetStatus.SUPERSEDED
        ),
        reference_path=(
            "assets/characters/"
            "CHAR_TEST/master_v2.png"
        ),
    )
)


registry.register(
    AssetRecord(
        asset_id=(
            "ASSET_CHAR_TEST_MASTER_V3"
        ),
        entity_id="CHAR_TEST",
        asset_type=(
            RegistryAssetType.CHARACTER
        ),
        role=(
            AssetRole.MASTER_REFERENCE
        ),
        version=3,
        status=(
            AssetStatus.APPROVED
        ),
        reference_path=(
            "assets/characters/"
            "CHAR_TEST/master_v3.png"
        ),
    )
)


registry.register(
    AssetRecord(
        asset_id=(
            "ASSET_CHAR_TEST_MASTER_V4"
        ),
        entity_id="CHAR_TEST",
        asset_type=(
            RegistryAssetType.CHARACTER
        ),
        role=(
            AssetRole.MASTER_REFERENCE
        ),
        version=4,
        status=(
            AssetStatus.REVIEW_REQUIRED
        ),
        reference_path=(
            "assets/characters/"
            "CHAR_TEST/master_v4.png"
        ),
    )
)


# ================================================================
# SUPPORTING REFERENCE
# ================================================================

registry.register(
    AssetRecord(
        asset_id=(
            "ASSET_CHAR_TEST_SUPPORT_V1"
        ),
        entity_id="CHAR_TEST",
        asset_type=(
            RegistryAssetType.CHARACTER
        ),
        role=(
            AssetRole.SUPPORTING_REFERENCE
        ),
        version=1,
        status=(
            AssetStatus.APPROVED
        ),
        reference_path=(
            "assets/characters/"
            "CHAR_TEST/support_v1.png"
        ),
    )
)


# ================================================================
# DIFFERENT CHARACTER
# ================================================================

registry.register(
    AssetRecord(
        asset_id=(
            "ASSET_CHAR_OTHER_MASTER_V1"
        ),
        entity_id="CHAR_OTHER",
        asset_type=(
            RegistryAssetType.CHARACTER
        ),
        role=(
            AssetRole.MASTER_REFERENCE
        ),
        version=1,
        status=(
            AssetStatus.APPROVED
        ),
        reference_path=(
            "assets/characters/"
            "CHAR_OTHER/master_v1.png"
        ),
    )
)


# ================================================================
# PROP
# ================================================================

registry.register(
    AssetRecord(
        asset_id=(
            "ASSET_PROP_TEST_MASTER_V7"
        ),
        entity_id="PROP_TEST",
        asset_type=(
            RegistryAssetType.PROP
        ),
        role=(
            AssetRole.MASTER_REFERENCE
        ),
        version=7,
        status=(
            AssetStatus.APPROVED
        ),
        reference_path=(
            "assets/props/"
            "PROP_TEST/master_v7.png"
        ),
    )
)


resolver = AssetResolver(
    registry=registry
)


# ================================================================
# TEST 1 — HIGHEST APPROVED VERSION
# ================================================================

character_requirement = (
    make_requirement(
        asset_id=(
            "ASSET_CHAR_TEST_MASTER"
        ),
        entity_id="CHAR_TEST",
        asset_type="CHARACTER",
    )
)


result = (
    resolver.resolve_requirement(
        character_requirement
    )
)


assert (
    result.resolved
    is True
)


assert (
    result.resolved_asset_id
    ==
    "ASSET_CHAR_TEST_MASTER_V3"
)


assert (
    result.version
    == 3
)


assert (
    result.status
    == AssetStatus.APPROVED
)


# ================================================================
# TEST 2 — SUPPORTING REFERENCE MUST NOT WIN
# ================================================================

assert (
    result.resolved_asset_id
    !=
    "ASSET_CHAR_TEST_SUPPORT_V1"
)


# ================================================================
# TEST 3 — REVIEW REQUIRED MUST NOT WIN
# ================================================================

assert (
    result.resolved_asset_id
    !=
    "ASSET_CHAR_TEST_MASTER_V4"
)


# ================================================================
# TEST 4 — SUPERSEDED MUST NOT WIN
# ================================================================

assert (
    result.resolved_asset_id
    !=
    "ASSET_CHAR_TEST_MASTER_V2"
)


# ================================================================
# TEST 5 — MISSING REQUIRED ASSET
# ================================================================

missing_requirement = (
    make_requirement(
        asset_id=(
            "ASSET_LOC_MISSING_MASTER"
        ),
        entity_id="LOC_MISSING",
        asset_type="LOCATION",
    )
)


missing_result = (
    resolver.resolve_requirement(
        missing_requirement
    )
)


assert (
    missing_result.resolved
    is False
)


assert (
    missing_result.resolved_asset_id
    is None
)


# ================================================================
# TEST 6 — PROP RESOLUTION
# ================================================================

prop_requirement = (
    make_requirement(
        asset_id=(
            "ASSET_PROP_TEST_MASTER"
        ),
        entity_id="PROP_TEST",
        asset_type="PROP",
    )
)


prop_result = (
    resolver.resolve_requirement(
        prop_requirement
    )
)


assert (
    prop_result.resolved
    is True
)


assert (
    prop_result.version
    == 7
)


# ================================================================
# TEST 7 — REQUIRED FAILURE BLOCKS REPORT
# ================================================================

blocked_report = (
    resolver.resolve_requirements(
        episode_id="EP_TEST",
        requirements=[
            character_requirement,
            missing_requirement,
            prop_requirement,
        ],
    )
)


assert (
    blocked_report.status
    == "BLOCKED"
)


assert (
    len(
        blocked_report.resolutions
    )
    == 3
)


# ================================================================
# TEST 8 — ALL REQUIRED RESOLVED
# ================================================================

passing_report = (
    resolver.resolve_requirements(
        episode_id="EP_TEST",
        requirements=[
            character_requirement,
            prop_requirement,
        ],
    )
)


assert (
    passing_report.status
    == "PASSED"
)


# ================================================================
# TEST 9 — OPTIONAL MISSING DOES NOT BLOCK
# ================================================================

optional_requirement = (
    make_requirement(
        asset_id=(
            "ASSET_LOC_OPTIONAL_MASTER"
        ),
        entity_id="LOC_OPTIONAL",
        asset_type="LOCATION",
        required=False,
    )
)


optional_report = (
    resolver.resolve_requirements(
        episode_id="EP_TEST",
        requirements=[
            character_requirement,
            optional_requirement,
        ],
    )
)


assert (
    optional_report.status
    == "PASSED"
)


assert (
    optional_report
    .resolutions[1]
    .resolved
    is False
)


# ================================================================
# TEST 10 — UNKNOWN TYPE MUST FAIL EXPLICITLY
# ================================================================

unknown_requirement = (
    make_requirement(
        asset_id=(
            "ASSET_UNKNOWN_TEST"
        ),
        entity_id="UNKNOWN_TEST",
        asset_type="UNKNOWN",
    )
)


failed = False


try:

    resolver.resolve_requirement(
        unknown_requirement
    )

except ValueError:

    failed = True


assert (
    failed
    is True
)


print()
print(
    "========================================"
)
print(
    "BATCH 11D ASSET RESOLVER PASSED"
)
print(
    "========================================"
)