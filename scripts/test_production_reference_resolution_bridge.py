import json
import tempfile
from pathlib import Path

from app.assets.registry import (
    AssetRegistry,
)

from app.generation.request_compiler import (
    GenerationRequestCompiler,
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

from app.models.prompt import (
    EpisodeProductionPrompts,
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


def load_episode() -> Episode:

    payload = json.loads(
        Path(
            "data/ep001.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    return Episode(
        **payload
    )


# ================================================================
# STAGE HELPERS
# ================================================================


def get_stage(
    result: dict,
    stage_name: str,
) -> dict:

    for stage in result["stages"]:

        if (
            stage["stage"]
            == stage_name
        ):

            return stage

    raise AssertionError(
        f"Stage not found: {stage_name}"
    )


def get_prompt_list(
    result: dict,
) -> list:

    stage = get_stage(
        result,
        "PRODUCTION_PROMPTS",
    )

    prompts = []

    for scene in (
        stage["details"]["scenes"]
    ):

        prompts.extend(
            scene["prompts"]
        )

    return prompts


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 13G.2-A — "
        "PRODUCTION REFERENCE RESOLUTION BRIDGE"
    )
    print(
        "========================================"
    )

    episode = load_episode()

    # ============================================================
    # DISCOVER REAL EP001 LOGICAL REQUIREMENTS
    # ============================================================

    legacy_result = (
        EpisodeOrchestrator()
        .run(
            episode
        )
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

    assert logical_assets

    print(
        "TEST 1 — EP001 logical assets discovered → PASSED"
    )

    # ============================================================
    # TEMPORARY APPROVED PHYSICAL REGISTRY
    # ============================================================

    with tempfile.TemporaryDirectory() as temp_dir:

        root = Path(
            temp_dir
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
                root
                /
                "references"
                /
                f"reference_{index:03d}.png"
            )

            physical_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            physical_path.write_bytes(
                b"approved-test-reference"
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
            ] = (
                str(
                    physical_path
                )
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
        # RUN REAL EP001 PIPELINE THROUGH PRODUCTION PROMPTS
        #
        # No GenerationRunner is supplied.
        #
        # This batch intentionally tests the bridge offline.
        # GenerationRequestCompiler is invoked explicitly after
        # production prompt compilation.
        # ========================================================

        result = (
            EpisodeOrchestrator(
                asset_registry=(
                    registry
                )
            )
            .run(
                episode
            )
        )

        # ========================================================
        # ASSET RESOLUTION
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

        assert resolutions

        assert all(
            item[
                "resolved"
            ]
            is True
            for item
            in resolutions
        )

        print(
            "TEST 3 — all EP001 assets resolved → PASSED"
        )

        # ========================================================
        # PRODUCTION PROMPTS
        # ========================================================

        prompt_stage = (
            get_stage(
                result,
                "PRODUCTION_PROMPTS",
            )
        )

        prompt_package = (
            EpisodeProductionPrompts(
                **prompt_stage[
                    "details"
                ]
            )
        )

        prompts = (
            get_prompt_list(
                result
            )
        )

        assert prompts

        assert (
            prompt_package.total_shots
            ==
            len(
                prompts
            )
        )

        print(
            "TEST 4 — production prompts compiled → PASSED"
        )

        # ========================================================
        # HYDRATED PHYSICAL PATHS
        # ========================================================

        prompt_assets = []

        for prompt in prompts:

            prompt_assets.extend(
                prompt.get(
                    "assets",
                    [],
                )
            )

        assert prompt_assets

        assert all(
            asset.get(
                "reference_path"
            )
            for asset
            in prompt_assets
        )

        for asset in prompt_assets:

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
                )
                .is_file()
            )

        print(
            "TEST 5 — hydrated physical paths reach prompts → PASSED"
        )

        # ========================================================
        # REFERENCE USAGE SEMANTICS
        # ========================================================

        prompt_usages = []

        for prompt in prompts:

            usages = (
                prompt.get(
                    "reference_usages",
                    [],
                )
            )

            assets = (
                prompt.get(
                    "assets",
                    [],
                )
            )

            assert (
                len(
                    usages
                )
                ==
                len(
                    assets
                )
            )

            prompt_usages.extend(
                usages
            )

        assert prompt_usages

        print(
            "TEST 6 — shot reference usages compiled → PASSED"
        )

        # ========================================================
        # LOGICAL ASSET LINKAGE
        # ========================================================

        usage_by_asset = {}

        for usage in prompt_usages:

            asset_id = (
                usage[
                    "asset_id"
                ]
            )

            usage_by_asset.setdefault(
                asset_id,
                [],
            ).append(
                usage
            )

        assert usage_by_asset

        assert all(
            logical_id
            in expected_paths
            for logical_id
            in usage_by_asset
        )

        print(
            "TEST 7 — reference semantics remain linked "
            "to logical assets → PASSED"
        )

        # ========================================================
        # EXPLICIT OFFLINE PRODUCTION → GENERATION BRIDGE
        # ========================================================

        request_compiler = (
            GenerationRequestCompiler()
        )

        generation_request_models = (
            request_compiler.compile(
                prompt_package
            )
        )

        assert generation_request_models

        generation_requests = [
            request.model_dump(
                mode="json"
            )
            for request
            in generation_request_models
        ]

        assert (
            len(
                generation_requests
            )
            ==
            prompt_package.total_shots
        )

        print(
            "TEST 8 — generation requests compiled offline → PASSED"
        )

        # ========================================================
        # PHYSICAL REFERENCES
        # ========================================================

        generation_references = []

        for request in (
            generation_requests
        ):

            generation_references.extend(
                request[
                    "reference_assets"
                ]
            )

        assert generation_references

        for reference in (
            generation_references
        ):

            logical_id = (
                reference[
                    "asset_id"
                ]
            )

            assert (
                logical_id
                in expected_paths
            )

            assert (
                reference[
                    "reference_path"
                ]
                ==
                expected_paths[
                    logical_id
                ]
            )

            assert (
                Path(
                    reference[
                        "reference_path"
                    ]
                )
                .is_file()
            )

        print(
            "TEST 9 — physical paths reach generation requests → PASSED"
        )

        # ========================================================
        # PHYSICAL VERSION IDS MUST NOT LEAK
        # ========================================================

        downstream_ids = {
            reference[
                "asset_id"
            ]
            for reference
            in generation_references
        }

        assert (
            downstream_ids
            .isdisjoint(
                physical_ids
            )
        )

        assert all(
            logical_id
            in expected_paths
            for logical_id
            in downstream_ids
        )

        print(
            "TEST 10 — registry version IDs do not leak downstream → PASSED"
        )

        # ========================================================
        # REFERENCE ROLES
        # ========================================================

        valid_roles = {
            "CHARACTER",
            "LOCATION",
            "PROP",
            "STYLE",
            "GENERIC",
        }

        assert all(
            reference[
                "reference_role"
            ]
            in valid_roles
            for reference
            in generation_references
        )

        actual_roles = {
            reference[
                "reference_role"
            ]
            for reference
            in generation_references
        }

        # EP001 should exercise at least production character /
        # location / prop reference semantics.
        assert (
            "CHARACTER"
            in actual_roles
        )

        assert (
            "LOCATION"
            in actual_roles
        )

        assert (
            "PROP"
            in actual_roles
        )

        print(
            "TEST 11 — generation reference roles preserved → PASSED"
        )

        # ========================================================
        # PRESERVATION SEMANTICS
        # ========================================================

        assert all(
            len(
                reference.get(
                    "preserve_attributes",
                    [],
                )
            )
            > 0
            for reference
            in generation_references
        )

        print(
            "TEST 12 — preservation semantics survive bridge → PASSED"
        )

        # ========================================================
        # TRANSFORMATION SEMANTICS
        # ========================================================

        assert all(
            isinstance(
                reference.get(
                    "allowed_transformations",
                    [],
                ),
                list,
            )
            for reference
            in generation_references
        )

        assert any(
            reference[
                "allowed_transformations"
            ]
            for reference
            in generation_references
        )

        print(
            "TEST 13 — transformation permissions survive bridge → PASSED"
        )

        # ========================================================
        # USAGE INSTRUCTIONS
        # ========================================================

        assert all(
            reference.get(
                "usage_instruction"
            )
            for reference
            in generation_references
        )

        print(
            "TEST 14 — usage instructions survive bridge → PASSED"
        )

        # ========================================================
        # EXACT PROMPT → REQUEST SEMANTIC BRIDGE
        # ========================================================

        prompt_by_shot = {
            prompt[
                "shot_id"
            ]: prompt
            for prompt
            in prompts
        }

        for request in (
            generation_requests
        ):

            shot_id = (
                request[
                    "shot_id"
                ]
            )

            assert (
                shot_id
                in prompt_by_shot
            )

            prompt = (
                prompt_by_shot[
                    shot_id
                ]
            )

            usages = {
                usage[
                    "asset_id"
                ]: usage
                for usage
                in prompt[
                    "reference_usages"
                ]
            }

            for reference in (
                request[
                    "reference_assets"
                ]
            ):

                logical_id = (
                    reference[
                        "asset_id"
                    ]
                )

                assert (
                    logical_id
                    in usages
                )

                usage = (
                    usages[
                        logical_id
                    ]
                )

                assert (
                    reference[
                        "entity_id"
                    ]
                    ==
                    usage[
                        "entity_id"
                    ]
                )

                assert (
                    reference[
                        "reference_role"
                    ]
                    ==
                    usage[
                        "reference_role"
                    ]
                )

                assert (
                    reference[
                        "preserve_attributes"
                    ]
                    ==
                    usage[
                        "preserve_attributes"
                    ]
                )

                assert (
                    reference[
                        "allowed_transformations"
                    ]
                    ==
                    usage[
                        "allowed_transformations"
                    ]
                )

                assert (
                    reference[
                        "usage_instruction"
                    ]
                    ==
                    usage[
                        "usage_instruction"
                    ]
                )

        print(
            "TEST 15 — prompt-to-request semantics "
            "preserved exactly → PASSED"
        )

        # ========================================================
        # DETERMINISTIC REQUEST LINEAGE
        # ========================================================

        request_ids = [
            request[
                "request_id"
            ]
            for request
            in generation_requests
        ]

        assert (
            len(
                request_ids
            )
            ==
            len(
                set(
                    request_ids
                )
            )
        )

        assert all(
            episode.episode_id
            in request_id
            for request_id
            in request_ids
        )

        second_pass = (
            request_compiler.compile(
                prompt_package
            )
        )

        second_request_ids = [
            request.request_id
            for request
            in second_pass
        ]

        assert (
            request_ids
            ==
            second_request_ids
        )

        print(
            "TEST 16 — request lineage remains deterministic → PASSED"
        )

        # ========================================================
        # PROVIDER AGNOSTICISM
        # ========================================================

        serialized_prompts = (
            json.dumps(
                prompts
            )
            .lower()
        )

        serialized_requests = (
            json.dumps(
                generation_requests
            )
            .lower()
        )

        forbidden_provider_terms = [
            "gemini_api_key",
            "google_api_key",
            "replicate_api_token",
            "fal_key",
            "network_enabled",
        ]

        assert all(
            term
            not in serialized_prompts
            for term
            in forbidden_provider_terms
        )

        assert all(
            term
            not in serialized_requests
            for term
            in forbidden_provider_terms
        )

        print(
            "TEST 17 — bridge remains provider-agnostic → PASSED"
        )

        # ========================================================
        # NO GENERATION EXECUTION
        # ========================================================

        stage_names = {
            stage[
                "stage"
            ]
            for stage
            in result[
                "stages"
            ]
        }

        assert (
            "KEYFRAME_GENERATION"
            not in stage_names
        )

        print(
            "TEST 18 — offline bridge performs no generation → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13G.2-A "
        "PRODUCTION REFERENCE RESOLUTION BRIDGE PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()