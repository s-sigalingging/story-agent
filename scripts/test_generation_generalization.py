from app.generation import (
    FakeGenerationProvider,
    GenerationRequestCompiler,
    GenerationRunner,
)

from app.models.generation import (
    GenerationStatus,
)

from app.models.prompt import (
    EpisodeProductionPrompts,
    ProductionPrompt,
    PromptAssetReference,
    SceneProductionPrompts,
)


def build_episode_prompts():

    # ============================================================
    # CASE A — COMEDY / CHARACTER
    # ============================================================

    comedy_character = (
        PromptAssetReference(
            asset_id=(
                "ASSET_CHAR_COMEDY_MASTER"
            ),
            entity_id=(
                "CHAR_COMEDY"
            ),
            asset_type=(
                "CHARACTER"
            ),
            name=(
                "Comedy Character"
            ),
            purpose=(
                "Master character reference"
            ),
            reference_path=(
                "assets/test/comedy_character.png"
            ),
            required=True,
            master_reference_required=True,
        )
    )

    comedy_prompt = (
        ProductionPrompt(
            shot_id=(
                "EP_GEN_A-S01-SHOT01"
            ),
            scene_number=1,
            duration_seconds=5,
            image_prompt=(
                "Create a bright comedic kitchen frame "
                "with one embarrassed character."
            ),
            video_prompt=(
                "Hold the reaction with minimal motion."
            ),
            negative_prompt=(
                "Avoid exaggerated anatomy."
            ),
            assets=[
                comedy_character
            ],
            dialogue=None,
        )
    )

    # ============================================================
    # CASE B — SCI-FI / PROP
    # ============================================================

    scifi_prop = (
        PromptAssetReference(
            asset_id=(
                "ASSET_PROP_SCIFI_MASTER"
            ),
            entity_id=(
                "PROP_SCIFI_PANEL"
            ),
            asset_type=(
                "PROP"
            ),
            name=(
                "Control Panel"
            ),
            purpose=(
                "Master prop reference"
            ),
            reference_path=(
                "assets/test/scifi_panel.png"
            ),
            required=True,
            master_reference_required=True,
        )
    )

    scifi_prompt = (
        ProductionPrompt(
            shot_id=(
                "EP_GEN_B-S01-SHOT01"
            ),
            scene_number=1,
            duration_seconds=6,
            image_prompt=(
                "Create a quiet science-fiction control room "
                "with a glowing warning panel."
            ),
            video_prompt=(
                "Keep the frame stable."
            ),
            negative_prompt=None,
            assets=[
                scifi_prop
            ],
            dialogue=None,
        )
    )

    # ============================================================
    # CASE C — DRAMA / NO REFERENCES
    # ============================================================

    drama_prompt = (
        ProductionPrompt(
            shot_id=(
                "EP_GEN_C-S01-SHOT01"
            ),
            scene_number=1,
            duration_seconds=7,
            image_prompt=(
                "Create a restrained dramatic frame in an "
                "empty train station at dusk."
            ),
            video_prompt=(
                "Use very subtle environmental motion."
            ),
            negative_prompt=(
                "Avoid melodramatic posing."
            ),
            assets=[],
            dialogue=None,
        )
    )

    return [
        (
            "EP_GEN_A",
            EpisodeProductionPrompts(
                episode_id=(
                    "EP_GEN_A"
                ),
                title=(
                    "Comedy Test"
                ),
                target_duration_seconds=5,
                scenes=[
                    SceneProductionPrompts(
                        scene_number=1,
                        prompts=[
                            comedy_prompt
                        ],
                    )
                ],
                total_shots=1,
            ),
        ),
        (
            "EP_GEN_B",
            EpisodeProductionPrompts(
                episode_id=(
                    "EP_GEN_B"
                ),
                title=(
                    "Sci-Fi Test"
                ),
                target_duration_seconds=6,
                scenes=[
                    SceneProductionPrompts(
                        scene_number=1,
                        prompts=[
                            scifi_prompt
                        ],
                    )
                ],
                total_shots=1,
            ),
        ),
        (
            "EP_GEN_C",
            EpisodeProductionPrompts(
                episode_id=(
                    "EP_GEN_C"
                ),
                title=(
                    "Drama Test"
                ),
                target_duration_seconds=7,
                scenes=[
                    SceneProductionPrompts(
                        scene_number=1,
                        prompts=[
                            drama_prompt
                        ],
                    )
                ],
                total_shots=1,
            ),
        ),
    ]


