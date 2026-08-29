from typing import Optional

from app.models.episode import Episode
from app.models.state import WorldStateSnapshot

from app.story.story_engine import StoryEngine

from app.analyzers.story_structure_analyzer import (
    StoryStructureAnalyzer,
)

from app.analyzers.entity_analyzer import (
    EntityAnalyzer,
)

from app.analyzers.scene_analyzer import (
    SceneAnalyzer,
)

from app.analyzers.production_intent_analyzer import (
    ProductionIntentAnalyzer,
)

from app.analyzers.continuity_analyzer import (
    ContinuityAnalyzer,
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


class EpisodeOrchestrator:
    """
    Coordinates the complete episode production pipeline.

    The orchestrator contains no story-specific knowledge.

    Persistent world state may be supplied so that canonical state
    from previously approved episodes can be inherited.

    Pipeline:
        Story Analysis
        Story Structure
        Entity Analysis
        Scene Analysis
        Production Intent
        Continuity Analysis
        State Management
        World State Candidate
        Production Planning
        Asset Planning
        Production Execution
        Production Prompts
    """

    def __init__(
        self,
    ):

        # ============================================================
        # WORLD / ENTITY
        # ============================================================

        self.registry = (
            WorldRegistry()
        )

        self.entity_analyzer = (
            EntityAnalyzer()
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

        self.scene_analyzer = (
            SceneAnalyzer()
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
        # STAGE 1 — STORY ANALYSIS
        # ============================================================

        story_analysis = (
            self.story_engine
            .analyze(
                episode
            )
        )

        results["stages"].append({
            "stage": (
                "STORY_ANALYSIS"
            ),
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

            results["status"] = (
                "FAILED"
            )

            return results

        # ============================================================
        # STAGE 2 — STORY STRUCTURE
        # ============================================================

        story_structure = (
            self.story_structure_analyzer
            .analyze(
                episode
            )
        )

        results["stages"].append({
            "stage": (
                "STORY_STRUCTURE"
            ),
            "status": (
                story_structure.status
            ),
            "details": (
                story_structure
                .model_dump()
            ),
        })

        if (
            story_structure.status
            == "FAILED"
        ):

            results["status"] = (
                "FAILED"
            )

            return results

        # ============================================================
        # STAGE 3 — ENTITY ANALYSIS
        # ============================================================

        entity_analysis = (
            self.entity_analyzer
            .analyze(
                episode=(
                    episode
                ),
                registry=(
                    self.registry
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "ENTITY_ANALYSIS"
            ),
            "status": (
                entity_analysis.status
            ),
            "details": (
                entity_analysis
                .model_dump()
            ),
        })

        if (
            entity_analysis.status
            == "FAILED"
        ):

            results["status"] = (
                "FAILED"
            )

            return results

        # ============================================================
        # STAGE 4 — SCENE ANALYSIS
        # ============================================================

        scene_analysis = (
            self.scene_analyzer
            .analyze(
                episode=(
                    episode
                ),
                registry=(
                    self.registry
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "SCENE_ANALYSIS"
            ),
            "status": (
                scene_analysis.status
            ),
            "details": (
                scene_analysis
                .model_dump()
            ),
        })

        if (
            scene_analysis.status
            == "FAILED"
        ):

            results["status"] = (
                "FAILED"
            )

            return results

        # ============================================================
        # STAGE 5 — PRODUCTION INTENT
        # ============================================================

        production_intent = (
            self.production_intent_analyzer
            .analyze(
                episode=(
                    episode
                ),
                scene_analysis=(
                    scene_analysis
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "PRODUCTION_INTENT"
            ),
            "status": (
                production_intent.status
            ),
            "details": (
                production_intent
                .model_dump()
            ),
        })

        if (
            production_intent.status
            == "FAILED"
        ):

            results["status"] = (
                "FAILED"
            )

            return results

        # ============================================================
        # STAGE 6 — CONTINUITY ANALYSIS
        # ============================================================

        continuity = (
            self.continuity_analyzer
            .analyze(
                episode=(
                    episode
                ),
                registry=(
                    self.registry
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "CONTINUITY_ANALYSIS"
            ),
            "status": (
                continuity.status
            ),
            "details": (
                continuity
                .model_dump()
            ),
        })

        if (
            continuity.status
            == "FAILED"
        ):

            results["status"] = (
                "FAILED"
            )

            return results

        # ============================================================
        # STAGE 7 — STATE MANAGEMENT
        # ============================================================

        episode_state = (
            self.state_manager
            .build_episode_state(
                episode=(
                    episode
                ),
                continuity=(
                    continuity
                ),
                initial_world_state=(
                    initial_world_state
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "STATE_MANAGEMENT"
            ),
            "status": (
                "PASSED"
            ),
            "details": (
                episode_state
                .model_dump()
            ),
        })

        # ============================================================
        # STAGE 8 — WORLD STATE
        # ============================================================

        candidate_world_state = (
            episode_state
            .final_world_state
        )

        results["stages"].append({
            "stage": (
                "WORLD_STATE"
            ),
            "status": (
                "PASSED"
            ),
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
        # STAGE 9 — PRODUCTION PLANNING
        # ============================================================

        production_plan = (
            self.production_planner
            .create_plan(
                episode=(
                    episode
                ),
                state=(
                    episode_state
                ),
                scene_analysis=(
                    scene_analysis
                ),
                production_intent=(
                    production_intent
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "PRODUCTION_PLANNING"
            ),
            "status": (
                "PASSED"
            ),
            "details": (
                production_plan
                .model_dump()
            ),
        })

        # ============================================================
        # STAGE 10 — ASSET PLANNING
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
            "stage": (
                "ASSET_PLANNING"
            ),
            "status": (
                "PASSED"
            ),
            "details": (
                asset_plan
                .model_dump()
            ),
        })

        # ============================================================
        # STAGE 11 — PRODUCTION EXECUTION
        # ============================================================

        self.production_execution = (
            ProductionExecution(
                production_plan=(
                    production_plan
                ),
                asset_plan=(
                    asset_plan
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
            "status": (
                "PASSED"
            ),
            "details": (
                execution_plan
            ),
        })

        # ============================================================
        # STAGE 12 — PRODUCTION PROMPTS
        # ============================================================

        production_prompts = (
            self.prompt_compiler
            .compile(
                episode=(
                    episode
                ),
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
                    asset_plan
                ),
            )
        )

        results["stages"].append({
            "stage": (
                "PRODUCTION_PROMPTS"
            ),
            "status": (
                "PASSED"
            ),
            "details": (
                production_prompts
                .model_dump()
            ),
        })

        # ============================================================
        # FINAL STATUS
        # ============================================================

        results["status"] = (
            "WAITING_HUMAN_APPROVAL"
        )

        return results