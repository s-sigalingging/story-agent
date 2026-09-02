from app.generation.providers import (
    FakeGenerationProvider,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationReferenceAsset,
    GenerationRequest,
    GenerationType,
)

from app.models.generation_provider import (
    ProviderCapabilities,
)


def make_request(
    reference_count: int = 0,
    negative_prompt: str | None = None,
    output_format: str = "png",
    aspect_ratio: str = "1:1",
) -> GenerationRequest:

    references = []

    for index in range(
        1,
        reference_count + 1,
    ):

        references.append(
            GenerationReferenceAsset(
                asset_id=(
                    f"ASSET_TEST_{index}"
                ),
                entity_id=(
                    f"ENTITY_TEST_{index}"
                ),
                asset_type=(
                    "CHARACTER"
                ),
                name=(
                    f"Test Reference {index}"
                ),
                reference_path=(
                    f"assets/test/"
                    f"reference_{index}.png"
                ),
            )
        )

    return (
        GenerationRequest(
            request_id=(
                "GEN_REQ_CAPABILITY_TEST"
            ),
            episode_id=(
                "EP_TEST"
            ),
            shot_id=(
                "EP_TEST-S01-SHOT01"
            ),
            generation_type=(
                GenerationType.KEYFRAME
            ),
            prompt=(
                "Create one stable cinematic frame."
            ),
            negative_prompt=(
                negative_prompt
            ),
            reference_assets=(
                references
            ),
            output=(
                GenerationOutputSpec(
                    width=1024,
                    height=1024,
                    aspect_ratio=(
                        aspect_ratio
                    ),
                    output_format=(
                        output_format
                    ),
                )
            ),
        )
    )


