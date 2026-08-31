import json
import tempfile
from pathlib import Path

from app.generation import (
    FakeGenerationProvider,
    GenerationRunner,
    GenerationStore,
)

from app.models.episode import (
    Episode,
)

from app.orchestrator.episode_orchestrator import (
    EpisodeOrchestrator,
)


# ================================================================
# SOURCE EPISODE LOADER
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
# RETRYABLE FAILURE TEST
# ================================================================


def test_retryable_failure(
    episode: Episode,
):

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_root = Path(
            temp_dir
        )

        store = (
            GenerationStore(
                base_path=str(
                    temp_root
                    /
                    "generation"
                )
            )
        )

        provider = (
            FakeGenerationProvider(
                mode=(
                    "RETRYABLE_FAILURE"
                ),
                output_root=str(
                    temp_root
                    /
                    "generated"
                ),
            )
        )

        runner = (
            GenerationRunner(
                provider=provider,
                max_attempts=3,
                store=store,
            )
        )

        orchestrator = (
            EpisodeOrchestrator(
                generation_runner=(
                    runner
                )
            )
        )

        result = (
            orchestrator.run(
                episode
            )
        )

        # ========================================================
        # TEST 1 — FINAL STATUS
        # ========================================================

        assert (
            result["status"]
            ==
            "GENERATION_FAILED"
        )

        print(
            "TEST 1 — retry exhaustion fails episode → PASSED"
        )

        # ========================================================
        # TEST 2 — GENERATION STAGE FAILED
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
            "FAILED"
        )

        print(
            "TEST 2 — generation stage reports failure → PASSED"
        )

        # ========================================================
        # TEST 3 — ALL REQUESTS WERE ATTEMPTED
        # ========================================================

        request_stage = (
            get_stage(
                result,
                "GENERATION_REQUESTS",
            )
        )

        total_requests = (
            request_stage[
                "details"
            ][
                "total_requests"
            ]
        )

        generation_details = (
            generation_stage[
                "details"
            ]
        )

        assert (
            generation_details[
                "total_requests"
            ]
            ==
            total_requests
        )

        assert (
            len(
                generation_details[
                    "results"
                ]
            )
            ==
            total_requests
        )

        print(
            "TEST 3 — all generation requests attempted → PASSED"
        )

        # ========================================================
        # TEST 4 — ALL RESULTS FAILED
        # ========================================================

        assert (
            generation_details[
                "successful"
            ]
            == 0
        )

        assert (
            generation_details[
                "failed"
            ]
            ==
            total_requests
        )

        assert all(
            generation_result[
                "status"
            ]
            ==
            "FAILED"
            for generation_result
            in generation_details[
                "results"
            ]
        )

        print(
            "TEST 4 — aggregate failure counts correct → PASSED"
        )

        # ========================================================
        # TEST 5 — RETRYABLE FAILURE USES MAX ATTEMPTS
        # ========================================================

        for generation_result in (
            generation_details[
                "results"
            ]
        ):

            attempts = (
                generation_result[
                    "attempts"
                ]
            )

            assert (
                len(attempts)
                == 3
            )

            assert [
                attempt[
                    "attempt_number"
                ]
                for attempt
                in attempts
            ] == [
                1,
                2,
                3,
            ]

            assert all(
                attempt[
                    "status"
                ]
                ==
                "FAILED"
                for attempt
                in attempts
            )

            assert all(
                attempt[
                    "error"
                ]
                is not None
                for attempt
                in attempts
            )

            assert all(
                attempt[
                    "error"
                ][
                    "retryable"
                ]
                is True
                for attempt
                in attempts
            )

        print(
            "TEST 5 — retryable failures exhaust max attempts → PASSED"
        )

        # ========================================================
        # TEST 6 — FAILED RESULTS HAVE NO OUTPUT
        # ========================================================

        for generation_result in (
            generation_details[
                "results"
            ]
        ):

            assert (
                generation_result[
                    "outputs"
                ]
                == []
            )

            assert (
                generation_result[
                    "selected_output_id"
                ]
                is None
            )

        print(
            "TEST 6 — failed generations expose no output → PASSED"
        )

        # ========================================================
        # TEST 7 — FAILED LINEAGE PERSISTED
        # ========================================================

        persisted_records = (
            store.list_episode(
                episode.episode_id
            )
        )

        assert (
            len(
                persisted_records
            )
            ==
            total_requests
        )

        for record in (
            persisted_records
        ):

            assert (
                record.result
                is not None
            )

            assert (
                record.result
                .status
                .value
                ==
                "FAILED"
            )

            assert (
                len(
                    record.result
                    .attempts
                )
                == 3
            )

        print(
            "TEST 7 — failed retry lineage persisted → PASSED"
        )

        # ========================================================
        # TEST 8 — FAILURE NEVER BECOMES REVIEW
        # ========================================================

        assert (
            result["status"]
            !=
            "WAITING_KEYFRAME_REVIEW"
        )

        print(
            "TEST 8 — failed generation never reaches review → PASSED"
        )


# ================================================================
# PERMANENT FAILURE TEST
# ================================================================


