import json
import re
from pathlib import Path
from typing import List, Optional

from app.models.generation import (
    GenerationRecord,
    GenerationRequest,
    GenerationResult,
)


class GenerationStore:
    """
    Filesystem persistence for generation lineage.

    Each GenerationRequest is stored in its own JSON document.

    Default layout:

        data/generation/
            <episode_id>/
                <request_id>.json

    The store contains no retry policy and no creative approval
    behavior.
    """

    def __init__(
        self,
        base_path: str = (
            "data/generation"
        ),
    ):

        self.base_path = Path(
            base_path
        )

        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ================================================================
    # CREATE
    # ================================================================

    def create(
        self,
        request: GenerationRequest,
    ) -> GenerationRecord:
        """
        Persist a new generation request.

        Existing request IDs may not be silently overwritten.
        """

        path = (
            self._path_for(
                episode_id=(
                    request.episode_id
                ),
                request_id=(
                    request.request_id
                ),
            )
        )

        if path.exists():

            raise ValueError(
                "Generation request already exists: "
                f"{request.request_id}"
            )

        record = (
            GenerationRecord(
                request=request,
                result=None,
            )
        )

        self._write_record(
            path=path,
            record=record,
        )

        return record

    # ================================================================
    # SAVE RESULT
    # ================================================================

    def save_result(
        self,
        result: GenerationResult,
    ) -> GenerationRecord:
        """
        Attach the latest technical result to an existing request.
        """

        record = (
            self.load(
                episode_id=(
                    result.episode_id
                ),
                request_id=(
                    result.request_id
                ),
            )
        )

        if record is None:

            raise ValueError(
                "Cannot save result for unknown "
                "generation request: "
                f"{result.request_id}"
            )

        if (
            record.request.episode_id
            != result.episode_id
        ):

            raise ValueError(
                "Generation result episode_id "
                "does not match request."
            )

        if (
            record.request.shot_id
            != result.shot_id
        ):

            raise ValueError(
                "Generation result shot_id "
                "does not match request."
            )

        if (
            record.request.generation_type
            != result.generation_type
        ):

            raise ValueError(
                "Generation result type "
                "does not match request."
            )

        updated = (
            GenerationRecord(
                request=(
                    record.request
                ),
                result=result,
            )
        )

        path = (
            self._path_for(
                episode_id=(
                    result.episode_id
                ),
                request_id=(
                    result.request_id
                ),
            )
        )

        self._write_record(
            path=path,
            record=updated,
        )

        return updated

    # ================================================================
    # LOAD
    # ================================================================

    def load(
        self,
        episode_id: str,
        request_id: str,
    ) -> Optional[
        GenerationRecord
    ]:

        path = (
            self._path_for(
                episode_id=episode_id,
                request_id=request_id,
            )
        )

        if not path.exists():

            return None

        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return (
            GenerationRecord(
                **payload
            )
        )

    # ================================================================
    # EXISTS
    # ================================================================

    def exists(
        self,
        episode_id: str,
        request_id: str,
    ) -> bool:

        return (
            self._path_for(
                episode_id=episode_id,
                request_id=request_id,
            )
            .exists()
        )

    # ================================================================
    # LIST EPISODE
    # ================================================================

    def list_episode(
        self,
        episode_id: str,
    ) -> List[
        GenerationRecord
    ]:

        episode_path = (
            self.base_path
            /
            self._safe_identifier(
                episode_id
            )
        )

        if not episode_path.exists():

            return []

        records = []

        for path in sorted(
            episode_path.glob(
                "*.json"
            )
        ):

            payload = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            records.append(
                GenerationRecord(
                    **payload
                )
            )

        return records

    # ================================================================
    # DELETE
    # ================================================================

    def delete(
        self,
        episode_id: str,
        request_id: str,
    ) -> bool:

        path = (
            self._path_for(
                episode_id=episode_id,
                request_id=request_id,
            )
        )

        if not path.exists():

            return False

        path.unlink()

        episode_path = (
            path.parent
        )

        if (
            episode_path.exists()
            and
            not any(
                episode_path.iterdir()
            )
        ):

            episode_path.rmdir()

        return True

    # ================================================================
    # INTERNAL WRITE
    # ================================================================

    def _write_record(
        self,
        path: Path,
        record: GenerationRecord,
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = (
            path.with_suffix(
                ".tmp"
            )
        )

        payload = (
            record.model_dump(
                mode="json"
            )
        )

        temporary_path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(
            path
        )

    # ================================================================
    # PATH
    # ================================================================

    def _path_for(
        self,
        episode_id: str,
        request_id: str,
    ) -> Path:

        safe_episode_id = (
            self._safe_identifier(
                episode_id
            )
        )

        safe_request_id = (
            self._safe_identifier(
                request_id
            )
        )

        return (
            self.base_path
            /
            safe_episode_id
            /
            f"{safe_request_id}.json"
        )

    def _safe_identifier(
        self,
        value: str,
    ) -> str:

        cleaned = (
            value.strip()
        )

        if not cleaned:

            raise ValueError(
                "Identifier cannot be empty."
            )

        cleaned = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            cleaned,
        )

        cleaned = (
            cleaned.strip("_")
        )

        if not cleaned:

            raise ValueError(
                "Identifier contains no "
                "usable characters."
            )

        return cleaned