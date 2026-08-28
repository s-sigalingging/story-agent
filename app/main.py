
import json

from fastapi import FastAPI, HTTPException

from app.models.episode import Episode

from app.orchestrator.episode_orchestrator import (
    EpisodeOrchestrator
)

from app.storage.episode_store import (
    EpisodeStore
)


app = FastAPI(
    title="Archive Studio",
    version="0.1.0"
)


episode_store = EpisodeStore()


# ================================================================
# HEALTH CHECK
# ================================================================

@app.get("/")
def health_check():

    return {
        "service": "Archive Studio",
        "status": "ONLINE"
    }


# ================================================================
# ORCHESTRATE EPISODE
# ================================================================

@app.post("/episodes/{episode_id}/orchestrate")
def orchestrate_episode(
    episode_id: str
):

    episode_path = (
        f"data/{episode_id.lower()}.json"
    )

    # ============================================================
    # LOAD EPISODE
    # ============================================================

    try:

        with open(
            episode_path,
            "r",
            encoding="utf-8"
        ) as file:

            episode_data = json.load(file)

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "message": "Episode not found.",
                "episode_id": episode_id,
                "path": episode_path
            }
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    f"Episode file for {episode_id} "
                    "contains invalid JSON."
                ),
                "error": str(error)
            }
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
                "message": "Invalid episode data.",
                "episode_id": episode_id,
                "error": str(error)
            }
        )

    # ============================================================
    # VALIDATE PATH ID AGAINST EPISODE ID
    # ============================================================

    if episode.episode_id != episode_id:

        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Episode ID in URL does not match "
                    "episode_id in episode file."
                ),
                "url_episode_id": episode_id,
                "file_episode_id": episode.episode_id
            }
        )

    # ============================================================
    # RUN ORCHESTRATOR
    # ============================================================

    orchestrator = EpisodeOrchestrator()

    try:

        result = orchestrator.run(
            episode
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode orchestration failed."
                ),
                "episode_id": episode_id,
                "error": str(error)
            }
        )

    # ============================================================
    # SAVE RUNTIME RESULT
    # ============================================================

    try:

        episode_store.save(
            episode_id=episode_id,
            data=result
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode orchestration completed, "
                    "but runtime state could not be saved."
                ),
                "episode_id": episode_id,
                "error": str(error)
            }
        )

    # ============================================================
    # RETURN RESULT
    # ============================================================

    return result


# ================================================================
# GET EPISODE RUNTIME STATE
# ================================================================

@app.get("/episodes/{episode_id}/state")
def get_episode_state(
    episode_id: str
):

    try:

        result = episode_store.load(
            episode_id
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "Runtime state for episode "
                    "was not found."
                ),
                "episode_id": episode_id
            }
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Runtime state contains invalid JSON."
                ),
                "episode_id": episode_id,
                "error": str(error)
            }
        )

    return result


# ================================================================
# APPROVE EPISODE
# ================================================================

@app.post("/episodes/{episode_id}/approve")
def approve_episode(
    episode_id: str
):

    # ============================================================
    # LOAD CURRENT RUNTIME STATE
    # ============================================================

    try:

        result = episode_store.load(
            episode_id
        )

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "Episode has not been orchestrated yet."
                ),
                "episode_id": episode_id
            }
        )

    except json.JSONDecodeError as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Runtime state contains invalid JSON."
                ),
                "episode_id": episode_id,
                "error": str(error)
            }
        )

    # ============================================================
    # CHECK CURRENT STATUS
    # ============================================================

    current_status = result.get(
        "status"
    )

    if current_status != "WAITING_HUMAN_APPROVAL":

        raise HTTPException(
            status_code=409,
            detail={
                "message": (
                    "Episode cannot be approved "
                    "from its current status."
                ),
                "episode_id": episode_id,
                "current_status": current_status,
                "required_status": (
                    "WAITING_HUMAN_APPROVAL"
                )
            }
        )

    # ============================================================
    # UPDATE STATUS
    # ============================================================

    result["status"] = (
        "APPROVED_FOR_PRODUCTION"
    )

    # ============================================================
    # SAVE UPDATED STATE
    # ============================================================

    try:

        episode_store.save(
            episode_id=episode_id,
            data=result
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    "Episode was approved, "
                    "but the updated state could not be saved."
                ),
                "episode_id": episode_id,
                "error": str(error)
            }
        )

    # ============================================================
    # RETURN UPDATED STATE
    # ============================================================

    return result

