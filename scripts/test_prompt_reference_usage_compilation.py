from pathlib import Path
from tempfile import TemporaryDirectory

from app.generation.request_compiler import (
    GenerationRequestCompiler,
)
from app.models.generation import (
    GenerationReferenceRole,
    GenerationReferenceTransformation,
)
from app.models.prompt import (
    ProductionPrompt,
    PromptAssetReference,
    PromptCameraContext,
    PromptCharacterPerformance,
    PromptEnvironmentContext,
    PromptPropPerformance,
    PromptStyleContext,
    ShotPromptContext,
)
from app.prompting.compiler import PromptCompiler
from app.prompting.negative_prompt_builder import (
    NegativePromptBuilder,
)


def make_asset(
    asset_id: str,
    entity_id: str,
    asset_type: str,
    path: str,
) -> PromptAssetReference:

    return PromptAssetReference(
        asset_id=asset_id,
        entity_id=entity_id,
        asset_type=asset_type,
        name=asset_id,
        purpose=f"Master {asset_type.lower()} reference",
        reference_path=path,
        required=True,
        master_reference_required=True,
    )


def usage_for(
    usages,
    asset_id: str,
):

    return next(
        item
        for item in usages
        if item.asset_id == asset_id
    )


def main():

    print()
    print(
        "BATCH 13G.1-B — SHOT REFERENCE SEMANTICS COMPILATION"
    )
    print(
        "========================================"
    )

    with TemporaryDirectory() as temp_dir:

        root = Path(temp_dir)

        character_path = root / "character.png"
        location_path = root / "location.png"
        prop_path = root / "prop.png"

        character_path.write_bytes(b"character")
        location_path.write_bytes(b"location")
        prop_path.write_bytes(b"prop")

        character_asset = make_asset(
            asset_id="ASSET_CHAR_MASTER",
            entity_id="CHAR_TEST",
            asset_type="CHARACTER",
            path=str(character_path),
        )

        location_asset = make_asset(
            asset_id="ASSET_LOC_MASTER",
            entity_id="LOC_TEST",
            asset_type="LOCATION",
            path=str(location_path),
        )

        prop_asset = make_asset(
            asset_id="ASSET_PROP_MASTER",
            entity_id="PROP_TEST",
            asset_type="PROP",
            path=str(prop_path),
        )

        context = ShotPromptContext(
            shot_id="EP_TEST-S01-SHOT01",
            scene_number=1,
            duration_seconds=5,
            purpose="Test structured reference semantics.",
            style=PromptStyleContext(),
            camera=PromptCameraContext(
                shot_type="MEDIUM",
                camera_movement="STATIC",
                framing="CHARACTER_FOCUSED",
                composition="Character examines the prop.",
            ),
            environment=PromptEnvironmentContext(
                location_id="LOC_TEST",
                location_name="Test Location",
            ),
            characters=[
                PromptCharacterPerformance(
                    entity_id="CHAR_TEST",
                    name="Test Character",
                    action="EXAMINE_PROP",
                    gesture="CONTROLLED_HOLD",
                    facial_movement="FOCUSED",
                )
            ],
            props=[
                PromptPropPerformance(
                    entity_id="PROP_TEST",
                    name="Test Prop",
                    action="READ_DOCUMENT",
                )
            ],
            assets=[
                character_asset,
                location_asset,
                prop_asset,
            ],
        )

        compiler = PromptCompiler()

        usages = compiler._build_reference_usages(
            context
        )

        assert len(usages) == 3

        print(
            "TEST 1 — one reference usage per shot asset → PASSED"
        )

        character_usage = usage_for(
            usages,
            "ASSET_CHAR_MASTER",
        )

        assert character_usage.reference_role == "CHARACTER"
        assert "facial identity" in character_usage.preserve_attributes
        assert "CHANGE_POSE" in character_usage.allowed_transformations
        assert "CHANGE_EXPRESSION" in character_usage.allowed_transformations

        print(
            "TEST 2 — character identity semantics compiled → PASSED"
        )

        location_usage = usage_for(
            usages,
            "ASSET_LOC_MASTER",
        )

        assert location_usage.reference_role == "LOCATION"
        assert "architectural identity" in location_usage.preserve_attributes
        assert "CHANGE_VIEWPOINT" in location_usage.allowed_transformations
        assert "CHANGE_PERSPECTIVE" in location_usage.allowed_transformations

        print(
            "TEST 3 — location identity semantics compiled → PASSED"
        )

        prop_usage = usage_for(
            usages,
            "ASSET_PROP_MASTER",
        )

        assert prop_usage.reference_role == "PROP"
        assert "object identity" in prop_usage.preserve_attributes
        assert "ROTATE" in prop_usage.allowed_transformations
        assert "CHANGE_PERSPECTIVE" in prop_usage.allowed_transformations
        assert "OPEN_CLOSE" in prop_usage.allowed_transformations
        assert "ADAPT_TO_INTERACTION" in prop_usage.allowed_transformations

        print(
            "TEST 4 — interactive prop transformations compiled → PASSED"
        )

        assert "read document" in (
            prop_usage.usage_instruction or ""
        ).lower()

        assert "do not force the camera-facing view" in (
            prop_usage.usage_instruction or ""
        ).lower()

        print(
            "TEST 5 — prop action reaches usage instruction → PASSED"
        )

        stable_context = context.model_copy(
            update={
                "props": [
                    PromptPropPerformance(
                        entity_id="PROP_TEST",
                        name="Test Prop",
                        action="MAINTAIN_ESTABLISHED_STATE",
                    )
                ]
            },
            deep=True,
        )

        stable_usages = compiler._build_reference_usages(
            stable_context
        )

        stable_prop = usage_for(
            stable_usages,
            "ASSET_PROP_MASTER",
        )

        assert "ROTATE" not in stable_prop.allowed_transformations
        assert "OPEN_CLOSE" not in stable_prop.allowed_transformations
        assert "ADAPT_TO_INTERACTION" not in stable_prop.allowed_transformations

        print(
            "TEST 6 — stable prop does not receive interaction transforms → PASSED"
        )

        negative_prompt = NegativePromptBuilder().build(
            context
        )

        assert "prop identity changes" in negative_prompt
        assert "uncontrolled object morphing" in negative_prompt
        assert "unmotivated object redesign" in negative_prompt
        assert "object transformation" not in negative_prompt

        print(
            "TEST 7 — negative prompt preserves identity without blocking valid transforms → PASSED"
        )

        production_prompt = ProductionPrompt(
            shot_id=context.shot_id,
            scene_number=context.scene_number,
            duration_seconds=context.duration_seconds,
            image_prompt="Create the requested keyframe.",
            video_prompt="Animate the approved keyframe.",
            negative_prompt=negative_prompt,
            assets=context.assets,
            reference_usages=usages,
        )

        request = GenerationRequestCompiler(
            default_width=1080,
            default_height=1920,
            default_aspect_ratio="9:16",
            default_output_format="png",
        ).compile_prompt(
            episode_id="EP_TEST",
            prompt=production_prompt,
        )

        assert len(request.reference_assets) == 3

        print(
            "TEST 8 — prompt reference usages reach generation request → PASSED"
        )

        generation_character = request.reference_assets[0]
        generation_location = request.reference_assets[1]
        generation_prop = request.reference_assets[2]

        assert (
            generation_character.reference_role
            == GenerationReferenceRole.CHARACTER
        )

        assert (
            generation_location.reference_role
            == GenerationReferenceRole.LOCATION
        )

        assert (
            generation_prop.reference_role
            == GenerationReferenceRole.PROP
        )

        print(
            "TEST 9 — generation reference roles preserved → PASSED"
        )

        assert (
            GenerationReferenceTransformation.ROTATE
            in generation_prop.allowed_transformations
        )

        assert (
            GenerationReferenceTransformation.OPEN_CLOSE
            in generation_prop.allowed_transformations
        )

        assert (
            GenerationReferenceTransformation.ADAPT_TO_INTERACTION
            in generation_prop.allowed_transformations
        )

        print(
            "TEST 10 — generation transformation permissions preserved → PASSED"
        )

        assert (
            generation_prop.usage_instruction
            == prop_usage.usage_instruction
        )

        assert (
            generation_prop.preserve_attributes
            == prop_usage.preserve_attributes
        )

        print(
            "TEST 11 — preservation and usage semantics preserved exactly → PASSED"
        )

        request_again = GenerationRequestCompiler(
            default_width=1080,
            default_height=1920,
            default_aspect_ratio="9:16",
            default_output_format="png",
        ).compile_prompt(
            episode_id="EP_TEST",
            prompt=production_prompt,
        )

        assert (
            request.model_dump()
            == request_again.model_dump()
        )

        print(
            "TEST 12 — semantic compilation remains deterministic → PASSED"
        )

        assert "gemini" not in production_prompt.model_dump_json().lower()
        assert "google" not in production_prompt.model_dump_json().lower()

        print(
            "TEST 13 — prompt semantics remain provider-agnostic → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13G.1-B SHOT REFERENCE SEMANTICS COMPILATION PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()
