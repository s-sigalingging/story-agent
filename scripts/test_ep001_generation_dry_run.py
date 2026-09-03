import json
import tempfile
from pathlib import Path

from app.assets.registry import AssetRegistry

from app.generation.request_compiler import (
    GenerationRequestCompiler,
)

from app.models.asset_registry import (
    AssetRecord,
    AssetRole,
    AssetStatus,
    RegistryAssetType,
)

from app.models.episode import Episode

from app.orchestrator.episode_orchestrator import (
    EpisodeOrchestrator,
)


# ================================================================
# CONSTANTS
# ================================================================


TYPE_MAP = {
    "CHARACTER": RegistryAssetType.CHARACTER,
    "LOCATION": RegistryAssetType.LOCATION,
    "PROP": RegistryAssetType.PROP,
}


# ================================================================
# HELPERS
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


def has_stage(
    result: dict,
    stage_name: str,
) -> bool:

    return any(
        stage["stage"]
        == stage_name
        for stage
        in result["stages"]
    )


def discover_logical_assets(
    episode: Episode,
) -> list:

    result = (
        EpisodeOrchestrator()
        .run(
            episode
        )
    )

    stage = get_stage(
        result,
        "ASSET_PLANNING",
    )

    return stage[
        "details"
    ][
        "assets"
    ]


