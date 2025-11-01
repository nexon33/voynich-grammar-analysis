"""
Manual assessments of 50 Phase 17 words
Based on linguistic plausibility and known vocabulary
"""

import json

# My assessments based on analysis
assessments = {
    # SINGLE-LETTER ROOTS (1-20) - MOSTLY WRONG
    1: (
        "WRONG",
        "qokaiin should be root='qok', suffix='aiin' (definite article). Single 'a' is artifact",
    ),
    2: ("WRONG", "Unknown single letter 'm', likely noise or abbreviation mark"),
    3: (
        "UNCERTAIN",
        "Single 'r' could be substance root (289 instances) but suspicious",
    ),
    4: ("WRONG", "odal should probably be root='od' or whole word, not single 'o'"),
    5: ("WRONG", "rain should be whole word or 'ra-in', not single 'r'"),
    6: ("WRONG", "qokeedy should be root='qok' + 'eedy', not stripping to single 'e'"),
    7: ("WRONG", "odaiin should be root='od' + 'aiin', not single 'o'"),
    8: ("WRONG", "otedol - looks like 'ote' (oat) + 'd' + 'ol', not single 'e'"),
    9: ("WRONG", "kedy could be whole word or 'ked-y', not single 'k'"),
    10: (
        "WRONG",
        "lal could be whole word or 'l' repetition, suspicious single letter",
    ),
    11: ("WRONG", "kain could be whole word or 'ka-in', not single 'k'"),
    12: (
        "UNCERTAIN",
        "qoky might be 'qok-y' (oak+copula compound) - your discovery! But single 'y' is suspicious",
    ),
    13: ("WRONG", "pol should be whole word or 'po-l', not single 'p'"),
    14: ("WRONG", "Duplicate of #2 - unknown single 'm'"),
    15: ("WRONG", "odaldy with 3 suffixes + single 'o' = clear over-stripping"),
    16: ("WRONG", "qokedy should be root='qok' + 'edy', not single 'e'"),
    17: (
        "UNCERTAIN",
        "qoty might be 'qot-y' (oat+copula) - similar to #12, suspicious",
    ),
    18: ("WRONG", "ral should be whole word or 'ra-l', not single 'r'"),
    19: ("WRONG", "oteedy should be root='ot' or 'ote' + 'edy', not single 'e'"),
    20: ("WRONG", "oteor should be root='ot' or 'ote' + 'or', not single 'e'"),
    # TWO-LETTER ROOTS (21-35) - MIXED
    21: (
        "CORRECT",
        "chor = ch (take/mix) + or (instrumental) - known verb root, correct",
    ),
    22: ("CORRECT", "lkeedy = lk (liquid) + eedy (VERB) - plausible, pattern OK"),
    23: ("CORRECT", "or = known conjunction 'and/or', standalone is correct"),
    24: (
        "UNCERTAIN",
        "qoedy = qo + edy - 'qo' is uncertain root, could be whole word 'qoedy'",
    ),
    25: (
        "WRONG",
        "otar looks like 'ot' (prefix/article) + 'ar' (at/in), not standalone 'ar'",
    ),
    26: ("CORRECT", "shedy = sh (mix/prepare) + edy (VERB) - known verb root, correct"),
    27: ("WRONG", "qotar same as #25 - looks like 'qot' + 'ar', not standalone 'ar'"),
    28: ("CORRECT", "shedy - duplicate of #26, correct"),
    29: (
        "CORRECT",
        "tchor = t + ch + or - 'ch' is known verb, pattern OK (t- might be prefix)",
    ),
    30: ("CORRECT", "ot = known prefix/article or oat variant, standalone OK"),
    31: (
        "CORRECT",
        "otol might be 'ot' + 'ol' but could also be standalone particle - uncertain but OK",
    ),
    32: ("CORRECT", "lkar = lk (liquid) + ar (directional) - plausible pattern"),
    33: (
        "UNCERTAIN",
        "olor could be 'ol' + 'or' or standalone - repetitive pattern suspicious",
    ),
    34: ("UNCERTAIN", "do = unknown, could be standalone particle or abbreviation"),
    35: ("CORRECT", "tchedy = t + ch + edy - 'ch' is known verb, pattern OK"),
    # THREE+ LETTER ROOTS (36-50) - MOSTLY CORRECT
    36: ("UNCERTAIN", "yhy = unknown, could be standalone word, unusual pattern"),
    37: ("CORRECT", "daiin = known demonstrative 'this/that', standalone correct"),
    38: ("CORRECT", "dchor = dch (compound/root) + or (instrumental) - pattern OK"),
    39: (
        "UNCERTAIN",
        "raraiiin = unusual root 'rarai', could be reduplicated form or error",
    ),
    40: ("UNCERTAIN", "kcho = might be 'k' + 'cho' (vessel) or standalone - unclear"),
    41: (
        "UNCERTAIN",
        "chldaiin = chl + d + aiin - 'chl' unknown, could be variant of 'ch' + 'l'",
    ),
    42: ("CORRECT", "kair = standalone word, no clear segmentation needed"),
    43: ("CORRECT", "okeeedy = oke (oak variant) + eedy (VERB) - good segmentation"),
    44: (
        "UNCERTAIN",
        "okeeody = okeeo might be compound or should be 'oke' + 'eo' + 'dy'",
    ),
    45: (
        "CORRECT",
        "tshy = standalone particle, no segmentation needed (similar to 'chy')",
    ),
    46: (
        "UNCERTAIN",
        "chokeey = might be compound 'cho' + 'keey' or standalone - unclear",
    ),
    47: ("CORRECT", "sheeo = standalone, possibly 'she' + 'eo' compound (water+boil)"),
    48: (
        "CORRECT",
        "okeey = known compound 'oak-GEN', your key discovery, standalone correct",
    ),
    49: ("CORRECT", "sheekchy = standalone complex word, no segmentation needed"),
    50: ("CORRECT", "sho = known root 'vessel', standalone correct"),
}

