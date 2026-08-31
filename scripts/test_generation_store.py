import tempfile
from pathlib import Path

from app.generation import (
    FakeGenerationProvider,
    GenerationStore,
    KeyframeGenerator,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationRequest,
    GenerationStatus,
    GenerationType,
)


def make_request(
    request_id: str,
    shot_id: str,
) -> GenerationRequest:

    return (
        GenerationRequest(
            request_id=request_id,
            episode_id="EP_TEST",
            shot_id=shot_id,
            generation_type=(
                GenerationType.KEYFRAME
            ),
            prompt=(
                "Create one stable cinematic frame."
            ),
            negative_prompt=(
                "Avoid distorted anatomy."
            ),
            output=(
                GenerationOutputSpec(
                    width=1280,
                    height=720,
                    aspect_ratio="16:9",
                    output_format="png",
                )
            ),
        )
    )


def main():

    print()
    print(
        "BATCH 12E — GENERATION LINEAGE STORE"
    )
    print(
        "========================================"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        store = (
            GenerationStore(
                base_path=temp_dir
            )
        )

        request = (
            make_request(
                request_id=(
                    "GEN_REQ_STORE_TEST_001"
                ),
                shot_id=(
                    "EP_TEST-S01-SHOT01"
                ),
            )
        )

        # ============================================================
        # TEST 1 — CREATE REQUEST
        # ============================================================

        record = (
            store.create(
                request
            )
        )

        assert (
            record.request.request_id
            ==
            request.request_id
        )

        assert (
            record.result
            is None
        )

        assert (
            store.exists(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
            is True
        )

        print(
            "TEST 1 — request persisted → PASSED"
        )

        # ============================================================
        # TEST 2 — LOAD REQUEST
        # ============================================================

        loaded = (
            store.load(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
        )

        assert (
            loaded
            is not None
        )

        assert (
            loaded.request.shot_id
            ==
            request.shot_id
        )

        assert (
            loaded.result
            is None
        )

        print(
            "TEST 2 — request reload → PASSED"
        )

        # ============================================================
        # TEST 3 — DUPLICATE CREATE REJECTED
        # ============================================================

        failed = False

        try:

            store.create(
                request
            )

        except ValueError:

            failed = True

        assert failed

        print(
            "TEST 3 — duplicate request rejected → PASSED"
        )

        # ============================================================
        # TEST 4 — GENERATE RESULT
        # ============================================================

        generator = (
            KeyframeGenerator(
                provider=(
                    FakeGenerationProvider()
                )
            )
        )

        result = (
            generator.generate(
                request
            )
        )

        assert (
            result.status
            ==
            GenerationStatus.SUCCEEDED
        )

        print(
            "TEST 4 — technical result generated → PASSED"
        )

        # ============================================================
        # TEST 5 — SAVE RESULT
        # ============================================================

        updated = (
            store.save_result(
                result
            )
        )

        assert (
            updated.result
            is not None
        )

        assert (
            updated.result.status
            ==
            GenerationStatus.SUCCEEDED
        )

        assert (
            len(
                updated.result.attempts
            )
            == 1
        )

        print(
            "TEST 5 — result persisted → PASSED"
        )

        # ============================================================
        # TEST 6 — LINEAGE SURVIVES RELOAD
        # ============================================================

        reloaded = (
            store.load(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
        )

        assert (
            reloaded
            is not None
        )

        assert (
            reloaded.result
            is not None
        )

        assert (
            reloaded.result.request_id
            ==
            request.request_id
        )

        assert (
            reloaded.result.attempts[
                0
            ].attempt_number
            == 1
        )

        assert (
            reloaded.result.outputs[
                0
            ].output_id
            ==
            result.outputs[
                0
            ].output_id
        )

        print(
            "TEST 6 — lineage survives reload → PASSED"
        )

        # ============================================================
        # TEST 7 — MULTIPLE REQUESTS PER EPISODE
        # ============================================================

        request_2 = (
            make_request(
                request_id=(
                    "GEN_REQ_STORE_TEST_002"
                ),
                shot_id=(
                    "EP_TEST-S01-SHOT02"
                ),
            )
        )

        store.create(
            request_2
        )

        records = (
            store.list_episode(
                "EP_TEST"
            )
        )

        assert (
            len(records)
            == 2
        )

        request_ids = {
            item.request.request_id
            for item
            in records
        }

        assert (
            request.request_id
            in request_ids
        )

        assert (
            request_2.request_id
            in request_ids
        )

        print(
            "TEST 7 — episode lineage listing → PASSED"
        )

        # ============================================================
        # TEST 8 — UNKNOWN RESULT REJECTED
        # ============================================================

        unknown_result = (
            result.model_copy(
                update={
                    "request_id": (
                        "GEN_REQ_UNKNOWN"
                    )
                }
            )
        )

        failed = False

        try:

            store.save_result(
                unknown_result
            )

        except ValueError:

            failed = True

        assert failed

        print(
            "TEST 8 — unknown result rejected → PASSED"
        )

        # ============================================================
        # TEST 9 — PHYSICAL JSON EXISTS
        # ============================================================

        json_files = list(
            Path(
                temp_dir
            )
            .rglob(
                "*.json"
            )
        )

        assert (
            len(json_files)
            == 2
        )

        print(
            "TEST 9 — lineage JSON persisted → PASSED"
        )

        # ============================================================
        # TEST 10 — DELETE
        # ============================================================

        deleted = (
            store.delete(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
        )

        assert (
            deleted
            is True
        )

        assert (
            store.exists(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
            is False
        )

        assert (
            store.delete(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
            is False
        )

        print(
            "TEST 10 — lineage deletion → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12E GENERATION LINEAGE STORE PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()