def main():

    print()
    print(
        "BATCH 13B — PROVIDER CAPABILITY CONTRACT"
    )
    print(
        "========================================"
    )

    # ============================================================
    # TEST 1 — DEFAULT FAKE CAPABILITIES
    # ============================================================

    provider = (
        FakeGenerationProvider()
    )

    capabilities = (
        provider.capabilities
    )

    assert (
        capabilities.supports_keyframe
        is True
    )

    assert (
        capabilities.supports_reference_images
        is True
    )

    assert (
        "png"
        in capabilities.supported_output_formats
    )

    print(
        "TEST 1 — provider exposes capabilities → PASSED"
    )

    # ============================================================
    # TEST 2 — COMPATIBLE REQUEST
    # ============================================================

    request = (
        make_request(
            reference_count=1,
            negative_prompt=(
                "Avoid distorted anatomy."
            ),
            output_format="png",
        )
    )

    validation = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    assert (
        validation.compatible
        is True
    )

    assert (
        validation.issues
        == []
    )

    print(
        "TEST 2 — compatible request accepted → PASSED"
    )

    # ============================================================
    # TEST 3 — REFERENCE IMAGE UNSUPPORTED
    # ============================================================

    provider = (
        FakeGenerationProvider(
            capabilities=(
                ProviderCapabilities(
                    supports_keyframe=True,
                    supports_reference_images=False,
                    supports_negative_prompt=True,
                    supported_output_formats=[
                        "png"
                    ],
                )
            )
        )
    )

    request = (
        make_request(
            reference_count=1
        )
    )

    validation = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    assert (
        validation.compatible
        is False
    )

    assert any(
        "reference images"
        in issue.lower()
        for issue
        in validation.issues
    )

    print(
        "TEST 3 — unsupported references rejected → PASSED"
    )

    # ============================================================
    # TEST 4 — MAX REFERENCE LIMIT
    # ============================================================

    provider = (
        FakeGenerationProvider(
            capabilities=(
                ProviderCapabilities(
                    supports_keyframe=True,
                    supports_reference_images=True,
                    max_reference_images=2,
                    supports_negative_prompt=True,
                    supported_output_formats=[
                        "png"
                    ],
                )
            )
        )
    )

    request = (
        make_request(
            reference_count=3
        )
    )

    validation = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    assert (
        validation.compatible
        is False
    )

    assert any(
        "at most 2"
        in issue.lower()
        for issue
        in validation.issues
    )

    print(
        "TEST 4 — max reference limit enforced → PASSED"
    )

    # ============================================================
    # TEST 5 — NEGATIVE PROMPT UNSUPPORTED
    # ============================================================

    provider = (
        FakeGenerationProvider(
            capabilities=(
                ProviderCapabilities(
                    supports_keyframe=True,
                    supports_reference_images=True,
                    supports_negative_prompt=False,
                    supported_output_formats=[
                        "png"
                    ],
                )
            )
        )
    )

    request = (
        make_request(
            negative_prompt=(
                "Avoid distorted anatomy."
            )
        )
    )

    validation = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    assert (
        validation.compatible
        is False
    )

    assert any(
        "negative prompts"
        in issue.lower()
        for issue
        in validation.issues
    )

    print(
        "TEST 5 — unsupported negative prompt rejected → PASSED"
    )

    # ============================================================
    # TEST 6 — OUTPUT FORMAT
    # ============================================================

    provider = (
        FakeGenerationProvider(
            capabilities=(
                ProviderCapabilities(
                    supports_keyframe=True,
                    supports_reference_images=True,
                    supports_negative_prompt=True,
                    supported_output_formats=[
                        "png"
                    ],
                )
            )
        )
    )

    request = (
        make_request(
            output_format="webp"
        )
    )

    validation = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    assert (
        validation.compatible
        is False
    )

    assert any(
        "output format"
        in issue.lower()
        for issue
        in validation.issues
    )

    print(
        "TEST 6 — unsupported output format rejected → PASSED"
    )

    # ============================================================
    # TEST 7 — ASPECT RATIO
    # ============================================================

    provider = (
        FakeGenerationProvider(
            capabilities=(
                ProviderCapabilities(
                    supports_keyframe=True,
                    supports_reference_images=True,
                    supports_negative_prompt=True,
                    supported_output_formats=[
                        "png"
                    ],
                    supported_aspect_ratios=[
                        "1:1",
                        "16:9",
                    ],
                )
            )
        )
    )

    request = (
        make_request(
            aspect_ratio="9:16"
        )
    )

    validation = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    assert (
        validation.compatible
        is False
    )

    assert any(
        "aspect ratio"
        in issue.lower()
        for issue
        in validation.issues
    )

    print(
        "TEST 7 — unsupported aspect ratio rejected → PASSED"
    )

    # ============================================================
    # TEST 8 — UNRESTRICTED ASPECT RATIOS
    # ============================================================

    provider = (
        FakeGenerationProvider(
            capabilities=(
                ProviderCapabilities(
                    supports_keyframe=True,
                    supports_reference_images=True,
                    supports_negative_prompt=True,
                    supported_output_formats=[
                        "png"
                    ],
                    supported_aspect_ratios=[],
                )
            )
        )
    )

    request = (
        make_request(
            aspect_ratio="9:16"
        )
    )

    validation = (
        provider
        .validate_request_capabilities(
            request
        )
    )

    assert (
        validation.compatible
        is True
    )

    print(
        "TEST 8 — unrestricted aspect ratios accepted → PASSED"
    )

    # ============================================================
    # TEST 9 — CAPABILITY COPY IS ISOLATED
    # ============================================================

    provider = (
        FakeGenerationProvider()
    )

    capabilities = (
        provider.capabilities
    )

    capabilities.supported_output_formats.append(
        "unexpected-format"
    )

    fresh_capabilities = (
        provider.capabilities
    )

    assert (
        "unexpected-format"
        not in fresh_capabilities
        .supported_output_formats
    )

    print(
        "TEST 9 — capability declaration cannot mutate provider → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13B PROVIDER CAPABILITY CONTRACT PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()