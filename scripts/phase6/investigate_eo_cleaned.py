"""
Investigate "eo" candidate more carefully
REMEMBER: We do e↔o substitution, so check for variants
Also: Remove instances that are just part of ok/ot/cho/shee decomposition
"""

import re
from collections import Counter, defaultdict


def load_and_analyze_eo():
    """
    Load corpus and find TRUE instances of 'eo'
    Exclude cases where it's just residue from known roots
    """

    # Known roots that might create false "eo" matches
    known_roots = ["ok", "qok", "ot", "qot", "shee", "she", "cho", "cheo", "dor", "sho"]

    all_sections = {
        "herbal": [],
        "pharmaceutical": [],
        "biological": [],
        "astronomical": [],
    }

    # Load all folios
    import os

    folios_dir = "data/voynich_zl_ivtff_1r"

    for filename in os.listdir(folios_dir):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(folios_dir, filename)

        # Determine section
        folio_num = filename.replace(".txt", "")
        if folio_num.startswith("f") and len(folio_num) > 1:
            num_part = folio_num[1:].rstrip("rv")
            try:
                num = int(num_part)
                if 1 <= num <= 66:
                    section = "herbal"
                elif 67 <= num <= 73:
                    section = "astronomical"
                elif 75 <= num <= 84:
                    section = "biological"
                elif 85 <= num <= 116:
                    section = "pharmaceutical"
                else:
                    section = "unknown"
            except:
                section = "unknown"
        else:
            section = "unknown"

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#") or line.startswith("<"):
                    continue
                words = line.strip().split()
                if section in all_sections:
                    all_sections[section].extend(words)

    # Find "eo" instances
    eo_contexts = []

    for section, words in all_sections.items():
        for i, word in enumerate(words):
            # Clean word
            word_clean = word.lower().strip(".,;!?")

            # Check if contains 'eo'
            if "eo" not in word_clean:
                continue

            # EXCLUDE if it's just part of a known root decomposition
            # e.g., "okeol" = ok + eol, not a true "eo" instance
            exclude = False
            for root in known_roots:
                if word_clean.startswith(root):
                    # It's root + suffix, not a true "eo" instance
                    exclude = True
                    break

            if exclude:
                continue

            # Get context
            before = words[i - 2 : i] if i >= 2 else words[:i]
            after = words[i + 1 : i + 3] if i < len(words) - 1 else words[i + 1 :]

            eo_contexts.append(
                {
                    "word": word_clean,
                    "section": section,
                    "before": " ".join(before),
                    "after": " ".join(after),
                }
            )

    return eo_contexts


def analyze_true_eo(contexts):
    """Analyze the TRUE eo instances (not just decomposition residue)"""

    print("\n" + "=" * 70)
    print("TRUE 'EO' INSTANCES (excluding ok/ot/cho/etc. decomposition)")
    print("=" * 70)

    print(f"\nTotal TRUE instances: {len(contexts)}")

    # Section distribution
    section_counts = Counter(c["section"] for c in contexts)
    print("\nSection distribution:")
    for section, count in section_counts.most_common():
        pct = 100 * count / len(contexts)
        print(f"  {section}: {count} ({pct:.1f}%)")

    # Word forms
    word_counts = Counter(c["word"] for c in contexts)
    print(f"\nTop 20 TRUE forms:")
    for word, count in word_counts.most_common(20):
        print(f"  {word:20} ({count})")

    # Check for e↔o substitution patterns
    print("\n" + "=" * 70)
    print("CHECKING e↔o SUBSTITUTION")
    print("=" * 70)
    print("If 'eo' → 'oo', does it match any known roots?")
    print("  Known roots: ok, ot, shee/she, cho, cheo, dor, sho")
    print("  'eo' → 'oo' = no match")
    print("\nIf 'eo' is actually 'e' + 'o' with substitution:")
    print("  'e' could be 'o' → but we don't have standalone 'o' root")
    print("  'o' could be 'e' → but we don't have standalone 'e' root")

    # Morphological analysis
    case_markers = ["al", "ol", "ar", "or"]
    verbal_markers = ["dy", "edy"]

    case_count = 0
    verbal_count = 0

    for ctx in contexts:
        word = ctx["word"]
        if any(word.endswith(m) for m in case_markers):
            case_count += 1
        if any(word.endswith(m) for m in verbal_markers):
            verbal_count += 1

    case_pct = 100 * case_count / len(contexts) if contexts else 0
    verbal_pct = 100 * verbal_count / len(contexts) if contexts else 0

    print("\n" + "=" * 70)
    print("MORPHOLOGICAL PATTERNS (TRUE instances only)")
    print("=" * 70)
    print(f"With case markers: {case_count} ({case_pct:.1f}%)")
    print(f"With verbal markers: {verbal_count} ({verbal_pct:.1f}%)")

    # Sample contexts
    print("\n" + "=" * 70)
    print("SAMPLE CONTEXTS (first 15 TRUE instances)")
    print("=" * 70)
    for i, ctx in enumerate(contexts[:15], 1):
        print(f"{i:2}. {ctx['before']:30} >>> {ctx['word']} <<< {ctx['after']}")

    # Assessment
    print("\n" + "=" * 70)
    print("ASSESSMENT")
    print("=" * 70)

    if len(contexts) < 100:
        print("  ✗ TOO FEW instances after removing known root decompositions")
        print("  ✗ 'eo' is likely just morphological residue, not a true root")
    elif case_pct < 20 or case_pct > 70:
        print(f"  ? Case marking outside nominal range: {case_pct:.1f}%")
    elif verbal_pct > 20:
        print(f"  ? High verbal rate: {verbal_pct:.1f}%")
    else:
        print(f"  ✓ Nominal pattern: case {case_pct:.1f}%, verbal {verbal_pct:.1f}%")


if __name__ == "__main__":
    contexts = load_and_analyze_eo()
    analyze_true_eo(contexts)
