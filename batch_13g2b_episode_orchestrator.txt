from typing import Optional

from app.models.episode import Episode
from app.models.state import WorldStateSnapshot

from app.story.story_engine import (
    StoryEngine,
)

from app.analyzers.story_structure_analyzer import (
    StoryStructureAnalyzer,
)

from app.analyzers.prop_analyzer import (
    PropAnalyzer,
)

from app.analyzers.entity_analyzer import (
    EntityAnalyzer,
)

from app.analyzers.scene_analyzer import (
    SceneAnalyzer,
)

from app.analyzers.character_role_analyzer import (
    CharacterRoleAnalyzer,
)

from app.analyzers.prop_content_analyzer import (
    PropContentAnalyzer,
)

from app.analyzers.production_intent_analyzer import (
    ProductionIntentAnalyzer,
)

from app.analyzers.continuity_analyzer import (
    ContinuityAnalyzer,
)

from app.engines.scene_semantic_enricher import (
    SceneSemanticEnricher,
)

from app.engines.state_manager import (
    StateManager,
)

from app.engines.production_planner import (
    ProductionPlanner,
)

from app.engines.asset_planner import (
    AssetPlanner,
)

from app.engines.production_execution import (
    ProductionExecution,
)

from app.prompting.compiler import (
    PromptCompiler,
)

from app.world.registry import (
    WorldRegistry,
)

from app.assets.registry import (
    AssetRegistry,
)

from app.assets.resolver import (
    AssetResolver,
)

from app.assets.validator import (
    AssetValidator,
)

from app.generation.request_compiler import (
    GenerationRequestCompiler,
)

from app.generation.runner import (
    GenerationRunner,
)

from app.models.generation import (
    GenerationStatus,
)


