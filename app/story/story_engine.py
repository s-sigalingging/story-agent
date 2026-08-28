from app.models.episode import Episode


class StoryEngine:

    def analyze(self, episode: Episode):

        issues = []
        warnings = []

        # -------------------------------------------------
        # 1. Scene validation
        # -------------------------------------------------

        if not episode.scenes:
            issues.append("Episode contains no scenes.")
            return {
                "status": "FAILED",
                "issues": issues,
                "warnings": warnings
            }

        # -------------------------------------------------
        # 2. Scene numbering
        # -------------------------------------------------

        expected_scene_number = 1

        for scene in episode.scenes:

            if scene.scene_number != expected_scene_number:
                issues.append(
                    f"Scene numbering error. "
                    f"Expected scene {expected_scene_number}, "
                    f"found {scene.scene_number}."
                )

            expected_scene_number += 1

        # -------------------------------------------------
        # 3. Duration analysis
        # -------------------------------------------------

        total_duration = sum(
            scene.duration_seconds
            for scene in episode.scenes
        )

        duration_difference = (
            total_duration -
            episode.target_duration_seconds
        )

        if duration_difference != 0:

            warnings.append(
                f"Episode duration is {total_duration}s "
                f"while target is "
                f"{episode.target_duration_seconds}s."
            )

        # -------------------------------------------------
        # 4. Scene content validation
        # -------------------------------------------------

        for scene in episode.scenes:

            if not scene.location:
                issues.append(
                    f"Scene {scene.scene_number} "
                    f"has no location."
                )

            if not scene.characters:
                warnings.append(
                    f"Scene {scene.scene_number} "
                    f"has no characters."
                )

            if not scene.visual_description:
                warnings.append(
                    f"Scene {scene.scene_number} "
                    f"has no visual description."
                )

            if not scene.narrative_purpose:
                warnings.append(
                    f"Scene {scene.scene_number} "
                    f"has no narrative purpose."
                )

        # -------------------------------------------------
        # 5. Narrative continuity
        # -------------------------------------------------

        continuity = self.check_continuity(episode)

        warnings.extend(continuity)

        # -------------------------------------------------
        # Final status
        # -------------------------------------------------

        status = "FAILED" if issues else "PASSED"

        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "analysis": {
                "scene_count": len(episode.scenes),
                "planned_duration": total_duration,
                "target_duration": episode.target_duration_seconds,
                "duration_difference": duration_difference
            }
        }

    def check_continuity(self, episode: Episode):

        warnings = []

        previous_location = None

        for scene in episode.scenes:

            if previous_location is not None:

                if scene.location != previous_location:

                    if not scene.continuity_notes:

                        warnings.append(
                            f"Scene {scene.scene_number} "
                            f"changes location from "
                            f"'{previous_location}' to "
                            f"'{scene.location}' "
                            f"without continuity notes."
                        )

            previous_location = scene.location

        return warnings