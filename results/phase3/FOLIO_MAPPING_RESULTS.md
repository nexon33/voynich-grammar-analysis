# Folio Mapping Results: Critical Validation Step

## Summary: Section 4 Maps to Folios f19r-f22v

Our automated alignment has mapped the highest medical density section to specific manuscript folios.

---

## Section 4 (Highest Medical Density: 1.6%)

### Location in Manuscript:
**Folios: f19r, f19v, f20r, f20v, f21r, f21v, f22r, f22v**

### Medical Content Found:
- **8 medical terms** (highest density in manuscript)
- **"sor" (sore/wound)** - 2 occurrences
- **Body part terms** - 5 occurrences (ched, ere, erem, perer, terer)
- **Condition term** - 1 occurrence (chetel)

### Word Range:
Words 2000-2500 (Section 4)

### First Words:
"ol chy kchey kchor dal pcho daiin chopol shoiin daiin"

---

## What These Folios Should Show (PREDICTION):

Based on the medical content, we predict folios f19r-f22v contain:

1. **Wound-healing plants**, specifically one or more of:
   - Plantain (Plantago major/minor)
   - Betony (Betonica officinalis) 
   - Yarrow (Achillea millefolium)
   - Woundwort (Stachys)
   - Comfrey (Symphytum)

2. **Herbal illustrations** with:
   - Roots, stems, leaves, flowers
   - Text labels near medicinal parts
   - Typical medieval herbal format

---

## Alignment Caveat: 2.07% Similarity

**⚠ IMPORTANT LIMITATION:**

The Takahashi and ZL transcriptions showed only 2.07% similarity in the first 100 words, suggesting:

1. **Different page ordering** - transcriptions may sequence folios differently
2. **Different text extraction** - one may include/exclude certain sections
3. **Transcription variations** - different interpretations of unclear characters

**This means the folio mapping may not be accurate.**

### Alternative Approach Needed:

Instead of automatic alignment, we should:

1. **Manual search**: Search for "ol chy kchey kchor dal pcho" in the ZL transcription
2. **Direct mapping**: Find which folio actually contains this text
3. **Visual verification**: Check if that folio has wound-healing plants

---

## Other High-Density Sections Mapped:

| Section | Density | Folios | Medical Terms | Key Content |
|---------|---------|--------|---------------|-------------|
| 24 | 1.2% | f75r, f75v | 6 | sor + body parts |
| 51 | 1.2% | f105v, f106r | 6 | sor + conditions |
| 55 | 1.2% | f108r, f108v | 6 | sor + body parts |
| 60 | 1.2% | f112v, f113r | 6 | sor + body parts |

### Notable Pattern:

**Section 24 (f75r, f75v) and later sections** are in the **Cosmological/Stars section** of the manuscript, NOT the herbal section.

This is unexpected if our translation is correct. The cosmological section typically has:
- Circular diagrams
- Star/zodiac illustrations
- Astronomical symbols

**If Section 24 really is f75r-f75v, finding "sor" (sore) there would be puzzling.**

---

## Critical Questions to Answer:

### 1. Is the alignment correct?

**Test:** Manually search for Section 4's first words in ZL transcription
- Expected: Should find "ol chy kchey kchor dal pcho" on a specific folio
- Compare: Does automatic mapping match manual search?

### 2. What illustrations are actually on f19r-f22v?

**Test:** View these folios in Yale Beinecke scans
- Link: https://brbl-dl.library.yale.edu/vufind/Record/3519597
- Check: Are they herbal pages or something else?

### 3. Do the plants match wound-healing species?

**Test:** If f19r-f22v are herbal pages:
- Compare illustrations to known medieval herbals
- Check if they resemble plantain, betony, yarrow, etc.
- Look for identifying features (leaf shape, root structure)

### 4. Why is Section 24 in the cosmological section?

**Possible explanations:**
- Alignment is wrong (most likely)
- Medical annotations in astronomical sections (possible)
- Our translation is identifying false positives (concerning)

---

## Next Steps: Manual Verification

### Step 1: Search ZL Transcription

```python
# Create a script to:
# 1. Search for "ol chy kchey kchor dal pcho" in ZL file
# 2. Extract the folio marker for that line
# 3. Compare to automatic alignment result
```

### Step 2: View Actual Folios

Access Yale Beinecke and view:
- f19r through f22v (automatic mapping)
- Whatever folio manual search finds

### Step 3: Document What's Actually There

Record for each folio:
- Illustration type (herbal, cosmological, pharmaceutical, biological)
- Plant identification (if herbal)
- Any features matching our predicted wound-healing plants

### Step 4: Calculate Correlation

Compare all high-density sections:
- How many show expected illustrations?
- Is there statistical correlation?
- Or is the pattern random?

---

## Validation Criteria

### STRONG CONFIRMATION if:
✓ Section 4 → Herbal folio → Wound-healing plant identified
✓ Section 24 → Herbal folio (not cosmological) → Medical plant
✓ Multiple high-density sections → Consistent pattern

### WEAK/NO CONFIRMATION if:
✗ Section 4 → Non-herbal illustration
✗ Folios show random plants (not wound-related)
✗ No pattern between medical terms and illustration types

### REQUIRES RECONSIDERATION if:
⚠ Multiple high-density sections → Cosmological/Stars pages
⚠ Alignment is systematically wrong
⚠ No correlation between our terms and visual content

---

## Resources for Manual Verification

### Voynich Manuscript Scans:
- **Yale Beinecke**: https://brbl-dl.library.yale.edu/vufind/Record/3519597
- **Voynich.nu**: http://www.voynich.nu/folios.html
- **Jason Davies**: https://www.jasondavies.com/voynich/

### Transcription with Folios:
- **ZL file we downloaded**: `data/voynich/eva_transcription/ZL3b-n.txt`
- Can search directly in this file for text strings

### Medieval Herbal References:
- **British Library Sloane 1975**: https://www.bl.uk/manuscripts/FullDisplay.aspx?ref=Sloane_MS_1975
- **Medieval Plants Database**: http://medieval-plants.org/
- **Edith Sherwood's identifications**: http://www.edithsherwood.com/voynich_botanical_plants/

---

## Current Status

**Completed:**
- ✓ Downloaded ZL EVA transcription with folio markers
- ✓ Created automated alignment script
- ✓ Mapped sections to folios (with caveats)
- ✓ Identified critical test folios

**Pending:**
- ⚠ Manual verification of alignment accuracy
- ⚠ Visual examination of predicted folios
- ⚠ Plant identification confirmation
- ⚠ Correlation analysis

**Critical Test:**
The prediction that Section 4 contains wound-healing plant illustrations **can now be tested** by viewing folios f19r-f22v (or whatever folio manual search finds).

This is independent validation that doesn't depend on our text analysis being correct.

---

*Generated: 2025-10-29*
*Alignment quality: Low (2.07% similarity) - manual verification needed*
*Critical folios to examine: f19r, f19v, f20r, f20v, f21r, f21v, f22r, f22v*
*Prediction: Wound-healing plants (plantain, betony, yarrow, woundwort)*
