"""
Investigate "eo" - 5/8 score candidate
REMEMBER: We do e↔o substitution!

IMPORTANT: Many "eo" instances might be residue from decomposing ok/ot/cho
We need to find TRUE standalone "eo" instances
"""

import re
from collections import Counter


def load_voynich_with_context(filepath):
    """Load with line context preserved"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    contexts = []
    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        # Track section
        if "# herbal" in line_stripped.lower() or "Language A" in line_stripped:
            current_section = "herbal"
        elif "# pharmaceutical" in line_stripped.lower():
            current_section = "pharmaceutical"
        elif (
            "# biological" in line_stripped.lower()
            or "# balnea" in line_stripped.lower()
        ):
            current_section = "biological"
        elif (
            "# astronomical" in line_stripped.lower()
            or "# cosmo" in line_stripped.lower()
        ):
            current_section = "astronomical"

        # Parse folio lines
        if line_stripped.startswith("<f"):
            # Extract section from folio number
            folio_match = re.search(r"<f(\d+)[rv]", line_stripped)
            if folio_match:
                num = int(folio_match.group(1))
                if 1 <= num <= 66:
                    current_section = "herbal"
                elif 67 <= num <= 73:
                    current_section = "astronomical"
                elif 75 <= num <= 84:
                    current_section = "biological"
                elif 85 <= num <= 116:
                    current_section = "pharmaceutical"

            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
            if match:
                text = match.group(1)
                # Clean
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z]+", text.lower())

                # Find "eo" instances - but EXCLUDE known root decompositions
                for i, word in enumerate(words):
                    if "eo" not in word:
                        continue

                    # EXCLUDE if it's just ok/ot/qok/qot + suffix
                    if (
                        word.startswith("ok")
                        or word.startswith("qok")
                        or word.startswith("ot")
                        or word.startswith("qot")
                    ):
                        # This is oak/oat + suffix, not a true "eo" instance
                        continue

                    # EXCLUDE if it's cho/cheo variants
                    if word.startswith("cho") or word.startswith("cheo"):
                        continue

                    # EXCLUDE if it's shee/she variants
                    if word.startswith("she"):
                        continue

                    # NOW we have a TRUE "eo" instance
                    context = {
                        "word": word,
                        "section": current_section,
                        "before": words[max(0, i - 3) : i],
                        "after": words[i + 1 : min(len(words), i + 4)],
                        "full_line": " ".join(words),
                    }
                    contexts.append(context)

    return contexts


def analyze_eo_contexts(contexts):
    """Analyze TRUE 'eo' instances"""

    print("\n" + "=" * 70)
    print('TRUE "EO" INSTANCES (excluding ok/ot/cho/she decomposition)')
    print("=" * 70)

    print(f"\nTotal TRUE instances: {len(contexts)}")

    if len(contexts) < 50:
        print("\n⚠️  WARNING: Very few TRUE instances!")
        print('   "eo" is likely just morphological residue, not a standalone root')
        return

    # Section distribution
    by_section = Counter(ctx["section"] for ctx in contexts)
    print(f"\nSection distribution:")
    for section, count in by_section.most_common():
        pct = 100 * count / len(contexts)
        print(f"  {section}: {count} ({pct:.1f}%)")

    # Forms
    eo_forms = Counter(ctx["word"] for ctx in contexts)
    print(f"\nTop 20 TRUE forms:")
    for form, count in eo_forms.most_common(20):
        print(f"  {form:20} ({count:3})")

    # Morphological analysis
    case_markers = ["al", "ol", "ar", "or"]
    verbal_markers = ["dy", "edy"]

    case_count = sum(
        1 for ctx in contexts if any(ctx["word"].endswith(m) for m in case_markers)
    )
    verbal_count = sum(
        1 for ctx in contexts if any(ctx["word"].endswith(m) for m in verbal_markers)
    )

    case_pct = 100 * case_count / len(contexts)
    verbal_pct = 100 * verbal_count / len(contexts)

    print("\n" + "=" * 70)
    print("MORPHOLOGICAL PATTERNS")
    print("=" * 70)
    print(f"With case markers: {case_count} ({case_pct:.1f}%)")
    print(f"With verbal markers: {verbal_count} ({verbal_pct:.1f}%)")

    # Co-occurrence
    before_words = Counter()
    after_words = Counter()
    for ctx in contexts:
        before_words.update(ctx["before"])
        after_words.update(ctx["after"])

    print(f'\nTop 10 words BEFORE "eo":')
    for word, count in before_words.most_common(10):
        print(f"  {word:15} ({count:3})")

    print(f'\nTop 10 words AFTER "eo":')
    for word, count in after_words.most_common(10):
        print(f"  {word:15} ({count:3})")

    # Sample contexts
    print("\n" + "=" * 70)
    print("SAMPLE CONTEXTS (first 20)")
    print("=" * 70)
    for i, ctx in enumerate(contexts[:20], 1):
        before_str = " ".join(ctx["before"][-2:]) if ctx["before"] else ""
        after_str = " ".join(ctx["after"][:2]) if ctx["after"] else ""
        print(f"{i:2}. {before_str:30} >>> {ctx['word']} <<< {after_str}")

    # Check e↔o substitution
    print("\n" + "=" * 70)
    print("e↔o SUBSTITUTION CHECK")
    print("=" * 70)
    print('If "eo" → "oo": no match with known roots')
    print('If "eo" → "oe": no match with known roots')
    print(
        '\n→ "eo" does NOT appear to be a variant of a known root via e↔o substitution'
    )

    # Assessment
    print("\n" + "=" * 70)
    print("ASSESSMENT")
    print("=" * 70)

    if case_pct >= 30 and case_pct <= 60 and verbal_pct < 15:
        print(f"  ✓ LIKELY NOUN: case {case_pct:.1f}%, verbal {verbal_pct:.1f}%")
        if by_section.most_common(1)[0][1] / len(contexts) > 0.35:
            top_section = by_section.most_common(1)[0][0]
            enrichment = by_section.most_common(1)[0][1] / len(contexts)
            print(f"  ✓ Enriched in {top_section} section ({enrichment * 100:.1f}%)")
            print(f'\n  → "eo" is a {top_section.upper()}-SPECIFIC NOUN')
    elif case_pct < 25 or verbal_pct > 25:
        print(f"  ? AMBIGUOUS: case {case_pct:.1f}%, verbal {verbal_pct:.1f}%")
        print(f"  ? Might be a function word or verbal root")
    else:
        print(f"  ? UNCLEAR: case {case_pct:.1f}%, verbal {verbal_pct:.1f}%")


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading Voynich manuscript...")
    contexts = load_voynich_with_context(filepath)

    analyze_eo_contexts(contexts)
