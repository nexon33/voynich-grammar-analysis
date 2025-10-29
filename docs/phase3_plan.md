# Phase 3: Translation Using Selective Obfuscation Model

**Date:** 2025-10-29  
**Status:** INITIATED

---

## Objectives

Using the selective obfuscation discovery, attempt partial translation of Voynich text by:

1. Identifying which words are likely unchanged (common vocabulary)
2. Applying selective e↔o conversion to medical/technical terms
3. Building medical vocabulary database from ME corpus
4. Translating passages and checking for coherence
5. Validating translations against ME medical texts

---

## The Selective Obfuscation Model

### Key Insights:

**41.2% of words are unchanged** → Start by identifying these  
**71% of 'e's obfuscated** → Try multiple e↔o combinations  
**Medical terms more obfuscated** → Focus on context  
**Common words left alone** → Use as anchors  

### Translation Strategy:

```
STEP 1: Identify unchanged words
├─ Look for common ME vocabulary
├─ Short words likely unchanged
└─ Function words (she, the, and, of, to...)

STEP 2: Build context
├─ Use unchanged words as anchors
├─ Identify sentence structure
└─ Determine if section is narrative vs. medical

STEP 3: Apply selective e↔o
├─ Test different combinations
├─ Medical words: higher obfuscation
├─ Common words: try unchanged first
└─ Use morphology (-or → -er when appropriate)

STEP 4: Validate coherence
├─ Does it make grammatical sense?
├─ Does it fit medical context?
├─ Does vocabulary match ME corpus?
└─ Do patterns repeat consistently?
```

---

## Phase 3 Tasks

### Task 1: Extract and Analyze Voynich Sections

**Goal:** Separate Voynich into analyzable sections

**Actions:**
- Split text into ~500-word sections
- Identify sections with high illustration density
- Mark narrative vs. diagram-heavy sections
- Create section metadata

**Expected outcome:** ~80-100 sections to analyze

---

### Task 2: Build ME Medical Vocabulary Database

**Goal:** Create searchable medical term database

**Actions:**
- Extract medical terminology from ME corpus
- Categories: herbs, body parts, conditions, treatments
- Include variants and spellings
- Add frequency information

**Data sources:**
- CMEPV corpus (general ME)
- Known ME medical texts
- Herbal glossaries

**Expected outcome:** 2,000-5,000 medical terms

---

### Task 3: Identify Unchanged Words in Voynich

**Goal:** Find words that are likely not obfuscated

**Method:**
```python
def find_unchanged_candidates(voynich_text, me_vocab):
    """
    Find words that:
    1. Appear in ME corpus
    2. Are short (< 5 letters)
    3. Are high frequency
    4. Match common function words
    """
    candidates = []
    for word in voynich_text.split():
        if word in me_vocab:
            if len(word) < 5:
                if is_common_word(word):
                    candidates.append(word)
    return candidates
```

**Expected outcome:** Identify ~40% of Voynich vocabulary as unchanged

---

### Task 4: Create Selective Translation Tool

**Goal:** Build tool that tries multiple e↔o combinations

**Features:**
- Apply e↔o to all possible combinations
- Rank by ME vocabulary match rate
- Show most coherent versions
- Highlight medical vocabulary
- Compare with ME texts

**Algorithm:**
```python
def selective_translate(voynich_word):
    """
    Generate all possible e↔o combinations.
    For word with N 'o's or 'e's, generate 2^N variants.
    """
    variants = []
    
    # Try unchanged first
    variants.append(voynich_word)
    
    # Try all 'o' → 'e'
    variants.append(voynich_word.replace('o', 'e'))
    
    # Try all 'e' → 'o'  
    variants.append(voynich_word.replace('e', 'o'))
    
    # Try selective combinations
    # (for each 'o' or 'e', convert or don't)
    
    # Rank by:
    # 1. Match in ME vocabulary
    # 2. Match in medical terms
    # 3. Frequency in ME corpus
    
    return sorted_variants
```

---

### Task 5: Translate Sample Sections

**Priority sections:**

**A. Narrative/Introduction (if exists)**
- Expected: less obfuscation
- Common vocabulary
- May set context

**B. Simple Plant Pages**
- Single illustration
- Short text
- Likely plant description

**C. Bathing/Women Sections**
- Women's health context
- Expected medical vocabulary
- Key to hypothesis

**D. "Pharmaceutical" Section**
- Jars and containers
- Recipe-like text
- Treatment instructions

**E. Star/Astronomical Sections**
- May be calendar
- Seasonal herb gathering
- Medical astrology

---

### Task 6: Medical Vocabulary Analysis

**Goal:** Test if Voynich contains expected medical terms

**Expected vocabulary:**

**Herbs (common in ME herbals):**
- betony, camomile, comfrey, fennel, henbane
- lavender, mint, pennyroyal, rue, sage
- valerian, vervain, wormwood, yarrow

