"""
Investigate "cth" - herbal-enriched candidate (882 instances, 5/8 score)

Observations:
- 20.3% case-marking (below nominal range but not zero)
- 10.9% verbal rate (good for noun)
- 2.13x herbal enrichment

Question: Is "cth" a noun or a prefix/particle?
"""

import re
from collections import Counter


def load_voynich_with_context(filepath):
    """Load with context"""

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    contexts = []
    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        if line_stripped.startswith("<f"):
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
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z]+", text.lower())

                # Find "cth" instances
                for i, word in enumerate(words):
                    if "cth" in word:
                        context = {
                            "word": word,
                            "section": current_section,
                            "before": words[max(0, i - 2) : i],
                            "after": words[i + 1 : min(len(words), i + 3)],
                        }
                        contexts.append(context)

    return contexts


def analyze_cth_position(contexts):
    """Analyze where 'cth' appears in words"""

    print("\\n" + "=" * 70)
    print('"CTH" POSITION ANALYSIS')
    print("=" * 70)

    position_counts = {
        "word_start": 0,  # cth at beginning
        "word_middle": 0,  # cth in middle
        "word_end": 0,  # cth at end
        "standalone": 0,  # just "cth"
    }

    for ctx in contexts:
        word = ctx["word"]

        if word == "cth":
            position_counts["standalone"] += 1
        elif word.startswith("cth"):
            position_counts["word_start"] += 1
        elif word.endswith("cth"):
            position_counts["word_end"] += 1
        else:
            position_counts["word_middle"] += 1

    total = len(contexts)
    print(f"\\nTotal instances: {total}")
    print(f"\\nPosition distribution:")
    for pos, count in position_counts.items():
        pct = 100 * count / total
        print(f"  {pos:15} {count:4} ({pct:5.1f}%)")

    return position_counts


def analyze_cth_forms(contexts):
    """Analyze cth forms"""

    print("\\n" + "=" * 70)
    print('"CTH" FORMS ANALYSIS')
    print("=" * 70)

    forms = Counter(ctx["word"] for ctx in contexts)

    print(f"\\nTop 30 forms:")
    for form, count in forms.most_common(30):
        print(f"  {form:25} ({count:3})")

    return forms


def analyze_cth_patterns(contexts):
    """Look for patterns"""

    print("\\n" + "=" * 70)
    print('"CTH" PATTERN ANALYSIS')
    print("=" * 70)

    # Common cth- starts
    cth_starts = Counter()
    for ctx in contexts:
        word = ctx["word"]
        if word.startswith("cth") and len(word) > 3:
            cth_starts[word] += 1

    print(f'\\nTop "cth..." forms (word-initial):')
    for form, count in cth_starts.most_common(15):
        print(f"  {form:25} ({count:3})")

    # Check if cth appears with known roots
    print(f"\\nCombinations with validated roots:")
    validated_roots = ["ok", "ot", "she", "sho", "keo", "teo", "cho", "cheo", "dor"]

    for root in validated_roots:
        matches = [
            ctx for ctx in contexts if root in ctx["word"] and "cth" in ctx["word"]
        ]
        if matches:
            print(f"  cth + {root:6} {len(matches):3} instances")
            # Show examples
            examples = [ctx["word"] for ctx in matches[:3]]
            print(f"             Examples: {', '.join(examples)}")


if __name__ == "__main__":
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    print("Loading Voynich manuscript...")
    contexts = load_voynich_with_context(filepath)

    print(f'\\nTotal "cth" instances: {len(contexts)}')

    # Section distribution
    by_section = Counter(ctx["section"] for ctx in contexts)
    print(f"\\nSection distribution:")
    for section, count in by_section.most_common():
        pct = 100 * count / len(contexts)
        print(f"  {section:20} {count:4} ({pct:5.1f}%)")

    # Position analysis
    position_counts = analyze_cth_position(contexts)

    # Forms analysis
    forms = analyze_cth_forms(contexts)

    # Pattern analysis
    analyze_cth_patterns(contexts)

    # Sample contexts
    print("\\n" + "=" * 70)
    print("SAMPLE CONTEXTS (first 20)")
    print("=" * 70)
    for i, ctx in enumerate(contexts[:20], 1):
        before_str = " ".join(ctx["before"][-2:]) if ctx["before"] else ""
        after_str = " ".join(ctx["after"][:2]) if ctx["after"] else ""
        print(f"{i:2}. {before_str:25} >>> {ctx['word']:20} <<< {after_str}")

    # Conclusion
    print("\\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if position_counts["word_start"] > position_counts["standalone"] * 2:
        print('  → "cth" appears mostly at WORD START')
        print("  → Likely a PREFIX, not a standalone root")
        print("  → Examples: cthol, cthey, cthal, cthy")
    elif position_counts["standalone"] > len(contexts) * 0.3:
        print('  → "cth" appears frequently STANDALONE')
        print("  → Could be a function word or noun")
    else:
        print('  → "cth" has mixed distribution')
        print("  → Unclear if prefix or root")

    print("\\n  → NOT recommended for noun validation")
    print("  → Investigate as potential PREFIX or grammatical element")
