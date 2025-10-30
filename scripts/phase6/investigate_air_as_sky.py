#!/usr/bin/env python3
"""
Investigate AIR as "sky"
========================

User's intuition: "air reminds me of in the sky"

Hypothesis: "air" = "sky" (celestial/aerial realm)

This would explain:
1. Why "dair" (there) + "air" (sky) = "there in the sky" (100% co-occurrence)
2. Why compounds like "okair" = "oak-sky" (botanical in celestial context?)
3. Why astronomical section has 12.7% of instances
4. Low morphology (concrete noun, but treated as locational)

Author: Voynich Research Team
Date: 2025-10-29
"""

import re
from collections import Counter


def load_voynich_with_context(filepath):
    """Load Voynich text with full sentence context and section tracking"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    words_with_context = []
    current_section = "unknown"

    for line in lines:
        line_stripped = line.strip()

        # Track sections from comments
        if "# herbal" in line_stripped.lower():
            current_section = "herbal"
        elif "# astronomical" in line_stripped.lower():
            current_section = "astronomical"
        elif "# biological" in line_stripped.lower():
            current_section = "biological"
        elif "# pharmaceutical" in line_stripped.lower():
            current_section = "pharmaceutical"
        elif "# recipes" in line_stripped.lower():
            current_section = "recipes"

        # Parse actual text lines
        if line_stripped.startswith("<f"):
            match = re.search(r"(<f\d+[rv]\d*\.[^>]+>)\s+(.+)$", line_stripped)
            if match:
                locator = match.group(1)
                text = match.group(2)

                # Clean text
                text = re.sub(r"<[^>]+>", "", text)
                text = re.sub(r"\{[^}]+\}", "", text)
                text = re.sub(r"\[[^\]]+\]", "", text)
                text = re.sub(r"[@!]\d+;", "", text)
                text = re.sub(r"[.,;:!?<>]", " ", text)

                words = re.findall(r"[a-z]+", text.lower())

                for i, word in enumerate(words):
                    context_before = " ".join(words[max(0, i - 3) : i])
                    context_after = " ".join(words[i + 1 : min(len(words), i + 4)])

                    words_with_context.append(
                        {
                            "word": word,
                            "locator": locator,
                            "section": current_section,
                            "context_before": context_before,
                            "context_after": context_after,
                            "full_sentence": " ".join(words),
                        }
                    )

    return words_with_context


def analyze_air_as_sky(words_with_context):
    """Analyze AIR as 'sky' hypothesis"""

    # Find AIR instances (excluding dair, chair, etc.)
    air_instances = []
    for entry in words_with_context:
        word = entry["word"]
        if word == "air" or word.startswith("air") or word.endswith("air"):
            if "dair" not in word and "chair" not in word and "shair" not in word:
                air_instances.append(entry)

    print("=" * 80)
    print("AIR AS 'SKY' HYPOTHESIS INVESTIGATION")
    print("=" * 80)
    print(f"\nTotal AIR instances: {len(air_instances)}")

    # 1. Test: "dair air" = "there [in the] sky"
    print("\n" + "=" * 80)
    print("1. TESTING: 'dair air' = 'there [in the] sky'")
    print("=" * 80)

    dair_cooc = [inst for inst in air_instances if "dair" in inst["full_sentence"]]
    print(f"\nSentences with 'dair' + 'air': {len(dair_cooc)}")

    # Count "dair ar air" patterns
    dair_ar_air = 0
    dair_air_direct = 0

    for inst in dair_cooc:
        sentence = inst["full_sentence"]
        if "dair ar air" in sentence or "dair ar" in sentence:
            dair_ar_air += 1
        if re.search(r"\bdair\s+\w*air", sentence):
            dair_air_direct += 1

    print(f"Pattern 'dair ar ...' (there at ...): {dair_ar_air}")
    print(f"Pattern 'dair ...air' (there ...sky): {dair_air_direct}")

    print("\nSample astronomical contexts with 'dair' + 'air':")
    astro_dair = [inst for inst in dair_cooc if inst["section"] == "astronomical"]
    for i, inst in enumerate(astro_dair[:5], 1):
        sentence = inst["full_sentence"]
        sentence = sentence.replace(" dair ", " [DAIR=there] ")
        sentence = re.sub(r"\bair\b", "[AIR=sky?]", sentence)
        sentence = re.sub(r"(\w+air\b)", r"[\1=?-sky]", sentence)
        print(f"\n{i}. {inst['locator']}")
        print(f"   {sentence[:100]}...")

    # 2. Compound analysis: "X-air" = "X in/of the sky"?
    print("\n" + "=" * 80)
    print("2. COMPOUND ANALYSIS: Does 'X-air' mean 'X of/in the sky'?")
    print("=" * 80)

    compounds = Counter()
    for inst in air_instances:
        word = inst["word"]
        if word != "air" and word.endswith("air"):
            # Extract root
            root = word[:-3]  # Remove 'air'
            compounds[root] += 1

    print("\nTop compound roots + 'air':")
    print(f"{'Root':15s} {'Count':>8s} {'Possible meaning (if air=sky)'}")
    print("-" * 70)

    meanings = {
        "ok": "oak-sky (oak constellation?)",
        "qok": "oak-sky (variant)",
        "ot": "oat-sky (oat constellation?)",
        "qot": "oat-sky (variant)",
        "s": "s-sky (?)",
        "k": "k-sky (?)",
        "t": "t-sky (?)",
        "yk": "yk-sky (?)",
        "ol": "ol-sky (?)",
        "p": "p-sky (?)",
        "o": "o-sky (?)",
        "yt": "yt-sky (?)",
        "olk": "olk-sky (?)",
        "op": "op-sky (?)",
        "lk": "lk-sky (?)",
        "r": "r-sky (?)",
    }

    for root, count in compounds.most_common(15):
        meaning = meanings.get(root, "?-sky")
        print(f"{root:15s} {count:>8d}    {meaning}")

    # 3. Astronomical enrichment test
    print("\n" + "=" * 80)
    print("3. ASTRONOMICAL ENRICHMENT (Sky = astronomical context?)")
    print("=" * 80)

    section_dist = Counter(inst["section"] for inst in air_instances)
    total_words_by_section = Counter(entry["section"] for entry in words_with_context)

    print(f"\n{'Section':20s} {'AIR count':>12s} {'% of AIR':>12s} {'Enrichment':>12s}")
    print("-" * 70)

    for section in ["astronomical", "pharmaceutical", "herbal", "biological"]:
        air_count = section_dist[section]
        air_pct = (air_count / len(air_instances)) * 100

        section_total = total_words_by_section[section]
        section_pct = (section_total / len(words_with_context)) * 100

        enrichment = air_pct / section_pct if section_pct > 0 else 0

        status = "✓" if enrichment > 1.2 else ""
        print(
            f"{section:20s} {air_count:>12d} {air_pct:>11.1f}% {enrichment:>11.2f}x {status}"
        )

    # 4. Morphological behavior - is it a concrete noun or locational particle?
    print("\n" + "=" * 80)
    print("4. MORPHOLOGICAL BEHAVIOR")
    print("=" * 80)

    case_suffixes = ["ol", "al", "or", "ar", "ody", "eody"]
    verbal_suffixes = ["y", "edy", "dy"]

    case_count = sum(
        1
        for inst in air_instances
        if any(inst["word"].endswith(suf) for suf in case_suffixes)
    )
    verbal_count = sum(
        1
        for inst in air_instances
        if any(inst["word"].endswith(suf) for suf in verbal_suffixes)
    )

    case_pct = (case_count / len(air_instances)) * 100
    verbal_pct = (verbal_count / len(air_instances)) * 100

    print(f"\nCase-marking: {case_count}/{len(air_instances)} ({case_pct:.1f}%)")
    print(f"Verbal rate:  {verbal_count}/{len(air_instances)} ({verbal_pct:.1f}%)")
    print(f"\nComparison:")
    print(f"  Function words:  <10% case, <10% verbal")
    print(f"  Concrete nouns:  30-60% case, <15% verbal")
    print(
        f"  'air' behavior:  {case_pct:.1f}% case, {verbal_pct:.1f}% verbal → Function word / Locational"
    )

    # 5. Sample translations with "air" = "sky"
    print("\n" + "=" * 80)
    print("5. SAMPLE TRANSLATIONS: air = 'sky'")
    print("=" * 80)

    print("\nAstronomical section examples:")
    astro_samples = [
        inst for inst in air_instances if inst["section"] == "astronomical"
    ]

    for i, inst in enumerate(astro_samples[:8], 1):
        sentence = inst["full_sentence"].split()[:12]  # First 12 words

        # Translate known terms
        translation = []
        for word in sentence:
            if "dair" in word:
                translation.append("THERE")
            elif word == "air" or word.endswith("air"):
                if word == "air":
                    translation.append("SKY")
                elif word.startswith("ok") or word.startswith("qok"):
                    translation.append("OAK-SKY")
                elif word.startswith("ot") or word.startswith("qot"):
                    translation.append("OAT-SKY")
                else:
                    translation.append(f"{word[:-3]}-SKY")
            elif "ok" in word or "qok" in word:
                translation.append("OAK[...]")
            elif "ot" in word or "qot" in word:
                translation.append("OAT[...]")
            elif "cho" in word:
                translation.append("VESSEL[...]")
            elif "she" in word or "shee" in word:
                translation.append("WATER[...]")
            else:
                translation.append("[?]")

        print(f"\n{i}. {inst['locator']}")
        print(f"   Original: {' '.join(sentence)}")
        print(f"   If air=sky: {' '.join(translation)}")


def main():
    filepath = (
        r"C:\Users\adria\Documents\manuscript\data\voynich\eva_transcription\ZL3b-n.txt"
    )

    print("Loading Voynich manuscript...")
    words_with_context = load_voynich_with_context(filepath)
    print(f"Loaded {len(words_with_context)} words\n")

    analyze_air_as_sky(words_with_context)

    print("\n" + "=" * 80)
    print("HYPOTHESIS EVALUATION: air = 'sky'")
    print("=" * 80)
    print("""
HYPOTHESIS: "air" = "sky" (celestial/aerial realm)

Evidence in FAVOR:
  ✓ "dair air" = "there [in the] sky" (perfect semantic fit!)
  ✓ Compounds "okair" = "oak-sky" (constellation names?)
  ✓ LOW morphology = locational/environmental term
  ✓ Universal distribution = sky visible from all contexts
  ✓ Explains 100% "dair" co-occurrence asymmetry

Evidence AGAINST:
  ✗ No astronomical enrichment (should be higher if "sky")
  ✗ Too common for specific celestial term
  ✗ Different morphology from other nouns

VERDICT will be based on patterns above.

If TRUE: We've decoded the spatial system!
  - "dair" = "there" (distal demonstrative)
  - "air" = "sky" (celestial realm)
  - "dair air" = "there in the sky"
  - "okair" = "oak-sky" (constellation name)
    """)


if __name__ == "__main__":
    main()
