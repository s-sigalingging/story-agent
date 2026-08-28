
from app.models.episode import Episode

from app.story.story_engine import StoryEngine

from app.analyzers.story_structure_analyzer import (
    StoryStructureAnalyzer
)

from app.analyzers.continuity_analyzer import (
    ContinuityAnalyzer
)

from app.engines.state_manager import (
    StateManager
)

from app.engines.production_planner import (
    ProductionPlanner
)

from app.engines.asset_planner import (
    AssetPlanner
)

from app.engines.production_execution import (
    ProductionExecution
)


class EpisodeOrchestrator:

    def __init__(self):

        # ============================================================
        # ANALYSIS COMPONENTS
        # ============================================================

        self.story_engine = StoryEngine()

        self.story_structure_analyzer = (
            StoryStructureAnalyzer()
        )

        self.continuity_analyzer = (
            ContinuityAnalyzer()
        )

        # ============================================================
        # STATE MANAGEMENT
        # ============================================================

        self.state_manager = StateManager()

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

    # ================================================================
    # MAIN PIPELINE
    # ================================================================

    def run(
        self,
        episode: Episode
    ):

        results = {

            "episode_id": episode.episode_id,

            "title": episode.title,

            "status": "ORCHESTRATING",

            "stages": []
        }

        # ============================================================
        # STAGE 1 — STORY ANALYSIS
        # ============================================================

        story_analysis = (
            self.story_engine.analyze(
                episode
            )
        )

        results["stages"].append({

            "stage": "STORY_ANALYSIS",

            "status": story_analysis["status"],

            "details": story_analysis
        })

        if story_analysis["status"] == "FAILED":

            results["status"] = "FAILED"

            return results

        # ============================================================
        # STAGE 2 — STORY STRUCTURE
        # ============================================================

        story_structure = (
            self.story_structure_analyzer.analyze(
                episode
            )
        )

        results["stages"].append({

            "stage": "STORY_STRUCTURE",

            "status": story_structure.status,

            "details": story_structure.model_dump()
        })

        if story_structure.status == "FAILED":

            results["status"] = "FAILED"

            return results

        # ============================================================
        # STAGE 3 — CONTINUITY ANALYSIS
        # ============================================================

        continuity = (
            self.continuity_analyzer.analyze(
                episode
            )
        )

        results["stages"].append({

            "stage": "CONTINUITY_ANALYSIS",

            "status": continuity.status,

            "details": continuity.model_dump()
        })

        if continuity.status == "FAILED":

            results["status"] = "FAILED"

            return results

        # ============================================================
        # STAGE 4 — STATE MANAGEMENT
        # ============================================================

        episode_state = (
            self.state_manager.build_episode_state(
                episode,
                continuity
            )
        )

        results["stages"].append({

            "stage": "STATE_MANAGEMENT",

            "status": "PASSED",

            "details": episode_state.model_dump()
        })

        # ============================================================
        # STAGE 5 — PRODUCTION PLANNING
        # ============================================================

        production_plan = (
            self.production_planner.create_plan(
                episode,
                episode_state
            )
        )

        results["stages"].append({

            "stage": "PRODUCTION_PLANNING",

            "status": "PASSED",

            "details": production_plan.model_dump()
        })

        # ============================================================
        # STAGE 6 — ASSET PLANNING
        # ============================================================

        asset_plan = (
            self.asset_planner.create_plan(
                episode,
                episode_state,
                continuity,
                production_plan
            )
        )

        results["stages"].append({

            "stage": "ASSET_PLANNING",

            "status": "PASSED",

            "details": asset_plan.model_dump()
        })

        # ============================================================
        # STAGE 7 — PRODUCTION EXECUTION
        # ============================================================

        self.production_execution = ProductionExecution(
            production_plan=production_plan,
            asset_plan=asset_plan
        )

        execution_plan = (
            self.production_execution.build()
        )

        results["stages"].append({

            "stage": "PRODUCTION_EXECUTION",

            "status": "PASSED",

            "details": execution_plan
        })

        # ============================================================
        # FINAL STATUS
        # ============================================================

        results["status"] = (
            "WAITING_HUMAN_APPROVAL"
        )

        return results