def main():

    print()
    print(
        "BATCH 12H.3 — GENERATION GENERALIZATION"
    )
    print(
        "========================================"
    )

    compiler = (
        GenerationRequestCompiler(
            default_width=1024,
            default_height=1024,
            default_aspect_ratio="1:1",
            default_output_format="png",
        )
    )

    runner = (
        GenerationRunner(
            provider=(
                FakeGenerationProvider(
                    mode="SUCCESS"
                )
            ),
            max_attempts=3,
        )
    )

    cases = (
        build_episode_prompts()
    )

    passed = 0

    # ============================================================
    # TEST 1 — ALL CASES COMPILE
    # ============================================================

    for (
        episode_id,
        prompts,
    ) in cases:

        requests = (
            compiler.compile(
                prompts
            )
        )

        assert (
            len(requests)
            == 1
        )

        assert (
            requests[0]
            .episode_id
            ==
            episode_id
        )

    print(
        "TEST 1 — synthetic episodes compile → PASSED"
    )

    # ============================================================
    # TEST 2 — ALL CASES GENERATE
    # ============================================================

    for (
        _,
        prompts,
    ) in cases:

        requests = (
            compiler.compile(
                prompts
            )
        )

        result = (
            runner.run(
                requests[0]
            )
        )

        assert (
            result.status
            ==
            GenerationStatus.SUCCEEDED
        )

        assert (
            len(
                result.outputs
            )
            >= 1
        )

        passed += 1

    assert (
        passed
        ==
        3
    )

    print(
        "TEST 2 — all synthetic generations succeed → PASSED"
    )

    # ============================================================
    # TEST 3 — CHARACTER REFERENCE SURVIVES
    # ============================================================

    comedy_requests = (
        compiler.compile(
            cases[0][1]
        )
    )

    comedy_reference = (
        comedy_requests[0]
        .reference_assets[0]
    )

    assert (
        comedy_reference.entity_id
        ==
        "CHAR_COMEDY"
    )

    assert (
        comedy_reference.reference_path
        ==
        "assets/test/comedy_character.png"
    )

    print(
        "TEST 3 — character references generalize → PASSED"
    )

    # ============================================================
    # TEST 4 — PROP REFERENCE SURVIVES
    # ============================================================

    scifi_requests = (
        compiler.compile(
            cases[1][1]
        )
    )

    scifi_reference = (
        scifi_requests[0]
        .reference_assets[0]
    )

    assert (
        scifi_reference.entity_id
        ==
        "PROP_SCIFI_PANEL"
    )

    assert (
        scifi_reference.asset_type
        ==
        "PROP"
    )

    print(
        "TEST 4 — prop references generalize → PASSED"
    )

    # ============================================================
    # TEST 5 — NO-REFERENCE CASE REMAINS VALID
    # ============================================================

    drama_requests = (
        compiler.compile(
            cases[2][1]
        )
    )

    assert (
        drama_requests[0]
        .reference_assets
        == []
    )

    print(
        "TEST 5 — reference-free generation remains valid → PASSED"
    )

    # ============================================================
    # TEST 6 — REQUEST IDS REMAIN DETERMINISTIC
    # ============================================================

    for (
        episode_id,
        prompts,
    ) in cases:

        first = (
            compiler.compile(
                prompts
            )[0]
        )

        second = (
            compiler.compile(
                prompts
            )[0]
        )

        assert (
            first.request_id
            ==
            second.request_id
        )

        assert (
            episode_id
            in first.request_id
        )

    print(
        "TEST 6 — generalized lineage IDs remain deterministic → PASSED"
    )

    # ============================================================
    # TEST 7 — NO CROSS-CASE LEAKAGE
    # ============================================================

    request_ids = {
        compiler.compile(
            prompts
        )[0].request_id
        for (
            _,
            prompts,
        ) in cases
    }

    assert (
        len(
            request_ids
        )
        == 3
    )

    print(
        "TEST 7 — synthetic cases remain isolated → PASSED"
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12H.3 GENERATION GENERALIZATION PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":

    main()