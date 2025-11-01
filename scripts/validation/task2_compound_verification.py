"""
TASK 2: COMPOUND PATTERN VERIFICATION

Verify claimed productive morphology patterns:
- Type 1: NOUN-COPULA (oky, aly)
- Type 2: VERB-VERB (sheo, eeo)
- Type 3: NOUN-VERB (kch, okch, dch, pch, opch)
- Type 4: NOUN-GEN (okeey, keey)

Goal: Verify ≥85% of instances fit claimed pattern
"""

import json
from collections import Counter, defaultdict

print("=" * 80)
print("TASK 2: COMPOUND PATTERN VERIFICATION")
print("=" * 80)
print()

# Load data
print("Loading Phase 17 data...")
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data.get("translations", [])
print(f"✓ Loaded {len(translations)} sentences")
print()

# Compounds to verify
COMPOUNDS = {
    "TYPE1_N_COPULA": ["oky", "aly"],
    "TYPE2_V_V": ["sheo", "eeo"],
    "TYPE3_N_V": ["kch", "okch", "dch", "pch", "opch"],
    "TYPE4_N_GEN": ["okeey", "keey"],
}


def extract_context(sentence_words, target_index, window=3):
    """Extract words before and after target"""
    before = []
    after = []

    for i in range(max(0, target_index - window), target_index):
        before.append(sentence_words[i].get("original", ""))

    for i in range(
        target_index + 1, min(len(sentence_words), target_index + window + 1)
    ):
        after.append(sentence_words[i].get("original", ""))

    return before, after


def analyze_compound(root_name, translations, compound_type):
    """Analyze all instances of a compound"""
    instances = []

    for sent_idx, sentence in enumerate(translations):
        words = sentence.get("words", [])
        for word_idx, word_data in enumerate(words):
            morphology = word_data.get("morphology", {})
            root = morphology.get("root", "")

            if root == root_name:
                before, after = extract_context(words, word_idx)

                instance = {
                    "sentence_idx": sent_idx,
                    "word_idx": word_idx,
                    "original": word_data.get("original", ""),
                    "root": root,
                    "suffixes": morphology.get("suffixes", []),
                    "standalone": len(morphology.get("suffixes", [])) == 0,
                    "before": before,
                    "after": after,
                }
                instances.append(instance)

    return instances


def verify_n_copula_pattern(instances):
    """
    Verify NOUN-COPULA pattern:
    - Should appear standalone (96%+) or with minimal suffixation
    - Context: appears between nouns or after nouns
    """
    total = len(instances)
    standalone_count = sum(1 for inst in instances if inst["standalone"])
    standalone_rate = standalone_count / total if total > 0 else 0

    # Expected: >90% standalone for copula
    pattern_fits = standalone_rate >= 0.85

    return {
        "total_instances": total,
        "standalone_count": standalone_count,
        "standalone_rate": standalone_rate,
        "expected_standalone": ">85%",
        "pattern_fits": pattern_fits,
        "consistency_rate": standalone_rate if pattern_fits else 0,
    }


def verify_v_v_pattern(instances):
    """
    Verify VERB-VERB pattern:
    - Should show verbal behavior (takes verb suffixes)
    - Or appears standalone in recipe contexts
    """
    total = len(instances)
    verb_suffix_count = 0
    standalone_count = 0

    for inst in instances:
        suffixes = inst["suffixes"]
        if any(vs in s for s in suffixes for vs in ["dy", "edy", "ody"]):
            verb_suffix_count += 1
        elif len(suffixes) == 0:
            standalone_count += 1

    verbal_rate = (verb_suffix_count + standalone_count) / total if total > 0 else 0

    # Expected: >50% verbal behavior for V-V compounds
    pattern_fits = verbal_rate >= 0.50

    return {
        "total_instances": total,
        "verb_suffix_count": verb_suffix_count,
        "standalone_count": standalone_count,
        "verbal_rate": verbal_rate,
        "expected_verbal": ">50%",
        "pattern_fits": pattern_fits,
        "consistency_rate": verbal_rate if pattern_fits else 0,
    }


def verify_n_v_pattern(instances):
    """
    Verify NOUN-VERB pattern:
    - Should show verbal behavior (takes verb suffixes)
    - Expected: >40% verbal suffixation
    """
    total = len(instances)
    verb_suffix_count = 0

    for inst in instances:
        suffixes = inst["suffixes"]
        if any(vs in s for s in suffixes for vs in ["dy", "edy", "ody"]):
            verb_suffix_count += 1

    verbal_rate = verb_suffix_count / total if total > 0 else 0

    # Expected: >40% verbal for N-V compounds
    pattern_fits = verbal_rate >= 0.40

    return {
        "total_instances": total,
        "verb_suffix_count": verb_suffix_count,
        "verbal_rate": verbal_rate,
        "expected_verbal": ">40%",
        "pattern_fits": pattern_fits,
        "consistency_rate": verbal_rate if pattern_fits else 0,
    }


