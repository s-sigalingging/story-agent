from pathlib import Path
import re


class GenerationArtifactStore:
    """
    Filesystem storage for generated media artifacts.

    Responsibilities:
    - build deterministic artifact paths
    - sanitize filesystem identifiers
    - write physical bytes
    - prevent accidental overwrite by default
    - verify physical artifact existence
    - delete artifacts when explicitly requested

    This store does not:
    - call generation providers
    - make creative approval decisions
    - manage generation retry policy
    - persist GenerationRequest / GenerationResult lineage
    """

    def __init__(
        self,
        base_path: str = "data/generated",
    ):

        self.base_path = Path(
            base_path
        )

        self.base_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ================================================================
    # WRITE
    # ================================================================

    def write(
        self,
        episode_id: str,
        shot_id: str,
        output_id: str,
        output_format: str,
        content: bytes,
        overwrite: bool = False,
    ) -> str:
        """
        Persist one generated artifact and return its physical path.
        """

        if not isinstance(
            content,
            bytes,
        ):

            raise TypeError(
                "Artifact content must be bytes."
            )

        if len(content) == 0:

            raise ValueError(
                "Artifact content cannot be empty."
            )

        path = (
            self.build_path(
                episode_id=episode_id,
                shot_id=shot_id,
                output_id=output_id,
                output_format=output_format,
            )
        )

        if (
            path.exists()
            and
            not overwrite
        ):

            raise FileExistsError(
                "Generation artifact already exists: "
                f"{path}"
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = (
            path.with_suffix(
                path.suffix
                + ".tmp"
            )
        )

        temporary_path.write_bytes(
            content
        )

        temporary_path.replace(
            path
        )

        if (
            not path.exists()
            or
            not path.is_file()
        ):

            raise IOError(
                "Generation artifact was not "
                "materialized successfully."
            )

        if (
            path.stat().st_size
            <= 0
        ):

            raise IOError(
                "Generation artifact was written "
                "with zero bytes."
            )

        return str(
            path
        )

    # ================================================================
    # BUILD PATH
    # ================================================================

    def build_path(
        self,
        episode_id: str,
        shot_id: str,
        output_id: str,
        output_format: str,
    ) -> Path:

        safe_episode_id = (
            self._safe_identifier(
                episode_id
            )
        )

        safe_shot_id = (
            self._safe_identifier(
                shot_id
            )
        )

        safe_output_id = (
            self._safe_identifier(
                output_id
            )
        )

        safe_format = (
            self._safe_format(
                output_format
            )
        )

        return (
            self.base_path
            /
            safe_episode_id
            /
            safe_shot_id
            /
            f"{safe_output_id}.{safe_format}"
        )

    # ================================================================
    # EXISTS
    # ================================================================

    def exists(
        self,
        episode_id: str,
        shot_id: str,
        output_id: str,
        output_format: str,
    ) -> bool:

        return (
            self.build_path(
                episode_id=episode_id,
                shot_id=shot_id,
                output_id=output_id,
                output_format=output_format,
            )
            .is_file()
        )

    # ================================================================
    # DELETE
    # ================================================================

    def delete(
        self,
        episode_id: str,
        shot_id: str,
        output_id: str,
        output_format: str,
    ) -> bool:

        path = (
            self.build_path(
                episode_id=episode_id,
                shot_id=shot_id,
                output_id=output_id,
                output_format=output_format,
            )
        )

        if not path.exists():

            return False

        path.unlink()

        shot_directory = (
            path.parent
        )

        episode_directory = (
            shot_directory.parent
        )

        if (
            shot_directory.exists()
            and
            not any(
                shot_directory.iterdir()
            )
        ):

            shot_directory.rmdir()

        if (
            episode_directory.exists()
            and
            not any(
                episode_directory.iterdir()
            )
        ):

            episode_directory.rmdir()

        return True

    # ================================================================
    # VERIFY
    # ================================================================

    def verify_path(
        self,
        path: str,
    ) -> bool:

        physical_path = Path(
            path
        )

        return (
            physical_path.exists()
            and
            physical_path.is_file()
            and
            physical_path.stat().st_size
            > 0
        )

    # ================================================================
    # SANITIZATION
    # ================================================================

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

    def _safe_format(
        self,
        value: str,
    ) -> str:

        cleaned = (
            value.strip()
            .lower()
        )

        if cleaned.startswith(
            "."
        ):

            cleaned = (
                cleaned[1:]
            )

        if not cleaned:

            raise ValueError(
                "output_format cannot be empty."
            )

        if (
            re.fullmatch(
                r"[a-z0-9]+",
                cleaned,
            )
            is None
        ):

            raise ValueError(
                "output_format contains "
                "unsupported characters."
            )

        return cleaned