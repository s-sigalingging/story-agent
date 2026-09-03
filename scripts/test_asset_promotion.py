import tempfile
from pathlib import Path

from app.assets.promotion import (
    AssetPromotionService,
)

from app.assets.registry import (
    AssetRegistry,
)

from app.assets.store import (
    AssetStore,
)

from app.models.asset_registry import (
    AssetRole,
    AssetSource,
    AssetStatus,
    RegistryAssetType,
)


def main():

    print()
    print(
        "BATCH 13G.2-C2 — "
        "CANONICAL ASSET PROMOTION CONTRACT"
    )
    print(
        "========================================"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        root = Path(
            temp_dir
        )

        candidate_root = (
            root
            /
            "generated"
        )

        canonical_root = (
            root
            /
            "canonical"
        )

        registry_root = (
            root
            /
            "registry"
        )

        candidate_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ========================================================
        # CANDIDATE V1
        # ========================================================

        candidate_v1 = (
            candidate_root
            /
            "candidate_v1.png"
        )

        candidate_v1.write_bytes(
            b"generated-candidate-v1"
        )

        assert (
            candidate_v1.is_file()
        )

        print(
            "TEST 1 — candidate artifact exists → PASSED"
        )

        # ========================================================
        # REGISTRY / STORE / SERVICE
        # ========================================================

        registry = (
            AssetRegistry()
        )

        store = (
            AssetStore(
                base_path=(
                    str(
                        registry_root
                    )
                )
            )
        )

        service = (
            AssetPromotionService(
                registry=registry,
                store=store,
                registry_id=(
                    "OAKHAVEN_TEST"
                ),
                canonical_root=(
                    str(
                        canonical_root
                    )
                ),
            )
        )

        # ========================================================
        # INVALID CANDIDATE
        # ========================================================

        missing_failed = False

        try:

            service.promote(
                candidate_path=(
                    str(
                        root
                        /
                        "does_not_exist.png"
                    )
                ),
                entity_id=(
                    "CHAR_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .CHARACTER
                ),
            )

        except FileNotFoundError:

            missing_failed = True

        assert (
            missing_failed
            is True
        )

        print(
            "TEST 2 — missing candidate rejected → PASSED"
        )

        # ========================================================
        # FIRST PROMOTION
        # ========================================================

        record_v1 = (
            service.promote(
                candidate_path=(
                    str(
                        candidate_v1
                    )
                ),
                entity_id=(
                    "CHAR_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .CHARACTER
                ),
                role=(
                    AssetRole
                    .MASTER_REFERENCE
                ),
                source=(
                    AssetSource
                    .GENERATED
                ),
                metadata={
                    "provider": (
                        "TEST_PROVIDER"
                    ),
                    "generation_request_id": (
                        "REQ_TEST_V1"
                    ),
                    "generation_attempt_id": (
                        "ATTEMPT_TEST_V1"
                    ),
                    "generation_output_id": (
                        "OUTPUT_TEST_V1"
                    ),
                    "promotion_note": (
                        "Human approved test candidate."
                    ),
                },
            )
        )

        assert (
            record_v1.version
            == 1
        )

        print(
            "TEST 3 — first promotion becomes V1 → PASSED"
        )

        assert (
            record_v1.status
            == AssetStatus.APPROVED
        )

        assert (
            record_v1.source
            == AssetSource.GENERATED
        )

        print(
            "TEST 4 — promoted record is APPROVED generated asset → PASSED"
        )

        # ========================================================
        # CANONICAL PATH
        # ========================================================

        canonical_v1 = Path(
            record_v1.reference_path
        )

        assert (
            canonical_v1.is_file()
        )

        assert (
            canonical_v1
            ==
            (
                canonical_root
                /
                "characters"
                /
                "CHAR_TEST"
                /
                "master_reference_v001.png"
            )
        )

        print(
            "TEST 5 — canonical destination is deterministic → PASSED"
        )

        assert (
            canonical_v1.read_bytes()
            ==
            candidate_v1.read_bytes()
        )

        print(
            "TEST 6 — candidate bytes copied losslessly → PASSED"
        )

        assert (
            candidate_v1.is_file()
        )

        assert (
            candidate_v1.read_bytes()
            ==
            b"generated-candidate-v1"
        )

        print(
            "TEST 7 — source candidate remains untouched → PASSED"
        )

        # ========================================================
        # PROVENANCE
        # ========================================================

        assert (
            record_v1.metadata[
                "source_artifact_path"
            ]
            ==
            str(
                candidate_v1
            )
        )

        assert (
            record_v1.metadata[
                "provider"
            ]
            ==
            "TEST_PROVIDER"
        )

        assert (
            record_v1.metadata[
                "generation_request_id"
            ]
            ==
            "REQ_TEST_V1"
        )

        print(
            "TEST 8 — generation provenance preserved → PASSED"
        )

        # ========================================================
        # REGISTRY
        # ========================================================

        registered_v1 = (
            registry.get(
                record_v1.asset_id
            )
        )

        assert (
            registered_v1
            is not None
        )

        assert (
            registered_v1.status
            == AssetStatus.APPROVED
        )

        print(
            "TEST 9 — promoted record registered → PASSED"
        )

        approved = (
            registry.approved_for_entity(
                entity_id=(
                    "CHAR_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .CHARACTER
                ),
                role=(
                    AssetRole
                    .MASTER_REFERENCE
                ),
            )
        )

        assert (
            len(
                approved
            )
            == 1
        )

        assert (
            approved[0].asset_id
            ==
            record_v1.asset_id
        )

        print(
            "TEST 10 — V1 is active approved master → PASSED"
        )

        # ========================================================
        # PERSISTENCE
        # ========================================================

        assert (
            store.exists(
                "OAKHAVEN_TEST"
            )
            is True
        )

        loaded_snapshot = (
            store.load(
                "OAKHAVEN_TEST"
            )
        )

        assert (
            loaded_snapshot
            is not None
        )

        restored_registry = (
            AssetRegistry(
                snapshot=(
                    loaded_snapshot
                )
            )
        )

        restored_v1 = (
            restored_registry.get(
                record_v1.asset_id
            )
        )

        assert (
            restored_v1
            is not None
        )

        assert (
            restored_v1.reference_path
            ==
            record_v1.reference_path
        )

        print(
            "TEST 11 — registry persists and reloads → PASSED"
        )

        # ========================================================
        # CANDIDATE V2
        # ========================================================

        candidate_v2 = (
            candidate_root
            /
            "candidate_v2.png"
        )

        candidate_v2.write_bytes(
            b"generated-candidate-v2"
        )

        record_v2 = (
            service.promote(
                candidate_path=(
                    str(
                        candidate_v2
                    )
                ),
                entity_id=(
                    "CHAR_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .CHARACTER
                ),
                role=(
                    AssetRole
                    .MASTER_REFERENCE
                ),
                source=(
                    AssetSource
                    .GENERATED
                ),
                metadata={
                    "provider": (
                        "TEST_PROVIDER"
                    ),
                    "generation_request_id": (
                        "REQ_TEST_V2"
                    ),
                },
            )
        )

        assert (
            record_v2.version
            == 2
        )

        print(
            "TEST 12 — second promotion becomes V2 → PASSED"
        )

        # ========================================================
        # SUPERSESSION
        # ========================================================

        current_v1 = (
            registry.get(
                record_v1.asset_id
            )
        )

        assert (
            current_v1.status
            == AssetStatus.SUPERSEDED
        )

        assert (
            record_v2.status
            == AssetStatus.APPROVED
        )

        assert (
            record_v2.supersedes_asset_id
            ==
            record_v1.asset_id
        )

        print(
            "TEST 13 — V2 supersedes V1 → PASSED"
        )

        assert (
            canonical_v1.is_file()
        )

        assert (
            Path(
                record_v2.reference_path
            ).is_file()
        )

        print(
            "TEST 14 — superseded V1 physical asset remains available → PASSED"
        )

        # ========================================================
        # ACTIVE MASTER
        # ========================================================

        approved_after_v2 = (
            registry.approved_for_entity(
                entity_id=(
                    "CHAR_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .CHARACTER
                ),
                role=(
                    AssetRole
                    .MASTER_REFERENCE
                ),
            )
        )

        assert (
            len(
                approved_after_v2
            )
            == 1
        )

        assert (
            approved_after_v2[0]
            .asset_id
            ==
            record_v2.asset_id
        )

        print(
            "TEST 15 — V2 becomes sole active approved master → PASSED"
        )

        # ========================================================
        # PERSISTED SUPERSESSION
        # ========================================================

        reloaded_snapshot = (
            store.load(
                "OAKHAVEN_TEST"
            )
        )

        assert (
            reloaded_snapshot
            is not None
        )

        reloaded_registry = (
            AssetRegistry(
                snapshot=(
                    reloaded_snapshot
                )
            )
        )

        assert (
            reloaded_registry.get(
                record_v1.asset_id
            ).status
            ==
            AssetStatus.SUPERSEDED
        )

        assert (
            reloaded_registry.get(
                record_v2.asset_id
            ).status
            ==
            AssetStatus.APPROVED
        )

        print(
            "TEST 16 — supersession persists across reload → PASSED"
        )

        # ========================================================
        # NEXT VERSION FROM ALL FAMILY RECORDS
        # ========================================================

        candidate_v3 = (
            candidate_root
            /
            "candidate_v3.png"
        )

        candidate_v3.write_bytes(
            b"generated-candidate-v3"
        )

        record_v3 = (
            service.promote(
                candidate_path=(
                    str(
                        candidate_v3
                    )
                ),
                entity_id=(
                    "CHAR_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .CHARACTER
                ),
            )
        )

        assert (
            record_v3.version
            == 3
        )

        assert (
            record_v3.supersedes_asset_id
            ==
            record_v2.asset_id
        )

        print(
            "TEST 17 — versioning continues across superseded history → PASSED"
        )

        # ========================================================
        # COLLISION SAFETY
        # ========================================================

        collision_path = (
            canonical_root
            /
            "locations"
            /
            "LOC_TEST"
            /
            "master_reference_v001.png"
        )

        collision_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        collision_path.write_bytes(
            b"existing-canonical-file"
        )

        location_candidate = (
            candidate_root
            /
            "location_candidate.png"
        )

        location_candidate.write_bytes(
            b"location-candidate"
        )

        collision_failed = False

        try:

            service.promote(
                candidate_path=(
                    str(
                        location_candidate
                    )
                ),
                entity_id=(
                    "LOC_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .LOCATION
                ),
            )

        except FileExistsError:

            collision_failed = True

        assert (
            collision_failed
            is True
        )

        assert (
            collision_path.read_bytes()
            ==
            b"existing-canonical-file"
        )

        assert (
            registry.find(
                entity_id=(
                    "LOC_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .LOCATION
                ),
                role=(
                    AssetRole
                    .MASTER_REFERENCE
                ),
            )
            ==
            []
        )

        print(
            "TEST 18 — canonical collision rejected safely → PASSED"
        )

        # ========================================================
        # EMPTY CANDIDATE
        # ========================================================

        empty_candidate = (
            candidate_root
            /
            "empty.png"
        )

        empty_candidate.write_bytes(
            b""
        )

        empty_failed = False

        try:

            service.promote(
                candidate_path=(
                    str(
                        empty_candidate
                    )
                ),
                entity_id=(
                    "PROP_TEST"
                ),
                asset_type=(
                    RegistryAssetType
                    .PROP
                ),
            )

        except ValueError:

            empty_failed = True

        assert (
            empty_failed
            is True
        )

        print(
            "TEST 19 — empty candidate rejected → PASSED"
        )

        # ========================================================
        # PROVIDER AGNOSTICISM
        # ========================================================

        promotion_source = Path(
            "app/assets/promotion.py"
        ).read_text(
            encoding="utf-8"
        ).lower()

        forbidden_imports = [
            "import google.genai",
            "from google import genai",
            "from google.genai",
            "import replicate",
            "from replicate",
            "import fal_client",
            "from fal_client",
        ]

        assert all(
            forbidden_import
            not in promotion_source
            for forbidden_import
            in forbidden_imports
        )

        print(
            "TEST 20 — promotion service remains provider-agnostic → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13G.2-C2 "
        "CANONICAL ASSET PROMOTION CONTRACT PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()