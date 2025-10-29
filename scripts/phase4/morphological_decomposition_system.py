"""
Morphological Decomposition System
===================================

Now that we've identified:
- 5 productive grammatical suffixes: -y, -r, -l, -dy, -ey
- 1 productive prefix: qok-
- ch/sh alternation pattern
- 8 grammatical morphemes (3 pronouns, 5 verbs)

Build a system to:
1. Decompose Voynich words into root + affixes
2. Track affix productivity (how many roots does each affix attach to?)
3. Identify root families (roots that share affixes)
4. Map affix co-occurrence patterns
5. Create a morphological ruleset

This will allow us to:
- Predict new word forms
- Identify roots vs grammatical markers
- Understand the agglutinative structure
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import re


def load_manuscript():
    """Load manuscript and get word frequencies"""
    transcription_path = Path(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt"
    )

    with open(transcription_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.lower().split()
    freq = Counter(words)

    return freq


def load_known_morphemes():
    """Load all identified morphemes from previous analyses"""

    # From affix analysis
    suffixes = {
        "y": {"productivity": 426, "type": "grammatical"},
        "l": {"productivity": 350, "type": "grammatical"},
        "dy": {"productivity": 255, "type": "grammatical"},
        "ey": {"productivity": 214, "type": "grammatical"},
        "r": {"productivity": 174, "type": "grammatical"},
        "n": {"productivity": 150, "type": "grammatical"},
        "ol": {"productivity": 100, "type": "case_or_article"},
        "al": {"productivity": 80, "type": "case_or_article"},
        "ar": {"productivity": 70, "type": "case_or_article"},
        "or": {"productivity": 60, "type": "case_or_article"},
        "in": {"productivity": 50, "type": "grammatical"},
        "ed": {"productivity": 40, "type": "grammatical"},
        "edy": {"productivity": 150, "type": "grammatical"},
        "eey": {"productivity": 120, "type": "grammatical"},
        "edy": {"productivity": 100, "type": "grammatical"},
    }

    prefixes = {
        "qok": {"productivity": 902, "type": "genitive"},
        "q": {"productivity": 500, "type": "grammatical"},
        "d": {"productivity": 300, "type": "grammatical"},
        "s": {"productivity": 200, "type": "grammatical"},
        "t": {"productivity": 150, "type": "grammatical"},
        "y": {"productivity": 100, "type": "grammatical"},
    }

    # Known roots
    roots = {
        "oke": {"meaning": "oak", "category": "plant"},
        "ot": {"meaning": "oat", "category": "plant"},
        "ote": {"meaning": "oat", "category": "plant"},
        "oko": {"meaning": "oak", "category": "plant"},
        "che": {"meaning": "unknown", "category": "verb_root"},
        "she": {"meaning": "unknown", "category": "verb_root"},
        "ke": {"meaning": "unknown", "category": "root"},
        "te": {"meaning": "unknown", "category": "root"},
        "cho": {"meaning": "unknown", "category": "root"},
        "sho": {"meaning": "unknown", "category": "root"},
        "da": {"meaning": "demonstrative_root", "category": "pronoun"},
        "a": {"meaning": "demonstrative_root", "category": "pronoun"},
        "sa": {"meaning": "demonstrative_root", "category": "pronoun"},
    }

    # Known alternations
    alternations = {
        "phonological": [
            ("ch", "sh"),  # Voicing alternation
            ("t", "d"),  # Voicing alternation
            ("k", "g"),  # Voicing alternation
            ("e", "o"),  # Vowel substitution (cipher)
            ("p", "b"),  # Voicing alternation
            ("f", "v"),  # Voicing alternation
        ]
    }

    return suffixes, prefixes, roots, alternations


def decompose_word(word, suffixes, prefixes, roots, max_iterations=3):
    """
    Recursively decompose a word into morphemes

    Returns: {
        'root': str,
        'prefixes': [str],
        'suffixes': [str],
        'decomposition': str,
        'confidence': float
    }
    """
    original_word = word
    result = {
        "root": None,
        "prefixes": [],
        "suffixes": [],
        "decomposition": None,
        "confidence": 0.0,
    }

    # Step 1: Strip prefixes
    for prefix in sorted(prefixes.keys(), key=len, reverse=True):
        if word.startswith(prefix) and len(word) > len(prefix):
            result["prefixes"].append(prefix)
            word = word[len(prefix) :]
            break

    # Step 2: Strip suffixes (may be multiple)
    iteration = 0
    while iteration < max_iterations:
        found_suffix = False
        for suffix in sorted(suffixes.keys(), key=len, reverse=True):
            if word.endswith(suffix) and len(word) > len(suffix):
                # Check if remaining part could be a root or another suffix
                remaining = word[: -len(suffix)]
                if len(remaining) >= 2:  # Minimum root length
                    result["suffixes"].insert(
                        0, suffix
                    )  # Add at beginning (we're working backwards)
                    word = remaining
                    found_suffix = True
                    break

        if not found_suffix:
            break
        iteration += 1

    # Step 3: What's left should be the root
    result["root"] = word

    # Step 4: Calculate confidence
    confidence = 0.0

    # Known root: +0.5
    if word in roots:
        confidence += 0.5
    elif len(word) >= 2:  # Plausible root length
        confidence += 0.2

    # Recognized affixes: +0.1 each
    confidence += len(result["prefixes"]) * 0.1
    confidence += len(result["suffixes"]) * 0.1

    # Successful decomposition (not just the word itself): +0.2
    if result["prefixes"] or result["suffixes"]:
        confidence += 0.2

    result["confidence"] = min(confidence, 1.0)

    # Step 5: Create decomposition string
    parts = []
    if result["prefixes"]:
        parts.append("-".join(result["prefixes"]) + "-")
    parts.append(result["root"])
    if result["suffixes"]:
        parts.append("-" + "-".join(result["suffixes"]))

    result["decomposition"] = "".join(parts)

    return result


def build_root_family_database(word_freq, suffixes, prefixes, roots):
    """
    Decompose all words and group by root family
    """
    root_families = defaultdict(
        lambda: {
            "root": None,
            "variants": [],
            "total_frequency": 0,
            "prefix_patterns": Counter(),
            "suffix_patterns": Counter(),
            "examples": [],
        }
    )

    print("Decomposing all words...")
    decompositions = {}

    for word, freq in word_freq.most_common():
        if freq < 3:  # Skip rare words
            continue

        decomp = decompose_word(word, suffixes, prefixes, roots)
        decompositions[word] = decomp

        if decomp["confidence"] >= 0.4:  # Only high-confidence decompositions
            root = decomp["root"]

            root_families[root]["root"] = root
            root_families[root]["variants"].append(word)
            root_families[root]["total_frequency"] += freq

            if decomp["prefixes"]:
                prefix_str = "-".join(decomp["prefixes"])
                root_families[root]["prefix_patterns"][prefix_str] += freq

            if decomp["suffixes"]:
                suffix_str = "-".join(decomp["suffixes"])
                root_families[root]["suffix_patterns"][suffix_str] += freq

            if len(root_families[root]["examples"]) < 10:
                root_families[root]["examples"].append(
                    {
                        "word": word,
                        "decomposition": decomp["decomposition"],
                        "frequency": freq,
                    }
                )

    return root_families, decompositions


def analyze_affix_cooccurrence(decompositions):
    """
    Analyze which affixes appear together
    """
    prefix_suffix_pairs = Counter()
    suffix_suffix_chains = Counter()

    for word, decomp in decompositions.items():
        if decomp["confidence"] < 0.4:
            continue

        # Prefix-suffix pairs
        if decomp["prefixes"] and decomp["suffixes"]:
            prefix = "-".join(decomp["prefixes"])
            suffix = "-".join(decomp["suffixes"])
            prefix_suffix_pairs[(prefix, suffix)] += 1

        # Suffix chains (multiple suffixes)
        if len(decomp["suffixes"]) > 1:
            chain = "-".join(decomp["suffixes"])
            suffix_suffix_chains[chain] += 1

    return prefix_suffix_pairs, suffix_suffix_chains


def identify_morphological_rules(root_families, decompositions):
    """
    Identify patterns that could be morphological rules
    """
    rules = []

    # Rule 1: Highly productive root + affix patterns
    for root, data in root_families.items():
        if len(data["variants"]) >= 10:  # Highly productive
            # Check for systematic affix patterns
            for suffix, count in data["suffix_patterns"].most_common(5):
                if count >= 5:
                    rules.append(
                        {
                            "type": "productive_suffixation",
                            "root": root,
                            "affix": suffix,
                            "frequency": count,
                            "pattern": f"{root} + {suffix} → {root}{suffix.replace('-', '')}",
                        }
                    )

    # Rule 2: Obligatory prefix patterns
    qok_prefixed = [d for w, d in decompositions.items() if "qok" in d["prefixes"]]
    if len(qok_prefixed) > 100:
        rules.append(
            {
                "type": "genitive_prefix",
                "pattern": "qok- + ROOT → genitive/possessive",
                "frequency": len(qok_prefixed),
                "examples": [d["decomposition"] for d in qok_prefixed[:5]],
            }
        )

    # Rule 3: Ch/sh alternation on same root
    ch_sh_alternations = []
    for root, data in root_families.items():
        ch_variants = [v for v in data["variants"] if v.startswith("ch")]
        sh_variants = [v for v in data["variants"] if v.startswith("sh")]

        if ch_variants and sh_variants:
            ch_sh_alternations.append(
                {"root": root, "ch_forms": ch_variants[:3], "sh_forms": sh_variants[:3]}
            )

    if ch_sh_alternations:
        rules.append(
            {
                "type": "ch_sh_alternation",
                "pattern": "ch- ↔ sh- (grammatical voicing)",
                "instances": len(ch_sh_alternations),
                "examples": ch_sh_alternations[:5],
            }
        )

    return rules


def main():
    print("=" * 80)
    print("MORPHOLOGICAL DECOMPOSITION SYSTEM")
    print("=" * 80)
    print()

    # Load data
    print("Loading manuscript...")
    word_freq = load_manuscript()
    print(f"Unique words: {len(word_freq):,}")
    print(f"Total tokens: {sum(word_freq.values()):,}")
    print()

    print("Loading known morphemes...")
    suffixes, prefixes, roots, alternations = load_known_morphemes()
    print(f"Known suffixes: {len(suffixes)}")
    print(f"Known prefixes: {len(prefixes)}")
    print(f"Known roots: {len(roots)}")
    print()

    # Build root family database
    print("=" * 80)
    print("BUILDING ROOT FAMILY DATABASE")
    print("=" * 80)
    print()

    root_families, decompositions = build_root_family_database(
        word_freq, suffixes, prefixes, roots
    )

    print(f"Identified {len(root_families)} root families")
    print()

    # Show top root families
    print("Top 20 Most Productive Roots:")
    print(f"{'Root':<15} {'Variants':<10} {'Frequency':<12} {'Top Suffixes':<30}")
    print("-" * 80)

    sorted_families = sorted(
        root_families.items(), key=lambda x: x[1]["total_frequency"], reverse=True
    )

    for root, data in sorted_families[:20]:
        top_suffix = data["suffix_patterns"].most_common(1)
        suffix_str = top_suffix[0][0] if top_suffix else "none"

        print(
            f"{root:<15} {len(data['variants']):<10} {data['total_frequency']:<12,} {suffix_str:<30}"
        )

    print()

    # Analyze affix co-occurrence
    print("=" * 80)
    print("AFFIX CO-OCCURRENCE PATTERNS")
    print("=" * 80)
    print()

    prefix_suffix_pairs, suffix_chains = analyze_affix_cooccurrence(decompositions)

    print("Top 10 Prefix-Suffix Combinations:")
    for (prefix, suffix), count in prefix_suffix_pairs.most_common(10):
        print(f"  {prefix} + ROOT + {suffix}: {count} instances")

    print()
    print("Top 10 Suffix Chains (multiple suffixes):")
    for chain, count in suffix_chains.most_common(10):
        print(f"  -{chain}: {count} instances")

    print()

    # Identify morphological rules
    print("=" * 80)
    print("MORPHOLOGICAL RULES")
    print("=" * 80)
    print()

    rules = identify_morphological_rules(root_families, decompositions)

    for i, rule in enumerate(rules, 1):
        print(f"Rule {i}: {rule['type']}")
        print(f"  Pattern: {rule['pattern']}")
        if "frequency" in rule:
            print(f"  Frequency: {rule['frequency']}")
        if "examples" in rule:
            print(f"  Examples: {', '.join(str(e) for e in rule['examples'][:3])}")
        print()

    # Save results
    output = {
        "root_families": {
            root: {
                "variants": data["variants"],
                "total_frequency": data["total_frequency"],
                "prefix_patterns": dict(data["prefix_patterns"]),
                "suffix_patterns": dict(data["suffix_patterns"]),
                "examples": data["examples"],
            }
            for root, data in sorted_families[:100]  # Top 100 roots
        },
        "decompositions": {
            word: decomp
            for word, decomp in list(decompositions.items())[:500]  # Top 500 words
        },
        "affix_patterns": {
            "prefix_suffix_pairs": [
                {"prefix": p, "suffix": s, "count": c}
                for (p, s), c in prefix_suffix_pairs.most_common(50)
            ],
            "suffix_chains": [
                {"chain": chain, "count": c}
                for chain, c in suffix_chains.most_common(50)
            ],
        },
        "morphological_rules": rules,
        "statistics": {
            "total_roots": len(root_families),
            "total_decompositions": len(
                [d for d in decompositions.values() if d["confidence"] >= 0.4]
            ),
            "avg_suffixes_per_word": sum(
                len(d["suffixes"]) for d in decompositions.values()
            )
            / len(decompositions),
            "avg_prefixes_per_word": sum(
                len(d["prefixes"]) for d in decompositions.values()
            )
            / len(decompositions),
        },
    }

    output_path = Path("results/phase4/morphological_decomposition.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_path}")
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Root families identified: {len(root_families)}")
    print(
        f"High-confidence decompositions: {output['statistics']['total_decompositions']}"
    )
    print(f"Morphological rules: {len(rules)}")
    print(f"Avg suffixes per word: {output['statistics']['avg_suffixes_per_word']:.2f}")
    print(f"Avg prefixes per word: {output['statistics']['avg_prefixes_per_word']:.2f}")


if __name__ == "__main__":
    main()
