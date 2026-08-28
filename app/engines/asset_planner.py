
from app.models.episode import Episode
from app.models.state import EpisodeState
from app.models.continuity import EpisodeContinuity
from app.models.production import ProductionPlan

from app.models.asset import (
    AssetPlan,
    AssetReference,
    SceneAssetPlan,
    ShotAssetPlan
)


class AssetPlanner:

    def create_plan(
        self,
        episode: Episode,
        state: EpisodeState,
        continuity: EpisodeContinuity,
        production_plan: ProductionPlan
    ) -> AssetPlan:

        all_assets = {}

        scene_plans = []

        for scene_plan in production_plan.scenes:

            scene_state = state.scene_states[
                scene_plan.scene_number
            ]

            scene_continuity = next(
                scene
                for scene in continuity.scenes
                if scene.scene_number
                == scene_plan.scene_number
            )

            scene_assets = []

            # ========================================================
            # CHARACTER ASSETS
            # ========================================================

            for character_id in scene_state.active_characters:

                character = state.characters[
                    character_id
                ]

                asset = self.build_character_asset(
                    character
                )

                scene_assets.append(asset)
                all_assets[asset.asset_id] = asset

            # ========================================================
            # LOCATION ASSET
            # ========================================================

            location = scene_state.location

            location_asset = (
                self.build_location_asset(
                    location
                )
            )

            scene_assets.append(location_asset)
            all_assets[
                location_asset.asset_id
            ] = location_asset

            # ========================================================
            # PROP ASSETS
            # ========================================================

            for prop_id in scene_state.active_props:

                prop = state.props[
                    prop_id
                ]

                asset = self.build_prop_asset(
                    prop
                )

                scene_assets.append(asset)
                all_assets[
                    asset.asset_id
                ] = asset

            # ========================================================
            # SHOT ASSETS
            # ========================================================

            shot_plans = []

            for shot in scene_plan.shots:

                shot_assets = []

                # Character references

                for character_id in shot.characters:

                    character = state.characters[
                        character_id
                    ]

                    asset = self.build_character_asset(
                        character
                    )

                    shot_assets.append(asset)

                # Location reference

                location = state.locations[
                    scene_plan.location_id
                ]

                location_asset = (
                    self.build_location_asset(
                        location
                    )
                )

                shot_assets.append(
                    location_asset
                )

                # Prop references

                for prop_id in shot.props:

                    prop = state.props[
                        prop_id
                    ]

                    asset = self.build_prop_asset(
                        prop
                    )

                    shot_assets.append(
                        asset
                    )

                shot_plans.append(
                    ShotAssetPlan(
                        shot_id=shot.shot_id,
                        assets=shot_assets
                    )
                )

            scene_plans.append(
                SceneAssetPlan(
                    scene_number=scene_plan.scene_number,

                    assets=scene_assets,

                    shots=shot_plans
                )
            )

        return AssetPlan(
            episode_id=episode.episode_id,

            title=episode.title,

            assets=list(
                all_assets.values()
            ),

            scenes=scene_plans
        )

    # ================================================================
    # CHARACTER
    # ================================================================

    def build_character_asset(
        self,
        character
    ) -> AssetReference:

        asset_id = (
            f"ASSET_{character.entity_id}_MASTER"
        )

        return AssetReference(
            asset_id=asset_id,

            entity_id=character.entity_id,

            asset_type="CHARACTER",

            name=character.name,

            purpose="Master character reference",

            required=True,

            master_reference_required=(
                character.master_character_required
            )
        )

    # ================================================================
    # LOCATION
    # ================================================================

    def build_location_asset(
        self,
        location
    ) -> AssetReference:

        asset_id = (
            f"ASSET_{location.entity_id}_MASTER"
        )

        return AssetReference(
            asset_id=asset_id,

            entity_id=location.entity_id,

            asset_type="LOCATION",

            name=location.name,

            purpose="Master location reference",

            required=True,

            master_reference_required=False
        )

    # ================================================================
    # PROP
    # ================================================================

    def build_prop_asset(
        self,
        prop
    ) -> AssetReference:

        asset_id = (
            f"ASSET_{prop.entity_id}_MASTER"
        )

        return AssetReference(
            asset_id=asset_id,

            entity_id=prop.entity_id,

            asset_type="PROP",

            name=prop.name,

            purpose="Master prop reference",

            required=True,

            master_reference_required=False
        )