def test_permanent_failure(
    episode: Episode,
):

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_root = Path(
            temp_dir
        )

        store = (
            GenerationStore(
                base_path=str(
                    temp_root
                    /
                    "generation"
                )
            )
        )

        provider = (
            FakeGenerationProvider(
                mode=(
                    "PERMANENT_FAILURE"
                ),
                output_root=str(
                    temp_root
                    /
                    "generated"
                ),
            )
        )

        runner = (
            GenerationRunner(
                provider=provider,
                max_attempts=5,
                store=store,
            )
        )

        orchestrator = (
            EpisodeOrchestrator(
                generation_runner=(
                    runner
                )
            )
        )

        result = (
            orchestrator.run(
                episode
            )
        )

        generation_stage = (
            get_stage(
                result,
                "KEYFRAME_GENERATION",
            )
        )

        generation_results = (
            generation_stage[
                "details"
            ][
                "results"
            ]
        )

        # ========================================================
        # TEST 9 — PERMANENT FAILURE FAILS EPISODE
        # ========================================================

        assert (
            result["status"]
            ==
            "GENERATION_FAILED"
        )

        assert (
            generation_stage[
                "status"
            ]
            ==
            "FAILED"
        )

        print(
            "TEST 9 — permanent provider failure fails episode → PASSED"
        )

        # ========================================================
        # TEST 10 — PERMANENT FAILURE DOES NOT RETRY
        # ========================================================

        for generation_result in (
            generation_results
        ):

            attempts = (
                generation_result[
                    "attempts"
                ]
            )

            assert (
                len(attempts)
                == 1
            )

            assert (
                attempts[0][
                    "attempt_number"
                ]
                == 1
            )

            assert (
                attempts[0][
                    "error"
                ]
                is not None
            )

            assert (
                attempts[0][
                    "error"
                ][
                    "retryable"
                ]
                is False
            )

        print(
            "TEST 10 — permanent failure does not retry → PASSED"
        )

        # ========================================================
        # TEST 11 — PERMANENT FAILURE LINEAGE PERSISTED
        # ========================================================

        persisted_records = (
            store.list_episode(
                episode.episode_id
            )
        )

        assert (
            len(
                persisted_records
            )
            ==
            len(
                generation_results
            )
        )

        for record in (
            persisted_records
        ):

            assert (
                record.result
                is not None
            )

            assert (
                record.result
                .status
                .value
                ==
                "FAILED"
            )

            assert (
                len(
                    record.result
                    .attempts
                )
                == 1
            )

        print(
            "TEST 11 — permanent failure lineage persisted → PASSED"
        )


# ================================================================
# RETRY THEN SUCCESS TEST
# ================================================================


def test_recovered_failure(
    episode: Episode,
):

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_root = Path(
            temp_dir
        )

        store = (
            GenerationStore(
                base_path=str(
                    temp_root
                    /
                    "generation"
                )
            )
        )

        provider = (
            FakeGenerationProvider(
                mode=(
                    "FAIL_THEN_SUCCESS"
                ),
                fail_attempts=2,
                output_root=str(
                    temp_root
                    /
                    "generated"
                ),
            )
        )

        runner = (
            GenerationRunner(
                provider=provider,
                max_attempts=3,
                store=store,
            )
        )

        orchestrator = (
            EpisodeOrchestrator(
                generation_runner=(
                    runner
                )
            )
        )

        result = (
            orchestrator.run(
                episode
            )
        )

        generation_stage = (
            get_stage(
                result,
                "KEYFRAME_GENERATION",
            )
        )

        generation_results = (
            generation_stage[
                "details"
            ][
                "results"
            ]
        )

        # ========================================================
        # TEST 12 — RECOVERED RETRIES ARE SUCCESS
        # ========================================================

        assert (
            result["status"]
            ==
            "WAITING_KEYFRAME_REVIEW"
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

        print(
            "TEST 12 — recovered retries count as success → PASSED"
        )

        # ========================================================
        # TEST 13 — COMPLETE RECOVERY LINEAGE
        # ========================================================

        for generation_result in (
            generation_results
        ):

            attempts = (
                generation_result[
                    "attempts"
                ]
            )

            assert (
                len(attempts)
                == 3
            )

            assert (
                attempts[0][
                    "status"
                ]
                ==
                "FAILED"
            )

            assert (
                attempts[1][
                    "status"
                ]
                ==
                "FAILED"
            )

            assert (
                attempts[2][
                    "status"
                ]
                ==
                "SUCCEEDED"
            )

            assert (
                len(
                    generation_result[
                        "outputs"
                    ]
                )
                >= 1
            )

        print(
            "TEST 13 — recovered retry lineage preserved → PASSED"
        )


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 12G.5 — GENERATION PIPELINE FAILURE PATH"
    )
    print(
        "========================================"
    )

    episode = (
        load_source_episode(
            "data/ep001.json"
        )
    )

    assert isinstance(
        episode,
        Episode,
    )

    test_retryable_failure(
        episode
    )

    test_permanent_failure(
        episode
    )

    test_recovered_failure(
        episode
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12G.5 GENERATION PIPELINE FAILURE PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()