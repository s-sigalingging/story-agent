import json

from fastapi import (
    FastAPI,
    HTTPException,
)

from app.models.episode import (
    Episode,
)

from app.models.state import (
    WorldStateSnapshot,
)

from app.orchestrator.episode_orchestrator import (
    EpisodeOrchestrator,
)

from app.storage.episode_store import (
    EpisodeStore,
)

from app.world.state_store import (
    WorldStateStore,
)


app = FastAPI(
    title="Archive Studio",
    version="0.2.0",
)


episode_store = (
    EpisodeStore()
)

world_state_store = (
    WorldStateStore()
)


# ================================================================
# CONFIGURATION
# ================================================================

DEFAULT_WORLD_ID = (
    "default"
)


# ================================================================
# HEALTH CHECK
# ================================================================


@app.get("/")
def health_check():

    return {
        "service": (
            "Archive Studio"
        ),
        "status": (
            "ONLINE"
        ),
        "version": (
            "0.2.0"
        ),
    }


# ================================================================
# ORCHESTRATE EPISODE
# ================================================================


@app.post(
    "/episodes/{episode_id}/orchestrate"
)
def orchestrate_episode(
    episode_id: str,
    world_id: str = DEFAULT_WORLD_ID,
):

    normalized_episode_id = (
        episode_id.upper()
    )

    episode_path = (
        f"data/"
        f"{normalized_episode_id.lower()}"
        ".json"
    )

    # ============================================================
    # LOAD EPISODE
    # ============================================================

    try:

        with open(
            episode_path,
            "r",
            encoding="utf-8",
        ) as file:

            episode_data = (
                json.load(
                    file
                )
            )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "Episode not found."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "path": (
                    episode_path
                ),
            },
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    f"Episode file for "
                    f"{normalized_episode_id} "
                    "contains invalid JSON."
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # CREATE EPISODE MODEL
    # ============================================================

    try:

        episode = Episode(
            **episode_data
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Invalid episode data."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # VALIDATE PATH ID AGAINST EPISODE ID
    # ============================================================

    if (
        episode.episode_id.upper()
        != normalized_episode_id
    ):

        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Episode ID in URL "
                    "does not match "
                    "episode_id in episode "
                    "file."
                ),
                "url_episode_id": (
                    normalized_episode_id
                ),
                "file_episode_id": (
                    episode.episode_id
                ),
            },
        )

    # ============================================================
    # LOAD CANONICAL WORLD STATE
    # ============================================================

    try:

        initial_world_state = (
            world_state_store.load(
                world_id
            )
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Canonical world state "
                    "contains invalid JSON."
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Canonical world state "
                    "could not be loaded."
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # RUN ORCHESTRATOR
    # ============================================================

    orchestrator = (
        EpisodeOrchestrator()
    )

    try:

        result = orchestrator.run(
            episode=episode,
            initial_world_state=(
                initial_world_state
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode orchestration "
                    "failed."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # ATTACH WORLD ID TO RUNTIME RESULT
    # ============================================================

    result["world_id"] = (
        world_id
    )

    # ============================================================
    # SAVE RUNTIME RESULT
    # ============================================================

    try:

        episode_store.save(
            episode_id=(
                normalized_episode_id
            ),
            data=result,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode orchestration "
                    "completed, but runtime "
                    "state could not be saved."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # RETURN RESULT
    # ============================================================

    return result


# ================================================================
# GET EPISODE RUNTIME STATE
# ================================================================


@app.get(
    "/episodes/{episode_id}/state"
)
def get_episode_state(
    episode_id: str,
):

    normalized_episode_id = (
        episode_id.upper()
    )

    try:

        result = (
            episode_store.load(
                normalized_episode_id
            )
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "Runtime state for "
                    "episode was not found."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
            },
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Runtime state contains "
                    "invalid JSON."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    return result


# ================================================================
# GET WORLD STATE
# ================================================================


@app.get(
    "/worlds/{world_id}/state"
)
def get_world_state(
    world_id: str,
):

    try:

        state = (
            world_state_store.load(
                world_id
            )
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Canonical world state "
                    "contains invalid JSON."
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Canonical world state "
                    "could not be loaded."
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    if state is None:

        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "World state was not found."
                ),
                "world_id": (
                    world_id
                ),
            },
        )

    return state.model_dump()


# ================================================================
# APPROVE EPISODE
# ================================================================


@app.post(
    "/episodes/{episode_id}/approve"
)
def approve_episode(
    episode_id: str,
):

    normalized_episode_id = (
        episode_id.upper()
    )

    # ============================================================
    # LOAD CURRENT RUNTIME STATE
    # ============================================================

    try:

        result = (
            episode_store.load(
                normalized_episode_id
            )
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "Episode has not been "
                    "orchestrated yet."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
            },
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Runtime state contains "
                    "invalid JSON."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # CHECK CURRENT STATUS
    # ============================================================

    current_status = (
        result.get(
            "status"
        )
    )

    if (
        current_status
        != "WAITING_HUMAN_APPROVAL"
    ):

        raise HTTPException(
            status_code=409,
            detail={
                "message": (
                    "Episode cannot be "
                    "approved from its "
                    "current status."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "current_status": (
                    current_status
                ),
                "required_status": (
                    "WAITING_HUMAN_APPROVAL"
                ),
            },
        )

    # ============================================================
    # RESOLVE WORLD ID
    # ============================================================

    world_id = (
        result.get(
            "world_id",
            DEFAULT_WORLD_ID,
        )
    )

    # ============================================================
    # FIND CANDIDATE WORLD STATE
    # ============================================================

    candidate_world_state_data = (
        _find_world_state_candidate(
            result
        )
    )

    if (
        candidate_world_state_data
        is None
    ):

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode runtime does "
                    "not contain a candidate "
                    "world state."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "world_id": (
                    world_id
                ),
            },
        )

    # ============================================================
    # VALIDATE CANDIDATE WORLD STATE
    # ============================================================

    try:

        candidate_world_state = (
            WorldStateSnapshot(
                **candidate_world_state_data
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Candidate world state "
                    "is invalid."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # COMMIT CANONICAL WORLD STATE
    # ============================================================

    try:

        world_state_store.save(
            world_id=(
                world_id
            ),
            state=(
                candidate_world_state
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode could not be "
                    "approved because the "
                    "canonical world state "
                    "could not be saved."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    # ============================================================
    # UPDATE WORLD STATE STAGE
    # ============================================================

    _mark_world_state_committed(
        result
    )

    # ============================================================
    # UPDATE STATUS
    # ============================================================

    result["status"] = (
        "APPROVED_FOR_PRODUCTION"
    )

    # ============================================================
    # SAVE UPDATED RUNTIME STATE
    # ============================================================

    try:

        episode_store.save(
            episode_id=(
                normalized_episode_id
            ),
            data=result,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode was approved "
                    "and world state was "
                    "committed, but the "
                    "updated runtime state "
                    "could not be saved."
                ),
                "episode_id": (
                    normalized_episode_id
                ),
                "world_id": (
                    world_id
                ),
                "error": (
                    str(error)
                ),
            },
        )

    return result


# ================================================================
# INTERNAL HELPERS
# ================================================================


def _find_world_state_candidate(
    result: dict,
):

    stages = result.get(
        "stages",
        [],
    )

    for stage in stages:

        if (
            stage.get("stage")
            == "WORLD_STATE"
        ):

            details = (
                stage.get(
                    "details",
                    {}
                )
            )

            return details.get(
                "candidate"
            )

    return None


def _mark_world_state_committed(
    result: dict,
):

    stages = result.get(
        "stages",
        [],
    )

    for stage in stages:

        if (
            stage.get("stage")
            == "WORLD_STATE"
        ):

            details = (
                stage.setdefault(
                    "details",
                    {}
                )
            )

            details[
                "commit_status"
            ] = "COMMITTED"

            return