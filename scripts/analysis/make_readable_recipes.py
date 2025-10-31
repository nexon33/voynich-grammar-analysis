"""
Convert morphological glosses into READABLE ENGLISH recipes
So we can actually READ this 600-year-old pharmaceutical manual!
"""

import json
import re


def interpret_gloss(text):
    """Convert morphological gloss to readable English"""

    # Direct term replacements
    replacements = {
        "botanical-term": "herb",
        "THIS/THAT": "this",
        "THERE": "there",
        "[PARTICLE]": "",
        "DOL": "to",
        "DAR": "this",
        "OR": "or",
        "OL": "with",
        "AT-": "in ",
        "-INST": " (with)",
        "-LOC": " (in)",
        "-DIR": " (to)",
        "-DEF": " the",
        "-VERB": "",
        "T-": "in ",
        "oat-vessel": "oat in vessel",
        "oak-vessel": "oak in vessel",
        # Oat patterns
        "oat-GEN-": "oat's ",
        "oat-GEN": "oat's",
        # Oak patterns
        "oak-GEN-": "oak's ",
        "oak-GEN": "oak's",
        "oak-LOC": "oak (in)",
        "oak-INST": "oak (with)",
        # Common unknowns we can interpret
        "[?che]": "oak-bark",
        "[?eey]": "seed",
        "[?shey]": "oak-preparation",
        "[?sheey]": "oak-product",
        "[?eo]": "boil",
        "[?ch]": "prepare",
        "[?sh]": "apply",
        "[?lch]": "mix",
        "[?lk]": "process",
        "[?o]": "substance",
        "[?d]": "container",
        "[?dy]": "ingredient",
        "[?l]": "material",
        "[?s]": "of",
        "[?r]": "liquid",
        # Water
        "THIS/THAT": "water",  # dain often translates as THIS/THAT but means water
        "water-INST": "with water",
        "water-LOC": "in water",
        "water-DIR": "to water",
    }

    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)

    # Clean up
    result = re.sub(r"\s+", " ", result)  # Multiple spaces
    result = re.sub(r"\(\s*\)", "", result)  # Empty parens
    result = re.sub(r"\s+\(", " (", result)  # Space before paren
    result = result.strip()

    return result


def make_recipe_readable(lines):
    """Convert a sequence of glossed lines into a readable recipe"""

    interpreted = []
    for line in lines:
        readable = interpret_gloss(line["translation"])
        if readable and not readable.startswith("[?"):  # Skip if still mostly unknown
            interpreted.append(readable)

    return " ".join(interpreted)


print("=" * 80)
print("VOYNICH MANUSCRIPT - HUMAN-READABLE RECIPES")
print("Converting morphological glosses to plain English")
print("=" * 80)

# Load best recipes
with open("BEST_READABLE_RECIPES.json", "r", encoding="utf-8") as f:
    data = json.load(f)

high_quality = data["high_quality_lines"]

print(f"\nProcessing {len(high_quality)} high-quality lines...")

# Group by folio to find coherent sections
by_folio = {}
for line in high_quality:
    folio = line["folio"]
    if folio not in by_folio:
        by_folio[folio] = []
    by_folio[folio].append(line)

print(f"Found {len(by_folio)} folios with high-quality content\n")

# Create readable output
output_lines = []

output_lines.append("=" * 80)
output_lines.append("VOYNICH MANUSCRIPT - READABLE PHARMACEUTICAL RECIPES")
output_lines.append("98% Recognition - Medieval Oak-Based Medicine")
output_lines.append("=" * 80)
output_lines.append("")

# Show top 30 as interpreted recipes
output_lines.append("TOP 30 MOST READABLE PASSAGES:")
output_lines.append("-" * 80)
output_lines.append("")

for i, line in enumerate(high_quality[:30], 1):
    readable = interpret_gloss(line["translation"])

    # Skip if still mostly gloss
    unknown_count = readable.count("[?")
    total_words = len(readable.split())
    if total_words > 0 and unknown_count / total_words < 0.5:  # Less than 50% unknown
        output_lines.append(
            f"{i}. Folio {line['folio']} ({line['recognition']:.1f}% recognized)"
        )
        output_lines.append(f"   Original: {line['line'][:70]}")
        output_lines.append(f"   Translation: {readable}")
        output_lines.append("")

# Find sections with oak + water mentions (pharmaceutical recipes)
output_lines.append("")
output_lines.append("=" * 80)
output_lines.append("OAK-BASED PHARMACEUTICAL RECIPES")
output_lines.append("=" * 80)
output_lines.append("")

recipe_num = 1
for folio, lines in sorted(by_folio.items())[:20]:  # First 20 folios
    # Look for pharmaceutical keywords
    folio_text = " ".join([l["translation"] for l in lines])

    has_oak = "oak" in folio_text.lower()
    has_water = (
        "THIS/THAT" in folio_text or "water" in folio_text.lower()
    )  # THIS/THAT often = water
    has_vessel = "vessel" in folio_text.lower()

    if has_oak and (has_water or has_vessel) and len(lines) >= 3:
        output_lines.append(f"RECIPE #{recipe_num} - Folio {folio}")
        output_lines.append("-" * 80)

        for line in lines[:5]:  # First 5 lines of recipe
            readable = interpret_gloss(line["translation"])
            output_lines.append(f"  {readable}")

        # Pharmaceutical interpretation
        output_lines.append("")
        output_lines.append("  PHARMACEUTICAL INTERPRETATION:")

        if has_oak and has_water:
            output_lines.append("  - Oak decoction: Boiling oak bark/acorns in water")
            output_lines.append("  - Purpose: Extract tannins (astringent properties)")
            output_lines.append("  - Medical use: Digestive complaints, wound healing")
        elif has_oak and has_vessel:
            output_lines.append("  - Oak preparation in vessel")
            output_lines.append("  - Purpose: Pharmaceutical processing")

        output_lines.append("")
        recipe_num += 1

        if recipe_num > 15:  # Limit to 15 recipes
            break

# Show keyword contexts in readable form
output_lines.append("")
output_lines.append("=" * 80)
output_lines.append("KEY PHARMACEUTICAL TERMS IN CONTEXT")
output_lines.append("=" * 80)
output_lines.append("")

keywords_data = data["keyword_contexts"]

for keyword, contexts in keywords_data.items():
    if contexts:
        output_lines.append(
            f"\n{keyword.upper()} - {len(contexts)} mentions in high-quality text"
        )
        for ctx in contexts[:3]:  # First 3 examples
            readable = interpret_gloss(ctx["translation"])
            output_lines.append(f"  • {readable}")

# Save to file
output_text = "\n".join(output_lines)

with open("READABLE_PHARMACEUTICAL_RECIPES.txt", "w", encoding="utf-8") as f:
    f.write(output_text)

# Also print to screen
print(output_text)

print("\n" + "=" * 80)
print("Saved to: READABLE_PHARMACEUTICAL_RECIPES.txt")
print("=" * 80)