# Load the checklist
with open("MANUAL_PHASE17_VALIDATION_CHECKLIST.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Apply assessments
for item in data["validation_checklist"]:
    item_id = item["id"]
    if item_id in assessments:
        assessment, reason = assessments[item_id]
        item["assessment"] = assessment
        item["assessment_reason"] = reason

# Save updated checklist
with open("MANUAL_PHASE17_VALIDATION_CHECKLIST.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("=" * 80)
print("MANUAL ASSESSMENTS APPLIED")
print("=" * 80)
print()
print(f"Total words assessed: {len(assessments)}")
print()

# Count by assessment
correct = sum(1 for a, r in assessments.values() if a == "CORRECT")
wrong = sum(1 for a, r in assessments.values() if a == "WRONG")
uncertain = sum(1 for a, r in assessments.values() if a == "UNCERTAIN")

print(f"CORRECT:   {correct:2d} ({correct / len(assessments) * 100:.1f}%)")
print(f"WRONG:     {wrong:2d} ({wrong / len(assessments) * 100:.1f}%)")
print(f"UNCERTAIN: {uncertain:2d} ({uncertain / len(assessments) * 100:.1f}%)")
print()

# By root length
single_letter_ids = list(range(1, 21))
two_letter_ids = list(range(21, 36))
three_plus_ids = list(range(36, 51))


def count_wrong(ids):
    wrong_count = sum(
        1 for i in ids if i in assessments and assessments[i][0] == "WRONG"
    )
    uncertain_count = sum(
        1 for i in ids if i in assessments and assessments[i][0] == "UNCERTAIN"
    )
    return wrong_count, uncertain_count, len(ids)


single_wrong, single_uncertain, single_total = count_wrong(single_letter_ids)
two_wrong, two_uncertain, two_total = count_wrong(two_letter_ids)
three_wrong, three_uncertain, three_total = count_wrong(three_plus_ids)

print("BY ROOT LENGTH:")
print(
    f"Single-letter: {single_wrong} wrong, {single_uncertain} uncertain / {single_total} total"
)
print(
    f"               Error rate: {(single_wrong + single_uncertain * 0.5) / single_total * 100:.1f}%"
)
print(
    f"Two-letter:    {two_wrong} wrong, {two_uncertain} uncertain / {two_total} total"
)
print(
    f"               Error rate: {(two_wrong + two_uncertain * 0.5) / two_total * 100:.1f}%"
)
print(
    f"Three+ letter: {three_wrong} wrong, {three_uncertain} uncertain / {three_total} total"
)
print(
    f"               Error rate: {(three_wrong + three_uncertain * 0.5) / three_total * 100:.1f}%"
)
print()

print("=" * 80)
print("Updated checklist saved to: MANUAL_PHASE17_VALIDATION_CHECKLIST.json")
print("Now run: python scripts/validation/calculate_phase17_error_rate.py")
print("=" * 80)
