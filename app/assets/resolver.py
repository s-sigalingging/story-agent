from typing import Dict, List

from app.assets.registry import (
    AssetRegistry,
)

from app.models.asset import (
    AssetPlan,
    AssetReference,
    SceneAssetPlan,
    ShotAssetPlan,
)

from app.models.asset_registry import (
    AssetResolutionReport,
    AssetResolutionResult,
    AssetRole,
    AssetStatus,
    RegistryAssetType,
)


class AssetResolver:
    """
    Resolve logical production asset requirements against
    the canonical AssetRegistry.

    Responsibilities
    ----------------
    - match by entity, asset type, and asset role
    - consider APPROVED assets only
    - select the highest approved version
    - return structured resolution results
    - hydrate AssetPlan reference paths without mutating the source plan
    - never modify asset lifecycle state
    """

    def __init__(
        self,
        registry: AssetRegistry,
    ):

        self.registry = registry

    # ================================================================
    # SINGLE REQUIREMENT
    # ================================================================

    def resolve_requirement(
        self,
        requirement: AssetReference,
        role: AssetRole = (
            AssetRole.MASTER_REFERENCE
        ),
    ) -> AssetResolutionResult:

        asset_type = (
            self._registry_asset_type(
                requirement.asset_type
            )
        )

        candidates = (
            self.registry.find(
                entity_id=(
                    requirement.entity_id
                ),
                asset_type=(
                    asset_type
                ),
                role=role,
                status=(
                    AssetStatus.APPROVED
                ),
            )
        )

        if not candidates:

            return (
                AssetResolutionResult(
                    requirement_asset_id=(
                        requirement.asset_id
                    ),
                    entity_id=(
                        requirement.entity_id
                    ),
                    asset_type=(
                        asset_type
                    ),
                    role=role,
                    resolved=False,
                    reason=(
                        "No approved asset found "
                        "for the required "
                        "entity/type/role."
                    ),
                )
            )

        selected = max(
            candidates,
            key=lambda item: (
                item.version,
                item.asset_id,
            ),
        )

        return (
            AssetResolutionResult(
                requirement_asset_id=(
                    requirement.asset_id
                ),
                entity_id=(
                    requirement.entity_id
                ),
                asset_type=(
                    asset_type
                ),
                role=role,
                resolved=True,
                resolved_asset_id=(
                    selected.asset_id
                ),
                reference_path=(
                    selected.reference_path
                ),
                version=(
                    selected.version
                ),
                status=(
                    selected.status
                ),
                reason=(
                    "Resolved to highest "
                    "approved matching "
                    "asset version."
                ),
            )
        )

    # ================================================================
    # MANY REQUIREMENTS
    # ================================================================

    def resolve_requirements(
        self,
        episode_id: str,
        requirements: List[
            AssetReference
        ],
    ) -> AssetResolutionReport:

        resolutions = []

        unresolved_required = []

        for requirement in requirements:

            resolution = (
                self.resolve_requirement(
                    requirement
                )
            )

            resolutions.append(
                resolution
            )

            if (
                requirement.required
                and
                not resolution.resolved
            ):

                unresolved_required.append(
                    resolution
                )

        status = (
            "PASSED"
            if not unresolved_required
            else "BLOCKED"
        )

        return (
            AssetResolutionReport(
                episode_id=(
                    episode_id
                ),
                status=status,
                resolutions=(
                    resolutions
                ),
            )
        )

    # ================================================================
    # ASSET PLAN RESOLUTION
    # ================================================================

    def resolve_plan(
        self,
        asset_plan: AssetPlan,
    ) -> AssetResolutionReport:

        return (
            self.resolve_requirements(
                episode_id=(
                    asset_plan.episode_id
                ),
                requirements=(
                    asset_plan.assets
                ),
            )
        )

    # ================================================================
    # ASSET PLAN HYDRATION
    # ================================================================

    def hydrate_plan(
        self,
        asset_plan: AssetPlan,
        resolution_report: (
            AssetResolutionReport
        ),
    ) -> AssetPlan:
        """
        Return a new AssetPlan with resolved reference paths applied.

        The original AssetPlan is never mutated.

        Logical requirement asset IDs are preserved.
        Only reference_path is hydrated.
        """

        resolution_map: Dict[
            str,
            AssetResolutionResult,
        ] = {
            item.requirement_asset_id: item
            for item
            in resolution_report.resolutions
        }

        hydrated_assets = [
            self._hydrate_asset_reference(
                asset=asset,
                resolution_map=(
                    resolution_map
                ),
            )
            for asset
            in asset_plan.assets
        ]

        hydrated_scenes = []

        for scene in asset_plan.scenes:

            hydrated_scene_assets = [
                self._hydrate_asset_reference(
                    asset=asset,
                    resolution_map=(
                        resolution_map
                    ),
                )
                for asset
                in scene.assets
            ]

            hydrated_shots = []

            for shot in scene.shots:

                hydrated_shot_assets = [
                    self._hydrate_asset_reference(
                        asset=asset,
                        resolution_map=(
                            resolution_map
                        ),
                    )
                    for asset
                    in shot.assets
                ]

                hydrated_shots.append(
                    ShotAssetPlan(
                        shot_id=(
                            shot.shot_id
                        ),
                        assets=(
                            hydrated_shot_assets
                        ),
                    )
                )

            hydrated_scenes.append(
                SceneAssetPlan(
                    scene_number=(
                        scene.scene_number
                    ),
                    assets=(
                        hydrated_scene_assets
                    ),
                    shots=(
                        hydrated_shots
                    ),
                )
            )

        return (
            AssetPlan(
                episode_id=(
                    asset_plan.episode_id
                ),
                title=(
                    asset_plan.title
                ),
                assets=(
                    hydrated_assets
                ),
                scenes=(
                    hydrated_scenes
                ),
            )
        )

    def _hydrate_asset_reference(
        self,
        asset: AssetReference,
        resolution_map: Dict[
            str,
            AssetResolutionResult,
        ],
    ) -> AssetReference:

        resolution = (
            resolution_map.get(
                asset.asset_id
            )
        )

        if (
            resolution is None
            or
            not resolution.resolved
            or
            not resolution.reference_path
        ):

            return asset.model_copy(
                deep=True
            )

        return asset.model_copy(
            update={
                "reference_path": (
                    resolution.reference_path
                )
            },
            deep=True,
        )

    # ================================================================
    # TYPE MAPPING
    # ================================================================

    def _registry_asset_type(
        self,
        value: str,
    ) -> RegistryAssetType:

        normalized = (
            value
            or ""
        ).strip().upper()

        mapping = {
            "CHARACTER": (
                RegistryAssetType.CHARACTER
            ),
            "LOCATION": (
                RegistryAssetType.LOCATION
            ),
            "PROP": (
                RegistryAssetType.PROP
            ),
        }

        resolved = (
            mapping.get(
                normalized
            )
        )

        if resolved is None:

            raise ValueError(
                "Unsupported production "
                "asset type: "
                f"{value!r}"
            )

        return resolved