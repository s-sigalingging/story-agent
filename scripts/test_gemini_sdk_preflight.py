import importlib.metadata
import os

from google import genai


def main():

    print()
    print(
        "BATCH 13E.1 — GEMINI SDK PREFLIGHT"
    )
    print(
        "========================================"
    )

    # ============================================================
    # TEST 1 — SDK INSTALLED
    # ============================================================

    try:

        version = (
            importlib.metadata.version(
                "google-genai"
            )
        )

    except (
        importlib.metadata.PackageNotFoundError
    ) as exc:

        raise AssertionError(
            "google-genai is not installed."
        ) from exc

    assert (
        version.strip()
    )

    print(
        "TEST 1 — google-genai installed → PASSED"
    )

    print(
        f"         version: {version}"
    )

    # ============================================================
    # TEST 2 — API KEY AVAILABLE
    # ============================================================

    api_key = (
        os.getenv(
            "GEMINI_API_KEY"
        )
    )

    assert (
        api_key is not None
        and
        api_key.strip()
    ), (
        "GEMINI_API_KEY is not set."
    )

    print(
        "TEST 2 — GEMINI_API_KEY available → PASSED"
    )

    # ============================================================
    # TEST 3 — CLIENT CONSTRUCTION
    # ============================================================

    client = (
        genai.Client(
            api_key=(
                api_key
            )
        )
    )

    assert (
        client is not None
    )

    print(
        "TEST 3 — Gemini client constructed → PASSED"
    )

    # ============================================================
    # TEST 4 — INTERACTIONS SURFACE
    # ============================================================

    interactions = getattr(
        client,
        "interactions",
        None,
    )

    assert (
        interactions is not None
    ), (
        "Installed google-genai SDK does not expose "
        "client.interactions."
    )

    print(
        "TEST 4 — client.interactions available → PASSED"
    )

    # ============================================================
    # TEST 5 — CREATE METHOD
    # ============================================================

    create_method = getattr(
        interactions,
        "create",
        None,
    )

    assert (
        create_method is not None
        and
        callable(
            create_method
        )
    ), (
        "Installed google-genai SDK does not expose "
        "client.interactions.create()."
    )

    print(
        "TEST 5 — interactions.create available → PASSED"
    )

    # ============================================================
    # TEST 6 — NO NETWORK CALL
    # ============================================================

    # Deliberately do not call interactions.create().
    # This batch only validates the local SDK surface.

    print(
        "TEST 6 — no generation request executed → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13E.1 GEMINI SDK PREFLIGHT PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()