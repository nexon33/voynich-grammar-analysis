# 📋 MANUAL VALIDATION GUIDE - Phase 17 Root Extraction

**Status:** 50 words sampled and ready for manual review  
**File:** `MANUAL_PHASE17_VALIDATION_CHECKLIST.json`  
**Goal:** Determine if Phase 17's morphological analyzer is trustworthy  

---

## 🎯 QUICK START

### What You Need to Do

1. **Review the 50 words** printed above (or in the JSON file)
2. **For each word, assess if the root extraction makes sense**
3. **Edit the JSON file** to record your assessments
4. **Run the calculator script** to get the error rate

**Estimated time:** 30-60 minutes

---

## 📊 SAMPLE BREAKDOWN

Your 50-word sample includes:

| Root Length | Count | Why Sampled |
|-------------|-------|-------------|
| **Single-letter roots** | 20 | Most suspicious - likely false positives |
| **Two-letter roots** | 15 | Moderately suspicious |
| **Three+ letter roots** | 15 | Least suspicious - likely genuine |

**This is a BIASED sample** - we deliberately oversampled suspicious cases to stress-test Phase 17.

---

## 🔍 HOW TO ASSESS EACH WORD

### Assessment Criteria

For each word, ask yourself:

#### 1. **Does the root extraction make linguistic sense?**

**Example CORRECT:**
```
Word: "chor" → root="ch", suffix="or"
Assessment: CORRECT
Reason: "ch" is a known verb root (take/mix), "-or" is instrumental suffix
```

**Example WRONG:**
```
Word: "qokaiin" → root="a", suffix="iin"  
Assessment: WRONG
Reason: Strips "qok" prefix leaving single "a" - should be root="qok", suffix="aiin"
```

#### 2. **Is the root too short to be plausible?**

**Single-letter roots are HIGHLY SUSPICIOUS:**
```
Word: "rain" → root="r", suffix="ain"
Assessment: WRONG (probably)
Reason: Single "r" unlikely to be standalone root - probably over-stripped
```

**But some single letters might be real:**
```
Word: "qoty" → root="y"
Assessment: UNCERTAIN (or possibly CORRECT)
Reason: "y" might be copula "is" (your discovery!) - but needs verification
```

#### 3. **Could this be a whole word (no segmentation needed)?**

**Example of over-segmentation:**
```
Word: "daiin" → root="daiin", no suffixes
Assessment: CORRECT
Reason: Standalone demonstrative "this/that" - doesn't need segmentation
```

**Example of correct segmentation:**
```
Word: "shedy" → root="sh", suffix="edy"
Assessment: CORRECT
Reason: "sh" = mix/prepare, "edy" = VERB suffix - makes sense
```

#### 4. **Are the affixes correctly identified?**

**Example CORRECT:**
```
Word: "okeeedy" → root="oke", suffix="eedy"
Assessment: CORRECT
Reason: "oke" = oak variant, "eedy" = VERB suffix
```

**Example WRONG:**
```
Word: "odaldy" → root="o", suffixes="d-al-dy"
Assessment: WRONG
Reason: 3 suffixes + single-letter root = over-stripping
```

---

## 🎯 QUICK DECISION GUIDE

### For Single-Letter Roots (20 words)

**Most should be WRONG** unless:
- It's a known grammatical particle (y = copula?)
- It appears in high-frequency standalone contexts
- You have independent evidence it's real

**Examples from your sample:**

| Word | Root | Assessment Guidance |
|------|------|---------------------|
| `qokaiin` | **a** | **WRONG** - Should be root="qok", suffix="aiin" |
| `m` | **m** | **WRONG** - Unknown single letter, probably noise |
| `r` | **r** | **UNCERTAIN** - Could be substance, but suspicious |
| `qoky` | **y** | **UNCERTAIN** - Might be copula (your discovery), needs verification |
| `kedy` | **k** | **WRONG** - "kedy" might be whole word or "ked-y" |

**Rule of thumb:** If unsure about single-letter → mark UNCERTAIN (not CORRECT)

### For Two-Letter Roots (15 words)

**More plausible, but still check:**
- Does the root appear independently?
- Is it in your known vocabulary?
- Does the segmentation make sense?

**Examples:**

| Word | Root | Assessment Guidance |
|------|------|---------------------|
| `chor` | **ch** | **CORRECT** - Known verb "take/mix" + instrumental suffix |
| `lkeedy` | **lk** | **CORRECT/UNCERTAIN** - "lk" might be liquid, pattern looks OK |
| `qoedy` | **qo** | **UNCERTAIN** - "qo" unknown, might be whole word |
| `or` | **or** | **CORRECT** - Known conjunction "and/or" |

**Rule of thumb:** If it's in your known vocabulary → CORRECT

### For Three+ Letter Roots (15 words)

**Most should be CORRECT:**
- These are likely genuine roots
- Less chance of over-stripping
- Check if segmentation makes sense

**Examples:**

| Word | Root | Assessment Guidance |
|------|------|---------------------|
| `daiin` | **daiin** | **CORRECT** - Known demonstrative "this/that" |
| `okeey` | **okeey** | **CORRECT** - Known compound "oak-GEN" |
| `sho` | **sho** | **CORRECT** - Known root "vessel" |
| `kcho` | **kcho** | **UNCERTAIN** - Unknown, might be compound or whole word |

