#!/usr/bin/env python3
"""
Investigate AR as Locative Preposition
======================================

Pattern observed: "dair ar chedar" = "there [?] [term]"
Pattern observed: "qotair ar alor" = "oat-constellation [?] [place]"

Hypothesis: "ar" = "at/in" (locative preposition)

Expected evidence if preposition:
- High frequency (prepositions are common)
- Low morphology (<10%)
- Pre-nominal position (between demonstrative/noun and following noun)
- Completes spatial formula: "dair ar air" = "there at sky"
- Astronomical enrichment (spatial references)

IMPORTANT: Must distinguish:
- "ar" standalone (preposition)
- "-ar" suffix (directional case marker)

Author: Voynich Research Team
Date: 2025-10-30
"""

import re
from collections import Counter, defaultdict


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


def analyze_ar_preposition(words_with_context):
    """Analyze AR as preposition hypothesis"""

    # Find all AR instances
    # CRITICAL: Distinguish standalone "ar" from "-ar" suffix
    ar_instances = []
    ar_suffix_instances = []

    for entry in words_with_context:
        word = entry["word"]

        # Standalone "ar" or "ar" with minimal morphology
        if word == "ar" or word in ["ary", "ars", "arl"]:
            ar_instances.append(entry)
        # Words ending in "-ar" (directional case suffix)
        elif word.endswith("ar") and len(word) > 2:
            ar_suffix_instances.append(entry)

    print("=" * 80)
    print("AR AS LOCATIVE PREPOSITION HYPOTHESIS")
    print("=" * 80)
    print(f"\nStandalone 'ar' instances: {len(ar_instances)}")
    print(f"Words with '-ar' suffix: {len(ar_suffix_instances)}")
    print(f"Total 'ar' in manuscript: {len(ar_instances) + len(ar_suffix_instances)}")

    if len(ar_instances) == 0:
        print("\nERROR: No standalone AR instances found!")
        print("This suggests 'ar' may only exist as suffix, not preposition.")
        return 0

    print(f"\nAnalyzing standalone 'ar' for preposition hypothesis...")

    # 1. Form distribution
    print("\n" + "=" * 80)
    print("1. FORM VARIANTS (Standalone vs suffix)")
    print("=" * 80)

    form_dist = Counter(inst["word"] for inst in ar_instances)
    standalone_ar = form_dist.get("ar", 0)
    print(
        f"\nStandalone 'ar': {standalone_ar} instances ({standalone_ar / len(ar_instances) * 100:.1f}%)"
    )
    print(f"\nAll standalone forms:")
    for form, count in form_dist.most_common():
        pct = (count / len(ar_instances)) * 100
        print(f"  {form:15s}: {count:4d} ({pct:5.1f}%)")

    # 2. Section distribution
    print("\n" + "=" * 80)
    print("2. SECTION DISTRIBUTION")
    print("=" * 80)

    section_dist = Counter(inst["section"] for inst in ar_instances)
    total_words_by_section = Counter(entry["section"] for entry in words_with_context)

    print(f"\n{'Section':20s} {'AR count':>10s} {'% of AR':>10s} {'Enrichment':>12s}")
    print("-" * 70)

    for section in ["astronomical", "herbal", "pharmaceutical", "biological"]:
        ar_count = section_dist[section]
        ar_pct = (ar_count / len(ar_instances)) * 100

        section_total = total_words_by_section[section]
        section_pct = (section_total / len(words_with_context)) * 100

        enrichment = ar_pct / section_pct if section_pct > 0 else 0

        status = "✓ enriched" if enrichment > 1.2 else ""
        print(
            f"{section:20s} {ar_count:>10d} {ar_pct:>9.1f}% {enrichment:>11.2f}x {status}"
        )

    # 3. Critical pattern: "dair ar" co-occurrence
    print("\n" + "=" * 80)
    print("3. CRITICAL PATTERN: 'dair ar' (there + preposition)")
    print("=" * 80)

    dair_ar_pattern = 0
    dair_ar_examples = []

    for inst in ar_instances:
        sentence = inst["full_sentence"]
        if "dair" in sentence:
            dair_ar_pattern += 1
            if len(dair_ar_examples) < 10:
                # Extract context around "ar"
                words = sentence.split()
                try:
                    ar_pos = words.index(inst["word"])
                    context = words[max(0, ar_pos - 3) : min(len(words), ar_pos + 4)]
                    dair_ar_examples.append(" ".join(context))
                except ValueError:
                    pass

    dair_ar_pct = (dair_ar_pattern / len(ar_instances)) * 100
    print(f"\nPattern 'dair...ar': {dair_ar_pattern} instances ({dair_ar_pct:.1f}%)")

    if dair_ar_pattern > 0:
        print(f"\nSample 'dair ar' contexts (testing: there AT ...):")
        for i, example in enumerate(dair_ar_examples, 1):
            # Translate known terms
            translated = example.replace("dair", "[THERE]").replace("air", "[SKY]")
            for term in ["ok", "qok", "ot", "qot"]:
                translated = re.sub(
                    rf"\b\w*{term}\w*\b", f"[{term.upper()}...]", translated
                )
            translated = translated.replace("ar", "[AT/IN?]")
            print(f"  {i}. {example}")
            print(f"     → {translated}")

    # 4. Position analysis (prepositions = pre-nominal)
    print("\n" + "=" * 80)
    print("4. POSITION ANALYSIS (Prepositions before nouns)")
    print("=" * 80)

    positions = {"phrase_initial": 0, "phrase_medial": 0, "phrase_final": 0}

    for inst in ar_instances:
        before = inst["context_before"].strip()
        after = inst["context_after"].strip()

        if not before or before == "":
            positions["phrase_initial"] += 1
        elif not after or after == "":
            positions["phrase_final"] += 1
        else:
            positions["phrase_medial"] += 1

    for pos, count in positions.items():
        pct = (count / len(ar_instances)) * 100
        marker = "✓ typical" if pos == "phrase_medial" and pct > 40 else ""
        print(f"  {pos:20s}: {count:4d} ({pct:5.1f}%) {marker}")

    # 5. Morphological behavior (should be LOW)
    print("\n" + "=" * 80)
    print("5. MORPHOLOGICAL BEHAVIOR (Prepositions <10%)")
    print("=" * 80)

    case_suffixes = ["ol", "al", "or", "ody", "eody"]
    verbal_suffixes = ["dy", "edy"]

    case_count = 0
    verbal_count = 0

    for inst in ar_instances:
        word = inst["word"]
        # Check if word has additional suffixes beyond "ar"
        if any(word.endswith(suf) for suf in case_suffixes):
            case_count += 1
        if any(word.endswith(suf) for suf in verbal_suffixes):
            verbal_count += 1

    case_pct = (case_count / len(ar_instances)) * 100
    verbal_pct = (verbal_count / len(ar_instances)) * 100

    print(
        f"\nAdditional case-marking: {case_count}/{len(ar_instances)} ({case_pct:.1f}%)"
    )
    print(f"Verbal marking: {verbal_count}/{len(ar_instances)} ({verbal_pct:.1f}%)")

    print(f"\nComparison:")
    print(f"  Expected for preposition: <10% morphology")
    print(f"  'ar' behavior: {case_pct:.1f}% case, {verbal_pct:.1f}% verbal", end="")

    if case_pct < 10 and verbal_pct < 10:
        print(" → ✓✓ PREPOSITION PATTERN!")
    else:
        print(" → ? Unclear")

    # 6. Co-occurrence with spatial terms
    print("\n" + "=" * 80)
    print("6. CO-OCCURRENCE WITH SPATIAL TERMS")
    print("=" * 80)

    spatial_terms = ["dair", "air", "okair", "otair", "qokair", "qotair", "sair"]

    with_spatial = 0
    spatial_examples = []

    for inst in ar_instances:
        sentence = inst["full_sentence"]
        if any(term in sentence for term in spatial_terms):
            with_spatial += 1
            if len(spatial_examples) < 8:
                spatial_examples.append((inst["locator"], sentence[:80]))

    with_spatial_pct = (with_spatial / len(ar_instances)) * 100
    print(
        f"\nCo-occurs with spatial terms: {with_spatial} instances ({with_spatial_pct:.1f}%)"
    )

    if with_spatial > 0:
        print(f"\nSample spatial contexts:")
        for i, (loc, sentence) in enumerate(spatial_examples, 1):
            print(f"  {i}. {loc}: {sentence}...")

    # 7. Sample translations
    print("\n" + "=" * 80)
    print("7. SAMPLE TRANSLATIONS (Testing ar = 'at/in')")
    print("=" * 80)

    # Get diverse samples
    samples_by_section = defaultdict(list)
    for inst in ar_instances:
        section = inst["section"]
        if len(samples_by_section[section]) < 4:
            samples_by_section[section].append(inst)

    print("\nIf ar = 'at/in', these should make spatial sense:")

    for section in ["astronomical", "herbal", "pharmaceutical"]:
        if section in samples_by_section:
            print(f"\n{section.upper()} section:")
            for i, inst in enumerate(samples_by_section[section], 1):
                sentence = inst["full_sentence"].split()[:12]

                # Simple translation
                translated = []
                for word in sentence:
                    if word == "ar" or word in ["ary", "arl"]:
                        translated.append("[AT/IN]")
                    elif "dair" in word:
                        translated.append("THERE")
                    elif word == "air" or word.endswith("air"):
                        if word == "air":
                            translated.append("SKY")
                        else:
                            root = word[:-3]
                            translated.append(f"{root.upper()}-SKY")
                    elif any(root in word for root in ["ok", "qok"]):
                        translated.append("OAK[...]")
                    elif any(root in word for root in ["ot", "qot"]):
                        translated.append("OAT[...]")
                    elif any(root in word for root in ["she", "shee"]):
                        translated.append("WATER[...]")
                    elif "cho" in word and "cheo" not in word:
                        translated.append("VESSEL[...]")
                    else:
                        translated.append("[?]")

                print(f"\n  {i}. {inst['locator']}")
                print(f"     Original: {' '.join(sentence)}")
                print(f"     If ar=AT: {' '.join(translated)}")

    # 8. VALIDATION SCORING
    print("\n" + "=" * 80)
    print("8. VALIDATION SCORING (12/12 possible)")
    print("=" * 80)

    score = 0
    criteria = []

    # Criterion 1: Low additional morphology (2 pts)
    if case_pct < 5 and verbal_pct < 5:
        score += 2
        criteria.append(
            (
                "Low morphology (<5%)",
                2,
                f"{case_pct:.1f}% case, {verbal_pct:.1f}% verbal ✓✓",
            )
        )
    elif case_pct < 10 and verbal_pct < 10:
        score += 1
        criteria.append(
            (
                "Low morphology (<10%)",
                1,
                f"{case_pct:.1f}% case, {verbal_pct:.1f}% verbal ✓",
            )
        )
    else:
        criteria.append(
            ("Low morphology", 0, f"{case_pct:.1f}% case, {verbal_pct:.1f}% verbal ✗")
        )

    # Criterion 2: High standalone rate (2 pts)
    standalone_pct = (standalone_ar / len(ar_instances)) * 100
    if standalone_pct > 80:
        score += 2
        criteria.append(("High standalone (>80%)", 2, f"{standalone_pct:.1f}% ✓✓"))
    elif standalone_pct > 60:
        score += 1
        criteria.append(("High standalone (>60%)", 1, f"{standalone_pct:.1f}% ✓"))
    else:
        criteria.append(("High standalone", 0, f"{standalone_pct:.1f}% ✗"))

    # Criterion 3: Co-occurs with "dair" (2 pts)
    if dair_ar_pct > 15:
        score += 2
        criteria.append(("Co-occurs with 'dair' (>15%)", 2, f"{dair_ar_pct:.1f}% ✓✓"))
    elif dair_ar_pct > 5:
        score += 1
        criteria.append(("Co-occurs with 'dair' (>5%)", 1, f"{dair_ar_pct:.1f}% ✓"))
    else:
        criteria.append(("Co-occurs with 'dair'", 0, f"{dair_ar_pct:.1f}% ✗"))

    # Criterion 4: Co-occurs with spatial terms (2 pts)
    if with_spatial_pct > 20:
        score += 2
        criteria.append(("Spatial context (>20%)", 2, f"{with_spatial_pct:.1f}% ✓✓"))
    elif with_spatial_pct > 10:
        score += 1
        criteria.append(("Spatial context (>10%)", 1, f"{with_spatial_pct:.1f}% ✓"))
    else:
        criteria.append(("Spatial context", 0, f"{with_spatial_pct:.1f}% ✗"))

    # Criterion 5: Position (2 pts - medial for prepositions)
    medial_pct = (positions["phrase_medial"] / len(ar_instances)) * 100
    if medial_pct > 50:
        score += 2
        criteria.append(("Medial position (>50%)", 2, f"{medial_pct:.1f}% ✓✓"))
    elif medial_pct > 40:
        score += 1
        criteria.append(("Medial position (>40%)", 1, f"{medial_pct:.1f}% ✓"))
    else:
        criteria.append(("Medial position", 0, f"{medial_pct:.1f}% ✗"))

    # Criterion 6: Contextual coherence (2 pts - manual)
    print("\nCriterion 6: Contextual coherence")
    print("Review sample translations above. Does ar='at/in' make spatial sense?")
    print("Especially: 'dair ar air' = 'there at sky' - does this work?")
    coherence_input = input("Score 0-2 points (0=no, 1=some, 2=yes): ").strip()
    try:
        coherence_score = int(coherence_input)
        coherence_score = max(0, min(2, coherence_score))
    except:
        coherence_score = 1

    score += coherence_score
    if coherence_score == 2:
        criteria.append(("Contextual coherence", 2, "Spatial translations work ✓✓"))
    elif coherence_score == 1:
        criteria.append(("Contextual coherence", 1, "Some work ✓"))
    else:
        criteria.append(("Contextual coherence", 0, "Unclear ✗"))

    # Print scoring summary
    print(f"\n{'Criterion':45s} {'Score':>7s} {'Evidence':s}")
    print("-" * 85)
    for criterion, pts, evidence in criteria:
        print(f"{criterion:45s} {pts:>3d}/2    {evidence}")

    print("-" * 85)
    print(f"{'TOTAL SCORE':45s} {score:>3d}/12")
    print("=" * 85)

    # Validation decision
    print("\nVALIDATION DECISION:")
    if score >= 10:
        print(f"✓✓✓ VALIDATED as preposition meaning 'at/in' ({score}/12)")
        print("Evidence strongly supports preposition hypothesis")
        print("SPATIAL SYSTEM COMPLETE: dair (there) + ar (at) + air (sky)")
    elif score >= 8:
        print(f"✓✓ LIKELY preposition ({score}/12)")
        print("Evidence supports hypothesis, needs minor confirmation")
    elif score >= 6:
        print(f"✓ POSSIBLE preposition ({score}/12)")
        print("Evidence partially supports, needs more investigation")
    else:
        print(f"✗ NOT VALIDATED as preposition ({score}/12)")
        print("May only exist as directional suffix -ar, not standalone preposition")

    return score


def main():
    filepath = (
        r"C:\Users\adria\Documents\manuscript\data\voynich\eva_transcription\ZL3b-n.txt"
    )

    print("Loading Voynich manuscript...")
    words_with_context = load_voynich_with_context(filepath)
    print(f"Loaded {len(words_with_context)} words\n")

    score = analyze_ar_preposition(words_with_context)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"""
Hypothesis: "ar" = "at/in" (locative preposition)

Final validation score: {score}/12

Key test: "dair ar air" = "there at sky"
          "dair ar chedar" = "there at [term]"

If VALIDATED (≥10/12):
  → Completes spatial-prepositional system
  → Add to function words: ar = [AT/IN]
  → Explains astronomical diagram labels
  → "there at sky" = perfect pointing formula

If NOT validated:
  → "ar" may only be directional case suffix (-ar)
  → No standalone prepositional use
  → Spatial system still works (dair + air sufficient)

Next steps:
  1. If validated: Update grammar reference with complete prepositional system
  2. Investigate "daiin" as demonstrative particle (2,302 instances!)
  3. Re-translate with all new terms
    """)


if __name__ == "__main__":
    main()
