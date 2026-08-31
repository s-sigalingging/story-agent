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
    """
    Load an authored source episode.

    EpisodeStore is intentionally NOT used here because EpisodeStore
    persists orchestration runtime state under data/runtime/.

    This test needs the authored episode definition instead.
    """

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
        "BATCH 12G.4 — GENERATION PIPELINE SUCCESS PATH"
    )
    print(
        "========================================"
    )

    # ============================================================
    # LOAD AUTHORED SOURCE EPISODE
    # ============================================================

    episode = (
        load_source_episode(
            "data/ep001.json"
        )
    )

    assert isinstance(
        episode,
        Episode,
    )

    # ============================================================
    # TEMPORARY GENERATION ENVIRONMENT
    # ============================================================

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_root = Path(
            temp_dir
        )

        generation_store = (
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
                mode="SUCCESS",
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
                store=(
                    generation_store
                ),
            )
        )

        # ========================================================
        # ORCHESTRATOR
        #
        # Asset registry is intentionally omitted.
        #
        # Batch 11 already validates asset-gated behavior.
        # This test isolates the generation-enabled success path.
        # ========================================================

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
            "WAITING_KEYFRAME_REVIEW"
        )

        print(
            "TEST 1 — episode reaches keyframe review → PASSED"
        )

        # ========================================================
        # TEST 2 — GENERATION REQUEST STAGE
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

        assert (
            request_stage[
                "details"
            ][
                "total_requests"
            ]
            > 0
        )

        print(
            "TEST 2 — generation requests emitted → PASSED"
        )

        # ========================================================
        # TEST 3 — KEYFRAME GENERATION STAGE
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

        print(
            "TEST 3 — keyframe generation stage passed → PASSED"
        )

        # ========================================================
        # TEST 4 — ONE RESULT PER REQUEST
        # ========================================================

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
            "TEST 4 — one result per request → PASSED"
        )

        # ========================================================
        # TEST 5 — ALL GENERATIONS SUCCEEDED
        # ========================================================

        assert (
            generation_details[
                "successful"
            ]
            ==
            total_requests
        )

        assert (
            generation_details[
                "failed"
            ]
            == 0
        )

        assert all(
            generation_result[
                "status"
            ]
            ==
            "SUCCEEDED"
            for generation_result
            in generation_details[
                "results"
            ]
        )

        print(
            "TEST 5 — all keyframes succeeded → PASSED"
        )

        # ========================================================
        # TEST 6 — REQUEST / RESULT LINEAGE
        # ========================================================

        request_payloads = (
            request_stage[
                "details"
            ][
                "requests"
            ]
        )

        result_payloads = (
            generation_details[
                "results"
            ]
        )

        requests_by_id = {
            request[
                "request_id"
            ]: request
            for request
            in request_payloads
        }

        results_by_id = {
            generation_result[
                "request_id"
            ]: generation_result
            for generation_result
            in result_payloads
        }

        assert (
            set(
                requests_by_id
            )
            ==
            set(
                results_by_id
            )
        )

        for request_id, request in (
            requests_by_id.items()
        ):

            generation_result = (
                results_by_id[
                    request_id
                ]
            )

            assert (
                generation_result[
                    "episode_id"
                ]
                ==
                request[
                    "episode_id"
                ]
            )

            assert (
                generation_result[
                    "shot_id"
                ]
                ==
                request[
                    "shot_id"
                ]
            )

            assert (
                generation_result[
                    "generation_type"
                ]
                ==
                request[
                    "generation_type"
                ]
            )

        print(
            "TEST 6 — request/result lineage preserved → PASSED"
        )

        # ========================================================
        # TEST 7 — EVERY RESULT HAS OUTPUT
        # ========================================================

        for generation_result in (
            result_payloads
        ):

            assert (
                len(
                    generation_result[
                        "outputs"
                    ]
                )
                >= 1
            )

            assert (
                generation_result[
                    "selected_output_id"
                ]
                is None
            )

        print(
            "TEST 7 — outputs produced without auto-selection → PASSED"
        )

        # ========================================================
        # TEST 8 — CLEAN SUCCESS USES ONE ATTEMPT
        # ========================================================

        for generation_result in (
            result_payloads
        ):

            assert (
                len(
                    generation_result[
                        "attempts"
                    ]
                )
                == 1
            )

            attempt = (
                generation_result[
                    "attempts"
                ][0]
            )

            assert (
                attempt[
                    "attempt_number"
                ]
                == 1
            )

            assert (
                attempt[
                    "status"
                ]
                ==
                "SUCCEEDED"
            )

        print(
            "TEST 8 — clean success uses one attempt → PASSED"
        )

        # ========================================================
        # TEST 9 — PERSISTED LINEAGE COUNT
        # ========================================================

        persisted_records = (
            generation_store
            .list_episode(
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

        print(
            "TEST 9 — all generation lineage persisted → PASSED"
        )

        # ========================================================
        # TEST 10 — PERSISTED RESULTS COMPLETE
        # ========================================================

        persisted_request_ids = set()

        for record in (
            persisted_records
        ):

            persisted_request_ids.add(
                record
                .request
                .request_id
            )

            assert (
                record.result
                is not None
            )

            assert (
                record.result
                .status
                .value
                ==
                "SUCCEEDED"
            )

            assert (
                len(
                    record.result
                    .outputs
                )
                >= 1
            )

            assert (
                len(
                    record.result
                    .attempts
                )
                == 1
            )

        assert (
            persisted_request_ids
            ==
            set(
                requests_by_id
            )
        )

        print(
            "TEST 10 — persisted results retain complete lineage → PASSED"
        )

        # ========================================================
        # TEST 11 — PIPELINE ORDER
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

        production_prompt_index = (
            stage_names.index(
                "PRODUCTION_PROMPTS"
            )
        )

        request_index = (
            stage_names.index(
                "GENERATION_REQUESTS"
            )
        )

        generation_index = (
            stage_names.index(
                "KEYFRAME_GENERATION"
            )
        )

        assert (
            production_prompt_index
            <
            request_index
            <
            generation_index
        )

        print(
            "TEST 11 — generation stage ordering preserved → PASSED"
        )

        # ========================================================
        # TEST 12 — GENERATION DOES NOT IMPLY APPROVAL
        # ========================================================

        assert (
            result["status"]
            ==
            "WAITING_KEYFRAME_REVIEW"
        )

        assert all(
            generation_result[
                "selected_output_id"
            ]
            is None
            for generation_result
            in result_payloads
        )

        print(
            "TEST 12 — generation does not imply approval → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12G.4 GENERATION PIPELINE SUCCESS PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()