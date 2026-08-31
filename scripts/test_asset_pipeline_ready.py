import json
import tempfile
from pathlib import Path

from app.assets.registry import (
    AssetRegistry,
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


def stage_map(
    result: dict,
):

    return {
        item["stage"]: item
        for item
        in result["stages"]
    }


def main():

    print()
    print(
        "BATCH 11F.5 — ASSET PIPELINE READY PATH"
    )
    print(
        "========================================"
    )

    episode = load_episode()

    # ============================================================
    # COLLECT LOGICAL REQUIREMENTS USING LEGACY MODE
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

    legacy_stages = (
        stage_map(
            legacy_result
        )
    )

    logical_assets = (
        legacy_stages[
            "ASSET_PLANNING"
        ]["details"][
            "assets"
        ]
    )

    assert logical_assets

    print(
        "TEST 1 — logical requirements collected → PASSED"
    )

    # ============================================================
    # BUILD TEMP APPROVED REGISTRY
    # ============================================================

    with tempfile.TemporaryDirectory() as temp_dir:

        root = Path(
            temp_dir
        )

        registry = (
            AssetRegistry()
        )

        expected_paths = {}

        for index, asset in enumerate(
            logical_assets,
            start=1,
        ):

            asset_type = (
                TYPE_MAP[
                    asset[
                        "asset_type"
                    ]
                ]
            )

            reference_file = (
                root
                /
                "references"
                /
                f"asset_{index}.png"
            )

            reference_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            reference_file.write_bytes(
                b"approved-test-reference"
            )

            registry.register(
                AssetRecord(
                    asset_id=(
                        f"{asset['asset_id']}_V1"
                    ),
                    entity_id=(
                        asset[
                            "entity_id"
                        ]
                    ),
                    asset_type=(
                        asset_type
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
                            reference_file
                        )
                    ),
                )
            )

            expected_paths[
                asset[
                    "asset_id"
                ]
            ] = str(
                reference_file
            )

        # ========================================================
        # RUN ASSET-GATED PIPELINE
        # ========================================================

        gated_result = (
            EpisodeOrchestrator(
                asset_registry=(
                    registry
                )
            )
            .run(
                episode
            )
        )

        gated_stages = (
            stage_map(
                gated_result
            )
        )

        assert (
            gated_result["status"]
            ==
            "WAITING_HUMAN_APPROVAL"
        )

        print(
            "TEST 2 — gated episode reaches approval → PASSED"
        )

        assert (
            gated_stages[
                "ASSET_RESOLUTION"
            ]["status"]
            == "PASSED"
        )

        assert (
            gated_stages[
                "ASSET_VALIDATION"
            ]["status"]
            ==
            "PRODUCTION_READY"
        )

        print(
            "TEST 3 — asset gate ready → PASSED"
        )

        assert (
            "PRODUCTION_EXECUTION"
            in gated_stages
        )

        assert (
            "PRODUCTION_PROMPTS"
            in gated_stages
        )

        print(
            "TEST 4 — production continues → PASSED"
        )

        # ========================================================
        # VERIFY HYDRATED PROMPT REFERENCES
        # ========================================================

        prompt_scenes = (
            gated_stages[
                "PRODUCTION_PROMPTS"
            ]["details"][
                "scenes"
            ]
        )

        prompt_assets = []

        for scene in prompt_scenes:

            for prompt in (
                scene[
                    "prompts"
                ]
            ):

                prompt_assets.extend(
                    prompt.get(
                        "assets",
                        []
                    )
                )

        assert prompt_assets

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
                ).is_file()
            )

        print(
            "TEST 5 — hydrated paths reach prompts → PASSED"
        )

        # ========================================================
        # LOGICAL IDs MUST REMAIN LOGICAL
        # ========================================================

        physical_ids = {
            record.asset_id
            for record
            in registry.records.values()
        }

        prompt_ids = {
            asset[
                "asset_id"
            ]
            for asset
            in prompt_assets
        }

        assert (
            physical_ids
            .isdisjoint(
                prompt_ids
            )
        )

        print(
            "TEST 6 — logical IDs remain stable → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 11F.5 ASSET PIPELINE READY PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()