**Body parts (women's health):**
- womb (wombe), breast (brest), head (hede)
- belly, blood, bone, child (childe)

**Conditions:**
- ache, fever (feuer), pain (peyne), sore
- sick (seke), swelling, wound

**Treatments:**
- heal (hele), medicine, salve, plaster
- drink, bath, poultice

**Test:**
```python
def find_medical_terms(voynich_section):
    """
    Try e↔o variations and look for medical vocabulary.
    If medical terms found → section is medical
    If not found → may be narrative or different topic
    """
    medical_matches = []
    for word in section:
        variants = generate_variants(word)
        for variant in variants:
            if variant in medical_vocabulary:
                medical_matches.append((word, variant))
    return medical_matches
```

---

### Task 7: Validation Methods

**How to know if translation is correct:**

**Test 1: Grammatical Coherence**
- Does it follow ME grammar?
- Subject-verb agreement?
- Appropriate word order?

**Test 2: Vocabulary Consistency**
- Words appear in ME corpus
- Frequency matches natural language
- No impossible combinations

**Test 3: Context Matching**
- Medical sections have medical terms
- Plant pages have plant names
- Illustrations match text

**Test 4: Pattern Repetition**
- Same words decoded same way
- Consistent morphology
- Repeated phrases recognizable

**Test 5: Expert Validation**
- ME linguists can read it
- Medical historians recognize content
- Matches known ME medical texts

---

## Success Criteria

### Minimal Success (Phase 3 Complete):
- ✓ Identify 20+ unchanged words
- ✓ Translate 3-5 short passages coherently
- ✓ Find 10+ medical terms
- ✓ Show grammatical ME structure
- ✓ Match text to illustration context

### Moderate Success:
- ✓ Translate 10+ passages
- ✓ Find 50+ medical terms
- ✓ Identify herb names
- ✓ Decode recipe/treatment instructions
- ✓ External validation by ME experts

### Complete Success:
- ✓ Translate entire sections coherently
- ✓ Full medical vocabulary mapped
- ✓ Consistent translation throughout
- ✓ Publishable decipherment
- ✓ Academic acceptance

---

## Risks and Challenges

### Challenge 1: Multiple Valid Readings
- **Problem:** Different e↔o combinations may all seem valid
- **Solution:** Use context, frequency, and consistency checks

### Challenge 2: Dialectal Variation
- **Problem:** ME had many dialects, spelling variations
- **Solution:** Build comprehensive vocabulary, expect variants

### Challenge 3: Ambiguous Context
- **Problem:** Can't always tell if word should be obfuscated
- **Solution:** Try both, see which makes more sense in context

### Challenge 4: Incomplete Vocabulary
- **Problem:** Some medical terms may not be in our corpus
- **Solution:** Use known ME herbals, medical texts as reference

### Challenge 5: Confirmation Bias
- **Problem:** May see patterns we want to see
- **Solution:** Blind testing, independent verification, strict criteria

---

## Deliverables

### Phase 3 Outputs:

1. **ME Medical Vocabulary Database** (medical_terms.json)
2. **Selective Translation Tool** (selective_translator.py)
3. **Section Analysis** (section_analysis.json)
4. **Translation Attempts** (translations/ directory)
5. **Validation Report** (phase3_validation.md)
6. **Medical Term Findings** (medical_vocabulary_found.txt)
7. **Coherent Passages** (translated_passages.txt)

---

## Timeline

**Week 1: Setup and Tools**
- Build medical vocabulary database
- Create selective translation tool
- Analyze Voynich sections

**Week 2: Initial Translations**
- Attempt narrative sections
- Test on simple plant pages
- Validate findings

**Week 3: Medical Sections**
- Focus on women's health sections
- Decode herbal vocabulary
- Test against ME medical texts

**Week 4: Validation and Refinement**
- Check consistency across sections
- External validation
- Prepare findings report

---

## Next Immediate Steps

1. ✓ Create Phase 3 plan (THIS DOCUMENT)
2. Build ME medical vocabulary extractor
3. Create selective translation tool
4. Analyze Voynich text structure
5. Begin translation attempts

**Let's start with building the medical vocabulary database from the ME corpus.**

---

## Decision Points

### Decision Point 1: After Initial Translations

**IF**: We find 10+ coherent passages with medical vocabulary  
**THEN**: Proceed to full manuscript translation  
**ELSE**: Refine model and try additional sections

### Decision Point 2: After Medical Section Analysis

**IF**: Medical terms found match expected ME herbals  
**THEN**: Confirms women's medical knowledge hypothesis  
**ELSE**: May be different medical tradition, revise expectations

### Decision Point 3: After Validation

**IF**: Independent ME experts confirm coherence  
**THEN**: Prepare academic publication  
**ELSE**: Continue refinement and additional testing

---

## Success Indicators We're Looking For

✓ **Grammatical ME sentences** (subject-verb-object order)  
✓ **Medical vocabulary** (herbs, body parts, treatments)  
✓ **Repeated phrases** (decoded consistently)  
✓ **Text-illustration match** (plant name matches drawing)  
✓ **Recipe structure** ("Take [herb], boil in water...")  
✓ **Contextual coherence** (medical sections have medical terms)  
✓ **Natural frequency** (common words appear often)  

If we see these patterns emerge, **we have successful decipherment**.

---

**Phase 3 begins now.** 🚀📜✨