def verify_n_gen_pattern(instances):
    """
    Verify NOUN-GEN pattern:
    - Should appear standalone (genitive particle behavior)
    - Expected: >70% standalone
    """
    total = len(instances)
    standalone_count = sum(1 for inst in instances if inst["standalone"])
    standalone_rate = standalone_count / total if total > 0 else 0

    # Expected: >70% standalone for GEN particle
    pattern_fits = standalone_rate >= 0.70

    return {
        "total_instances": total,
        "standalone_count": standalone_count,
        "standalone_rate": standalone_rate,
        "expected_standalone": ">70%",
        "pattern_fits": pattern_fits,
        "consistency_rate": standalone_rate if pattern_fits else 0,
    }


# Verification functions by type
VERIFIERS = {
    "TYPE1_N_COPULA": verify_n_copula_pattern,
    "TYPE2_V_V": verify_v_v_pattern,
    "TYPE3_N_V": verify_n_v_pattern,
    "TYPE4_N_GEN": verify_n_gen_pattern,
}

# Run verification
results = {}
all_consistency_rates = []

for compound_type, roots in COMPOUNDS.items():
    print(f"{'=' * 80}")
    print(f"Verifying {compound_type}: {', '.join(roots)}")
    print(f"{'=' * 80}")
    print()

    type_results = {}

    for root in roots:
        print(f"Analyzing [{root}]...")
        instances = analyze_compound(root, translations, compound_type)

        if len(instances) == 0:
            print(f"  ⚠ No instances found!")
            continue

        # Verify pattern
        verifier = VERIFIERS[compound_type]
        verification = verifier(instances)

        # Store results
        type_results[root] = {
            "instances": instances[:10],  # Store first 10 for inspection
            "verification": verification,
        }

        # Print results
        pattern_status = "✓ FITS" if verification["pattern_fits"] else "✗ FAILS"
        consistency = verification["consistency_rate"] * 100

        print(f"  Total instances: {verification['total_instances']}")
        print(f"  Pattern consistency: {consistency:.1f}%")
        print(f"  Status: {pattern_status}")

        all_consistency_rates.append(verification["consistency_rate"])

        # Sample contexts
        if instances:
            print(f"  Sample contexts:")
            for i, inst in enumerate(instances[:3], 1):
                before_str = " ".join(inst["before"][-2:])
                after_str = " ".join(inst["after"][:2])
                print(f"    {i}. ...{before_str} [{inst['original']}] {after_str}...")

        print()

    results[compound_type] = type_results

# Overall summary
print("=" * 80)
print("COMPOUND VERIFICATION SUMMARY")
print("=" * 80)
print()

total_compounds = sum(len(type_res) for type_res in results.values())
passing_compounds = sum(
    1
    for type_res in results.values()
    for root_res in type_res.values()
    if root_res["verification"]["pattern_fits"]
)

overall_consistency = (
    sum(all_consistency_rates) / len(all_consistency_rates)
    if all_consistency_rates
    else 0
)

print(f"Total compounds tested: {total_compounds}")
print(f"Compounds passing pattern test: {passing_compounds}")
print(f"Pass rate: {passing_compounds / total_compounds * 100:.1f}%")
print(f"Average consistency: {overall_consistency * 100:.1f}%")
print()

# Determine result
if passing_compounds / total_compounds >= 0.85 and overall_consistency >= 0.85:
    task2_result = "✓ PASS"
    task2_status = "STRONG - 85%+ compounds fit patterns"
elif passing_compounds / total_compounds >= 0.75 and overall_consistency >= 0.75:
    task2_result = "⚠ MODERATE"
    task2_status = "75-84% consistency - some issues"
else:
    task2_result = "✗ FAIL"
    task2_status = "<75% consistency - patterns questionable"

print(f"Task 2 Result: {task2_result}")
print(f"Status: {task2_status}")
print()

# Save results
output = {
    "summary": {
        "total_compounds": total_compounds,
        "passing_compounds": passing_compounds,
        "pass_rate": passing_compounds / total_compounds if total_compounds > 0 else 0,
        "average_consistency": overall_consistency,
        "result": task2_result,
        "status": task2_status,
    },
    "by_type": {},
}

for compound_type, type_results in results.items():
    output["by_type"][compound_type] = {}
    for root, root_data in type_results.items():
        output["by_type"][compound_type][root] = {
            "verification": root_data["verification"],
            "sample_contexts": [
                {
                    "original": inst["original"],
                    "before": inst["before"],
                    "after": inst["after"],
                    "standalone": inst["standalone"],
                }
                for inst in root_data["instances"][:5]
            ],
        }

with open("VALIDATION_TASK2_COMPOUND_VERIFICATION.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✓ Detailed results saved to: VALIDATION_TASK2_COMPOUND_VERIFICATION.json")
print()
