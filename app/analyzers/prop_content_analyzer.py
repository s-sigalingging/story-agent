import re
from typing import Dict, List, Set, Tuple

from app.models.episode import (
    Episode,
    Scene,
)

from app.models.prop_content import (
    EpisodePropContentAnalysis,
    PropContentSemantics,
    ScenePropContentAnalysis,
)

from app.models.scene_analysis import (
    EpisodeSceneAnalysis,
    SceneAnalysis,
)


class PropContentAnalyzer:
    """
    Generic prop-content semantic analyzer.

    This analyzer does NOT discover new props.

    Prop discovery belongs to PropAnalyzer.

    This analyzer receives already-resolved props and determines whether
    they carry meaningful visual information such as:

        TEXT
        IMAGE
        MARKING

    This distinction can later drive:
        - text-sensitive prompt generation
        - close-up readability requirements
        - negative prompting
        - asset/reference requirements

    No story-specific entity names are allowed here.
    """

    # ================================================================
    # GENERIC CONTENT-BEARING OBJECT CLASSES
    # ================================================================

    TEXT_OBJECT_TERMS: Set[str] = {
        "book",
        "card",
        "certificate",
        "contract",
        "document",
        "file",
        "form",
        "journal",
        "label",
        "letter",
        "log",
        "logbook",
        "manual",
        "menu",
        "newspaper",
        "note",
        "notice",
        "paper",
        "record",
        "report",
        "sign",
        "ticket",
    }

    IMAGE_OBJECT_TERMS: Set[str] = {
        "blueprint",
        "diagram",
        "drawing",
        "image",
        "map",
        "painting",
        "photo",
        "photograph",
        "picture",
        "portrait",
        "sketch",
    }

    # ================================================================
    # GENERIC SIGNAL TERMS
    # ================================================================

    TEXT_SIGNAL_TERMS: Set[str] = {
        "caption",
        "code",
        "date",
        "entry",
        "heading",
        "inscription",
        "label",
        "lettering",
        "name",
        "number",
        "serial",
        "signature",
        "text",
        "title",
        "word",
        "words",
        "written",
    }

    READABILITY_SIGNAL_TERMS: Set[str] = {
        "code",
        "decipher",
        "deciphers",
        "lettering",
        "read",
        "readable",
        "reading",
        "reads",
        "serial",
        "signature",
        "text",
        "written",
    }

    IMAGE_SIGNAL_TERMS: Set[str] = {
        "diagram",
        "drawing",
        "image",
        "map",
        "photo",
        "photograph",
        "picture",
        "portrait",
        "sketch",
    }

    MARKING_SIGNAL_TERMS: Set[str] = {
        "barcode",
        "code",
        "emblem",
        "engraving",
        "inscription",
        "insignia",
        "mark",
        "marking",
        "number",
        "seal",
        "serial",
        "signature",
        "stamp",
        "symbol",
    }

    # ================================================================
    # SCORING
    # ================================================================

    CONTENT_THRESHOLD = 0.60

    OBJECT_CLASS_SCORE = 0.75

    STRONG_CONTEXT_SCORE = 0.65

    SUPPORTING_CONTEXT_SCORE = 0.25

    MARKING_CONTEXT_SCORE = 0.70

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze(
        self,
        episode: Episode,
        scene_analysis: EpisodeSceneAnalysis,
    ) -> EpisodePropContentAnalysis:

        scene_map: Dict[
            int,
            SceneAnalysis
        ] = {
            item.scene_number: item
            for item in scene_analysis.scenes
        }

        results = []

        for scene in episode.scenes:

            analyzed_scene = (
                scene_map.get(
                    scene.scene_number
                )
            )

            results.append(
                self._analyze_scene(
                    scene=scene,
                    analyzed_scene=(
                        analyzed_scene
                    ),
                )
            )

        return EpisodePropContentAnalysis(
            status="PASSED",
            episode_id=(
                episode.episode_id
            ),
            scenes=results,
        )

    # ================================================================
    # SCENE
    # ================================================================

    def _analyze_scene(
        self,
        scene: Scene,
        analyzed_scene: SceneAnalysis | None,
    ) -> ScenePropContentAnalysis:

        if analyzed_scene is None:

            return ScenePropContentAnalysis(
                scene_number=(
                    scene.scene_number
                )
            )

        prop_pairs = (
            self._build_prop_pairs(
                analyzed_scene
            )
        )

        if not prop_pairs:

            return ScenePropContentAnalysis(
                scene_number=(
                    scene.scene_number
                )
            )

        context = (
            self._build_scene_context(
                scene
            )
        )

        results = []

        for (
            entity_id,
            prop_name,
        ) in prop_pairs:

            results.append(
                self._classify_prop(
                    entity_id=(
                        entity_id
                    ),
                    prop_name=(
                        prop_name
                    ),
                    context=(
                        context
                    ),
                )
            )

        return ScenePropContentAnalysis(
            scene_number=(
                scene.scene_number
            ),
            props=results,
        )

    # ================================================================
    # PROP PAIRING
    # ================================================================

    def _build_prop_pairs(
        self,
        analysis: SceneAnalysis,
    ) -> List[
        Tuple[str, str]
    ]:
        """
        Pair human-readable prop names with canonical entity IDs.

        We intentionally refuse to guess when the lists do not align.
        """

        if (
            len(
                analysis.props
            )
            !=
            len(
                analysis.prop_ids
            )
        ):

            return []

        return [
            (
                analysis.prop_ids[index],
                analysis.props[index],
            )
            for index in range(
                len(
                    analysis.props
                )
            )
        ]

    # ================================================================
    # CLASSIFICATION
    # ================================================================

    def _classify_prop(
        self,
        entity_id: str,
        prop_name: str,
        context: str,
    ) -> PropContentSemantics:

        normalized_name = (
            self._normalize(
                prop_name
            )
        )

        normalized_context = (
            self._normalize(
                context
            )
        )

        name_words = set(
            normalized_name.split()
        )

        context_words = set(
            normalized_context.split()
        )

        modalities = []

        evidence = []

        text_score = 0.0
        image_score = 0.0
        marking_score = 0.0

        # ============================================================
        # TEXT CONTENT
        # ============================================================

        text_object_matches = (
            name_words
            & self.TEXT_OBJECT_TERMS
        )

        if text_object_matches:

            text_score += (
                self.OBJECT_CLASS_SCORE
            )

            evidence.append(
                "Prop class suggests "
                "text-bearing content."
            )

        text_signal_matches = (
            context_words
            & self.TEXT_SIGNAL_TERMS
        )

        if text_signal_matches:

            text_score += (
                self.SUPPORTING_CONTEXT_SCORE
            )

            evidence.append(
                "Scene context contains "
                "text-related information."
            )

        # ============================================================
        # IMAGE CONTENT
        # ============================================================

        image_object_matches = (
            name_words
            & self.IMAGE_OBJECT_TERMS
        )

        if image_object_matches:

            image_score += (
                self.OBJECT_CLASS_SCORE
            )

            evidence.append(
                "Prop class suggests "
                "image-bearing content."
            )

        image_signal_matches = (
            context_words
            & self.IMAGE_SIGNAL_TERMS
        )

        if image_signal_matches:

            image_score += (
                self.STRONG_CONTEXT_SCORE
            )

            evidence.append(
                "Scene context references "
                "visual image content."
            )

        # ============================================================
        # MARKINGS
        # ============================================================

        marking_matches = (
            context_words
            & self.MARKING_SIGNAL_TERMS
        )

        if marking_matches:

            marking_score += (
                self.MARKING_CONTEXT_SCORE
            )

            evidence.append(
                "Scene context references "
                "meaningful markings."
            )

        # ============================================================
        # MODALITIES
        # ============================================================

        if (
            text_score
            >= self.CONTENT_THRESHOLD
        ):

            modalities.append(
                "TEXT"
            )

        if (
            image_score
            >= self.CONTENT_THRESHOLD
        ):

            modalities.append(
                "IMAGE"
            )

        if (
            marking_score
            >= self.CONTENT_THRESHOLD
        ):

            modalities.append(
                "MARKING"
            )

        # ============================================================
        # READABILITY
        # ============================================================

        readability_matches = (
            context_words
            & self.READABILITY_SIGNAL_TERMS
        )

        readability_required = (
            "TEXT" in modalities
            and
            bool(
                readability_matches
            )
        )

        text_sensitive = (
            "TEXT" in modalities
            or
            "MARKING" in modalities
        )

        visual_detail_sensitive = (
            bool(
                modalities
            )
        )

        # ============================================================
        # CONFIDENCE
        # ============================================================

        confidence = max(
            text_score,
            image_score,
            marking_score,
            0.50,
        )

        confidence = min(
            round(
                confidence,
                2,
            ),
            1.0,
        )

        return PropContentSemantics(
            entity_id=(
                entity_id
            ),
            name=(
                prop_name
            ),
            content_modalities=(
                modalities
            ),
            text_sensitive=(
                text_sensitive
            ),
            readability_required=(
                readability_required
            ),
            visual_detail_sensitive=(
                visual_detail_sensitive
            ),
            confidence=(
                confidence
            ),
            evidence=(
                self._deduplicate(
                    evidence
                )
            ),
        )

    # ================================================================
    # CONTEXT
    # ================================================================

    def _build_scene_context(
        self,
        scene: Scene,
    ) -> str:
        """
        Dialogue may participate here because the prop already exists.

        We are not creating entities from dialogue.

        We are only classifying semantic content carried by an already
        resolved physical prop.
        """

        return " ".join(
            [
                scene.visual_description,
                scene.dialogue,
                scene.narrative_purpose,
                scene.continuity_notes,
            ]
        )

    # ================================================================
    # NORMALIZATION
    # ================================================================

    def _normalize(
        self,
        value: str,
    ) -> str:

        value = (
            value
            .strip()
            .lower()
        )

        value = re.sub(
            r"[^a-z0-9\s'-]",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return (
            value.strip()
        )

    # ================================================================
    # UTILITIES
    # ================================================================

    def _deduplicate(
        self,
        values: List[str],
    ) -> List[str]:

        result = []

        seen = set()

        for value in values:

            key = (
                value.strip()
                .lower()
            )

            if not key:
                continue

            if key in seen:
                continue

            seen.add(
                key
            )

            result.append(
                value
            )

        return result