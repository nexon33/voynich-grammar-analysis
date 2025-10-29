"""
Investigate "sho" - 6/8 score candidate

Evidence:
- 973 instances (2.58% of manuscript)
- 43.1% case-marking (in nominal sweet spot!)
- 10.7% verbal rate (low, nominal-leaning)
- 2.0x enriched in herbal section
- 3,283 co-occurrences with validated nouns

This looks like a BOTANICAL TERM!
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

        if "# herbal" in line_stripped.lower():
            current_section = "herbal"
        elif "# pharmaceutical" in line_stripped.lower():
            current_section = "pharmaceutical"

        if line_stripped.startswith("<f"):
            match = re.search(r"<f\d+[rv]\d*\.[^>]+>\s+(.+)$", line_stripped)
            if match:
                text = match.group(1)
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                words = re.findall(r"[a-z!]+", text.lower())

                # Find "sho" instances
                for i, word in enumerate(words):
                    if "sho" in word and "shee" not in word and "she" not in word:
                        context = {
                            "word": word,
                            "section": current_section,
                            "before": words[max(0, i - 3) : i],
                            "after": words[i + 1 : min(len(words), i + 4)],
                            "full_line": " ".join(words),
                        }
                        contexts.append(context)

    return contexts


def analyze_sho_contexts(contexts):
    """Analyze what "sho" appears with"""

    print("SHO CONTEXT ANALYSIS")
    print("=" * 70)

    # Co-occurrence patterns
    before_words = Counter()
    after_words = Counter()

    # Forms of sho
    sho_forms = Counter()

    for ctx in contexts:
        sho_forms[ctx["word"]] += 1
        before_words.update(ctx["before"])
        after_words.update(ctx["after"])

    # Section distribution
    by_section = Counter(ctx["section"] for ctx in contexts)

    print(f"\nTotal instances with context: {len(contexts)}")
    print(f"\nSection distribution:")
    for section, count in by_section.most_common():
        print(f"  {section}: {count} ({count / len(contexts) * 100:.1f}%)")

    print(f"\nTop forms of 'sho' (first 20):")
    for form, count in sho_forms.most_common(20):
        print(f"  {form:20} ({count:3})")

    print(f"\nTop 15 words BEFORE 'sho':")
    for word, count in before_words.most_common(15):
        print(f"  {word:15} ({count:3})")

    print(f"\nTop 15 words AFTER 'sho':")
    for word, count in after_words.most_common(15):
        print(f"  {word:15} ({count:3})")

    # Sample contexts from herbal section
    print(f"\n{'=' * 70}")
    print("SAMPLE CONTEXTS FROM HERBAL SECTION")
    print(f"{'=' * 70}")

    herbal_contexts = [ctx for ctx in contexts if ctx["section"] == "herbal"][:20]

    for i, ctx in enumerate(herbal_contexts, 1):
        before_str = " ".join(ctx["before"])
        after_str = " ".join(ctx["after"])
        print(f"\n{i}. ... {before_str} >>> {ctx['word']} <<< {after_str} ...")

    # Pattern analysis
    print(f"\n{'=' * 70}")
    print("PATTERN ANALYSIS")
    print(f"{'=' * 70}")

    # Check if sho appears with known botanical terms
    with_oak = sum(
        1
        for ctx in contexts
        if any("ok" in w or "qok" in w for w in ctx["before"] + ctx["after"])
    )
    with_oat = sum(
        1
        for ctx in contexts
        if any("ot" in w or "qot" in w for w in ctx["before"] + ctx["after"])
    )
    with_water = sum(
        1 for ctx in contexts if any("she" in w for w in ctx["before"] + ctx["after"])
    )
    with_vessel = sum(
        1
        for ctx in contexts
        if any("cho" in w and "cheo" not in w for w in ctx["before"] + ctx["after"])
    )

    print(f"\nCo-occurrence with validated botanical terms:")
    print(f"  With oak: {with_oak} instances ({with_oak / len(contexts) * 100:.1f}%)")
    print(f"  With oat: {with_oat} instances ({with_oat / len(contexts) * 100:.1f}%)")
    print(
        f"  With water: {with_water} instances ({with_water / len(contexts) * 100:.1f}%)"
    )
    print(
        f"  With vessel: {with_vessel} instances ({with_vessel / len(contexts) * 100:.1f}%)"
    )

    # Morphological analysis
    with_case = sum(
        1 for ctx in contexts if ctx["word"].endswith(("al", "ar", "ol", "or"))
    )
    with_verbal = sum(
        1 for ctx in contexts if "dy" in ctx["word"] or "edy" in ctx["word"]
    )
    standalone = sum(1 for ctx in contexts if ctx["word"] == "sho")

    print(f"\nMorphological patterns:")
    print(f"  With case markers: {with_case} ({with_case / len(contexts) * 100:.1f}%)")
    print(
        f"  With verbal suffix: {with_verbal} ({with_verbal / len(contexts) * 100:.1f}%)"
    )
    print(f"  Standalone 'sho': {standalone} ({standalone / len(contexts) * 100:.1f}%)")

    return contexts


def hypothesize_meaning(contexts):
    """Based on context, what could 'sho' mean?"""

    print(f"\n{'=' * 70}")
    print("SEMANTIC HYPOTHESIS")
    print(f"{'=' * 70}")

    print("\nEvidence:")
    print("  1. 43% case-marking → NOUN (not grammatical morpheme)")
    print("  2. 11% verbal rate → NOMINAL-LEANING (mostly noun, sometimes verb)")
    print("  3. 2.0x enriched in HERBAL section → BOTANICAL TERM")
    print("  4. Co-occurs with oak, oat, water, vessel")
    print("  5. Very frequent (973 instances, 2.58% of manuscript)")

    print("\nPossible meanings:")
    print("  1. Another plant name (like oak/oat)")
    print("  2. Plant part (leaf, root, flower, stem)")
    print("  3. Color/property (like 'red/dor')")
    print("  4. Action/process (if verbal forms are significant)")

    print("\nMost likely hypothesis:")
    print("  Given:")
    print("  - Herbal enrichment (2x)")
    print("  - Nominal preference (43% case, 11% verbal)")
    print("  - Co-occurs with other botanical terms")
    print("  - Very frequent")
    print("\n  → SHO is likely a COMMON BOTANICAL TERM")
    print("    (plant name, plant part, or botanical property)")

    print("\nNext steps to validate:")
    print("  1. Look at illustrations where 'sho' appears")
    print("  2. Check if 'sho' appears in specific plant contexts")
    print("  3. Analyze verbal forms (shody, shoeey) for semantic clues")
    print("  4. Compare distribution to oak/oat patterns")


def main():
    filepath = (
        "C:/Users/adria/Documents/manuscript/data/voynich/eva_transcription/ZL3b-n.txt"
    )

    contexts = load_voynich_with_context(filepath)
    analyze_sho_contexts(contexts)
    hypothesize_meaning(contexts)


if __name__ == "__main__":
    main()
