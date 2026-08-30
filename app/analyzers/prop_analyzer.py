import re
from typing import List, Set, Tuple

from app.models.analysis import (
    EpisodePropAnalysis,
    PropCandidate,
    ScenePropAnalysis,
)

from app.models.episode import (
    Episode,
    Scene,
)


class PropAnalyzer:
    """
    Generic interaction-based prop/object analyzer.

    Source authority
    ----------------
    DECLARED:
        scene.props

        Explicitly authored props are trusted and preserved.

    OBSERVED:
        scene.visual_description

        Physical objects may be inferred when they are targets of
        meaningful character/object interactions.

    CORROBORATING:
        scene.dialogue
        scene.narrative_purpose

        These sources may strengthen an already observed candidate,
        but they must never create a new physical prop by themselves.

    Core principle
    --------------
    A noun is not automatically a prop.

    A prop should normally represent a meaningful physical object
    that participates in the scene.
    """

    # ================================================================
    # INTERACTION VOCABULARY
    # ================================================================

    INTERACTION_PATTERNS = (
        "looks at",
        "looking at",
        "picks up",
        "picking up",
        "sets down",
        "setting down",
        "puts down",
        "putting down",
        "hands over",
        "handing over",
        "reaches for",
        "reaching for",
        "points at",
        "pointing at",
        "examines",
        "examine",
        "examining",
        "studies",
        "study",
        "studying",
        "holds",
        "hold",
        "holding",
        "opens",
        "open",
        "opening",
        "reads",
        "read",
        "reading",
        "finds",
        "find",
        "finding",
        "discovers",
        "discover",
        "discovering",
        "reveals",
        "reveal",
        "revealing",
        "takes",
        "take",
        "taking",
        "places",
        "place",
        "placing",
        "grabs",
        "grab",
        "grabbing",
        "carries",
        "carry",
        "carrying",
        "uses",
        "use",
        "using",
        "touches",
        "touch",
        "touching",
        "inspects",
        "inspect",
        "inspecting",
        "checks",
        "check",
        "checking",
        "unlocks",
        "unlock",
        "unlocking",
        "shows",
        "show",
        "showing",
        "gives",
        "give",
        "giving",
        "receives",
        "receive",
        "receiving",
    )

    # ================================================================
    # OBJECT PHRASE BOUNDARIES
    # ================================================================

    OBJECT_BOUNDARIES = {
        "above",
        "across",
        "against",
        "along",
        "around",
        "at",
        "below",
        "beside",
        "before",
        "behind",
        "beneath",
        "between",
        "beyond",
        "by",
        "during",
        "for",
        "from",
        "in",
        "inside",
        "into",
        "near",
        "off",
        "on",
        "onto",
        "outside",
        "over",
        "past",
        "through",
        "toward",
        "towards",
        "under",
        "upon",
        "with",
        "within",
        "while",
        "and",
        "but",
        "then",
        "because",
        "as",
    }

    # Words in this set commonly introduce a clause or spatial
    # continuation after an already complete object phrase.
    #
    # They are intentionally kept separate from OBJECT_BOUNDARIES so
    # that they can participate in clause-aware checks without changing
    # article or cleanup behavior elsewhere.
    CLAUSE_LINK_BOUNDARIES = {
        "above",
        "across",
        "against",
        "along",
        "around",
        "at",
        "below",
        "beside",
        "behind",
        "beneath",
        "between",
        "beyond",
        "by",
        "from",
        "in",
        "inside",
        "into",
        "near",
        "off",
        "on",
        "onto",
        "outside",
        "over",
        "past",
        "through",
        "toward",
        "towards",
        "under",
        "upon",
        "with",
        "within",
    }


    # Common irregular participles that cannot be recognized reliably
    # from an -ed / -ing suffix alone. This is grammar vocabulary, not
    # story-specific object knowledge.
    IRREGULAR_PARTICIPLES = {
        "built",
        "cast",
        "cut",
        "drawn",
        "driven",
        "hung",
        "laid",
        "left",
        "made",
        "put",
        "set",
        "shown",
        "spread",
        "stuck",
        "torn",
        "written",
    }

    ARTICLES = {
        "a",
        "an",
        "the",
        "this",
        "that",
        "these",
        "those",
    }

    # ================================================================
    # ABSTRACT CONCEPT FILTER
    # ================================================================

    NON_PHYSICAL_CONCEPTS = {
        "truth",
        "mystery",
        "history",
        "atmosphere",
        "investigation",
        "explanation",
        "information",
        "story",
        "death",
        "case",
        "situation",
        "event",
        "idea",
        "secret",
        "problem",
        "clue",
        "evidence",
        "knowledge",
        "understanding",
        "revelation",
        "discovery",
    }


    # ================================================================
    # NON-PHYSICAL EVENT / ACTION HEADS
    # ================================================================
    #
    # These are generic lexical categories, not story-specific prop
    # names. They prevent interaction complements that describe an
    # action, gesture, expression, or transient event from being
    # promoted to persistent physical props.
    #
    # Examples:
    #     "a relaxed sip"     -> event, not a prop
    #     "a quick glance"    -> event, not a prop
    #     "a nervous smile"   -> expression, not a prop
    #
    # The filter is intentionally applied to the semantic head (the
    # final word), so valid physical phrases such as "painted wooden
    # box" remain unaffected.
    NON_PHYSICAL_EVENT_HEADS = {
        "blink",
        "breath",
        "gesture",
        "glance",
        "grin",
        "inspection",
        "look",
        "nod",
        "reaction",
        "shake",
        "shrug",
        "sigh",
        "sip",
        "smile",
        "stare",
        "step",
        "walk",
        "wave",
    }

    # ================================================================
    # PUBLIC API
    # ================================================================

    def analyze(
        self,
        episode: Episode,
    ) -> EpisodePropAnalysis:

        known_characters = (
            self._collect_known_characters(
                episode
            )
        )

        known_locations = (
            self._collect_known_locations(
                episode
            )
        )

        scene_results = []

        for scene in episode.scenes:

            scene_results.append(
                self._analyze_scene(
                    scene=scene,
                    known_characters=(
                        known_characters
                    ),
                    known_locations=(
                        known_locations
                    ),
                )
            )

        return EpisodePropAnalysis(
            status="PASSED",
            episode_id=(
                episode.episode_id
            ),
            scenes=(
                scene_results
            ),
        )

    # ================================================================
    # SCENE ANALYSIS
    # ================================================================

    def _analyze_scene(
        self,
        scene: Scene,
        known_characters: Set[str],
        known_locations: Set[str],
    ) -> ScenePropAnalysis:

        # ============================================================
        # DECLARED PROPS
        # ============================================================

        explicit_props = (
            self._deduplicate_names(
                list(
                    scene.props
                )
            )
        )

        # ============================================================
        # OBSERVED PROPS
        # ============================================================

        inferred_props = (
            self._extract_observed_props(
                scene=scene,
                known_characters=(
                    known_characters
                ),
                known_locations=(
                    known_locations
                ),
            )
        )

        # ============================================================
        # CORROBORATION
        # ============================================================

        inferred_props = (
            self._apply_corroboration(
                scene=scene,
                candidates=(
                    inferred_props
                ),
            )
        )

        # ============================================================
        # RESOLUTION
        # ============================================================

        resolved_props = list(
            explicit_props
        )

        resolved_keys = {
            self._normalize_compare(
                item
            )
            for item in resolved_props
        }

        for candidate in inferred_props:

            key = (
                self._normalize_compare(
                    candidate.name
                )
            )

            if not key:
                continue

            if key in resolved_keys:
                continue

            if (
                self._matches_declared_prop_alias(
                    candidate_name=(
                        candidate.name
                    ),
                    declared_props=(
                        explicit_props
                    ),
                )
            ):
                continue

            if candidate.confidence < 0.7:
                continue

            resolved_props.append(
                candidate.name
            )

            resolved_keys.add(
                key
            )

        return ScenePropAnalysis(
            scene_number=(
                scene.scene_number
            ),
            explicit_props=(
                explicit_props
            ),
            inferred_props=(
                inferred_props
            ),
            resolved_props=(
                resolved_props
            ),
        )

    # ================================================================
    # DECLARED PROP ALIAS RESOLUTION
    # ================================================================

    def _matches_declared_prop_alias(
        self,
        candidate_name: str,
        declared_props: List[str],
    ) -> bool:
        """
        Conservatively determine whether an observed prop phrase is a
        descriptive expansion of an explicitly declared prop.

        Explicitly authored props remain canonical.

        Example:

            declared:
                Wooden Container

            observed:
                Plain Wooden Container

            result:
                same physical prop

        Safety rules:
        - the declared phrase must contain at least two tokens
        - the observed phrase must be longer than the declared phrase
        - the complete declared phrase must be preserved as the suffix
        - no fuzzy similarity or adjective stripping is performed

        These constraints intentionally prefer occasional duplicates over
        accidentally merging distinct physical objects.
        """

        candidate = (
            self._normalize_compare(
                candidate_name
            )
        )

        if not candidate:
            return False

        candidate_words = (
            candidate.split()
        )

        for declared_name in declared_props:

            declared = (
                self._normalize_compare(
                    declared_name
                )
            )

            if not declared:
                continue

            if candidate == declared:
                return True

            declared_words = (
                declared.split()
            )

            # Single-token declarations are too generic for safe aliasing.
            if len(declared_words) < 2:
                continue

            # The observed phrase must add descriptive information rather
            # than merely restate or shorten the declared phrase.
            if (
                len(candidate_words)
                <= len(declared_words)
            ):
                continue

            # Preserve the entire declared phrase as the semantic tail.
            if (
                candidate_words[
                    -len(declared_words):
                ]
                == declared_words
            ):
                return True

        return False

    # ================================================================
    # OBSERVED PROP EXTRACTION
    # ================================================================

    def _extract_observed_props(
        self,
        scene: Scene,
        known_characters: Set[str],
        known_locations: Set[str],
    ) -> List[
        PropCandidate
    ]:
        """
        Only visual_description is allowed to create inferred props.

        Dialogue and narrative purpose are intentionally excluded here.
        """

        text = (
            scene.visual_description
            .strip()
        )

        if not text:
            return []

        extracted = (
            self._extract_from_text(
                text
            )
        )

        candidates = []

        for (
            interaction,
            raw_object,
        ) in extracted:

            candidate_name = (
                self._clean_object_phrase(
                    raw_object
                )
            )

            if not candidate_name:
                continue

            if self._is_known_entity(
                candidate_name=(
                    candidate_name
                ),
                known_characters=(
                    known_characters
                ),
                known_locations=(
                    known_locations
                ),
            ):
                continue

            if not self._looks_like_physical_prop(
                candidate_name
            ):
                continue

            confidence = (
                self._score_observed_candidate(
                    candidate_name
                )
            )

            candidates.append(
                PropCandidate(
                    name=(
                        candidate_name
                    ),
                    source=(
                        "visual_description:"
                        f"{interaction}"
                    ),
                    confidence=(
                        confidence
                    ),
                    visually_important=(
                        confidence >= 0.8
                    ),
                )
            )

        return (
            self._deduplicate_candidates(
                candidates
            )
        )

    # ================================================================
    # CORROBORATION
    # ================================================================

    def _apply_corroboration(
        self,
        scene: Scene,
        candidates: List[
            PropCandidate
        ],
    ) -> List[
        PropCandidate
    ]:
        """
        Dialogue and narrative purpose may increase confidence or
        importance of an already observed object.

        They must never create a new candidate.
        """

        if not candidates:
            return []

        dialogue = (
            scene.dialogue
            .strip()
            .lower()
        )

        narrative = (
            scene.narrative_purpose
            .strip()
            .lower()
        )

        result = []

        for candidate in candidates:

            confidence = (
                candidate.confidence
            )

            visually_important = (
                candidate.visually_important
            )

            candidate_key = (
                self._normalize_compare(
                    candidate.name
                )
            )

            corroboration_sources = []

            # Exact or normalized mention in dialogue.
            if (
                dialogue
                and
                self._text_mentions_candidate(
                    text=dialogue,
                    candidate=(
                        candidate_key
                    ),
                )
            ):

                confidence += 0.05

                corroboration_sources.append(
                    "dialogue"
                )

            # Exact or normalized mention in narrative purpose.
            if (
                narrative
                and
                self._text_mentions_candidate(
                    text=narrative,
                    candidate=(
                        candidate_key
                    ),
                )
            ):

                confidence += 0.03

                corroboration_sources.append(
                    "narrative_purpose"
                )

            confidence = min(
                round(
                    confidence,
                    2,
                ),
                1.0,
            )

            if confidence >= 0.8:
                visually_important = True

            source = (
                candidate.source
            )

            if corroboration_sources:

                source = (
                    source
                    + "|corroborated:"
                    + ",".join(
                        corroboration_sources
                    )
                )

            result.append(
                PropCandidate(
                    name=(
                        candidate.name
                    ),
                    source=(
                        source
                    ),
                    confidence=(
                        confidence
                    ),
                    visually_important=(
                        visually_important
                    ),
                )
            )

        return result

    def _text_mentions_candidate(
        self,
        text: str,
        candidate: str,
    ) -> bool:

        normalized_text = (
            self._normalize_compare(
                text
            )
        )

        normalized_candidate = (
            self._normalize_compare(
                candidate
            )
        )

        if not normalized_text:
            return False

        if not normalized_candidate:
            return False

        if (
            normalized_candidate
            in normalized_text
        ):
            return True

        # Conservative fallback:
        # only compare the final noun when the candidate is multi-word.
        #
        # Example:
        # "Detailed Record"
        # may be corroborated by "record".
        candidate_words = (
            normalized_candidate
            .split()
        )

        if len(candidate_words) < 2:
            return False

        head_noun = (
            candidate_words[-1]
        )

        text_words = set(
            normalized_text
            .split()
        )

        return (
            head_noun
            in text_words
        )

    # ================================================================
    # INTERACTION EXTRACTION
    # ================================================================

    def _extract_from_text(
        self,
        text: str,
    ) -> List[
        Tuple[str, str]
    ]:
        """
        Extract interaction -> direct object pairs.

        Example:

            "A character examines a physical object on a table."

        becomes:

            interaction = "examines"
            object = "a physical object"
        """

        normalized_text = (
            self._normalize_sentence(
                text
            )
        )

        patterns = sorted(
            self.INTERACTION_PATTERNS,
            key=len,
            reverse=True,
        )

        verb_pattern = "|".join(
            re.escape(
                pattern
            )
            for pattern in patterns
        )

        regex = re.compile(
            rf"\b({verb_pattern})\b",
            flags=re.IGNORECASE,
        )

        matches = list(
            regex.finditer(
                normalized_text
            )
        )

        results = []

        for index, match in enumerate(
            matches
        ):

            interaction = (
                match.group(1)
                .strip()
                .lower()
            )

            object_start = (
                match.end()
            )

            if (
                index + 1
                < len(matches)
            ):

                object_end = (
                    matches[
                        index + 1
                    ]
                    .start()
                )

            else:

                object_end = len(
                    normalized_text
                )

            remainder = (
                normalized_text[
                    object_start:
                    object_end
                ]
                .strip()
            )

            raw_object = (
                self._extract_direct_object(
                    remainder
                )
            )

            if not raw_object:
                continue

            results.append(
                (
                    interaction,
                    raw_object,
                )
            )

        return results

    # ================================================================
    # DIRECT OBJECT EXTRACTION
    # ================================================================

    def _extract_direct_object(
        self,
        remainder: str,
    ) -> str:

        if not remainder:
            return ""

        # Stop at strong punctuation first.
        remainder = re.split(
            r"[.!?;,:]",
            remainder,
            maxsplit=1,
        )[0]

        words = (
            remainder
            .strip()
            .split()
        )

        if not words:
            return ""

        collected = []

        for index, word in enumerate(
            words
        ):

            normalized_word = (
                self._normalize_word(
                    word
                )
            )

            if not normalized_word:
                continue

            # Articles may occur at the beginning.
            # Other boundary words terminate the direct object.
            if (
                index > 0
                and
                normalized_word
                in self.OBJECT_BOUNDARIES
            ):

                break

            # A participial continuation often begins a new descriptive
            # clause after an already complete noun phrase:
            #
            #     "a metal object marked with a symbol"
            #     "an old chart spread across a table"
            #
            # We only treat -ed / -ing forms as clause boundaries when
            # they are followed by a spatial/linking boundary. This keeps
            # ordinary modifiers such as "painted wooden box" intact.
            if (
                collected
                and
                self._is_participial_clause_start(
                    words=words,
                    index=index,
                )
            ):

                break

            collected.append(
                word
            )

            # Safety against runaway extraction in malformed text.
            if len(collected) >= 6:
                break

        return " ".join(
            collected
        )

    def _is_participial_clause_start(
        self,
        words: List[str],
        index: int,
    ) -> bool:
        """
        Detect a likely participial clause that follows an already
        collected object phrase.

        This is intentionally grammar-oriented and does not contain
        story-specific object names.
        """

        if (
            index < 0
            or
            index >= len(words)
        ):

            return False

        if (
            index + 1
            >= len(words)
        ):

            return False

        current = (
            self._normalize_word(
                words[index]
            )
        )

        following = (
            self._normalize_word(
                words[
                    index + 1
                ]
            )
        )

        if not current:
            return False

        if not following:
            return False

        if (
            following
            not in self.CLAUSE_LINK_BOUNDARIES
        ):

            return False

        return (
            current.endswith(
                "ed"
            )
            or
            current.endswith(
                "ing"
            )
            or
            current
            in self.IRREGULAR_PARTICIPLES
        )

    # ================================================================
    # OBJECT CLEANUP
    # ================================================================

    def _clean_object_phrase(
        self,
        value: str,
    ) -> str:

        if not value:
            return ""

        cleaned = re.sub(
            r"\s+",
            " ",
            value,
        )

        cleaned = (
            cleaned
            .strip(
                " \t\r\n.,!?;:()[]{}\""
            )
        )

        words = (
            cleaned.split()
        )

        # Remove articles at beginning.
        while (
            words
            and
            self._normalize_word(
                words[0]
            )
            in self.ARTICLES
        ):

            words.pop(0)

        # Remove accidental boundary words at end.
        while (
            words
            and
            self._normalize_word(
                words[-1]
            )
            in self.OBJECT_BOUNDARIES
        ):

            words.pop()

        if not words:
            return ""

        normalized = " ".join(
            words
        )

        return (
            self._display_name(
                normalized
            )
        )

    # ================================================================
    # KNOWN ENTITY EXCLUSION
    # ================================================================

    def _collect_known_characters(
        self,
        episode: Episode,
    ) -> Set[str]:

        values = set()

        for scene in episode.scenes:

            for name in (
                scene.characters
            ):

                normalized = (
                    self._normalize_compare(
                        name
                    )
                )

                if normalized:

                    values.add(
                        normalized
                    )

        return values

    def _collect_known_locations(
        self,
        episode: Episode,
    ) -> Set[str]:

        values = set()

        for scene in episode.scenes:

            normalized = (
                self._normalize_compare(
                    scene.location
                )
            )

            if normalized:

                values.add(
                    normalized
                )

        return values

    def _is_known_entity(
        self,
        candidate_name: str,
        known_characters: Set[str],
        known_locations: Set[str],
    ) -> bool:

        candidate = (
            self._normalize_compare(
                candidate_name
            )
        )

        if not candidate:
            return True

        if candidate in known_characters:
            return True

        if candidate in known_locations:
            return True

        # Reject phrases beginning with an already known character.
        #
        # Example:
        # "Known Person"
        # "Known Person's Body"
        for character in (
            known_characters
        ):

            if (
                candidate.startswith(
                    f"{character} "
                )
                or
                candidate.startswith(
                    f"{character}'s "
                )
            ):

                return True

        # Reject phrases beginning with an already known location.
        for location in (
            known_locations
        ):

            if candidate.startswith(
                f"{location} "
            ):

                return True

        return False

    # ================================================================
    # PHYSICAL PROP FILTERING
    # ================================================================

    def _looks_like_physical_prop(
        self,
        candidate_name: str,
    ) -> bool:

        normalized = (
            self._normalize_compare(
                candidate_name
            )
        )

        if not normalized:
            return False

        words = (
            normalized.split()
        )

        if not words:
            return False

        if len(words) > 5:
            return False

        if (
            normalized
            in self.NON_PHYSICAL_CONCEPTS
        ):
            return False

        # The final noun is usually the semantic head.
        #
        # Example:
        # "First Major Clue"
        # head = clue
        #
        # This prevents narrative concepts from becoming props.
        if (
            words[-1]
            in self.NON_PHYSICAL_CONCEPTS
        ):
            return False

        # Possessive phrases are ambiguous and should not automatically
        # become persistent props.
        if "'s " in normalized:
            return False

        # A trailing adverb is a strong structural signal that the
        # extracted phrase describes an action rather than a physical
        # object:
        #
        #     "marking cautiously"
        #     "movement slowly"
        #
        # Physical noun phrases normally terminate on a noun, not an
        # adverbial modifier.
        if (
            len(words) >= 2
            and
            words[-1].endswith("ly")
        ):
            return False

        # Reject generic transient event/action heads. This check is
        # lexical-semantic rather than story-specific: it operates only
        # on the final semantic head and does not contain any character,
        # episode, location, or authored prop names.
        if (
            words[-1]
            in self.NON_PHYSICAL_EVENT_HEADS
        ):
            return False

        return True

    # ================================================================
    # SCORING
    # ================================================================

    def _score_observed_candidate(
        self,
        candidate_name: str,
    ) -> float:
        """
        Visual interaction is strong evidence.

        Observed candidates intentionally begin above the resolution
        threshold because they originate from explicit physical staging.
        """

        confidence = 0.90

        word_count = len(
            candidate_name
            .split()
        )

        # Specific noun phrases are generally safer than isolated words.
        if word_count >= 2:

            confidence += 0.05

        # Being present in visual staging is strong evidence.
        confidence += 0.03

        return min(
            round(
                confidence,
                2,
            ),
            1.0,
        )

    # ================================================================
    # NORMALIZATION
    # ================================================================

    def _normalize_sentence(
        self,
        value: str,
    ) -> str:

        return re.sub(
            r"\s+",
            " ",
            value.strip(),
        )

    def _normalize_word(
        self,
        value: str,
    ) -> str:

        return (
            value.strip()
            .strip(
                ".,!?;:()[]{}\""
            )
            .lower()
        )

    def _normalize_compare(
        self,
        value: str,
    ) -> str:

        cleaned = (
            value.strip()
            .lower()
        )

        cleaned = re.sub(
            r"[^\w\s'-]",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned,
        )

        return (
            cleaned.strip()
        )

    def _display_name(
        self,
        value: str,
    ) -> str:

        words = []

        for word in (
            value.split()
        ):

            if not word:
                continue

            words.append(
                word[0].upper()
                + word[1:]
            )

        return " ".join(
            words
        )

    # ================================================================
    # DEDUPLICATION
    # ================================================================

    def _deduplicate_names(
        self,
        values: List[str],
    ) -> List[str]:

        result = []

        seen = set()

        for value in values:

            cleaned = (
                value.strip()
            )

            if not cleaned:
                continue

            key = (
                self._normalize_compare(
                    cleaned
                )
            )

            if key in seen:
                continue

            seen.add(
                key
            )

            result.append(
                cleaned
            )

        return result

    def _deduplicate_candidates(
        self,
        candidates: List[
            PropCandidate
        ],
    ) -> List[
        PropCandidate
    ]:

        result = {}

        for candidate in candidates:

            key = (
                self._normalize_compare(
                    candidate.name
                )
            )

            if not key:
                continue

            existing = (
                result.get(
                    key
                )
            )

            if (
                existing is None
                or
                candidate.confidence
                > existing.confidence
            ):

                result[
                    key
                ] = candidate

        return list(
            result.values()
        )