#!/usr/bin/env python3
"""
Simple investigation: Are [?a], [?y], [?k] prefixes or suffixes?

Check if they appear at word boundaries or internal to compounds.
"""

import json
import re
from collections import Counter


def load_translations():
    with open(
        "COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)
        return data["translations"]


def analyze_element(element, translations):
    """
    Analyze where element appears:
    - Standalone: [?x]
    - Prefix position: [?x]-something
    - Suffix position: something-[?x]
    - Internal: something-[?x]-something
    """

    standalone = 0
    prefix_position = 0
    suffix_position = 0
    internal_position = 0

    # What comes before/after
    before_context = Counter()
    after_context = Counter()

    # Regex to find element with context
    pattern = r"(\S+\s+)?\[" + re.escape(element) + r"\](\s+\S+)?"

    for trans in translations:
        text = trans["final_translation"]

        # Find all occurrences
        for match in re.finditer(r"\[" + re.escape(element) + r"\]", text):
            start = match.start()
            end = match.end()

            # Check what's immediately before and after (within same word)
            before_char = text[start - 1] if start > 0 else " "
            after_char = text[end] if end < len(text) else " "

            # Standalone: spaces on both sides
            if before_char in " \n\t" and after_char in " \n\t":
                standalone += 1
            # Prefix: space before, hyphen after
            elif before_char in " \n\t" and after_char == "-":
                prefix_position += 1
                # Get what comes after
                after_match = re.search(
                    r"\[" + re.escape(element) + r"\]-(\S+)", text[start:]
                )
                if after_match:
                    after_context[after_match.group(1)] += 1
            # Suffix: hyphen before, space after
            elif before_char == "-" and after_char in " \n\t":
                suffix_position += 1
                # Get what comes before
                before_match = re.search(
                    r"(\S+)-\[" + re.escape(element) + r"\]", text[:end]
                )
                if before_match:
                    words = before_match.group(0).split("-")
                    if len(words) >= 2:
                        before_context[words[-2]] += 1
            # Internal: hyphens on both sides
            elif before_char == "-" and after_char == "-":
                internal_position += 1

    total = standalone + prefix_position + suffix_position + internal_position

    return {
        "total": total,
        "standalone": standalone,
        "prefix": prefix_position,
        "suffix": suffix_position,
        "internal": internal_position,
        "before_context": before_context.most_common(10),
        "after_context": after_context.most_common(10),
    }


def main():
    print("=" * 70)
    print("SIMPLE AFFIXATION ANALYSIS: [?a], [?y], [?k]")
    print("=" * 70)
    print()

    translations = load_translations()

    for element in ["?a", "?y", "?k"]:
        print("=" * 70)
        print(f"[{element}]")
        print("=" * 70)

        results = analyze_element(element, translations)

        total = results["total"]
        if total == 0:
            print("No instances found!")
            print()
            continue

        standalone = results["standalone"]
        prefix = results["prefix"]
        suffix = results["suffix"]
        internal = results["internal"]

        print(f"\nTotal instances: {total}")
        print(f"\nPosition distribution:")
        print(
            f"  Standalone [{element}]:           {standalone:4d} ({standalone / total * 100:5.1f}%)"
        )
        print(
            f"  Prefix [{element}]-X:             {prefix:4d} ({prefix / total * 100:5.1f}%)"
        )
        print(
            f"  Suffix X-[{element}]:             {suffix:4d} ({suffix / total * 100:5.1f}%)"
        )
        print(
            f"  Internal X-[{element}]-Y:         {internal:4d} ({internal / total * 100:5.1f}%)"
        )

        # Classification
        print(f"\n{'=' * 70}")
        print("CLASSIFICATION:")

        prefix_pct = prefix / total * 100
        suffix_pct = suffix / total * 100
        internal_pct = internal / total * 100
        standalone_pct = standalone / total * 100

        if suffix_pct > 60:
            print(f"  → LIKELY SUFFIX ({suffix_pct:.1f}% in suffix position)")
            if results["before_context"]:
                print(f"\n  What comes before X-[{element}]:")
                for item, count in results["before_context"]:
                    print(f"    {item}-[{element}]: {count}×")
        elif prefix_pct > 60:
            print(f"  → LIKELY PREFIX ({prefix_pct:.1f}% in prefix position)")
            if results["after_context"]:
                print(f"\n  What comes after [{element}]-X:")
                for item, count in results["after_context"]:
                    print(f"    [{element}]-{item}: {count}×")
        elif internal_pct > 40:
            print(f"  → LIKELY INFIX/DERIVATIONAL ({internal_pct:.1f}% internal)")
        elif standalone_pct > 40:
            print(f"  → LIKELY ROOT ({standalone_pct:.1f}% standalone)")
        else:
            print(f"  → MIXED PATTERN")
            print(f"    - Standalone: {standalone_pct:.1f}%")
            print(f"    - Prefix: {prefix_pct:.1f}%")
            print(f"    - Suffix: {suffix_pct:.1f}%")
            print(f"    - Internal: {internal_pct:.1f}%")

        print()

    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    print("If any element is predominantly a SUFFIX or PREFIX,")
    print("it explains the low VERB suffix rates in batch analysis -")
    print("they themselves are affixes, not stems!")
    print()


if __name__ == "__main__":
    main()
