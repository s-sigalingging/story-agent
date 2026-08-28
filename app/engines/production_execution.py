
from typing import List

from app.models.asset import AssetPlan, AssetReference
from app.models.production import ProductionPlan, ShotPlan


class ShotExecutionPlan:
    """
    Execution-ready representation of a single shot.

    A shot execution plan contains only the assets that are
    explicitly assigned to that shot by AssetPlanner.
    """

    def __init__(
        self,
        shot: ShotPlan,
        assets: List[AssetReference],
    ):
        self.shot_id = shot.shot_id
        self.scene_number = shot.scene_number
        self.duration_seconds = shot.duration_seconds
        self.purpose = shot.purpose

        self.characters = shot.characters
        self.props = shot.props

        self.camera = shot.camera

        self.character_actions = shot.character_actions
        self.prop_actions = shot.prop_actions

        self.visual_constraints = shot.visual_constraints
        self.dialogue = shot.dialogue

        self.assets = assets

    def to_dict(self):
        return {
            "shot_id": self.shot_id,
            "scene_number": self.scene_number,
            "duration_seconds": self.duration_seconds,
            "purpose": self.purpose,
            "characters": self.characters,
            "props": self.props,
            "camera": self.camera.model_dump(),
            "character_actions": [
                action.model_dump()
                for action in self.character_actions
            ],
            "prop_actions": [
                action.model_dump()
                for action in self.prop_actions
            ],
            "visual_constraints": self.visual_constraints,
            "dialogue": self.dialogue,
            "assets": [
                asset.model_dump()
                for asset in self.assets
            ],
        }


class SceneExecutionPlan:
    """
    Execution-ready representation of a scene.
    """

    def __init__(
        self,
        scene_number: int,
        duration_seconds: int,
        shots: List[ShotExecutionPlan],
    ):
        self.scene_number = scene_number
        self.duration_seconds = duration_seconds
        self.shots = shots

    def to_dict(self):
        return {
            "scene_number": self.scene_number,
            "duration_seconds": self.duration_seconds,
            "shots": [
                shot.to_dict()
                for shot in self.shots
            ],
        }


class ProductionExecution:
    """
    Converts production and asset plans into an execution-ready package.

    This class does not generate images, videos, voices, or audio yet.

    Important rule:
    Production execution uses ONLY the assets explicitly assigned
    to each shot by AssetPlanner.

    Scene-level assets are treated as a scene-level asset pool and
    are NOT automatically injected into every shot.
    """

    def __init__(
        self,
        production_plan: ProductionPlan,
        asset_plan: AssetPlan,
    ):
        self.production_plan = production_plan
        self.asset_plan = asset_plan

    # ================================================================
    # SHOT ASSETS
    # ================================================================

    def _get_shot_assets(
        self,
        scene_number: int,
        shot_id: str,
    ) -> List[AssetReference]:
        """
        Return the assets explicitly assigned to a specific shot.

        AssetPlanner is the source of truth for shot-level assets.
        """

        for scene in self.asset_plan.scenes:

            if scene.scene_number != scene_number:
                continue

            for shot in scene.shots:

                if shot.shot_id == shot_id:
                    return shot.assets

        return []

    # ================================================================
    # SHOT EXECUTION
    # ================================================================

    def _build_shot_execution(
        self,
        shot: ShotPlan,
    ) -> ShotExecutionPlan:
        """
        Build execution data for a single shot.

        Only shot-level assets are used here.

        We intentionally do NOT merge scene-level assets into the shot
        because doing so would cause unrelated characters and props
        from the same scene to appear as required assets for every shot.
        """

        shot_assets = self._get_shot_assets(
            shot.scene_number,
            shot.shot_id,
        )

        return ShotExecutionPlan(
            shot=shot,
            assets=shot_assets,
        )

    # ================================================================
    # SCENE EXECUTION
    # ================================================================

    def _build_scene_execution(
        self,
        scene,
    ) -> SceneExecutionPlan:
        """
        Build execution data for a complete scene.
        """

        shots = []

        for shot in scene.shots:

            shot_execution = self._build_shot_execution(
                shot
            )

            shots.append(shot_execution)

        return SceneExecutionPlan(
            scene_number=scene.scene_number,
            duration_seconds=scene.duration_seconds,
            shots=shots,
        )

    # ================================================================
    # BUILD
    # ================================================================

    def build(self) -> dict:
        """
        Build the complete production execution package.

        Each shot receives only the assets explicitly planned for
        that shot by AssetPlanner.
        """

        scenes = []

        for scene in self.production_plan.scenes:

            scene_execution = self._build_scene_execution(
                scene
            )

            scenes.append(scene_execution)

        return {
            "episode_id": self.production_plan.episode_id,
            "title": self.production_plan.title,
            "target_duration_seconds": (
                self.production_plan.target_duration_seconds
            ),
            "scenes": [
                scene.to_dict()
                for scene in scenes
            ],
        }

