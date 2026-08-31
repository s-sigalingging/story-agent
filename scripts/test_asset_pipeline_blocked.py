import json
from pathlib import Path

from app.assets.registry import (
    AssetRegistry,
)

from app.models.episode import (
    Episode,
)

from app.orchestrator.episode_orchestrator import (
    EpisodeOrchestrator,
)


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


def main():

    print()
    print(
        "BATCH 11F.4 — ASSET PIPELINE BLOCKED PATH"
    )
    print(
        "========================================"
    )

    episode = load_episode()

    registry = AssetRegistry()

    result = (
        EpisodeOrchestrator(
            asset_registry=registry
        )
        .run(
            episode
        )
    )

    stages = {
        item["stage"]: item
        for item
        in result["stages"]
    }

    assert (
        result["status"]
        ==
        "WAITING_ASSET_READINESS"
    )

    print(
        "TEST 1 — episode waits for assets → PASSED"
    )

    assert (
        "ASSET_RESOLUTION"
        in stages
    )

    assert (
        "ASSET_VALIDATION"
        in stages
    )

    print(
        "TEST 2 — asset gate stages emitted → PASSED"
    )

    assert (
        stages[
            "ASSET_RESOLUTION"
        ]["status"]
        == "BLOCKED"
    )

    assert (
        stages[
            "ASSET_VALIDATION"
        ]["status"]
        == "BLOCKED"
    )

    print(
        "TEST 3 — missing assets block gate → PASSED"
    )

    assert (
        "PRODUCTION_EXECUTION"
        not in stages
    )

    assert (
        "PRODUCTION_PROMPTS"
        not in stages
    )

    print(
        "TEST 4 — execution does not start → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 11F.4 ASSET PIPELINE BLOCKED PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()