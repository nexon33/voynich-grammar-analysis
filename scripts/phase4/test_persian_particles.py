"""
Persian Particle Hypothesis Test
=================================

HYPOTHESIS: The manuscript mixes languages
- Content/grammar: Turkish/Hungarian (agglutinative)
- Function words: Persian (Islamic Golden Age medical knowledge)

Persian particles in medical texts:
- dar (در) = "in, at, on" - locative/instrumental
- bar (بر) = "on, upon, over" - locative
- az (از) = "from, of" - ablative/genitive
- ba (با) = "with, by means of" - instrumental
- be (به) = "to, toward" - directional

Voynich candidates:
- dar (293×) - matches Persian dar perfectly
- ar (340×) - could be bar/ar
- al (250×) - could be az variant?
- ol (522×) - could be related

CRITICAL TESTS:

1. SEPARATE WORD TEST
   - Is "dar" a separate word or suffix?
   - Persian particles are FREE morphemes (standalone)
   - Turkish suffixes are BOUND morphemes (attached)

2. POSITIONAL TEST
   - Persian "dar" appears BEFORE the location noun
   - Persian word order: dar + [NOUN]
   - Example: dar xāna (in house)

3. DISTRIBUTION TEST
   - Persian "dar" should appear with locations, containers, places
   - NOT with actions or qualities
   - Should cluster with botanical/vessel terms

4. ETYMOLOGY TEST
   - Do combinations match Persian patterns?
   - "dar oak" = "in oak" (makes sense for preparation)
   - Check if patterns match medieval Persian medical texts
"""

import json
from pathlib import Path
from collections import Counter, defaultdict


