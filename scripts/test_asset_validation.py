import tempfile
from pathlib import Path

from app.assets.registry import (
    AssetRegistry,
)

from app.assets.resolver import (
    AssetResolver,
)

from app.assets.validator import (
    AssetValidator,
)

from app.models.asset import (
    AssetReference,
)

from app.models.asset_registry import (
    AssetRecord,
    AssetRole,
    AssetStatus,
    AssetValidationCode,
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


def main():

    print()
    print(
        "BATCH 11E — ASSET VALIDATION"
    )
    print(
        "========================================"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        project_root = Path(
            temp_dir
        )

        assets_dir = (
            project_root
            / "assets"
        )

        assets_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        valid_file = (
            assets_dir
            / "master.png"
        )

        valid_file.write_bytes(
            b"test-asset"
        )

        registry = AssetRegistry()

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
                    "assets/master.png"
                ),
            )
        )

        registry.register(
            AssetRecord(
                asset_id=(
                    "ASSET_PROP_TEST_MASTER_V1"
                ),
                entity_id="PROP_TEST",
                asset_type=(
                    RegistryAssetType.PROP
                ),
                role=(
                    AssetRole.MASTER_REFERENCE
                ),
                version=1,
                status=(
                    AssetStatus.APPROVED
                ),
                reference_path=(
                    "assets/missing.png"
                ),
            )
        )

        resolver = (
            AssetResolver(
                registry=registry
            )
        )

        validator = (
            AssetValidator(
                registry=registry,
                project_root=project_root,
            )
        )

        # TEST 1

        char_requirement = (
            make_requirement(
                asset_id=(
                    "ASSET_CHAR_TEST_MASTER"
                ),
                entity_id="CHAR_TEST",
                asset_type="CHARACTER",
            )
        )

        char_resolution = (
            resolver.resolve_requirement(
                char_requirement
            )
        )

        char_validation = (
            validator.validate_requirement(
                char_requirement,
                char_resolution,
            )
        )

        assert (
            char_validation.ready
            is True
        )

        assert (
            char_validation.code
            ==
            AssetValidationCode.READY
        )

        print(
            "TEST 1 — valid approved asset"
            " → PASSED"
        )

        # TEST 2

        prop_requirement = (
            make_requirement(
                asset_id=(
                    "ASSET_PROP_TEST_MASTER"
                ),
                entity_id="PROP_TEST",
                asset_type="PROP",
            )
        )

        prop_resolution = (
            resolver.resolve_requirement(
                prop_requirement
            )
        )

        prop_validation = (
            validator.validate_requirement(
                prop_requirement,
                prop_resolution,
            )
        )

        assert (
            prop_validation.ready
            is False
        )

        assert (
            prop_validation.code
            ==
            AssetValidationCode
            .REFERENCE_NOT_FOUND
        )

        print(
            "TEST 2 — missing physical file"
            " → PASSED"
        )

        # TEST 3

        missing_requirement = (
            make_requirement(
                asset_id=(
                    "ASSET_LOC_TEST_MASTER"
                ),
                entity_id="LOC_TEST",
                asset_type="LOCATION",
            )
        )

        missing_resolution = (
            resolver.resolve_requirement(
                missing_requirement
            )
        )

        missing_validation = (
            validator.validate_requirement(
                missing_requirement,
                missing_resolution,
            )
        )

        assert (
            missing_validation.ready
            is False
        )

        assert (
            missing_validation.code
            ==
            AssetValidationCode
            .MISSING_RESOLUTION
        )

        print(
            "TEST 3 — missing resolution"
            " → PASSED"
        )

        # TEST 4

        blocked_resolution_report = (
            resolver.resolve_requirements(
                episode_id="EP_TEST",
                requirements=[
                    char_requirement,
                    prop_requirement,
                ],
            )
        )

        blocked_validation_report = (
            validator.validate_report(
                episode_id="EP_TEST",
                requirements=[
                    char_requirement,
                    prop_requirement,
                ],
                resolution_report=(
                    blocked_resolution_report
                ),
            )
        )

        assert (
            blocked_validation_report.status
            == "BLOCKED"
        )

        print(
            "TEST 4 — required failure gate"
            " → PASSED"
        )

        # TEST 5

        ready_resolution_report = (
            resolver.resolve_requirements(
                episode_id="EP_TEST",
                requirements=[
                    char_requirement,
                ],
            )
        )

        ready_validation_report = (
            validator.validate_report(
                episode_id="EP_TEST",
                requirements=[
                    char_requirement,
                ],
                resolution_report=(
                    ready_resolution_report
                ),
            )
        )

        assert (
            ready_validation_report.status
            == "PRODUCTION_READY"
        )

        print(
            "TEST 5 — production ready gate"
            " → PASSED"
        )

        # TEST 6

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

        optional_resolution_report = (
            resolver.resolve_requirements(
                episode_id="EP_TEST",
                requirements=[
                    char_requirement,
                    optional_requirement,
                ],
            )
        )

        optional_validation_report = (
            validator.validate_report(
                episode_id="EP_TEST",
                requirements=[
                    char_requirement,
                    optional_requirement,
                ],
                resolution_report=(
                    optional_resolution_report
                ),
            )
        )

        assert (
            optional_validation_report.status
            == "PRODUCTION_READY"
        )

        assert (
            optional_validation_report
            .results[1]
            .ready
            is False
        )

        print(
            "TEST 6 — optional failure "
            "does not block → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 11E ASSET VALIDATION PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()