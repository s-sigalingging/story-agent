import re
import sys
from pathlib import Path


# ================================================================
# PROJECT
# ================================================================


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


# ================================================================
# FILES UNDER AUDIT
# ================================================================


GENERATION_CORE_FILES = [
    "app/models/generation.py",
    "app/generation/__init__.py",
    "app/generation/keyframe_generator.py",
    "app/generation/request_compiler.py",
    "app/generation/runner.py",
    "app/generation/store.py",
    "app/generation/providers/base.py",
    "app/generation/providers/fake.py",
]


# ================================================================
# STORY-SPECIFIC TERMS
# ================================================================


STORY_TERMS = [
    "Julian",
    "Ren",
    "Sterling",
    "Sam Bell",
    "Samuel Bell",
    "Oakhaven",
    "EP001",
    "Mira",
    "Lena",
    "Nadia",
    "Theo",
    "Arin",
    "Sora",
    "Mysterious Document",
    "Old Brass Key",
    "Metal Compass",
    "Old Map",
    "Metal Container",
    "Ceramic Mug",
    "Warning Panel",
    "CHAR_JULIAN",
    "PROP_MYSTERIOUS_DOCUMENT",
]


# ================================================================
# PROVIDER-SPECIFIC TERMS
# ================================================================


PROVIDER_TERMS = [
    "OpenAI",
    "Digen",
    "Kling",
    "Midjourney",
    "Stability",
    "Replicate",
    "Fal",
]


# ================================================================
# MATCHER
# ================================================================


def build_pattern(
    term: str,
) -> re.Pattern:
    """
    Match an exact term using Python-identifier boundaries.

    This avoids false positives such as:

        Ren
        -> reference
        -> rendering
        -> current

    while still detecting:

        "Ren"
        CHAR_JULIAN
        "Old Brass Key"
    """

    escaped = re.escape(
        term
    )

    escaped = escaped.replace(
        r"\ ",
        r"\s+",
    )

    return re.compile(
        rf"(?<![A-Za-z0-9_])"
        rf"{escaped}"
        rf"(?![A-Za-z0-9_])",
        flags=re.IGNORECASE,
    )


# ================================================================
# FILE AUDIT
# ================================================================


def audit_terms(
    terms,
):

    findings = []

    patterns = {
        term: build_pattern(
            term
        )
        for term
        in terms
    }

    for relative_path in (
        GENERATION_CORE_FILES
    ):

        path = (
            PROJECT_ROOT
            /
            relative_path
        )

        if not path.exists():

            findings.append({
                "file": relative_path,
                "line": 0,
                "term": "MISSING_FILE",
                "content": "",
            })

            continue

        lines = (
            path.read_text(
                encoding="utf-8"
            )
            .splitlines()
        )

        for (
            line_number,
            line,
        ) in enumerate(
            lines,
            start=1,
        ):

            for (
                term,
                pattern,
            ) in patterns.items():

                if (
                    pattern.search(
                        line
                    )
                    is None
                ):

                    continue

                findings.append({
                    "file": relative_path,
                    "line": line_number,
                    "term": term,
                    "content": (
                        line.strip()
                    ),
                })

    return findings


# ================================================================
# OUTPUT
# ================================================================


def print_findings(
    title: str,
    findings,
):

    print()
    print(
        title
    )
    print(
        "----------------------------------------"
    )

    if not findings:

        print(
            "Findings: 0"
        )

        return

    print(
        "Findings:",
        len(findings),
    )

    for finding in findings:

        print(
            f"{finding['file']}:"
            f"{finding['line']} "
            f"[{finding['term']}] "
            f"{finding['content']}"
        )


# ================================================================
# MAIN
# ================================================================


def main():

    print()
    print(
        "BATCH 12H.2 — GENERATION HARDCODE AUDIT"
    )
    print(
        "========================================"
    )

    story_findings = (
        audit_terms(
            STORY_TERMS
        )
    )

    provider_findings = (
        audit_terms(
            PROVIDER_TERMS
        )
    )

    print(
        "Match mode: "
        "EXACT_TERM_WITH_IDENTIFIER_BOUNDARIES"
    )

    print_findings(
        "STORY-SPECIFIC AUDIT",
        story_findings,
    )

    print_findings(
        "PROVIDER-LEAKAGE AUDIT",
        provider_findings,
    )

    total_findings = (
        len(
            story_findings
        )
        +
        len(
            provider_findings
        )
    )

    print()
    print(
        "========================================"
    )
    print(
        "BATCH 12H.2 SUMMARY"
    )
    print(
        "========================================"
    )

    print(
        "Story findings:",
        len(
            story_findings
        ),
    )

    print(
        "Provider leakage findings:",
        len(
            provider_findings
        ),
    )

    print(
        "Total findings:",
        total_findings,
    )

    print()

    if total_findings:

        print(
            "BATCH 12H.2 FAILED"
        )

        return 1

    print(
        "BATCH 12H.2 PASSED"
    )

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )