"""
Investigate astronomical roots more carefully

Observation: Top candidates are verbal forms (ykeody, yteody)
These suggest underlying roots: yk, yt, te

Let's decompose and find the TRUE roots
"""

import re
from collections import Counter


def load_astronomical_section(filepath):
    """Load only astronomical section"""

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    astro_words = []
    astro_contexts = []

    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith("<f"):
            folio_match = re.search(r"<f(\d+)[rv]", line_stripped)
            if folio_match:
                num = int(folio_match.group(1))
                if 67 <= num <= 73:  # Astronomical section
                    match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
                    if match:
                        text = match.group(1)
                        text = re.sub(r"<[^>]+>", "", text)
                        text = re.sub(r"\{[^}]+\}", "", text)
                        text = re.sub(r"\[[^\]]+\]", "", text)
                        text = re.sub(r"[@!]\d+;", "", text)
                        words = re.findall(r"[a-z]+", text.lower())

                        astro_words.extend(words)

                        # Keep context
                        for i, word in enumerate(words):
                            before = words[max(0, i - 2) : i]
                            after = words[i + 1 : min(len(words), i + 3)]
                            astro_contexts.append(
                                {"word": word, "before": before, "after": after}
                            )

    return astro_words, astro_contexts


def decompose_astronomical_words(astro_words):
    """Decompose to find roots"""

    print("\n" + "=" * 70)
    print("ASTRONOMICAL SECTION DECOMPOSITION")
    print("=" * 70)

    # Known morphemes to remove
    suffixes = ["edy", "dy", "aiin", "iin", "ain", "al", "ol", "ar", "or"]
    prefixes = ["qok", "qot"]
    known_roots = ["ok", "ot", "shee", "she", "sho", "keo", "cho", "cheo", "dor"]

    # Decompose
    potential_roots = Counter()

    for word in astro_words:
        remainder = word

        # Remove prefix
        for prefix in prefixes:
            if remainder.startswith(prefix):
                remainder = remainder[len(prefix) :]
                break

        # Remove known roots
        skip = False
        for root in known_roots:
            if remainder.startswith(root):
                skip = True
                break

        if skip:
            continue

        # Remove suffixes
        for suffix in suffixes:
            if remainder.endswith(suffix):
                remainder = remainder[: -len(suffix)]
                break

        # What's left is potential root
        if remainder and len(remainder) >= 2:
            potential_roots[remainder] += 1

    return potential_roots


def analyze_root_candidates(potential_roots, astro_contexts, top_n=20):
    """Analyze root candidates"""

    print(f"\nTop {top_n} potential astronomical roots:")
    print(f"{'Root':15} {'Count':>6}")
    print("-" * 25)

    candidates = []

    for root, count in potential_roots.most_common(top_n):
        print(f"{root:15} {count:6}")
        candidates.append((root, count))

    return candidates


def investigate_root_contexts(root, astro_contexts):
    """Show contexts for a specific root"""

    print("\n" + "=" * 70)
    print(f"CONTEXTS FOR ROOT: {root.upper()}")
    print("=" * 70)

    matching = [ctx for ctx in astro_contexts if root in ctx["word"]]

    print(f"\nTotal instances in astronomical: {len(matching)}")

    # Show forms
    forms = Counter(ctx["word"] for ctx in matching)
    print(f"\nTop 10 forms:")
    for form, count in forms.most_common(10):
        print(f"  {form:20} ({count})")

    # Sample contexts
    print(f"\nSample contexts (first 10):")
    for i, ctx in enumerate(matching[:10], 1):
        before_str = " ".join(ctx["before"][-2:]) if ctx["before"] else ""
        after_str = " ".join(ctx["after"][:2]) if ctx["after"] else ""
        print(f"{i:2}. {before_str:25} >>> {ctx['word']:15} <<< {after_str}")

    # Morphological check
    case_markers = ["al", "ol", "ar", "or"]
    verbal_markers = ["dy", "edy"]

    case_count = sum(
        1 for ctx in matching if any(ctx["word"].endswith(m) for m in case_markers)
    )
    verbal_count = sum(
        1 for ctx in matching if any(ctx["word"].endswith(m) for m in verbal_markers)
    )

    case_pct = 100 * case_count / len(matching) if matching else 0
    verbal_pct = 100 * verbal_count / len(matching) if matching else 0

    print(f"\nMorphological patterns:")
    print(f"  Case-marking: {case_count} ({case_pct:.1f}%)")
    print(f"  Verbal rate: {verbal_count} ({verbal_pct:.1f}%)")

    # Assessment
    print("\nQuick assessment:")
    if 30 <= case_pct <= 60 and verbal_pct < 15:
        print("  ✓ NOMINAL pattern (likely noun)")
        return "NOUN"
    elif verbal_pct > 30:
        print("  ? HIGH verbal rate (likely verb root)")
        return "VERB"
    elif case_pct < 20 and verbal_pct < 10:
        print("  ? LOW morphology (function word or particle?)")
        return "FUNCTION"
    else:
        print("  ? UNCLEAR pattern")
        return "UNCLEAR"


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading astronomical section...")
    astro_words, astro_contexts = load_astronomical_section(filepath)

    print(
        f"Astronomical section: {len(astro_words)} words, {len(set(astro_words))} unique"
    )

    print("\nDecomposing to find roots...")
    potential_roots = decompose_astronomical_words(astro_words)

    print(f"\nFound {len(potential_roots)} potential roots")

    candidates = analyze_root_candidates(potential_roots, astro_contexts, top_n=20)

    # Investigate top 5
    print("\n" + "=" * 70)
    print("DETAILED INVESTIGATION OF TOP 5")
    print("=" * 70)

    top_5_results = []

    for root, count in candidates[:5]:
        if count >= 5:  # Minimum threshold
            assessment = investigate_root_contexts(root, astro_contexts)
            top_5_results.append((root, count, assessment))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: TOP 5 ASTRONOMICAL ROOTS")
    print("=" * 70)

    for root, count, assessment in top_5_results:
        print(f"{root:15} {count:4} instances  →  {assessment}")

    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)

    noun_candidates = [r for r, c, a in top_5_results if a == "NOUN"]

    if noun_candidates:
        print(f"✓ Found {len(noun_candidates)} noun candidate(s):")
        for root in noun_candidates:
            print(f"  - {root} (investigate with full 8/8 scoring)")
    else:
        print("? No clear noun candidates in top 5")
        print(
            "? Astronomical section may use different word types (verbs, function words)"
        )
        print("? Consider investigating lower-frequency candidates")
