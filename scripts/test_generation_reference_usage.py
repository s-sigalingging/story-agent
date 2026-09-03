import tempfile
from pathlib import Path

from app.generation import (
    GenerationArtifactStore,
    GeminiGenerationProvider,
    GeminiRequestMapper,
)

from app.models.generation import (
    GenerationOutputSpec,
    GenerationReferenceAsset,
    GenerationReferenceRole,
    GenerationReferenceTransformation,
    GenerationRequest,
    GenerationType,
)


def make_reference(
    asset_id: str,
    entity_id: str,
    asset_type: str,
    path: str,
    reference_role=None,
    preserve_attributes=None,
    allowed_transformations=None,
    usage_instruction=None,
):

    return GenerationReferenceAsset(
        asset_id=asset_id,
        entity_id=entity_id,
        asset_type=asset_type,
        name=asset_id,
        reference_path=path,
        reference_role=reference_role,
        preserve_attributes=(
            preserve_attributes
            or []
        ),
        allowed_transformations=(
            allowed_transformations
            or []
        ),
        usage_instruction=(
            usage_instruction
        ),
    )


def make_request(
    references,
):

    return GenerationRequest(
        request_id="GEN_REQ_REFERENCE_USAGE",
        episode_id="EP_REFERENCE_USAGE",
        shot_id="EP_REFERENCE_USAGE-S01-SHOT01",
        generation_type=(
            GenerationType.KEYFRAME
        ),
        prompt=(
            "Create one cinematic frame using the supplied references."
        ),
        negative_prompt=(
            "Avoid identity drift."
        ),
        reference_assets=(
            references
        ),
        output=GenerationOutputSpec(
            width=1080,
            height=1920,
            aspect_ratio="9:16",
            output_format="png",
        ),
    )