**Rule of thumb:** If ≥3 characters and in known vocabulary → CORRECT

---

## 📝 HOW TO EDIT THE JSON FILE

### Open the file:
```
MANUAL_PHASE17_VALIDATION_CHECKLIST.json
```

### Find each word entry:
```json
{
  "id": 1,
  "original": "qokaiin",
  "root": "a",
  "prefixes": [],
  "suffixes": ["iin"],
  "decomposition": "**a**-[iin]",
  "root_length": 1,
  "num_suffixes": 1,
  "num_prefixes": 0,
  "issues": ["! SINGLE-LETTER ROOT"],
  "assessment": null    ← CHANGE THIS
}
```

### Change `"assessment": null` to one of:
```json
"assessment": "CORRECT"    // Root extraction looks good
"assessment": "WRONG"      // Root extraction is clearly wrong  
"assessment": "UNCERTAIN"  // Hard to tell, needs more context
```

### Example edited entry:
```json
{
  "id": 1,
  "original": "qokaiin",
  "root": "a",
  "suffixes": ["iin"],
  "assessment": "WRONG"    ← FILLED IN
}
```

**Tip:** Search for `"assessment": null` to jump to next unassessed word

---

## 🧮 AFTER YOU FINISH

### Run the calculator:
```bash
python scripts/validation/calculate_phase17_error_rate.py
```

### It will show you:
- Total error rate
- Error rate by root length
- Examples of wrong extractions
- **RECOMMENDATION** (Trust / Filter / Rebuild)

### Decision Tree:

**If error rate <10%:**
- ✅ Phase 17 is MOSTLY TRUSTWORTHY
- Filter single-letter roots with <500 instances
- Recalculate semantic % (expect ~45-50%)

**If error rate 10-20%:**
- ⚠️ Phase 17 has ISSUES but is salvageable
- Remove ALL single-letter roots
- Use only 3+ character roots
- Recalculate semantic % (expect ~40-45%)

**If error rate >20%:**
- ❌ Phase 17 is UNRELIABLE
- Do NOT trust automatic root extraction
- Rebuild from scratch or manually validate each root

---

## 💡 HELPFUL TIPS

### When in doubt, mark UNCERTAIN (not CORRECT)

**Conservative is better:**
- UNCERTAIN = "I'm not sure"
- WRONG = "This is definitely broken"
- CORRECT = "I'm confident this is right"

**If you're unsure, don't mark it CORRECT** - mark UNCERTAIN and let the error rate calculator handle it (counts as 0.5 wrong).

### Cross-reference with your known vocabulary

**You've identified these as high-confidence:**
- qok, qot, ok (oak, oat)
- sho, cho (vessel)
- dain (water)
- ar (at/in)
- ch, sh (process verbs)
- or, ol (and/or)

**If Phase 17 extracted these correctly → CORRECT**  
**If Phase 17 messed these up → WRONG**

### Look for patterns in errors

**Common error patterns:**
1. **Over-stripping:** root="o", suffixes="d-al-dy" (too many suffixes)
2. **Under-segmentation:** root="okeey" (might be correct as whole word)
3. **Wrong boundary:** root="a" in "qokaiin" (should be "qok" + "aiin")

### Remember: This is a biased sample

**We OVERSAMPLED single-letter roots intentionally.**

**Expected error rates:**
- Single-letter roots: 60-80% wrong (NORMAL)
- Two-letter roots: 20-40% wrong
- Three+ letter roots: 5-15% wrong

**Overall error rate will be ~15-25%** due to biased sampling.

---

## 📊 WHAT TO EXPECT

### Predicted Results

**Based on the sample, I predict:**
- **Single-letter roots:** 15-18 out of 20 WRONG (~80% error rate)
- **Two-letter roots:** 4-6 out of 15 WRONG (~35% error rate)
- **Three+ letter roots:** 1-3 out of 15 WRONG (~15% error rate)

**Overall predicted error rate:** ~45-50% (due to biased sample)

**BUT:** This doesn't mean Phase 17 is 50% wrong overall!

**Adjusted for bias:**
- In real corpus: Single-letter roots = 16% of words
- Most errors are in single-letter roots
- If we remove single-letter roots, error rate drops to ~10-15%

**Likely outcome:** Phase 17 is salvageable with filtering

---

## 🎯 BOTTOM LINE

### This manual validation will tell you:

1. **Is Phase 17 fundamentally broken?** (>30% error rate on 3+ letter roots = YES)
2. **Are single-letter roots mostly false positives?** (>70% error rate = YES)
3. **Can we trust 2+ character roots?** (<20% error rate = YES)

### Based on results, you'll know:

**SCENARIO A: <15% overall error (after bias adjustment)**
- Trust Phase 17 for roots with:
  - ≥3 characters, OR
  - ≥500 instances (for shorter roots)
- Expected honest semantic %: ~45-50%

**SCENARIO B: 15-25% error**
- Trust Phase 17 for roots with:
  - ≥3 characters
  - >100 instances
- Expected honest semantic %: ~40-45%

**SCENARIO C: >25% error**
- Phase 17 unreliable
- Manual validation needed for each root
- Expected honest semantic %: ~35-40%

---

## ✅ YOU'RE READY

**Next step:** Review the 50 words above and fill in assessments in the JSON file.

**Take your time** - this is the foundation for everything that follows.

**Good luck!** 🎯
