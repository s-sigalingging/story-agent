
import json
from pathlib import Path
from typing import Any, Dict


class EpisodeStore:

    def __init__(self):

        self.runtime_directory = (
            Path("data") / "runtime"
        )

        self.runtime_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    # ================================================================
    # PATH
    # ================================================================

    def get_episode_path(
        self,
        episode_id: str
    ) -> Path:

        return (
            self.runtime_directory
            / f"{episode_id.upper()}.json"
        )

    # ================================================================
    # SAVE
    # ================================================================

    def save(
        self,
        episode_id: str,
        data: Dict[str, Any]
    ) -> None:

        episode_path = (
            self.get_episode_path(
                episode_id
            )
        )

        with open(
            episode_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )

    # ================================================================
    # LOAD
    # ================================================================

    def load(
        self,
        episode_id: str
    ) -> Dict[str, Any]:

        episode_path = (
            self.get_episode_path(
                episode_id
            )
        )

        if not episode_path.exists():

            raise FileNotFoundError(
                f"Runtime state for episode "
                f"{episode_id} was not found."
            )

        with open(
            episode_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # ================================================================
    # EXISTS
    # ================================================================

    def exists(
        self,
        episode_id: str
    ) -> bool:

        return (
            self.get_episode_path(
                episode_id
            ).exists()
        )