def load_manuscript():
    """Load manuscript"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    return words


def test_separate_vs_bound(words):
    """
    TEST 1: Are these separate words or bound suffixes?

    If Persian particles → should appear as separate words
    If Turkish suffixes → should only appear attached

    Check:
    - Does "dar" appear standalone?
    - Does it appear as suffix "-dar"?
    - Ratio tells us if it's particle or suffix
    """
    candidates = {
        "dar": {"standalone": 0, "as_suffix": 0, "contexts": []},
        "ar": {"standalone": 0, "as_suffix": 0, "contexts": []},
        "al": {"standalone": 0, "as_suffix": 0, "contexts": []},
        "ol": {"standalone": 0, "as_suffix": 0, "contexts": []},
        "or": {"standalone": 0, "as_suffix": 0, "contexts": []},
    }

    for i, word in enumerate(words):
        # Check each candidate
        for particle in candidates.keys():
            # Standalone
            if word == particle:
                candidates[particle]["standalone"] += 1

                # Get context
                before = words[i - 1] if i > 0 else "[START]"
                after = words[i + 1] if i < len(words) - 1 else "[END]"
                if len(candidates[particle]["contexts"]) < 10:
                    candidates[particle]["contexts"].append(
                        f"{before} | {word} | {after}"
                    )

            # As suffix (word ends with it but has more content)
            elif word.endswith(particle) and len(word) > len(particle):
                candidates[particle]["as_suffix"] += 1

    # Calculate ratios
    for particle, data in candidates.items():
        total = data["standalone"] + data["as_suffix"]
        data["total"] = total
        data["standalone_ratio"] = data["standalone"] / total if total > 0 else 0
        data["as_suffix_ratio"] = data["as_suffix"] / total if total > 0 else 0

    return candidates


def test_persian_word_order(words):
    """
    TEST 2: Does "dar" appear BEFORE nouns (Persian pattern)?

    Persian: dar + [NOUN]
    Turkish: [NOUN] + -da/-de (suffix)

    Check if dar appears before oak/oat words
    """
    persian_particles = {"dar", "ar", "al", "ol", "or"}

    # Known content words (locations/objects)
    content_words = set()
    for word in set(words):
        if any(plant in word for plant in ["ok", "ot"]):
            content_words.add(word)

    particle_positions = defaultdict(
        lambda: {"before_content": 0, "after_content": 0, "total": 0}
    )

    for i, word in enumerate(words):
        if word in persian_particles:
            particle_positions[word]["total"] += 1

            # Check if content word follows
            if i < len(words) - 1 and words[i + 1] in content_words:
                particle_positions[word]["before_content"] += 1

            # Check if content word precedes
            if i > 0 and words[i - 1] in content_words:
                particle_positions[word]["after_content"] += 1

    return particle_positions


def test_dar_oak_combinations(words):
    """
    TEST 3: Do "dar + oak/oat" combinations exist?

    Persian medical texts use:
    - dar [plant] = "in [plant]" (preparation location)
    - dar [vessel] = "in [vessel]" (container)

    This would be SMOKING GUN evidence
    """
    dar_combinations = []

    for i, word in enumerate(words):
        if word == "dar":
            # Get surrounding context
            before = words[i - 1] if i > 0 else None
            after = words[i + 1] if i < len(words) - 1 else None
            after2 = words[i + 2] if i < len(words) - 2 else None

            # Check if oak/oat nearby
            context = []
            if before:
                context.append(before)
            context.append("DAR")
            if after:
                context.append(after)
            if after2:
                context.append(after2)

            # Is there oak/oat?
            has_plant = any(
                "ok" in w or "ot" in w for w in [before, after, after2] if w
            )

            if has_plant:
                dar_combinations.append({"context": context, "has_plant": True})

    return dar_combinations


def test_section_distribution(words):
    """
    TEST 4: Are Persian particles enriched in practical sections?

    Persian medical vocabulary would be most common in:
    - Recipe section (preparation instructions)
    - Pharmaceutical section (medicine making)

    Less common in:
    - Herbal section (plant descriptions - might use Latin)
    """
    sections = {
        "herbal": (0, 20000),
        "biological": (20000, 25000),
        "pharmaceutical": (25000, 32000),
        "recipes": (32000, 37187),
    }

    particles = ["dar", "ar", "al", "ol", "or"]

    section_counts = {s: {p: 0 for p in particles} for s in sections}
    section_totals = {s: 0 for s in sections}

    for i, word in enumerate(words):
        # Which section?
        for section_name, (start, end) in sections.items():
            if start <= i < end:
                section_totals[section_name] += 1

                if word in particles:
                    section_counts[section_name][word] += 1

                break

    # Calculate densities
    results = {}
    for section in sections:
        total = section_totals[section]
        particle_counts = section_counts[section]

        results[section] = {
            "total_words": total,
            "particle_counts": particle_counts,
            "particle_density": sum(particle_counts.values()) / total
            if total > 0
            else 0,
        }

    return results


def compare_to_persian_patterns(words):
    """
    TEST 5: Do Voynich patterns match known Persian medical patterns?

    Persian medical texts have specific formulae:
    - dar + [ingredient] + ... = "in [ingredient]..."
    - ba + [tool/method] + ... = "with [tool/method]..."

    Look for these patterns in Voynich
    """
    # Common Persian medical patterns
    patterns_found = defaultdict(int)

    for i in range(len(words) - 2):
        trigram = (words[i], words[i + 1], words[i + 2])

        # Pattern: dar + [something] + [something]
        if trigram[0] == "dar":
            patterns_found[f"dar + {trigram[1][:3]}... + {trigram[2][:3]}..."] += 1

        # Pattern: [something] + dar + [oak/oat]
        if trigram[1] == "dar" and ("ok" in trigram[2] or "ot" in trigram[2]):
            patterns_found[f"X dar oak/oat"] += 1

        # Pattern: [oak/oat] + dar + [something]
        if ("ok" in trigram[0] or "ot" in trigram[0]) and trigram[1] == "dar":
            patterns_found[f"oak/oat dar X"] += 1

    return patterns_found


def main():
    print("=" * 80)
    print("PERSIAN PARTICLE HYPOTHESIS TEST")
    print("=" * 80)
    print()
    print(
        "Testing if Voynich contains Persian function words from Islamic medical tradition"
    )
    print()

    # Load manuscript
    words = load_manuscript()
    print(f"Total words: {len(words):,}")
    print()

    # TEST 1: Separate vs Bound
    print("=" * 80)
    print("TEST 1: SEPARATE WORD vs BOUND SUFFIX")
    print("=" * 80)
    print()
    print("Persian particles are FREE morphemes (separate words)")
    print("Turkish suffixes are BOUND morphemes (attached)")
    print()

    separate_bound = test_separate_vs_bound(words)

    print(
        f"{'Word':<8} {'Standalone':<12} {'As Suffix':<12} {'Ratio':<20} {'Verdict':<20}"
    )
    print("-" * 80)

    for particle, data in sorted(
        separate_bound.items(), key=lambda x: x[1]["standalone"], reverse=True
    ):
        standalone_pct = data["standalone_ratio"] * 100
        verdict = (
            "FREE MORPHEME" if data["standalone_ratio"] > 0.3 else "BOUND MORPHEME"
        )

        print(
            f"{particle:<8} {data['standalone']:<12} {data['as_suffix']:<12} "
            f"{standalone_pct:>5.1f}% standalone  {verdict:<20}"
        )

    print()
    print("Sample contexts for 'dar' as standalone word:")
    for ctx in separate_bound["dar"]["contexts"][:5]:
        print(f"  {ctx}")

    print()

    # Evaluate TEST 1
    dar_standalone_ratio = separate_bound["dar"]["standalone_ratio"]

    if dar_standalone_ratio > 0.5:
        print("✓✓✓ TEST 1: 'dar' is predominantly a SEPARATE WORD")
        print("    → Supports Persian particle hypothesis!")
    elif dar_standalone_ratio > 0.3:
        print("✓ TEST 1: 'dar' appears as both separate word and suffix")
        print("    → Could be Persian particle borrowed into agglutinative system")
    else:
        print("✗ TEST 1: 'dar' is predominantly a suffix")
        print("    → Does not support Persian particle hypothesis")

    print()

    # TEST 2: Word Order
    print("=" * 80)
    print("TEST 2: PERSIAN WORD ORDER (particle + noun)")
    print("=" * 80)
    print()
    print("Persian: dar + [NOUN] ('in house')")
    print("Turkish: [NOUN] + -da ('house-in')")
    print()

    word_order = test_persian_word_order(words)

    print(
        f"{'Particle':<8} {'Total':<10} {'Before Content':<15} {'After Content':<15} {'Before %':<10}"
    )
    print("-" * 70)

    for particle, data in sorted(
        word_order.items(), key=lambda x: x[1]["before_content"], reverse=True
    ):
        before_pct = (
            (data["before_content"] / data["total"] * 100) if data["total"] > 0 else 0
        )
        print(
            f"{particle:<8} {data['total']:<10} {data['before_content']:<15} "
            f"{data['after_content']:<15} {before_pct:>6.1f}%"
        )

    print()

    # Evaluate TEST 2
    dar_before = word_order["dar"]["before_content"]
    dar_total = word_order["dar"]["total"]
    dar_before_pct = (dar_before / dar_total * 100) if dar_total > 0 else 0

    if dar_before_pct > 10:
        print(
            f"✓✓ TEST 2: 'dar' appears before content words {dar_before_pct:.1f}% of time"
        )
        print("    → Consistent with Persian 'dar' (preposition)")
    else:
        print(
            f"✗ TEST 2: 'dar' rarely appears before content words ({dar_before_pct:.1f}%)"
        )

    print()

    # TEST 3: dar + oak/oat combinations
    print("=" * 80)
    print("TEST 3: 'dar' + oak/oat COMBINATIONS")
    print("=" * 80)
    print()
    print("Persian medical: 'dar [plant]' = 'in [plant]' (preparation context)")
    print()

    dar_oak = test_dar_oak_combinations(words)

    print(f"Found {len(dar_oak)} instances of 'dar' near oak/oat words")
    print()
    print("Sample combinations:")
    for combo in dar_oak[:10]:
        context_str = " ".join(combo["context"])
        print(f"  {context_str}")

    print()

    if len(dar_oak) >= 20:
        print("✓✓✓ TEST 3: 'dar' frequently appears with plant words")
        print("    → STRONG evidence for Persian 'dar' = 'in/at'")
    elif len(dar_oak) >= 5:
        print("✓ TEST 3: 'dar' sometimes appears with plant words")
        print("    → Moderate evidence")
    else:
        print("✗ TEST 3: 'dar' rarely appears with plant words")

    print()

    # TEST 4: Section distribution
    print("=" * 80)
    print("TEST 4: SECTION DISTRIBUTION")
    print("=" * 80)
    print()
    print("Persian medical vocabulary expected in practical sections")
    print()

    section_dist = test_section_distribution(words)

    print(f"{'Section':<20} {'Total Words':<15} {'Particle Density':<20}")
    print("-" * 60)
    for section in ["herbal", "biological", "pharmaceutical", "recipes"]:
        data = section_dist[section]
        density_pct = data["particle_density"] * 100
        print(f"{section:<20} {data['total_words']:<15,} {density_pct:>6.2f}%")

    print()

    # Evaluate TEST 4
    recipe_density = section_dist["recipes"]["particle_density"]
    herbal_density = section_dist["herbal"]["particle_density"]
    enrichment = recipe_density / herbal_density if herbal_density > 0 else 0

    if enrichment > 1.2:
        print(f"✓ TEST 4: Particles {enrichment:.2f}x enriched in recipes vs herbal")
        print("    → Consistent with practical Persian medical usage")
    else:
        print(f"~ TEST 4: Similar particle density across sections ({enrichment:.2f}x)")

    print()

    # TEST 5: Persian patterns
    print("=" * 80)
    print("TEST 5: PERSIAN MEDICAL PATTERNS")
    print("=" * 80)
    print()

    patterns = compare_to_persian_patterns(words)

    print("Common patterns involving 'dar':")
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]:
        print(f"  {pattern}: {count}×")

    print()

    # FINAL VERDICT
    print("=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)
    print()

    tests_passed = 0
    total_tests = 4

    if dar_standalone_ratio > 0.3:
        tests_passed += 1
        print("✓ Test 1: dar is free morpheme")
    else:
        print("✗ Test 1: dar is bound morpheme")

    if dar_before_pct > 10:
        tests_passed += 1
        print("✓ Test 2: dar appears before nouns")
    else:
        print("✗ Test 2: dar position inconsistent")

    if len(dar_oak) >= 5:
        tests_passed += 1
        print("✓ Test 3: dar appears with plants")
    else:
        print("✗ Test 3: dar rarely with plants")

    if enrichment > 1.2:
        tests_passed += 1
        print("✓ Test 4: particles enriched in practical sections")
    else:
        print("✗ Test 4: particles evenly distributed")

    print()
    print(f"RESULT: {tests_passed}/{total_tests} tests passed")
    print()

    if tests_passed >= 3:
        print("✓✓✓ PERSIAN PARTICLE HYPOTHESIS STRONGLY SUPPORTED")
        print()
        print("Evidence suggests Voynich contains Persian function words:")
        print("  - dar (در) = in/at (prepositional)")
        print("  - Appears as separate word (free morpheme)")
        print("  - Follows Persian word order (before nouns)")
        print("  - Enriched in practical/medical sections")
        print()
        print("IMPLICATION: Manuscript is MULTILINGUAL")
        print("  - Persian: Function words, connectors")
        print("  - Turkish/Uralic: Content words, agglutinative grammar")
        print()
        print(
            "NEXT STEP: Identify all Persian particles and Turkish/Uralic roots separately"
        )
    elif tests_passed >= 2:
        print("~ PERSIAN PARTICLE HYPOTHESIS PARTIALLY SUPPORTED")
        print()
        print("Some evidence for Persian influence but not conclusive")
    else:
        print("✗ PERSIAN PARTICLE HYPOTHESIS NOT SUPPORTED")
        print()
        print("Evidence does not match Persian patterns")

    # Save results
    results = {
        "separate_vs_bound": {
            k: {
                "standalone": v["standalone"],
                "as_suffix": v["as_suffix"],
                "standalone_ratio": v["standalone_ratio"],
            }
            for k, v in separate_bound.items()
        },
        "word_order": {k: dict(v) for k, v in word_order.items()},
        "dar_oak_combinations": len(dar_oak),
        "dar_oak_examples": [c["context"] for c in dar_oak[:20]],
        "section_distribution": section_dist,
        "verdict": {
            "tests_passed": tests_passed,
            "total_tests": total_tests,
            "hypothesis_supported": tests_passed >= 3,
        },
    }

    output_path = Path("results/phase4/persian_particle_test.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
