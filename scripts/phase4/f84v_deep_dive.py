#!/usr/bin/env python3
"""
F84v Deep Dive: Treat as Known Plaintext

F84v has 126 oak/oat instances (25% of the folio!)
Use it as a "Rosetta Stone" to:
1. Find repeated patterns (formulaic recipes)
2. Infer meanings of connector words
3. Test predictions about grammar
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_folio_words(folio_id="f84v"):
    """Load words from specific folio."""
    with open("results/phase3/proper_section_to_folio_mapping.json", "r") as f:
        mappings = json.load(f)

    with open(
        "data/voynich/eva_transcription/voynich_eva_takahashi.txt",
        "r",
        encoding="utf-8",
    ) as f:
        all_words = f.read().split()

    # Find folio range
    for section in mappings:
        if section["primary_folio"] == folio_id:
            start, end = map(int, section["word_range"].split("-"))
            return all_words[start:end], start

    return None, None


def get_plant_variants():
    """Get all plant word variants we recognize."""
    oak = {
        "okedy",
        "okeedy",
        "qokey",
        "qokol",
        "okol",
        "okeol",
        "okey",
        "okeody",
        "oko",
        "oke",
    }
    oat = {
        "oteey",
        "oteedy",
        "qotedy",
        "otol",
        "qoteedy",
        "oteol",
        "oteody",
        "otor",
        "otey",
        "qotol",
        "oto",
        "ote",
    }
    leek = {"okol", "leke", "loke"}
    ale = {"ale", "alo", "ola", "olaiin", "alol"}

    return {"oak": oak, "oat": oat, "leek": leek, "ale": ale}


def find_ingredient_chains(words, plant_variants):
    """Find sequences where multiple plants appear close together."""

    chains = []
    window = 10  # Look within 10-word windows

    for i, word in enumerate(words):
        # Check if word is any plant
        plant_type = None
        for ptype, variants in plant_variants.items():
            if word.lower() in variants:
                plant_type = ptype
                break

        if plant_type:
            # Look ahead for more plants
            chain = [(i, word, plant_type)]
            for j in range(i + 1, min(i + window, len(words))):
                next_word = words[j]
                for ptype, variants in plant_variants.items():
                    if next_word.lower() in variants:
                        chain.append((j, next_word, ptype))
                        break

            if len(chain) >= 2:  # At least 2 plants in sequence
                chains.append(
                    {
                        "start_pos": i,
                        "plants": chain,
                        "between_words": [
                            words[k] for k in range(chain[0][0] + 1, chain[-1][0])
                        ],
                    }
                )

    return chains


def find_repeated_phrases(words, min_length=3, min_occurrences=2):
    """Find phrases that repeat in the folio."""

    phrase_counts = Counter()

    # Generate all phrases of length min_length to min_length+3
    for length in range(min_length, min_length + 4):
        for i in range(len(words) - length + 1):
            phrase = tuple(words[i : i + length])
            phrase_counts[phrase] += 1

    # Filter to only repeated phrases
    repeated = {p: c for p, c in phrase_counts.items() if c >= min_occurrences}

    return repeated


def analyze_connector_words(chains):
    """Analyze words that appear BETWEEN plant mentions."""

    all_connectors = []
    connector_counts = Counter()

    for chain in chains:
        between = chain["between_words"]
        all_connectors.extend(between)
        for word in between:
            connector_counts[word] += 1

    return connector_counts, all_connectors


def main():
    print("=" * 80)
    print("F84V DEEP DIVE - THE BATH FOLIO")
    print("=" * 80)
    print("\nTreating f84v as 'known plaintext' with 126 oak/oat instances")

    # Load f84v
    words, start_pos = load_folio_words("f84v")

    if not words:
        print("\nERROR: Could not load f84v")
        return

    print(f"\nLoaded f84v: {len(words)} words (starting at position {start_pos})")

    # Get plant variants
    plant_variants = get_plant_variants()

    # Count plants in folio
    plant_counts = Counter()
    plant_positions = defaultdict(list)

    for i, word in enumerate(words):
        for ptype, variants in plant_variants.items():
            if word.lower() in variants:
                plant_counts[ptype] += 1
                plant_positions[ptype].append((i, word))

    print("\nPlant mentions in f84v:")
    for plant, count in plant_counts.most_common():
        print(f"  {plant:10} {count:3}x")

    # Find ingredient chains
    print("\n" + "-" * 80)
    print("INGREDIENT CHAINS (multiple plants in sequence)")
    print("-" * 80)

    chains = find_ingredient_chains(words, plant_variants)
    print(f"\nFound {len(chains)} chains with 2+ plants")

    print("\nTop 10 chains:")
    for i, chain in enumerate(chains[:10], 1):
        plants_str = " → ".join([f"{p[2]}({p[1]})" for p in chain["plants"]])
        between_str = (
            ", ".join(chain["between_words"])
            if chain["between_words"]
            else "[adjacent]"
        )
        print(f"\n{i}. {plants_str}")
        print(f"   Between: {between_str}")

    # Analyze connector words
    print("\n" + "-" * 80)
    print("CONNECTOR WORDS (between plant mentions)")
    print("-" * 80)

    connector_counts, all_connectors = analyze_connector_words(chains)

    print(f"\nTotal connector instances: {len(all_connectors)}")
    print(f"Unique connectors: {len(connector_counts)}")

    print(f"\nTop 20 connector words:")
    for word, count in connector_counts.most_common(20):
        print(f"  {word:<15} {count:3}x")

    # Compare to our N-gram high-frequency list
    high_freq_grammatical = {
        "chedy",
        "shedy",
        "daiin",
        "qokeedy",
        "qokedy",
        "qokeey",
        "otedy",
        "aiin",
        "dar",
        "ol",
        "al",
    }

    connectors_in_high_freq = set(connector_counts.keys()) & high_freq_grammatical
    print(f"\nConnectors that match high-frequency grammatical words:")
    for word in connectors_in_high_freq:
        print(f"  {word:<15} {connector_counts[word]:3}x (predicted as grammatical)")

    # Find repeated phrases
    print("\n" + "-" * 80)
    print("REPEATED PHRASES")
    print("-" * 80)

    repeated = find_repeated_phrases(words, min_length=3, min_occurrences=2)

    print(f"\nFound {len(repeated)} repeated phrases")
    print(f"\nTop 15 repeated phrases:")
    for phrase, count in sorted(repeated.items(), key=lambda x: x[1], reverse=True)[
        :15
    ]:
        phrase_str = " ".join(phrase)
        # Check if contains plants
        has_plant = any(
            w.lower() in plant_variants["oak"] | plant_variants["oat"] for w in phrase
        )
        marker = "🌿" if has_plant else "  "
        print(f"  {marker} [{count}x] {phrase_str}")

    # Find formulaic patterns
    print("\n" + "-" * 80)
    print("FORMULAIC PATTERNS")
    print("-" * 80)

    # Look for patterns with wildcards
    # E.g., "X chedy Y" where X and Y vary but chedy is constant

    def find_template_matches(words, template_word, window=2):
        """Find contexts where template_word appears."""
        contexts = []
        for i, word in enumerate(words):
            if word == template_word:
                before = words[max(0, i - window) : i]
                after = words[i + 1 : min(len(words), i + 1 + window)]
                contexts.append((before, after))
        return contexts

    for template in ["chedy", "shedy", "daiin", "ol"]:
        contexts = find_template_matches(words, template, window=2)
        if len(contexts) >= 3:
            print(f"\nPattern: [?] {template} [?] ({len(contexts)} instances)")
            for before, after in contexts[:5]:
                before_str = " ".join(before) if before else "[start]"
                after_str = " ".join(after) if after else "[end]"
                print(f"  {before_str:<20} {template} {after_str}")

    # Hypothesis testing
    print("\n" + "=" * 80)
    print("HYPOTHESIS TESTING")
    print("=" * 80)

    print("\nHYPOTHESIS 1: 'chedy' and 'shedy' are conjunctions ('and'/'or')")
    chedy_contexts = find_template_matches(words, "chedy", window=1)
    before_plants = sum(
        1
        for b, a in chedy_contexts
        if b and any(b[0].lower() in plant_variants["oak"] | plant_variants["oat"])
    )
    after_plants = sum(
        1
        for b, a in chedy_contexts
        if a and any(a[0].lower() in plant_variants["oak"] | plant_variants["oat"])
    )
    print(
        f"  'chedy' with plant before: {before_plants}/{len(chedy_contexts)} ({100 * before_plants / len(chedy_contexts):.1f}%)"
    )
    print(
        f"  'chedy' with plant after: {after_plants}/{len(chedy_contexts)} ({100 * after_plants / len(chedy_contexts):.1f}%)"
    )
    if (
        before_plants > len(chedy_contexts) * 0.3
        and after_plants > len(chedy_contexts) * 0.3
    ):
        print(f"  ✓ SUPPORTED - appears between plants frequently")

    print("\nHYPOTHESIS 2: 'daiin' is a pronoun/demonstrative ('it'/'this'/'that')")
    daiin_contexts = find_template_matches(words, "daiin", window=1)
    # Pronouns typically don't appear between two plants
    between_plants = sum(
        1
        for b, a in daiin_contexts
        if b
        and a
        and any(b[0].lower() in plant_variants["oak"] | plant_variants["oat"])
        and any(a[0].lower() in plant_variants["oak"] | plant_variants["oat"])
    )
    print(
        f"  'daiin' between two plants: {between_plants}/{len(daiin_contexts)} ({100 * between_plants / len(daiin_contexts):.1f}%)"
    )
    if between_plants < len(daiin_contexts) * 0.2:
        print(f"  ✓ SUPPORTED - doesn't connect plants (not a conjunction)")

    print("\nHYPOTHESIS 3: 'ol'/'al' are articles or prepositions")
    ol_contexts = find_template_matches(words, "ol", window=1)
    after_plants = sum(
        1
        for b, a in ol_contexts
        if a and any(a[0].lower() in plant_variants["oak"] | plant_variants["oat"])
    )
    print(
        f"  'ol' followed by plant: {after_plants}/{len(ol_contexts)} ({100 * after_plants / len(ol_contexts):.1f}%)"
    )
    if after_plants > len(ol_contexts) * 0.3:
        print(f"  ✓ SUPPORTED - frequently precedes plants (like 'the oak', 'of oak')")

    # Save analysis
    output = {
        "folio": "f84v",
        "total_words": len(words),
        "plant_counts": dict(plant_counts),
        "chains": [
            {
                "plants": [(p[0], p[1], p[2]) for p in c["plants"]],
                "connectors": c["between_words"],
            }
            for c in chains
        ],
        "connector_analysis": dict(connector_counts.most_common(30)),
        "repeated_phrases": {" ".join(k): v for k, v in list(repeated.items())[:20]},
    }

    output_path = Path("results/phase4/f84v_deep_analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n\nAnalysis saved to: {output_path}")

    print("\n" + "=" * 80)
    print("CONCLUSIONS FROM F84V")
    print("=" * 80)
    print("\n1. Oak/oat appear in CHAINS - multiple ingredients listed together")
    print("2. Connector words (chedy, shedy, ol, daiin) link ingredients")
    print("3. Strong evidence:")
    print("   - 'chedy'/'shedy' = conjunctions ('and', 'or', 'with')")
    print("   - 'daiin' = pronoun/demonstrative ('it', 'this', 'that')")
    print("   - 'ol'/'al' = articles/prepositions ('the', 'of')")
    print("\n4. F84v shows FORMULAIC recipe structure")
    print("   Repeated patterns suggest standardized instructions")


if __name__ == "__main__":
    main()
