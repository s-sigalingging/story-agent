import re
from typing import Dict, List, Optional, Tuple

from app.models.character_role import (
    CharacterRoleAnalysis,
    EpisodeCharacterRoleAnalysis,
    SceneCharacterRoleAnalysis,
)

from app.models.episode import (
    Episode,
    Scene,
)

from app.models.scene_analysis import (
    EpisodeSceneAnalysis,
    SceneAnalysis,
)


class CharacterRoleAnalyzer:
    """
    Generic character-role analyzer.

    Responsibilities
    ----------------
    - distinguish active subjects from supporting characters
    - detect observers / passive presence
    - select a primary subject when semantic evidence supports it
    - remain story-agnostic

    This analyzer does not decide camera grammar or shot structure.
    It only describes semantic roles already present in scene text.
    """

    # ================================================================
    # ACTIVE INTERACTIONS
    # ================================================================

    ACTIVE_INTERACTIONS = {
        "examines": "EXAMINE",
        "examine": "EXAMINE",
        "studies": "STUDY",
        "study": "STUDY",
        "opens": "OPEN",
        "open": "OPEN",
        "reads": "READ",
        "read": "READ",
        "holds": "HOLD",
        "hold": "HOLD",
        "finds": "FIND",
        "find": "FIND",
        "discovers": "DISCOVER",
        "discover": "DISCOVER",
        "takes": "TAKE",
        "take": "TAKE",
        "grabs": "GRAB",
        "grab": "GRAB",
        "uses": "USE",
        "use": "USE",
        "inspects": "INSPECT",
        "inspect": "INSPECT",
        "checks": "CHECK",
        "check": "CHECK",
        "unlocks": "UNLOCK",
        "unlock": "UNLOCK",
        "questions": "QUESTION",
        "question": "QUESTION",
        "confronts": "CONFRONT",
        "confront": "CONFRONT",
        "speaks": "SPEAK",
        "says": "SPEAK",
        "asks": "ASK",
        "replies": "REPLY",
        "enters": "ENTER",
        "enter": "ENTER",
        "walks": "MOVE",
        "moves": "MOVE",
        "approaches": "APPROACH",
    }

    # ================================================================
    # SUPPORTING / PASSIVE INTERACTIONS
    # ================================================================

    SUPPORTING_INTERACTIONS = {
        "stands nearby": (
            "SUPPORTING_PRESENCE",
            "STAND_NEARBY",
        ),
        "stands behind": (
            "SUPPORTING_PRESENCE",
            "STAND_BEHIND",
        ),
        "stands beside": (
            "SUPPORTING_PRESENCE",
            "STAND_BESIDE",
        ),
        "waits nearby": (
            "SUPPORTING_PRESENCE",
            "WAIT_NEARBY",
        ),
        "waits": (
            "SUPPORTING_PRESENCE",
            "WAIT",
        ),
        "watches": (
            "OBSERVER",
            "WATCH",
        ),
        "observes": (
            "OBSERVER",
            "OBSERVE",
        ),
        "looks on": (
            "OBSERVER",
            "OBSERVE",
        ),
        "listens": (
            "OBSERVER",
            "LISTEN",
        ),
        "remains nearby": (
            "SUPPORTING_PRESENCE",
            "REMAIN_NEARBY",
        ),
    }

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze(
        self,
        episode: Episode,
        scene_analysis: EpisodeSceneAnalysis,
    ) -> EpisodeCharacterRoleAnalysis:

        scene_analysis_map: Dict[
            int,
            SceneAnalysis,
        ] = {
            item.scene_number: item
            for item in scene_analysis.scenes
        }

        results = []

        for scene in episode.scenes:

            analyzed_scene = (
                scene_analysis_map.get(
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

        return EpisodeCharacterRoleAnalysis(
            status="PASSED",
            episode_id=(
                episode.episode_id
            ),
            scenes=(
                results
            ),
        )

    # ================================================================
    # SCENE
    # ================================================================

    def _analyze_scene(
        self,
        scene: Scene,
        analyzed_scene: Optional[
            SceneAnalysis
        ],
    ) -> SceneCharacterRoleAnalysis:

        identities = (
            self._build_identity_map(
                scene=scene,
                analyzed_scene=(
                    analyzed_scene
                ),
            )
        )

        # ------------------------------------------------------------
        # NO CHARACTERS
        # ------------------------------------------------------------

        if not identities:

            return SceneCharacterRoleAnalysis(
                scene_number=(
                    scene.scene_number
                ),
            )

        # ------------------------------------------------------------
        # SINGLE CHARACTER
        # ------------------------------------------------------------

        if len(identities) == 1:

            entity_id, name = (
                identities[0]
            )

            interaction = (
                self._detect_character_interaction(
                    name=name,
                    text=(
                        scene.visual_description
                    ),
                    character_names=[
                        item_name
                        for _, item_name
                        in identities
                    ],
                )
            )

            role = CharacterRoleAnalysis(
                entity_id=entity_id,
                name=name,
                role="ACTIVE_SUBJECT",
                interaction=(
                    interaction[1]
                    if interaction
                    else "SCENE_PARTICIPATION"
                ),
                confidence=0.95,
                primary_candidate=True,
                evidence=(
                    interaction[2]
                    if interaction
                    else (
                        "Only declared character "
                        "in the scene."
                    )
                ),
            )

            return SceneCharacterRoleAnalysis(
                scene_number=(
                    scene.scene_number
                ),
                characters=[
                    role
                ],
                primary_subject_id=(
                    entity_id
                ),
                primary_subject_name=(
                    name
                ),
            )

        # ------------------------------------------------------------
        # MULTI-CHARACTER
        # ------------------------------------------------------------

        role_results = []

        for (
            entity_id,
            name,
        ) in identities:

            detected = (
                self._detect_character_interaction(
                    name=name,
                    text=(
                        scene.visual_description
                    ),
                    character_names=[
                        item_name
                        for _, item_name
                        in identities
                    ],
                )
            )

            if detected is None:

                role_results.append(
                    CharacterRoleAnalysis(
                        entity_id=(
                            entity_id
                        ),
                        name=name,
                        role="PARTICIPANT",
                        interaction="UNSPECIFIED",
                        confidence=0.4,
                        primary_candidate=False,
                        evidence="",
                    )
                )

                continue

            (
                role_name,
                interaction,
                evidence,
                confidence,
            ) = detected

            role_results.append(
                CharacterRoleAnalysis(
                    entity_id=(
                        entity_id
                    ),
                    name=name,
                    role=(
                        role_name
                    ),
                    interaction=(
                        interaction
                    ),
                    confidence=(
                        confidence
                    ),
                    primary_candidate=(
                        role_name
                        == "ACTIVE_SUBJECT"
                    ),
                    evidence=(
                        evidence
                    ),
                )
            )

        (
            primary_subject_id,
            primary_subject_name,
        ) = (
            self._resolve_primary_subject(
                role_results
            )
        )

        return SceneCharacterRoleAnalysis(
            scene_number=(
                scene.scene_number
            ),
            characters=(
                role_results
            ),
            primary_subject_id=(
                primary_subject_id
            ),
            primary_subject_name=(
                primary_subject_name
            ),
        )

    # ================================================================
    # IDENTITY MAP
    # ================================================================

    def _build_identity_map(
        self,
        scene: Scene,
        analyzed_scene: Optional[
            SceneAnalysis
        ],
    ) -> List[
        Tuple[str, str]
    ]:

        if analyzed_scene is None:
            return []

        if (
            len(
                scene.characters
            )
            !=
            len(
                analyzed_scene
                .character_ids
            )
        ):
            return []

        result = []

        for index, name in enumerate(
            scene.characters
        ):

            result.append(
                (
                    analyzed_scene
                    .character_ids[
                        index
                    ],
                    name,
                )
            )

        return result

    # ================================================================
    # CHARACTER INTERACTION
    # ================================================================

    def _detect_character_interaction(
        self,
        name: str,
        text: str,
        character_names: Optional[
            List[str]
        ] = None,
    ):
        """
        Analyze the text fragment controlled by one character.

        The analyzer remains story-agnostic and only consumes the
        character identity plus scene text supplied by upstream stages.
        """

        if not text:
            return None

        fragment = (
            self._extract_character_fragment(
                name=name,
                text=text,
                character_names=(
                    character_names
                    or []
                ),
            )
        )

        if not fragment:
            return None

        normalized = (
            fragment.lower()
        )

        # ------------------------------------------------------------
        # SUPPORTING ROLE
        # ------------------------------------------------------------

        for (
            phrase,
            (
                role,
                interaction,
            ),
        ) in (
            self.SUPPORTING_INTERACTIONS
            .items()
        ):

            if phrase in normalized:

                return (
                    role,
                    interaction,
                    fragment,
                    0.95,
                )

        # ------------------------------------------------------------
        # ACTIVE ROLE
        # ------------------------------------------------------------

        for (
            verb,
            interaction,
        ) in (
            self.ACTIVE_INTERACTIONS
            .items()
        ):

            pattern = (
                rf"\b"
                f"{re.escape(verb)}"
                rf"\b"
            )

            if re.search(
                pattern,
                normalized,
            ):

                return (
                    "ACTIVE_SUBJECT",
                    interaction,
                    fragment,
                    0.9,
                )

        return (
            "PARTICIPANT",
            "SCENE_PARTICIPATION",
            fragment,
            0.55,
        )

    # ================================================================
    # FRAGMENT EXTRACTION
    # ================================================================

    def _extract_character_fragment(
        self,
        name: str,
        text: str,
        character_names: Optional[
            List[str]
        ] = None,
    ) -> str:
        """
        Extract the semantic fragment controlled by one character.

        Within the first sentence, the fragment still stops before
        "while" so multi-character clauses remain isolated.

        Across sentence boundaries, continuation is conservative:
        - the same named character may continue
        - a pronoun continuation is allowed only when the scene has a
          single declared character
        - a sentence beginning with another declared character stops
          the fragment
        - unrelated sentence subjects are not absorbed
        """

        if not text:
            return ""

        character_names = (
            character_names
            or []
        )

        pattern = re.compile(
            rf"\b"
            f"{re.escape(name)}"
            rf"\b",
            flags=(
                re.IGNORECASE
            ),
        )

        match = pattern.search(
            text
        )

        if not match:
            return ""

        # Work from the first occurrence of this character onward.
        remainder = (
            text[
                match.start():
            ]
        )

        sentence_parts = (
            self._split_sentences(
                remainder
            )
        )

        if not sentence_parts:
            return ""

        fragments = []

        first_sentence = (
            sentence_parts[0]
        )

        first_fragment = (
            self._truncate_at_while(
                first_sentence
            )
        )

        if first_fragment:
            fragments.append(
                first_fragment
            )

        # Pronoun continuation is intentionally conservative. When
        # multiple declared characters exist, "he", "she", or "they"
        # may be ambiguous, so cross-sentence pronoun linking is disabled.
        single_character_scene = (
            len(
                character_names
            )
            <= 1
        )

        for sentence in (
            sentence_parts[1:]
        ):

            cleaned = (
                sentence.strip(
                    " ,"
                )
            )

            if not cleaned:
                continue

            if self._starts_with_other_character(
                sentence=cleaned,
                current_name=name,
                character_names=(
                    character_names
                ),
            ):
                break

            if self._starts_with_character(
                sentence=cleaned,
                name=name,
            ):
                fragments.append(
                    self._truncate_at_while(
                        cleaned
                    )
                )
                continue

            if (
                single_character_scene
                and
                self._starts_with_subject_pronoun(
                    cleaned
                )
            ):
                fragments.append(
                    self._truncate_at_while(
                        cleaned
                    )
                )
                continue

            break

        return " ".join(
            item
            for item in fragments
            if item
        ).strip(
            " ,"
        )

    def _split_sentences(
        self,
        text: str,
    ) -> List[str]:
        """
        Split scene prose into sentence-like units while preserving the
        sentence content needed for semantic interaction detection.
        """

        if not text:
            return []

        parts = re.split(
            r"(?<=[.!?;])\s+",
            text.strip(),
        )

        return [
            item.strip()
            for item in parts
            if item.strip()
        ]

    def _truncate_at_while(
        self,
        text: str,
    ) -> str:
        """
        Preserve the existing same-sentence protection around "while".
        """

        if not text:
            return ""

        boundary = re.search(
            r"\bwhile\b",
            text,
            flags=(
                re.IGNORECASE
            ),
        )

        if boundary:

            return (
                text[
                    :boundary.start()
                ]
                .strip(
                    " ,"
                )
            )

        return (
            text.strip(
                " ,"
            )
        )

    def _starts_with_subject_pronoun(
        self,
        sentence: str,
    ) -> bool:
        """
        Detect conservative third-person subject-pronoun continuation.
        """

        return (
            re.match(
                r"^(he|she|they)\b",
                sentence,
                flags=(
                    re.IGNORECASE
                ),
            )
            is not None
        )

    def _starts_with_character(
        self,
        sentence: str,
        name: str,
    ) -> bool:

        return (
            re.match(
                rf"^{re.escape(name)}\b",
                sentence,
                flags=(
                    re.IGNORECASE
                ),
            )
            is not None
        )

    def _starts_with_other_character(
        self,
        sentence: str,
        current_name: str,
        character_names: List[str],
    ) -> bool:

        for candidate in (
            character_names
        ):

            if (
                candidate.lower()
                ==
                current_name.lower()
            ):
                continue

            if self._starts_with_character(
                sentence=sentence,
                name=candidate,
            ):
                return True

        return False

    # ================================================================
    # PRIMARY SUBJECT
    # ================================================================

    def _resolve_primary_subject(
        self,
        roles: List[
            CharacterRoleAnalysis
        ],
    ) -> Tuple[
        Optional[str],
        Optional[str],
    ]:
        """
        Select a primary subject only when evidence is sufficiently
        unambiguous.

        We intentionally avoid guessing when multiple characters have
        comparable ACTIVE_SUBJECT scores.
        """

        active = [
            role
            for role in roles
            if (
                role.role
                == "ACTIVE_SUBJECT"
            )
        ]

        if len(active) != 1:

            return (
                None,
                None,
            )

        primary = (
            active[0]
        )

        if (
            primary.confidence
            < 0.75
        ):

            return (
                None,
                None,
            )

        return (
            primary.entity_id,
            primary.name,
        )