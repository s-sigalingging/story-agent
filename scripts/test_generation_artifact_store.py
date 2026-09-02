import tempfile
from pathlib import Path

from app.generation import (
    GenerationArtifactStore,
)


def main():

    print()
    print(
        "BATCH 13C — GENERATION ARTIFACT STORE"
    )
    print(
        "========================================"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        store = (
            GenerationArtifactStore(
                base_path=temp_dir
            )
        )

        # ============================================================
        # TEST 1 — DETERMINISTIC PATH
        # ============================================================

        path_1 = (
            store.build_path(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT01",
                output_id="GEN_OUTPUT_001",
                output_format="png",
            )
        )

        path_2 = (
            store.build_path(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT01",
                output_id="GEN_OUTPUT_001",
                output_format="png",
            )
        )

        assert (
            path_1
            ==
            path_2
        )

        print(
            "TEST 1 — deterministic artifact path → PASSED"
        )

        # ============================================================
        # TEST 2 — WRITE PHYSICAL BYTES
        # ============================================================

        written_path = (
            store.write(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT01",
                output_id="GEN_OUTPUT_001",
                output_format="png",
                content=(
                    b"fake-image-bytes"
                ),
            )
        )

        physical_path = Path(
            written_path
        )

        assert (
            physical_path.exists()
        )

        assert (
            physical_path.is_file()
        )

        print(
            "TEST 2 — artifact physically written → PASSED"
        )

        # ============================================================
        # TEST 3 — FILE SIZE
        # ============================================================

        assert (
            physical_path
            .stat()
            .st_size
            > 0
        )

        assert (
            physical_path
            .read_bytes()
            ==
            b"fake-image-bytes"
        )

        print(
            "TEST 3 — artifact bytes preserved → PASSED"
        )

        # ============================================================
        # TEST 4 — VERIFY
        # ============================================================

        assert (
            store.verify_path(
                written_path
            )
            is True
        )

        print(
            "TEST 4 — physical artifact verification → PASSED"
        )

        # ============================================================
        # TEST 5 — OVERWRITE PROTECTION
        # ============================================================

        failed = False

        try:

            store.write(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT01",
                output_id="GEN_OUTPUT_001",
                output_format="png",
                content=(
                    b"replacement-bytes"
                ),
            )

        except FileExistsError:

            failed = True

        assert failed

        assert (
            physical_path
            .read_bytes()
            ==
            b"fake-image-bytes"
        )

        print(
            "TEST 5 — accidental overwrite rejected → PASSED"
        )

        # ============================================================
        # TEST 6 — EXPLICIT OVERWRITE
        # ============================================================

        store.write(
            episode_id="EP_TEST",
            shot_id="EP_TEST-S01-SHOT01",
            output_id="GEN_OUTPUT_001",
            output_format="png",
            content=(
                b"replacement-bytes"
            ),
            overwrite=True,
        )

        assert (
            physical_path
            .read_bytes()
            ==
            b"replacement-bytes"
        )

        print(
            "TEST 6 — explicit overwrite supported → PASSED"
        )

        # ============================================================
        # TEST 7 — EMPTY BYTES REJECTED
        # ============================================================

        failed = False

        try:

            store.write(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT02",
                output_id="GEN_OUTPUT_EMPTY",
                output_format="png",
                content=b"",
            )

        except ValueError:

            failed = True

        assert failed

        print(
            "TEST 7 — empty artifact rejected → PASSED"
        )

        # ============================================================
        # TEST 8 — NON-BYTES REJECTED
        # ============================================================

        failed = False

        try:

            store.write(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT02",
                output_id="GEN_OUTPUT_TEXT",
                output_format="png",
                content="not-bytes",
            )

        except TypeError:

            failed = True

        assert failed

        print(
            "TEST 8 — non-byte artifact rejected → PASSED"
        )

        # ============================================================
        # TEST 9 — SANITIZED PATH
        # ============================================================

        sanitized_path = (
            store.build_path(
                episode_id=(
                    "EP TEST/../../"
                ),
                shot_id=(
                    "SHOT 01 / weird"
                ),
                output_id=(
                    "OUTPUT:*?001"
                ),
                output_format=(
                    ".PNG"
                ),
            )
        )

        assert (
            sanitized_path
            .suffix
            ==
            ".png"
        )

        assert (
            ".."
            not in str(
                sanitized_path
                .relative_to(
                    Path(
                        temp_dir
                    )
                )
            )
        )

        print(
            "TEST 9 — unsafe path components sanitized → PASSED"
        )

        # ============================================================
        # TEST 10 — EPISODE / SHOT ISOLATION
        # ============================================================

        other_path = (
            store.write(
                episode_id="EP_OTHER",
                shot_id="EP_OTHER-S02-SHOT03",
                output_id="GEN_OUTPUT_001",
                output_format="png",
                content=(
                    b"other-image"
                ),
            )
        )

        assert (
            other_path
            !=
            written_path
        )

        assert (
            Path(
                other_path
            )
            .exists()
        )

        print(
            "TEST 10 — episode and shot isolation → PASSED"
        )

        # ============================================================
        # TEST 11 — EXISTS
        # ============================================================

        assert (
            store.exists(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT01",
                output_id="GEN_OUTPUT_001",
                output_format="png",
            )
            is True
        )

        print(
            "TEST 11 — artifact existence lookup → PASSED"
        )

        # ============================================================
        # TEST 12 — DELETE
        # ============================================================

        deleted = (
            store.delete(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT01",
                output_id="GEN_OUTPUT_001",
                output_format="png",
            )
        )

        assert (
            deleted
            is True
        )

        assert (
            physical_path.exists()
            is False
        )

        assert (
            store.delete(
                episode_id="EP_TEST",
                shot_id="EP_TEST-S01-SHOT01",
                output_id="GEN_OUTPUT_001",
                output_format="png",
            )
            is False
        )

        print(
            "TEST 12 — artifact deletion → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13C GENERATION ARTIFACT STORE PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()