def build_registry(
    logical_assets: list,
    root: Path,
):

    registry = AssetRegistry()

    expected_paths = {}

    physical_asset_ids = set()

    for (
        index,
        asset,
    ) in enumerate(
        logical_assets,
        start=1,
    ):

        asset_type = (
            asset[
                "asset_type"
            ]
        )

        assert (
            asset_type
            in TYPE_MAP
        )

        reference_path = (
            root
            /
            "approved"
            /
            f"reference_{index:03d}.png"
        )

        reference_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        reference_path.write_bytes(
            b"offline-approved-reference"
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
                        asset_type
                    ]
                ),
                role=(
                    AssetRole
                    .MASTER_REFERENCE
                ),
                version=1,
                status=(
                    AssetStatus
                    .APPROVED
                ),
                reference_path=(
                    str(
                        reference_path
                    )
                ),
            )
        )

        expected_paths[
            asset[
                "asset_id"
            ]
        ] = str(
            reference_path
        )

        physical_asset_ids.add(
            physical_asset_id
        )

    return (
        registry,
        expected_paths,
        physical_asset_ids,
    )


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 13G.2-B — "
        "EP001 GENERATION DRY-RUN"
    )
    print(
        "========================================"
    )

    episode = load_episode()

    assert (
        episode.episode_id
        == "EP001"
    )

    print(
        "TEST 1 — EP001 loaded → PASSED"
    )

    # ============================================================
    # LEGACY MODE REGRESSION
    # ============================================================

    legacy_result = (
        EpisodeOrchestrator()
        .run(
            episode
        )
    )

    assert (
        legacy_result[
            "status"
        ]
        ==
        "WAITING_HUMAN_APPROVAL"
    )

    assert has_stage(
        legacy_result,
        "PRODUCTION_PROMPTS",
    )

    assert not has_stage(
        legacy_result,
        "GENERATION_REQUESTS",
    )

    assert not has_stage(
        legacy_result,
        "KEYFRAME_GENERATION",
    )

    print(
        "TEST 2 — legacy mode remains unchanged → PASSED"
    )

    # ============================================================
    # LOGICAL ASSETS
    # ============================================================

    logical_assets = (
        discover_logical_assets(
            episode
        )
    )

    assert logical_assets

    print(
        "TEST 3 — EP001 logical assets discovered → PASSED"
    )

    # ============================================================
    # TEMPORARY APPROVED REGISTRY
    # ============================================================

    with tempfile.TemporaryDirectory() as temp_dir:

        root = Path(
            temp_dir
        )

        (
            registry,
            expected_paths,
            physical_asset_ids,
        ) = build_registry(
            logical_assets=(
                logical_assets
            ),
            root=root,
        )

        assert expected_paths

        print(
            "TEST 4 — approved physical registry built → PASSED"
        )

        # ========================================================
        # ACTUAL ORCHESTRATOR DRY-RUN
        # ========================================================

        orchestrator = (
            EpisodeOrchestrator(
                asset_registry=(
                    registry
                ),
                generation_request_compiler=(
                    GenerationRequestCompiler()
                ),
                generation_runner=None,
            )
        )

        result = (
            orchestrator.run(
                episode
            )
        )

        assert (
            result[
                "status"
            ]
            ==
            "GENERATION_READY"
        )

        print(
            "TEST 5 — orchestrator reaches GENERATION_READY → PASSED"
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
            resolution[
                "resolved"
            ]
            is True
            for resolution
            in resolutions
        )

        print(
            "TEST 6 — asset resolution passed → PASSED"
        )

        # ========================================================
        # ASSET VALIDATION
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

        print(
            "TEST 7 — asset validation production-ready → PASSED"
        )

        # ========================================================
        # PRODUCTION EXECUTION
        # ========================================================

        execution_stage = (
            get_stage(
                result,
                "PRODUCTION_EXECUTION",
            )
        )

        assert (
            execution_stage[
                "status"
            ]
            ==
            "PASSED"
        )

        print(
            "TEST 8 — production execution emitted → PASSED"
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

        assert (
            prompt_stage[
                "status"
            ]
            ==
            "PASSED"
        )

        total_shots = (
            prompt_stage[
                "details"
            ][
                "total_shots"
            ]
        )

        assert (
            total_shots
            > 0
        )

        print(
            "TEST 9 — production prompts emitted → PASSED"
        )

        # ========================================================
        # GENERATION REQUESTS
        # ========================================================

        request_stage = (
            get_stage(
                result,
                "GENERATION_REQUESTS",
            )
        )

        assert (
            request_stage[
                "status"
            ]
            ==
            "PASSED"
        )

        generation_requests = (
            request_stage[
                "details"
            ][
                "requests"
            ]
        )

        assert generation_requests

        print(
            "TEST 10 — generation requests emitted → PASSED"
        )

        # ========================================================
        # REQUEST COUNT
        # ========================================================

        assert (
            request_stage[
                "details"
            ][
                "total_requests"
            ]
            ==
            total_shots
        )

        assert (
            len(
                generation_requests
            )
            ==
            total_shots
        )

        print(
            "TEST 11 — request count matches shot count → PASSED"
        )

        # ========================================================
        # REQUEST LINEAGE
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

        print(
            "TEST 12 — request lineage is valid → PASSED"
        )

        # ========================================================
        # PHYSICAL REFERENCES
        # ========================================================

        all_references = [
            reference
            for request
            in generation_requests
            for reference
            in request[
                "reference_assets"
            ]
        ]

        assert all_references

        for reference in (
            all_references
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
            "TEST 13 — resolved physical references reach requests → PASSED"
        )

        # ========================================================
        # REFERENCE SEMANTICS
        # ========================================================

        for reference in (
            all_references
        ):

            assert (
                reference[
                    "reference_role"
                ]
            )

            assert (
                reference[
                    "preserve_attributes"
                ]
            )

            assert isinstance(
                reference[
                    "allowed_transformations"
                ],
                list,
            )

            assert (
                reference[
                    "usage_instruction"
                ]
            )

        print(
            "TEST 14 — reference semantics survive orchestrator boundary → PASSED"
        )

        # ========================================================
        # ROLE COVERAGE
        # ========================================================

        reference_roles = {
            reference[
                "reference_role"
            ]
            for reference
            in all_references
        }

        assert (
            "CHARACTER"
            in reference_roles
        )

        assert (
            "LOCATION"
            in reference_roles
        )

        assert (
            "PROP"
            in reference_roles
        )

        print(
            "TEST 15 — character/location/prop roles preserved → PASSED"
        )

        # ========================================================
        # LOGICAL ID PRESERVATION
        # ========================================================

        downstream_asset_ids = {
            reference[
                "asset_id"
            ]
            for reference
            in all_references
        }

        assert (
            downstream_asset_ids
            .isdisjoint(
                physical_asset_ids
            )
        )

        assert all(
            asset_id
            in expected_paths
            for asset_id
            in downstream_asset_ids
        )

        print(
            "TEST 16 — physical version IDs do not leak → PASSED"
        )

        # ========================================================
        # PROVIDER EXECUTION MUST NOT OCCUR
        # ========================================================

        assert not has_stage(
            result,
            "KEYFRAME_GENERATION",
        )

        print(
            "TEST 17 — provider execution not performed → PASSED"
        )

        # ========================================================
        # NO GENERATION RESULT / ARTIFACT LINEAGE
        # ========================================================

        forbidden_stages = {
            "KEYFRAME_GENERATION",
            "GENERATION_RESULTS",
        }

        actual_stage_names = {
            stage[
                "stage"
            ]
            for stage
            in result[
                "stages"
            ]
        }

        assert (
            forbidden_stages
            .isdisjoint(
                actual_stage_names
            )
        )

        print(
            "TEST 18 — no generation result persisted → PASSED"
        )

        # ========================================================
        # DETERMINISTIC DRY-RUN
        # ========================================================

        second_result = (
            EpisodeOrchestrator(
                asset_registry=(
                    registry
                ),
                generation_request_compiler=(
                    GenerationRequestCompiler()
                ),
                generation_runner=None,
            )
            .run(
                episode
            )
        )

        assert (
            second_result[
                "status"
            ]
            ==
            "GENERATION_READY"
        )

        second_request_stage = (
            get_stage(
                second_result,
                "GENERATION_REQUESTS",
            )
        )

        second_request_ids = [
            request[
                "request_id"
            ]
            for request
            in second_request_stage[
                "details"
            ][
                "requests"
            ]
        ]

        assert (
            request_ids
            ==
            second_request_ids
        )

        print(
            "TEST 19 — dry-run request lineage is deterministic → PASSED"
        )

        # ========================================================
        # DRY-RUN MUST REMAIN PROVIDER AGNOSTIC
        # ========================================================

        serialized_requests = (
            json.dumps(
                generation_requests
            )
            .lower()
        )

        forbidden_provider_terms = [
            "gemini_api_key",
            "google_api_key",
            "fal_key",
            "replicate_api_token",
        ]

        assert all(
            term
            not in serialized_requests
            for term
            in forbidden_provider_terms
        )

        print(
            "TEST 20 — dry-run remains provider-agnostic → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13G.2-B "
        "EP001 GENERATION DRY-RUN PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()