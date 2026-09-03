import tempfile
from pathlib import Path

from app.assets.registry import (
    AssetRegistry,
)

from app.assets.store import (
    AssetStore,
)

from app.models.asset_registry import (
    AssetRecord,
    AssetRole,
    AssetSource,
    AssetStatus,
    RegistryAssetType,
)


# ================================================================
# CREATE REGISTRY
# ================================================================

registry = AssetRegistry()


# ================================================================
# REGISTER V1
# ================================================================

v1 = AssetRecord(
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

registry.register(
    v1
)


# ================================================================
# REGISTER V2
# ================================================================

v2 = AssetRecord(
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
        AssetStatus.DRAFT
    ),
)

registry.register(
    v2
)


# ================================================================
# LOOKUP
# ================================================================

records = (
    registry.list_for_entity(
        "CHAR_TEST"
    )
)

assert (
    len(records)
    == 2
)

assert (
    records[0].version
    == 1
)

assert (
    records[1].version
    == 2
)


# ================================================================
# APPROVED LOOKUP
# ================================================================

approved = (
    registry.approved_for_entity(
        entity_id="CHAR_TEST",
        asset_type=(
            RegistryAssetType.CHARACTER
        ),
        role=(
            AssetRole.MASTER_REFERENCE
        ),
    )
)

assert (
    len(approved)
    == 1
)

assert (
    approved[0].asset_id
    == v1.asset_id
)


# ================================================================
# DUPLICATE VERSION MUST FAIL
# ================================================================

failed = False

try:

    registry.register(
        AssetRecord(
            asset_id=(
                "ASSET_CHAR_TEST_OTHER"
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
                AssetStatus.DRAFT
            ),
        )
    )

except ValueError:

    failed = True


assert (
    failed
    is True
)


# ================================================================
# UPDATE
# ================================================================

updated_v2 = (
    v2.model_copy(
        update={
            "status": (
                AssetStatus.APPROVED
            ),
            "reference_path": (
                "assets/characters/"
                "CHAR_TEST/master_v2.png"
            ),
        }
    )
)

registry.update(
    updated_v2
)

assert (
    registry.get(
        v2.asset_id
    ).status
    == AssetStatus.APPROVED
)


# ================================================================
# FILESYSTEM PERSISTENCE
# ================================================================

with tempfile.TemporaryDirectory() as temp_dir:

    store = AssetStore(
        base_path=temp_dir
    )

    path = store.save(
        registry_id=(
            "TEST_REGISTRY"
        ),
        snapshot=(
            registry.snapshot()
        ),
    )

    assert (
        Path(path).exists()
    )

    assert (
        store.exists(
            "TEST_REGISTRY"
        )
        is True
    )

    loaded = store.load(
        "TEST_REGISTRY"
    )

    assert (
        loaded
        is not None
    )

    assert (
        len(
            loaded.records
        )
        == 2
    )

    restored = (
        AssetRegistry(
            snapshot=loaded
        )
    )

    assert (
        restored.get(
            v1.asset_id
        )
        is not None
    )

    assert (
        restored.get(
            v2.asset_id
        ).version
        == 2
    )

    assert (
        store.delete(
            "TEST_REGISTRY"
        )
        is True
    )

    assert (
        store.exists(
            "TEST_REGISTRY"
        )
        is False
    )


print()
print(
    "========================================"
)
print(
    "BATCH 11C ASSET REGISTRY PASSED"
)
print(
    "========================================"
)