class EpisodeOrchestrator:
    """
    Coordinates the complete episode production pipeline.

    Modes
    -----
    Legacy mode:
        EpisodeOrchestrator()

        Runs through production prompts and returns
        WAITING_HUMAN_APPROVAL.

    Asset-gated mode:
        EpisodeOrchestrator(
            asset_registry=registry
        )

        Resolves and validates physical reference assets before
        production execution.

    Generation-enabled mode:
        EpisodeOrchestrator(
            generation_runner=runner
        )

        Compiles one KEYFRAME GenerationRequest per production
        prompt and executes the generation runner.

    Asset-gated + generation-enabled mode:
        Both systems operate together.
    """

    def __init__(
        self,
        asset_registry: Optional[
            AssetRegistry
        ] = None,
        generation_runner: Optional[
            GenerationRunner
        ] = None,
        generation_request_compiler: Optional[
            GenerationRequestCompiler
        ] = None,
    ):

        # ============================================================
        # WORLD
        # ============================================================

        self.registry = (
            WorldRegistry()
        )

        # ============================================================
        # ASSET REGISTRY
        # ============================================================

        self.asset_registry = (
            asset_registry
        )

        self.asset_resolver = None
        self.asset_validator = None

        if (
            self.asset_registry
            is not None
        ):

            self.asset_resolver = (
                AssetResolver(
                    registry=(
                        self.asset_registry
                    )
                )
            )

            self.asset_validator = (
                AssetValidator(
                    registry=(
                        self.asset_registry
                    )
                )
            )

        # ============================================================
        # GENERATION
        # ============================================================

        self.generation_runner = (
            generation_runner
        )

        self.generation_request_compiler = (
            generation_request_compiler
        )

        if (
            self.generation_runner
            is not None
            and
            self.generation_request_compiler
            is None
        ):

            self.generation_request_compiler = (
                GenerationRequestCompiler()
            )

        # ============================================================
        # ANALYSIS
        # ============================================================

        self.story_engine = (
            StoryEngine()
        )

        self.story_structure_analyzer = (
            StoryStructureAnalyzer()
        )

        self.prop_analyzer = (
            PropAnalyzer()
        )

        self.entity_analyzer = (
            EntityAnalyzer()
        )

        self.scene_analyzer = (
            SceneAnalyzer()
        )

        self.character_role_analyzer = (
            CharacterRoleAnalyzer()
        )

        self.prop_content_analyzer = (
            PropContentAnalyzer()
        )

        self.scene_semantic_enricher = (
            SceneSemanticEnricher()
        )

        self.production_intent_analyzer = (
            ProductionIntentAnalyzer()
        )

        self.continuity_analyzer = (
            ContinuityAnalyzer()
        )

        # ============================================================
        # STATE
        # ============================================================

        self.state_manager = (
            StateManager()
        )

        # ============================================================
        # PRODUCTION
        # ============================================================

        self.production_planner = (
            ProductionPlanner()
        )

        self.asset_planner = (
            AssetPlanner()
        )

        self.production_execution = None

        # ============================================================
        # PROMPTING
        # ============================================================

        self.prompt_compiler = (
            PromptCompiler()
        )

    # ================================================================
    # MAIN PIPELINE
    # ================================================================

    def run(
        self,
        episode: Episode,
        initial_world_state: Optional[
            WorldStateSnapshot
        ] = None,
    ):

        results = {
            "episode_id": (
                episode.episode_id
            ),
            "title": (
                episode.title
            ),
            "status": (
                "ORCHESTRATING"
            ),
            "stages": [],
        }

        # ============================================================
        # STORY ANALYSIS
        # ============================================================

        story_analysis = (
            self.story_engine
            .analyze(
                episode
            )
        )

        results["stages"].append({
            "stage": "STORY_ANALYSIS",
            "status": (
                story_analysis[
                    "status"
                ]
            ),
            "details": (
                story_analysis
            ),
        })

        if (
            story_analysis[
                "status"
            ]
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # STORY STRUCTURE
        # ============================================================

        story_structure = (
            self.story_structure_analyzer
            .analyze(
                episode
            )
        )

        results["stages"].append({
            "stage": "STORY_STRUCTURE",
            "status": (
                story_structure.status
            ),
            "details": (
                story_structure.model_dump()
            ),
        })

        if (
            story_structure.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # PROP ANALYSIS
        # ============================================================

        prop_analysis = (
            self.prop_analyzer
            .analyze(
                episode
            )
        )

        results["stages"].append({
            "stage": "PROP_ANALYSIS",
            "status": (
                prop_analysis.status
            ),
            "details": (
                prop_analysis.model_dump()
            ),
        })

        if (
            prop_analysis.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # ENTITY ANALYSIS
        # ============================================================

        entity_analysis = (
            self.entity_analyzer
            .analyze(
                episode=episode,
                registry=self.registry,
                prop_analysis=(
                    prop_analysis
                ),
            )
        )

        results["stages"].append({
            "stage": "ENTITY_ANALYSIS",
            "status": (
                entity_analysis.status
            ),
            "details": (
                entity_analysis.model_dump()
            ),
        })

        if (
            entity_analysis.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # BASE SCENE ANALYSIS
        # ============================================================

        base_scene_analysis = (
            self.scene_analyzer
            .analyze(
                episode=episode,
                registry=self.registry,
                prop_analysis=(
                    prop_analysis
                ),
                entity_analysis=(
                    entity_analysis
                ),
            )
        )

        if (
            base_scene_analysis.status
            == "FAILED"
        ):

            results["stages"].append({
                "stage": "SCENE_ANALYSIS",
                "status": (
                    base_scene_analysis.status
                ),
                "details": (
                    base_scene_analysis
                    .model_dump()
                ),
            })

            results["status"] = "FAILED"

            return results

        # ============================================================
        # CHARACTER ROLE ANALYSIS
        # ============================================================

        character_role_analysis = (
            self.character_role_analyzer
            .analyze(
                episode=episode,
                scene_analysis=(
                    base_scene_analysis
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "CHARACTER_ROLE_ANALYSIS"
            ),
            "status": (
                character_role_analysis.status
            ),
            "details": (
                character_role_analysis
                .model_dump()
            ),
        })

        if (
            character_role_analysis.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # PROP CONTENT ANALYSIS
        # ============================================================

        prop_content_analysis = (
            self.prop_content_analyzer
            .analyze(
                episode=episode,
                scene_analysis=(
                    base_scene_analysis
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "PROP_CONTENT_ANALYSIS"
            ),
            "status": (
                prop_content_analysis.status
            ),
            "details": (
                prop_content_analysis
                .model_dump()
            ),
        })

        if (
            prop_content_analysis.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # SCENE SEMANTIC ENRICHMENT
        # ============================================================

        scene_analysis = (
            self.scene_semantic_enricher
            .enrich_character_roles(
                scene_analysis=(
                    base_scene_analysis
                ),
                character_role_analysis=(
                    character_role_analysis
                ),
            )
        )

        scene_analysis = (
            self.scene_semantic_enricher
            .enrich_prop_content(
                scene_analysis=(
                    scene_analysis
                ),
                prop_content_analysis=(
                    prop_content_analysis
                ),
            )
        )

        results["stages"].append({
            "stage": "SCENE_ANALYSIS",
            "status": (
                scene_analysis.status
            ),
            "details": (
                scene_analysis.model_dump()
            ),
        })

        if (
            scene_analysis.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # PRODUCTION INTENT
        # ============================================================

        production_intent = (
            self.production_intent_analyzer
            .analyze(
                episode=episode,
                scene_analysis=(
                    scene_analysis
                ),
            )
        )

        results["stages"].append({
            "stage": "PRODUCTION_INTENT",
            "status": (
                production_intent.status
            ),
            "details": (
                production_intent.model_dump()
            ),
        })

        if (
            production_intent.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # CONTINUITY
        # ============================================================

        continuity = (
            self.continuity_analyzer
            .analyze(
                episode=episode,
                registry=self.registry,
            )
        )

        results["stages"].append({
            "stage": "CONTINUITY_ANALYSIS",
            "status": (
                continuity.status
            ),
            "details": (
                continuity.model_dump()
            ),
        })

        if (
            continuity.status
            == "FAILED"
        ):

            results["status"] = "FAILED"

            return results

        # ============================================================
        # STATE
        # ============================================================

        episode_state = (
            self.state_manager
            .build_episode_state(
                episode=episode,
                continuity=continuity,
                initial_world_state=(
                    initial_world_state
                ),
            )
        )

        results["stages"].append({
            "stage": "STATE_MANAGEMENT",
            "status": "PASSED",
            "details": (
                episode_state.model_dump()
            ),
        })

        # ============================================================
        # WORLD STATE
        # ============================================================

        candidate_world_state = (
            episode_state.final_world_state
        )

        results["stages"].append({
            "stage": "WORLD_STATE",
            "status": "PASSED",
            "details": {
                "commit_status": (
                    "PENDING_APPROVAL"
                ),
                "inherited_world_state": (
                    episode_state
                    .inherited_world_state
                ),
                "source_episode_id": (
                    episode_state
                    .source_episode_id
                ),
                "candidate": (
                    candidate_world_state
                    .model_dump()
                ),
            },
        })

        # ============================================================
        # PRODUCTION PLANNING
        # ============================================================

        production_plan = (
            self.production_planner
            .create_plan(
                episode=episode,
                state=episode_state,
                scene_analysis=(
                    scene_analysis
                ),
                production_intent=(
                    production_intent
                ),
            )
        )

        results["stages"].append({
            "stage": "PRODUCTION_PLANNING",
            "status": "PASSED",
            "details": (
                production_plan.model_dump()
            ),
        })

        # ============================================================
        # ASSET PLANNING
        # ============================================================

        asset_plan = (
            self.asset_planner
            .create_plan(
                episode,
                episode_state,
                continuity,
                production_plan,
            )
        )

        results["stages"].append({
            "stage": "ASSET_PLANNING",
            "status": "PASSED",
            "details": (
                asset_plan.model_dump()
            ),
        })

        production_asset_plan = (
            asset_plan
        )

        # ============================================================
        # ASSET RESOLUTION
        # ============================================================

        if (
            self.asset_registry
            is not None
        ):

            resolution_report = (
                self.asset_resolver
                .resolve_plan(
                    asset_plan
                )
            )

            results["stages"].append({
                "stage": (
                    "ASSET_RESOLUTION"
                ),
                "status": (
                    resolution_report
                    .status
                ),
                "details": (
                    resolution_report
                    .model_dump()
                ),
            })

            production_asset_plan = (
                self.asset_resolver
                .hydrate_plan(
                    asset_plan=(
                        asset_plan
                    ),
                    resolution_report=(
                        resolution_report
                    ),
                )
            )

            # ========================================================
            # ASSET VALIDATION
            # ========================================================

            validation_report = (
                self.asset_validator
                .validate_report(
                    episode_id=(
                        episode.episode_id
                    ),
                    requirements=(
                        asset_plan.assets
                    ),
                    resolution_report=(
                        resolution_report
                    ),
                )
            )

            results["stages"].append({
                "stage": (
                    "ASSET_VALIDATION"
                ),
                "status": (
                    validation_report
                    .status
                ),
                "details": (
                    validation_report
                    .model_dump()
                ),
            })

            if (
                validation_report.status
                != "PRODUCTION_READY"
            ):

                results["status"] = (
                    "WAITING_ASSET_READINESS"
                )

                return results

        # ============================================================
        # PRODUCTION EXECUTION
        # ============================================================

        self.production_execution = (
            ProductionExecution(
                production_plan=(
                    production_plan
                ),
                asset_plan=(
                    production_asset_plan
                ),
            )
        )

        execution_plan = (
            self.production_execution
            .build()
        )

        results["stages"].append({
            "stage": (
                "PRODUCTION_EXECUTION"
            ),
            "status": "PASSED",
            "details": execution_plan,
        })

        # ============================================================
        # PRODUCTION PROMPTS
        # ============================================================

        production_prompts = (
            self.prompt_compiler
            .compile(
                episode=episode,
                scene_analysis=(
                    scene_analysis
                ),
                episode_state=(
                    episode_state
                ),
                production_execution=(
                    execution_plan
                ),
                asset_plan=(
                    production_asset_plan
                ),
            )
        )

        results["stages"].append({
            "stage": "PRODUCTION_PROMPTS",
            "status": "PASSED",
            "details": (
                production_prompts
                .model_dump()
            ),
        })

        # ============================================================
        # LEGACY / NON-GENERATION MODE
        # ============================================================

        if (
            self.generation_runner
            is None
        ):

            results["status"] = (
                "WAITING_HUMAN_APPROVAL"
            )

            return results

        # ============================================================
        # GENERATION REQUESTS
        # ============================================================

        generation_requests = (
            self.generation_request_compiler
            .compile(
                production_prompts
            )
        )

        results["stages"].append({
            "stage": (
                "GENERATION_REQUESTS"
            ),
            "status": "PASSED",
            "details": {
                "total_requests": (
                    len(
                        generation_requests
                    )
                ),
                "requests": [
                    request.model_dump()
                    for request
                    in generation_requests
                ],
            },
        })

        # ============================================================
        # KEYFRAME GENERATION
        # ============================================================

        generation_results = []

        generation_failed = False

        for request in (
            generation_requests
        ):

            generation_result = (
                self.generation_runner
                .run(
                    request
                )
            )

            generation_results.append(
                generation_result
            )

            if (
                generation_result.status
                != GenerationStatus.SUCCEEDED
            ):

                generation_failed = True

        generation_stage_status = (
            "FAILED"
            if generation_failed
            else "PASSED"
        )

        results["stages"].append({
            "stage": (
                "KEYFRAME_GENERATION"
            ),
            "status": (
                generation_stage_status
            ),
            "details": {
                "total_requests": (
                    len(
                        generation_requests
                    )
                ),
                "successful": sum(
                    1
                    for result
                    in generation_results
                    if (
                        result.status
                        ==
                        GenerationStatus.SUCCEEDED
                    )
                ),
                "failed": sum(
                    1
                    for result
                    in generation_results
                    if (
                        result.status
                        !=
                        GenerationStatus.SUCCEEDED
                    )
                ),
                "results": [
                    result.model_dump()
                    for result
                    in generation_results
                ],
            },
        })

        # ============================================================
        # GENERATION FAILURE
        # ============================================================

        if generation_failed:

            results["status"] = (
                "GENERATION_FAILED"
            )

            return results

        # ============================================================
        # KEYFRAME REVIEW
        # ============================================================

        results["status"] = (
            "WAITING_KEYFRAME_REVIEW"
        )

        return results