def main():

    print()
    print(
        "BATCH 13F.3-C — REFERENCE USAGE CONTRACT"
    )
    print(
        "========================================"
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        root = Path(
            temp_dir
        )

        character_path = (
            root
            /
            "character.png"
        )

        location_path = (
            root
            /
            "location.png"
        )

        prop_path = (
            root
            /
            "prop.png"
        )

        character_path.write_bytes(
            b"character"
        )

        location_path.write_bytes(
            b"location"
        )

        prop_path.write_bytes(
            b"prop"
        )

        # ========================================================
        # TEST 1 — BACKWARD COMPATIBILITY
        # ========================================================

        old_style_reference = (
            GenerationReferenceAsset(
                asset_id="OLD_REFERENCE",
                entity_id="OLD_ENTITY",
                asset_type="PROP",
                name="Old Reference",
                reference_path=str(
                    prop_path
                ),
            )
        )

        assert (
            old_style_reference
            .reference_role
            is None
        )

        assert (
            old_style_reference
            .preserve_attributes
            == []
        )

        assert (
            old_style_reference
            .allowed_transformations
            == []
        )

        print(
            "TEST 1 — old reference contract remains valid → PASSED"
        )

        mapper = (
            GeminiRequestMapper(
                model="gemini-3.1-flash-image"
            )
        )

        # ========================================================
        # TEST 2 — ROLE INFERRED FROM ASSET TYPE
        # ========================================================

        plan = mapper.map(
            make_request([
                old_style_reference
            ])
        )

        mapped_prop = (
            plan.input_images[0]
        )

        assert (
            mapped_prop.reference_role
            ==
            "PROP"
        )

        print(
            "TEST 2 — generation role inferred from asset type → PASSED"
        )

        # ========================================================
        # TEST 3 — PROP IDENTITY DEFAULTS
        # ========================================================

        assert (
            "object identity"
            in mapped_prop
            .preserve_attributes
        )

        assert (
            "shape"
            in mapped_prop
            .preserve_attributes
        )

        print(
            "TEST 3 — prop identity invariants defaulted → PASSED"
        )

        # ========================================================
        # TEST 4 — PROP TRANSFORM DEFAULTS
        # ========================================================

        assert (
            "ROTATE"
            in mapped_prop
            .allowed_transformations
        )

        assert (
            "CHANGE_PERSPECTIVE"
            in mapped_prop
            .allowed_transformations
        )

        assert (
            "OPEN_CLOSE"
            in mapped_prop
            .allowed_transformations
        )

        assert (
            "ADAPT_TO_INTERACTION"
            in mapped_prop
            .allowed_transformations
        )

        print(
            "TEST 4 — prop transformations allowed by default → PASSED"
        )

        # ========================================================
        # TEST 5 — DEFAULT PROP INSTRUCTION IS ANTI-FRONT-LOCK
        # ========================================================

        assert (
            "visible side"
            in mapped_prop
            .usage_instruction
        )

        assert (
            "Do not force"
            in mapped_prop
            .usage_instruction
        )

        assert (
            "camera-facing orientation"
            in mapped_prop
            .usage_instruction
        )

        print(
            "TEST 5 — prop orientation is not treated as invariant → PASSED"
        )

        # ========================================================
        # TEST 6 — EXPLICIT SEMANTICS OVERRIDE DEFAULTS
        # ========================================================

        explicit_prop = make_reference(
            asset_id="PROP_EXPLICIT",
            entity_id="PROP_EXPLICIT",
            asset_type="PROP",
            path=str(
                prop_path
            ),
            reference_role=(
                GenerationReferenceRole.PROP
            ),
            preserve_attributes=[
                "brown folder identity",
                "paper material",
            ],
            allowed_transformations=[
                GenerationReferenceTransformation.ROTATE,
                GenerationReferenceTransformation.ADAPT_TO_INTERACTION,
            ],
            usage_instruction=(
                "Rotate the folder naturally so the open "
                "documents face the character reading them."
            ),
        )

        explicit_plan = mapper.map(
            make_request([
                explicit_prop
            ])
        )

        mapped_explicit = (
            explicit_plan.input_images[0]
        )

        assert (
            mapped_explicit.preserve_attributes
            ==
            [
                "brown folder identity",
                "paper material",
            ]
        )

        assert (
            mapped_explicit.allowed_transformations
            ==
            [
                "ROTATE",
                "ADAPT_TO_INTERACTION",
            ]
        )

        assert (
            mapped_explicit.usage_instruction
            ==
            (
                "Rotate the folder naturally so the open "
                "documents face the character reading them."
            )
        )

        print(
            "TEST 6 — explicit reference semantics override defaults → PASSED"
        )

        # ========================================================
        # TEST 7 — CHARACTER DEFAULTS DIFFER FROM PROP
        # ========================================================

        character = make_reference(
            asset_id="CHARACTER_REFERENCE",
            entity_id="CHARACTER_REFERENCE",
            asset_type="CHARACTER",
            path=str(
                character_path
            ),
        )

        character_plan = mapper.map(
            make_request([
                character
            ])
        )

        mapped_character = (
            character_plan.input_images[0]
        )

        assert (
            mapped_character.reference_role
            ==
            "CHARACTER"
        )

        assert (
            "facial identity"
            in mapped_character
            .preserve_attributes
        )

        assert (
            "CHANGE_POSE"
            in mapped_character
            .allowed_transformations
        )

        assert (
            "OPEN_CLOSE"
            not in mapped_character
            .allowed_transformations
        )

        print(
            "TEST 7 — character reference semantics remain role-specific → PASSED"
        )

        # ========================================================
        # TEST 8 — LOCATION DEFAULTS DIFFER FROM PROP
        # ========================================================

        location = make_reference(
            asset_id="LOCATION_REFERENCE",
            entity_id="LOCATION_REFERENCE",
            asset_type="LOCATION",
            path=str(
                location_path
            ),
        )

        location_plan = mapper.map(
            make_request([
                location
            ])
        )

        mapped_location = (
            location_plan.input_images[0]
        )

        assert (
            mapped_location.reference_role
            ==
            "LOCATION"
        )

        assert (
            "architectural identity"
            in mapped_location
            .preserve_attributes
        )

        assert (
            "CHANGE_VIEWPOINT"
            in mapped_location
            .allowed_transformations
        )

        print(
            "TEST 8 — location semantics remain role-specific → PASSED"
        )

        # ========================================================
        # TEST 9 — PROVIDER INTERLEAVES ROLE TEXT AND IMAGE
        # ========================================================

        artifact_store = (
            GenerationArtifactStore(
                base_path=str(
                    root
                    /
                    "artifacts"
                )
            )
        )

        provider = (
            GeminiGenerationProvider(
                artifact_store=(
                    artifact_store
                )
            )
        )

        combined_request = (
            make_request([
                character,
                location,
                explicit_prop,
            ])
        )

        combined_plan = (
            mapper.map(
                combined_request
            )
        )

        sdk_input = (
            provider._build_sdk_input(
                combined_plan
            )
        )

        assert isinstance(
            sdk_input,
            list,
        )

        # global text
        # role text + image x 3
        assert (
            len(
                sdk_input
            )
            == 7
        )

        assert (
            sdk_input[0][
                "type"
            ]
            ==
            "text"
        )

        assert (
            sdk_input[1][
                "type"
            ]
            ==
            "text"
        )

        assert (
            sdk_input[2][
                "type"
            ]
            ==
            "image"
        )

        assert (
            sdk_input[3][
                "type"
            ]
            ==
            "text"
        )

        assert (
            sdk_input[4][
                "type"
            ]
            ==
            "image"
        )

        assert (
            sdk_input[5][
                "type"
            ]
            ==
            "text"
        )

        assert (
            sdk_input[6][
                "type"
            ]
            ==
            "image"
        )

        print(
            "TEST 9 — SDK references are role-interleaved → PASSED"
        )

        # ========================================================
        # TEST 10 — PROP ROLE TEXT TRAVELS NEXT TO PROP IMAGE
        # ========================================================

        prop_instruction = (
            sdk_input[5][
                "text"
            ]
        )

        assert (
            "ROLE: PROP"
            in prop_instruction
        )

        assert (
            "ROTATE"
            in prop_instruction
        )

        assert (
            "ADAPT_TO_INTERACTION"
            in prop_instruction
        )

        assert (
            "face the character reading them"
            in prop_instruction
        )

        print(
            "TEST 10 — prop interaction semantics reach provider input → PASSED"
        )

        # ========================================================
        # TEST 11 — REFERENCE ORDER REMAINS STABLE
        # ========================================================

        assert (
            combined_plan
            .input_images[0]
            .asset_id
            ==
            "CHARACTER_REFERENCE"
        )

        assert (
            combined_plan
            .input_images[1]
            .asset_id
            ==
            "LOCATION_REFERENCE"
        )

        assert (
            combined_plan
            .input_images[2]
            .asset_id
            ==
            "PROP_EXPLICIT"
        )

        print(
            "TEST 11 — reference lineage/order remains stable → PASSED"
        )

        # ========================================================
        # TEST 12 — DOMAIN REMAINS PROVIDER-AGNOSTIC
        # ========================================================

        reference_fields = (
            GenerationReferenceAsset
            .model_fields
        )

        assert (
            "gemini_role"
            not in reference_fields
        )

        assert (
            "google_instruction"
            not in reference_fields
        )

        assert (
            "sdk_input"
            not in reference_fields
        )

        print(
            "TEST 12 — reference usage contract remains provider-agnostic → PASSED"
        )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 13F.3-C REFERENCE USAGE CONTRACT PASSED"
    )
    print(
        "========================================"
    )


if __name__ == "__main__":
    main()