"""
Extract the BEST TRANSLATED recipes from Phase 17
Show what we can actually READ at 98%+ recognition
"""

import json

print("=" * 80)
print("VOYNICH MANUSCRIPT - BEST READABLE RECIPES")
print("Extracting highest-recognition passages from complete translation")
print("=" * 80)

# Load Phase 17 translation
with open("COMPLETE_MANUSCRIPT_TRANSLATION_PHASE17.json", "r", encoding="utf-8") as f:
    data = json.load(f)

translations = data["translations"]

# Filter for high-recognition lines (>70%)
print("\nFinding best-recognized passages...")

high_quality = []
for trans in translations:
    stats = trans.get("statistics", {})
    recognition = stats.get("recognition_rate", 0)

    if recognition >= 70.0:
        high_quality.append(
            {
                "folio": trans["folio"],
                "line": trans["original"],
                "translation": trans["final_translation"],
                "recognition": recognition,
                "word_count": len(trans["original"].split()),
            }
        )

print(f"Found {len(high_quality)} lines with >=70% recognition")
print(f"(Out of {len(translations)} total lines)")

# Sort by recognition
high_quality.sort(key=lambda x: x["recognition"], reverse=True)

# Show top 30
print(f"\n{'=' * 80}")
print("TOP 30 BEST-RECOGNIZED RECIPES")
print(f"{'=' * 80}\n")

for i, recipe in enumerate(high_quality[:30], 1):
    print(f"{i}. Folio {recipe['folio']} - {recipe['recognition']:.1f}% recognized")
    print(f"   Original: {recipe['line']}")
    print(f"   Translation: {recipe['translation']}")
    print()

# Group consecutive high-quality lines to find complete recipes
print(f"\n{'=' * 80}")
print("COMPLETE HIGH-QUALITY RECIPE SEQUENCES")
print(f"{'=' * 80}\n")

# Find sequences of 3+ consecutive high-recognition lines
sequences = []
current_seq = []
prev_folio = None

for trans in translations:
    stats = trans.get("statistics", {})
    recognition = stats.get("recognition_rate", 0)
    folio = trans["folio"]

    if recognition >= 65.0:  # Slightly lower threshold for sequences
        if folio == prev_folio or not current_seq:
            current_seq.append(
                {
                    "folio": folio,
                    "line": trans["original"],
                    "translation": trans["final_translation"],
                    "recognition": recognition,
                }
            )
        else:
            if len(current_seq) >= 3:
                sequences.append(current_seq)
            current_seq = [
                {
                    "folio": folio,
                    "line": trans["original"],
                    "translation": trans["final_translation"],
                    "recognition": recognition,
                }
            ]
    else:
        if len(current_seq) >= 3:
            sequences.append(current_seq)
        current_seq = []

    prev_folio = folio

# Add final sequence if any
if len(current_seq) >= 3:
    sequences.append(current_seq)

print(
    f"Found {len(sequences)} complete recipe sequences (3+ lines, ≥65% recognition)\n"
)

# Show first 5 complete sequences
for seq_num, seq in enumerate(sequences[:5], 1):
    avg_recog = sum(line["recognition"] for line in seq) / len(seq)
    print(f"RECIPE SEQUENCE #{seq_num}")
    print(f"Folio: {seq[0]['folio']}")
    print(f"Length: {len(seq)} lines")
    print(f"Average recognition: {avg_recog:.1f}%")
    print()

    for line_num, line in enumerate(seq, 1):
        print(f"  {line_num}. ({line['recognition']:.1f}%) {line['translation']}")
    print()
    print("-" * 80)
    print()

# Find lines with key pharmaceutical terms
print(f"\n{'=' * 80}")
print("PHARMACEUTICAL KEYWORDS IN CONTEXT")
print(f"{'=' * 80}\n")

keywords = {"oak": [], "water": [], "vessel": [], "oat": [], "boil": [], "acorn": []}

for trans in translations:
    translation = trans["final_translation"].lower()
    stats = trans.get("statistics", {})
    recognition = stats.get("recognition_rate", 0)

    if recognition >= 60:  # Only look at reasonably-recognized lines
        for keyword in keywords:
            if keyword in translation:
                keywords[keyword].append(
                    {
                        "folio": trans["folio"],
                        "translation": trans["final_translation"],
                        "recognition": recognition,
                    }
                )

for keyword, lines in keywords.items():
    print(f"\n{keyword.upper()} - {len(lines)} mentions")
    for line in lines[:5]:  # Show first 5
        print(f"  ({line['recognition']:.1f}%) {line['translation'][:70]}...")

# Save results
output = {
    "high_quality_lines": high_quality[:50],
    "recipe_sequences": sequences[:10],
    "keyword_contexts": {k: v[:10] for k, v in keywords.items()},
}

with open("BEST_READABLE_RECIPES.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Create readable text file
with open("BEST_READABLE_RECIPES.txt", "w", encoding="utf-8") as f:
    f.write("VOYNICH MANUSCRIPT - BEST READABLE RECIPES\n")
    f.write("=" * 80 + "\n")
    f.write(f"Extracted {len(high_quality)} high-quality lines (≥70% recognition)\n")
    f.write(f"Found {len(sequences)} complete recipe sequences\n")
    f.write("=" * 80 + "\n\n")

    f.write("TOP 20 BEST-RECOGNIZED LINES:\n")
    f.write("-" * 80 + "\n\n")
    for i, recipe in enumerate(high_quality[:20], 1):
        f.write(
            f"{i}. Folio {recipe['folio']} - {recipe['recognition']:.1f}% recognized\n"
        )
        f.write(f"   {recipe['translation']}\n\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("COMPLETE RECIPE SEQUENCES:\n")
    f.write("=" * 80 + "\n\n")

    for seq_num, seq in enumerate(sequences[:10], 1):
        avg_recog = sum(line["recognition"] for line in seq) / len(seq)
        f.write(
            f"\nRECIPE #{seq_num} (Folio {seq[0]['folio']}, {avg_recog:.1f}% avg)\n"
        )
        f.write("-" * 80 + "\n")
        for line_num, line in enumerate(seq, 1):
            f.write(f"{line_num}. {line['translation']}\n")
        f.write("\n")

print(f"\n{'=' * 80}")
print("Results saved to:")
print("  - BEST_READABLE_RECIPES.json")
print("  - BEST_READABLE_RECIPES.txt")
print(f"{'=' * 80}")
