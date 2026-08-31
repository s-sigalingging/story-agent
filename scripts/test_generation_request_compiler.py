from app.generation import (
    GenerationRequestCompiler,
)

from app.models.generation import (
    GenerationType,
)

from app.models.prompt import (
    EpisodeProductionPrompts,
    ProductionPrompt,
    PromptAssetReference,
    SceneProductionPrompts,
)


def main():

    print()
    print(
        "BATCH 12G.2 — GENERATION REQUEST COMPILER"
    )
    print(
        "========================================"
    )

    # ============================================================
    # TEST DATA
    # ============================================================

    resolved_character = (
        PromptAssetReference(
            asset_id=(
                "ASSET_CHAR_TEST_MASTER"
            ),
            entity_id=(
                "CHAR_TEST"
            ),
            asset_type=(
                "CHARACTER"
            ),
            name=(
                "Test Character"
            ),
            purpose=(
                "Master character reference"
            ),
            reference_path=(
                "assets/characters/"
                "CHAR_TEST/master_v2.png"
            ),
            required=True,
            master_reference_required=True,
        )
    )

    unresolved_prop = (
        PromptAssetReference(
            asset_id=(
                "ASSET_PROP_TEST_MASTER"
            ),
            entity_id=(
                "PROP_TEST"
            ),
            asset_type=(
                "PROP"
            ),
            name=(
                "Test Prop"
            ),
            purpose=(
                "Master prop reference"
            ),
            reference_path=None,
            required=False,
            master_reference_required=False,
        )
    )

    prompt_1 = (
        ProductionPrompt(
            shot_id=(
                "EP_TEST-S01-SHOT01"
            ),
            scene_number=1,
            duration_seconds=5,
            image_prompt=(
                "Create one stable cinematic frame."
            ),
            video_prompt=(
                "Hold the composition with minimal motion."
            ),
            negative_prompt=(
                "Avoid distorted anatomy."
            ),
            assets=[
                resolved_character,
                unresolved_prop,
            ],
            dialogue=None,
        )
    )

    prompt_2 = (
        ProductionPrompt(
            shot_id=(
                "EP_TEST-S01-SHOT02"
            ),
            scene_number=1,
            duration_seconds=4,
            image_prompt=(
                "Create a close-up cinematic frame."
            ),
            video_prompt=(
                "Maintain a static close-up."
            ),
            negative_prompt=None,
            assets=[],
            dialogue=None,
        )
    )

    episode_prompts = (
        EpisodeProductionPrompts(
            episode_id=(
                "EP_TEST"
            ),
            title=(
                "Generation Compiler Test"
            ),
            target_duration_seconds=9,
            scenes=[
                SceneProductionPrompts(
                    scene_number=1,
                    prompts=[
                        prompt_1,
                        prompt_2,
                    ],
                )
            ],
            total_shots=2,
        )
    )

    compiler = (
        GenerationRequestCompiler(
            default_width=1280,
            default_height=720,
            default_aspect_ratio=(
                "16:9"
            ),
            default_output_format=(
                "png"
            ),
        )
    )

    requests = (
        compiler.compile(
            episode_prompts
        )
    )

    # ============================================================
    # TEST 1 — ONE REQUEST PER PRODUCTION PROMPT
    # ============================================================

    assert (
        len(requests)
        == 2
    )

    print(
        "TEST 1 — one request per shot → PASSED"
    )

    # ============================================================
    # TEST 2 — REQUEST TYPE
    # ============================================================

    assert all(
        request.generation_type
        ==
        GenerationType.KEYFRAME
        for request
        in requests
    )

    print(
        "TEST 2 — requests are KEYFRAME type → PASSED"
    )

    # ============================================================
    # TEST 3 — LINEAGE
    # ============================================================

    request_1 = (
        requests[0]
    )

    assert (
        request_1.episode_id
        ==
        "EP_TEST"
    )

    assert (
        request_1.shot_id
        ==
        "EP_TEST-S01-SHOT01"
    )

    assert (
        request_1.request_id
        ==
        "GEN_REQ_EP_TEST_"
        "EP_TEST-S01-SHOT01"
    )

    print(
        "TEST 3 — request lineage preserved → PASSED"
    )

    # ============================================================
    # TEST 4 — IMAGE PROMPT MAPPING
    # ============================================================

    assert (
        request_1.prompt
        ==
        prompt_1.image_prompt
    )

    assert (
        request_1.prompt
        !=
        prompt_1.video_prompt
    )

    print(
        "TEST 4 — image prompt mapped correctly → PASSED"
    )

    # ============================================================
    # TEST 5 — NEGATIVE PROMPT MAPPING
    # ============================================================

    assert (
        request_1.negative_prompt
        ==
        "Avoid distorted anatomy."
    )

    assert (
        requests[1]
        .negative_prompt
        is None
    )

    print(
        "TEST 5 — negative prompt preserved → PASSED"
    )

    # ============================================================
    # TEST 6 — ONLY RESOLVED PHYSICAL REFERENCES FORWARDED
    # ============================================================

    assert (
        len(
            request_1.reference_assets
        )
        == 1
    )

    reference = (
        request_1
        .reference_assets[0]
    )

    assert (
        reference.asset_id
        ==
        "ASSET_CHAR_TEST_MASTER"
    )

    assert (
        reference.reference_path
        ==
        "assets/characters/"
        "CHAR_TEST/master_v2.png"
    )

    assert (
        reference.entity_id
        ==
        "CHAR_TEST"
    )

    print(
        "TEST 6 — resolved references forwarded → PASSED"
    )

    # ============================================================
    # TEST 7 — UNRESOLVED REFERENCES NOT INVENTED
    # ============================================================

    reference_ids = {
        item.asset_id
        for item
        in request_1.reference_assets
    }

    assert (
        "ASSET_PROP_TEST_MASTER"
        not in reference_ids
    )

    print(
        "TEST 7 — unresolved references excluded → PASSED"
    )

    # ============================================================
    # TEST 8 — OUTPUT SPEC
    # ============================================================

    assert (
        request_1.output.width
        == 1280
    )

    assert (
        request_1.output.height
        == 720
    )

    assert (
        request_1.output.aspect_ratio
        == "16:9"
    )

    assert (
        request_1.output.output_format
        == "png"
    )

    print(
        "TEST 8 — output specification mapped → PASSED"
    )

    # ============================================================
    # TEST 9 — SHOT METADATA
    # ============================================================

    assert (
        request_1.metadata[
            "scene_number"
        ]
        == "1"
    )

    assert (
        request_1.metadata[
            "duration_seconds"
        ]
        == "5"
    )

    assert (
        request_1.metadata[
            "source"
        ]
        ==
        "PRODUCTION_PROMPTS"
    )

    print(
        "TEST 9 — shot metadata preserved → PASSED"
    )

    # ============================================================
    # TEST 10 — DETERMINISTIC REQUEST ID
    # ============================================================

    request_again = (
        compiler.compile_prompt(
            episode_id=(
                "EP_TEST"
            ),
            prompt=(
                prompt_1
            ),
        )
    )

    assert (
        request_again.request_id
        ==
        request_1.request_id
    )

    print(
        "TEST 10 — deterministic request ID → PASSED"
    )

    # ============================================================
    # TEST 11 — EMPTY IMAGE PROMPT REJECTED
    # ============================================================

    invalid_prompt = (
        prompt_1.model_copy(
            update={
                "image_prompt": "   "
            }
        )
    )

    failed = False

    try:

        compiler.compile_prompt(
            episode_id=(
                "EP_TEST"
            ),
            prompt=(
                invalid_prompt
            ),
        )

    except ValueError:

        failed = True

    assert failed

    print(
        "TEST 11 — empty image prompt rejected → PASSED"
    )

    # ============================================================
    # TEST 12 — NO VIDEO PROMPT LEAK INTO REQUEST
    # ============================================================

    request_fields = set(
        type(
            request_1
        )
        .model_fields
        .keys()
    )

    assert (
        "video_prompt"
        not in request_fields
    )

    print(
        "TEST 12 — request remains keyframe-specific → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12G.2 GENERATION REQUEST COMPILER PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()