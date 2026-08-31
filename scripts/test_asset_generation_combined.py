import json
import tempfile
from pathlib import Path

from app.assets.registry import (
    AssetRegistry,
)

from app.generation import (
    FakeGenerationProvider,
    GenerationRunner,
    GenerationStore,
)

from app.models.asset_registry import (
    AssetRecord,
    AssetRole,
    AssetStatus,
    RegistryAssetType,
)

from app.models.episode import (
    Episode,
)

from app.orchestrator.episode_orchestrator import (
    EpisodeOrchestrator,
)


# ================================================================
# TYPE MAPPING
# ================================================================


TYPE_MAP = {
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


# ================================================================
# SOURCE EPISODE
# ================================================================


def load_source_episode(
    path: str,
) -> Episode:

    episode_path = Path(
        path
    )

    if not episode_path.exists():

        raise FileNotFoundError(
            "Source episode was not found: "
            f"{episode_path}"
        )

    with episode_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        payload = json.load(
            file
        )

    return Episode(
        **payload
    )


# ================================================================
# STAGE HELPER
# ================================================================


def get_stage(
    result: dict,
    stage_name: str,
) -> dict:

    for stage in result[
        "stages"
    ]:

        if (
            stage["stage"]
            == stage_name
        ):

            return stage

    raise AssertionError(
        f"Stage not found: {stage_name}"
    )


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 12H.4 — "
        "ASSET + GENERATION COMBINED PATH"
    )
    print(
        "========================================"
    )

    episode = (
        load_source_episode(
            "data/ep001.json"
        )
    )

    # ============================================================
    # DISCOVER LOGICAL ASSET REQUIREMENTS
    #
    # Legacy mode is used only to discover AssetPlanner output.
    # No physical registry is involved yet.
    # ============================================================

    legacy_result = (
        EpisodeOrchestrator()
        .run(
            episode
        )
    )

    assert (
        legacy_result["status"]
        ==
        "WAITING_HUMAN_APPROVAL"
    )

    asset_plan_stage = (
        get_stage(
            legacy_result,
            "ASSET_PLANNING",
        )
    )

    logical_assets = (
        asset_plan_stage[
            "details"
        ][
            "assets"
        ]
    )

    assert (
        len(
            logical_assets
        )
        > 0
    )

    print(
        "TEST 1 — logical asset requirements discovered → PASSED"
    )

    # ============================================================
    # BUILD TEMPORARY PHYSICAL ASSET REGISTRY
    # ============================================================

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_root = Path(
            temp_dir
        )

        asset_root = (
            temp_root
            /
            "references"
        )

        generation_root = (
            temp_root
            /
            "generation"
        )

        output_root = (
            temp_root
            /
            "generated"
        )

        registry = (
            AssetRegistry()
        )

        expected_paths = {}

        physical_ids = set()

        for (
            index,
            asset,
        ) in enumerate(
            logical_assets,
            start=1,
        ):

            asset_type_name = (
                asset[
                    "asset_type"
                ]
            )

            assert (
                asset_type_name
                in TYPE_MAP
            )

            physical_path = (
                asset_root
                /
                f"reference_{index:03d}.png"
            )

            physical_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            physical_path.write_bytes(
                b"fake-approved-reference"
            )

            physical_asset_id = (
                f"{asset['asset_id']}_V1"
            )

            registry.register(
                AssetRecord(
                    asset_id=(
                        physical_asset_id
                    ),
                    entity_id=(
                        asset[
                            "entity_id"
                        ]
                    ),
                    asset_type=(
                        TYPE_MAP[
                            asset_type_name
                        ]
                    ),
                    role=(
                        AssetRole
                        .MASTER_REFERENCE
                    ),
                    version=1,
                    status=(
                        AssetStatus.APPROVED
                    ),
                    reference_path=(
                        str(
                            physical_path
                        )
                    ),
                )
            )

            expected_paths[
                asset[
                    "asset_id"
                ]
            ] = str(
                physical_path
            )

            physical_ids.add(
                physical_asset_id
            )

        assert (
            len(
                expected_paths
            )
            ==
            len(
                logical_assets
            )
        )

        print(
            "TEST 2 — approved physical registry built → PASSED"
        )

        # ========================================================
        # GENERATION ENVIRONMENT
        # ========================================================

        generation_store = (
            GenerationStore(
                base_path=str(
                    generation_root
                )
            )
        )

        provider = (
            FakeGenerationProvider(
                mode="SUCCESS",
                output_root=str(
                    output_root
                ),
            )
        )

        runner = (
            GenerationRunner(
                provider=provider,
                max_attempts=3,
                store=(
                    generation_store
                ),
            )
        )

        # ========================================================
        # FULL COMBINED PIPELINE
        # ========================================================

        orchestrator = (
            EpisodeOrchestrator(
                asset_registry=(
                    registry
                ),
                generation_runner=(
                    runner
                ),
            )
        )

        result = (
            orchestrator.run(
                episode
            )
        )

        # ========================================================
        # TEST 3 — FULL PIPELINE REACHES REVIEW
        # ========================================================

        assert (
            result["status"]
            ==
            "WAITING_KEYFRAME_REVIEW"
        )

        print(
            "TEST 3 — combined pipeline reaches keyframe review → PASSED"
        )

        # ========================================================
        # TEST 4 — ASSET RESOLUTION PASSED
        # ========================================================

        resolution_stage = (
            get_stage(
                result,
                "ASSET_RESOLUTION",
            )
        )

        assert (
            resolution_stage[
                "status"
            ]
            ==
            "PASSED"
        )

        resolutions = (
            resolution_stage[
                "details"
            ][
                "resolutions"
            ]
        )

        assert (
            len(
                resolutions
            )
            ==
            len(
                logical_assets
            )
        )

        assert all(
            item[
                "resolved"
            ]
            is True
            for item
            in resolutions
        )

        print(
            "TEST 4 — all logical assets resolved → PASSED"
        )

        # ========================================================
        # TEST 5 — ASSET VALIDATION READY
        # ========================================================

        validation_stage = (
            get_stage(
                result,
                "ASSET_VALIDATION",
            )
        )

        assert (
            validation_stage[
                "status"
            ]
            ==
            "PRODUCTION_READY"
        )

        validation_results = (
            validation_stage[
                "details"
            ][
                "results"
            ]
        )

        assert all(
            item[
                "ready"
            ]
            is True
            for item
            in validation_results
            if item[
                "required"
            ]
        )

        print(
            "TEST 5 — asset validation production-ready → PASSED"
        )

        # ========================================================
        # TEST 6 — PROMPTS CONTAIN HYDRATED REFERENCES
        # ========================================================

        prompt_stage = (
            get_stage(
                result,
                "PRODUCTION_PROMPTS",
            )
        )

        prompt_assets = []

        for scene in (
            prompt_stage[
                "details"
            ][
                "scenes"
            ]
        ):

            for prompt in (
                scene[
                    "prompts"
                ]
            ):

                prompt_assets.extend(
                    prompt.get(
                        "assets",
                        [],
                    )
                )

        assert (
            len(
                prompt_assets
            )
            > 0
        )

        hydrated_prompt_assets = [
            asset
            for asset
            in prompt_assets
            if asset.get(
                "reference_path"
            )
        ]

        assert (
            len(
                hydrated_prompt_assets
            )
            > 0
        )

        for asset in (
            hydrated_prompt_assets
        ):

            logical_id = (
                asset[
                    "asset_id"
                ]
            )

            assert (
                logical_id
                in expected_paths
            )

            assert (
                asset[
                    "reference_path"
                ]
                ==
                expected_paths[
                    logical_id
                ]
            )

            assert (
                Path(
                    asset[
                        "reference_path"
                    ]
                ).is_file()
            )

        print(
            "TEST 6 — hydrated references reach production prompts → PASSED"
        )

        # ========================================================
        # TEST 7 — GENERATION REQUESTS RECEIVE REFERENCES
        # ========================================================

        request_stage = (
            get_stage(
                result,
                "GENERATION_REQUESTS",
            )
        )

        generation_requests = (
            request_stage[
                "details"
            ][
                "requests"
            ]
        )

        assert (
            len(
                generation_requests
            )
            > 0
        )

        generation_reference_assets = []

        for request in (
            generation_requests
        ):

            generation_reference_assets.extend(
                request[
                    "reference_assets"
                ]
            )

        assert (
            len(
                generation_reference_assets
            )
            > 0
        )

        print(
            "TEST 7 — physical references reach generation requests → PASSED"
        )

        # ========================================================
        # TEST 8 — REFERENCE PATHS ARE EXACTLY REGISTRY PATHS
        # ========================================================

        for asset in (
            generation_reference_assets
        ):

            logical_id = (
                asset[
                    "asset_id"
                ]
            )

            assert (
                logical_id
                in expected_paths
            )

            assert (
                asset[
                    "reference_path"
                ]
                ==
                expected_paths[
                    logical_id
                ]
            )

            assert (
                Path(
                    asset[
                        "reference_path"
                    ]
                ).is_file()
            )

        print(
            "TEST 8 — registry paths preserved exactly → PASSED"
        )

        # ========================================================
        # TEST 9 — LOGICAL IDS REMAIN STABLE
        # ========================================================

        generation_logical_ids = {
            asset[
                "asset_id"
            ]
            for asset
            in generation_reference_assets
        }

        assert (
            generation_logical_ids
            .isdisjoint(
                physical_ids
            )
        )

        assert all(
            logical_id
            in expected_paths
            for logical_id
            in generation_logical_ids
        )

        print(
            "TEST 9 — physical version IDs do not leak downstream → PASSED"
        )

        # ========================================================
        # TEST 10 — PROMPT → REQUEST ASSET MAPPING
        # ========================================================

        prompt_assets_by_shot = {}

        for scene in (
            prompt_stage[
                "details"
            ][
                "scenes"
            ]
        ):

            for prompt in (
                scene[
                    "prompts"
                ]
            ):

                prompt_assets_by_shot[
                    prompt[
                        "shot_id"
                    ]
                ] = {
                    asset[
                        "asset_id"
                    ]: asset[
                        "reference_path"
                    ]
                    for asset
                    in prompt.get(
                        "assets",
                        [],
                    )
                    if asset.get(
                        "reference_path"
                    )
                }

        for request in (
            generation_requests
        ):

            shot_id = (
                request[
                    "shot_id"
                ]
            )

            expected_for_shot = (
                prompt_assets_by_shot[
                    shot_id
                ]
            )

            actual_for_shot = {
                asset[
                    "asset_id"
                ]: asset[
                    "reference_path"
                ]
                for asset
                in request[
                    "reference_assets"
                ]
            }

            assert (
                actual_for_shot
                ==
                expected_for_shot
            )

        print(
            "TEST 10 — prompt-to-generation asset mapping exact → PASSED"
        )

        # ========================================================
        # TEST 11 — KEYFRAME GENERATION PASSED
        # ========================================================

        generation_stage = (
            get_stage(
                result,
                "KEYFRAME_GENERATION",
            )
        )

        assert (
            generation_stage[
                "status"
            ]
            ==
            "PASSED"
        )

        assert (
            generation_stage[
                "details"
            ][
                "failed"
            ]
            == 0
        )

        assert (
            generation_stage[
                "details"
            ][
                "successful"
            ]
            ==
            generation_stage[
                "details"
            ][
                "total_requests"
            ]
        )

        print(
            "TEST 11 — combined keyframe generation succeeds → PASSED"
        )

        # ========================================================
        # TEST 12 — GENERATION LINEAGE PERSISTED
        # ========================================================

        persisted = (
            generation_store
            .list_episode(
                episode.episode_id
            )
        )

        assert (
            len(
                persisted
            )
            ==
            len(
                generation_requests
            )
        )

        assert all(
            record.result
            is not None
            for record
            in persisted
        )

        print(
            "TEST 12 — combined generation lineage persisted → PASSED"
        )

        # ========================================================
        # TEST 13 — FULL STAGE ORDER
        # ========================================================

        stage_names = [
            stage[
                "stage"
            ]
            for stage
            in result[
                "stages"
            ]
        ]

        required_order = [
            "ASSET_PLANNING",
            "ASSET_RESOLUTION",
            "ASSET_VALIDATION",
            "PRODUCTION_EXECUTION",
            "PRODUCTION_PROMPTS",
            "GENERATION_REQUESTS",
            "KEYFRAME_GENERATION",
        ]

        indices = [
            stage_names.index(
                stage_name
            )
            for stage_name
            in required_order
        ]

        assert (
            indices
            ==
            sorted(
                indices
            )
        )

        print(
            "TEST 13 — combined stage ordering preserved → PASSED"
        )

        # ========================================================
        # TEST 14 — STILL NO CREATIVE APPROVAL
        # ========================================================

        generation_results = (
            generation_stage[
                "details"
            ][
                "results"
            ]
        )

        assert all(
            generation_result[
                "selected_output_id"
            ]
            is None
            for generation_result
            in generation_results
        )

        assert (
            result[
                "status"
            ]
            ==
            "WAITING_KEYFRAME_REVIEW"
        )

        print(
            "TEST 14 — combined success still requires review → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12H.4 ASSET + GENERATION COMBINED PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()