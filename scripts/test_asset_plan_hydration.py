from app.assets.registry import (
    AssetRegistry,
)

from app.assets.resolver import (
    AssetResolver,
)

from app.models.asset import (
    AssetPlan,
    AssetReference,
    SceneAssetPlan,
    ShotAssetPlan,
)

from app.models.asset_registry import (
    AssetRecord,
    AssetRole,
    AssetStatus,
    RegistryAssetType,
)


def make_reference(
    asset_id: str,
    entity_id: str,
    asset_type: str,
) -> AssetReference:

    return AssetReference(
        asset_id=asset_id,
        entity_id=entity_id,
        asset_type=asset_type,
        name=entity_id,
        purpose="Master reference",
        required=True,
        master_reference_required=True,
        reference_path=None,
    )


def main():

    print()
    print(
        "BATCH 11F.2 — ASSET PLAN HYDRATION"
    )
    print(
        "========================================"
    )

    character = make_reference(
        asset_id=(
            "ASSET_CHAR_TEST_MASTER"
        ),
        entity_id="CHAR_TEST",
        asset_type="CHARACTER",
    )

    location = make_reference(
        asset_id=(
            "ASSET_LOC_TEST_MASTER"
        ),
        entity_id="LOC_TEST",
        asset_type="LOCATION",
    )

    prop = make_reference(
        asset_id=(
            "ASSET_PROP_TEST_MASTER"
        ),
        entity_id="PROP_TEST",
        asset_type="PROP",
    )

    plan = AssetPlan(
        episode_id="EP_TEST",
        title="Hydration Test",
        assets=[
            character,
            location,
            prop,
        ],
        scenes=[
            SceneAssetPlan(
                scene_number=1,
                assets=[
                    character.model_copy(
                        deep=True
                    ),
                    location.model_copy(
                        deep=True
                    ),
                    prop.model_copy(
                        deep=True
                    ),
                ],
                shots=[
                    ShotAssetPlan(
                        shot_id=(
                            "EP_TEST-S01-SHOT01"
                        ),
                        assets=[
                            character.model_copy(
                                deep=True
                            ),
                            location.model_copy(
                                deep=True
                            ),
                        ],
                    ),
                    ShotAssetPlan(
                        shot_id=(
                            "EP_TEST-S01-SHOT02"
                        ),
                        assets=[
                            prop.model_copy(
                                deep=True
                            ),
                        ],
                    ),
                ],
            )
        ],
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
                "assets/characters/"
                "CHAR_TEST/master_v1.png"
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
                AssetStatus.APPROVED
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
                "ASSET_LOC_TEST_MASTER_V1"
            ),
            entity_id="LOC_TEST",
            asset_type=(
                RegistryAssetType.LOCATION
            ),
            role=(
                AssetRole.MASTER_REFERENCE
            ),
            version=1,
            status=(
                AssetStatus.APPROVED
            ),
            reference_path=(
                "assets/locations/"
                "LOC_TEST/master_v1.png"
            ),
        )
    )

    resolver = AssetResolver(
        registry=registry
    )

    resolution_report = (
        resolver.resolve_plan(
            plan
        )
    )

    assert (
        resolution_report.status
        == "BLOCKED"
    )

    hydrated = (
        resolver.hydrate_plan(
            asset_plan=plan,
            resolution_report=(
                resolution_report
            ),
        )
    )

    # ============================================================
    # TEST 1
    # ============================================================

    assert (
        plan.assets[0].reference_path
        is None
    )

    assert (
        plan.scenes[0]
        .assets[0]
        .reference_path
        is None
    )

    print(
        "TEST 1 — source plan unchanged → PASSED"
    )

    # ============================================================
    # TEST 2
    # ============================================================

    assert (
        hydrated.assets[0]
        .asset_id
        ==
        "ASSET_CHAR_TEST_MASTER"
    )

    assert (
        hydrated.assets[0]
        .reference_path
        ==
        "assets/characters/"
        "CHAR_TEST/master_v2.png"
    )

    print(
        "TEST 2 — highest approved path "
        "hydrated → PASSED"
    )

    # ============================================================
    # TEST 3
    # ============================================================

    assert (
        hydrated.assets[1]
        .reference_path
        ==
        "assets/locations/"
        "LOC_TEST/master_v1.png"
    )

    print(
        "TEST 3 — location path hydrated → PASSED"
    )

    # ============================================================
    # TEST 4
    # ============================================================

    assert (
        hydrated.assets[2]
        .asset_id
        ==
        "ASSET_PROP_TEST_MASTER"
    )

    assert (
        hydrated.assets[2]
        .reference_path
        is None
    )

    print(
        "TEST 4 — unresolved asset preserved → PASSED"
    )

    # ============================================================
    # TEST 5
    # ============================================================

    scene_assets = (
        hydrated.scenes[0].assets
    )

    assert (
        scene_assets[0]
        .reference_path
        ==
        "assets/characters/"
        "CHAR_TEST/master_v2.png"
    )

    assert (
        scene_assets[1]
        .reference_path
        ==
        "assets/locations/"
        "LOC_TEST/master_v1.png"
    )

    assert (
        scene_assets[2]
        .reference_path
        is None
    )

    print(
        "TEST 5 — scene assets hydrated → PASSED"
    )

    # ============================================================
    # TEST 6
    # ============================================================

    shot_1_assets = (
        hydrated.scenes[0]
        .shots[0]
        .assets
    )

    assert (
        shot_1_assets[0]
        .reference_path
        ==
        "assets/characters/"
        "CHAR_TEST/master_v2.png"
    )

    assert (
        shot_1_assets[1]
        .reference_path
        ==
        "assets/locations/"
        "LOC_TEST/master_v1.png"
    )

    assert (
        hydrated.scenes[0]
        .shots[1]
        .assets[0]
        .reference_path
        is None
    )

    print(
        "TEST 6 — shot assets hydrated → PASSED"
    )

    # ============================================================
    # TEST 7
    # ============================================================

    all_logical_ids = [
        asset.asset_id
        for asset
        in hydrated.assets
    ]

    assert (
        "ASSET_CHAR_TEST_MASTER_V2"
        not in all_logical_ids
    )

    assert (
        "ASSET_CHAR_TEST_MASTER"
        in all_logical_ids
    )

    print(
        "TEST 7 — logical asset IDs preserved → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 11F.2 ASSET PLAN HYDRATION PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()