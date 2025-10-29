# Middle English Phonology Resources

## Why Phonology Matters for This Research

**Core hypothesis**: Voynich uses invented alphabet to represent ME phonemes.

**Testing approach**:
1. Extract ME phoneme inventory (1400-1450)
2. Calculate phoneme frequencies in ME corpus
3. Calculate Voynich symbol frequencies
4. Test if distributions correlate

## Primary Academic Resources

### 1. Roger Lass - "Middle English Phonology"

**Access**:
- Academia.edu: https://www.academia.edu/25303539/Middle_English_phonology
- Format: PDF chapter
- Status: Free with account

**Content**:
- Complete ME phonological system
- Historical development
- Dialect variations
- IPA transcriptions

**How to use**:
- Read for system overview
- Extract phoneme inventory
- Note frequency expectations
- Identify Norfolk variations

### 2. Wikipedia - Middle English Phonology

**URL**: https://en.wikipedia.org/wiki/Middle_English_phonology

**Why useful**:
- Quick reference
- Phoneme charts
- Links to academic sources
- Sound change summaries

### 3. Oxford Research Encyclopedia

**URL**: https://oxfordre.com/linguistics/linguistics/view/10.1093/acrefore/9780199384655.001.0001/acrefore-9780199384655-e-263

**Note**: May require institutional access
- Comprehensive scholarly treatment
- Recent research
- Dialect geography

## Phoneme Inventory to Extract

### Consonants (approximate for 1400-1450)

**Stops**:
- /p/ /b/ /t/ /d/ /k/ /g/

**Fricatives**:
- /f/ /v/ /θ/ /ð/ /s/ /z/ /ʃ/ /ʒ/ /h/

**Affricates**:
- /tʃ/ (church)
- /dʒ/ (judge)

**Nasals**:
- /m/ /n/ /ŋ/

**Liquids**:
- /l/ /r/

**Glides**:
- /w/ /j/

### Vowels (Pre-Great Vowel Shift)

**Short vowels**:
- /ɪ/ /ɛ/ /a/ /ɔ/ /ʊ/

**Long vowels**:
- /iː/ /eː/ /ɛː/ /aː/ /ɔː/ /oː/ /uː/

**Diphthongs**:
- /ai/ /au/ /ɔi/ /iu/ /ɛu/

**Schwa**:
- /ə/ (in unstressed syllables, starting to be lost by 1400)

## Frequency Analysis Method

### Step 1: Transcribe ME Corpus to IPA
- Use PPCME2 or CMEPV texts from 1400-1450
- Apply ME phonological rules
- Create phonemic transcription
- Account for Norfolk dialect features

### Step 2: Count Phoneme Frequencies
- Tally each phoneme across corpus
- Calculate percentages
- Create distribution chart
- Compare with Voynich

### Step 3: Statistical Testing
- Chi-square test for distribution fit
- Calculate correlation coefficients
- Test multiple alphabet hypotheses
- Validate or reject hypothesis

## Norfolk Dialect Phonology

### Key Differences from Standard ME

1. **H-Retention**
   - Norfolk keeps initial /h/
   - Most ME dialects drop it
   - Important for phoneme counting

2. **Consonant Clusters**
   - Possible simplification: /θr/ → /tr/
   - Affects frequency distribution

3. **Vowel Characteristics**
   - May have specific vowel qualities
   - Check LALME for details
   - Compare with London/standard forms

### Sources for Norfolk Features
- eLALME (Linguistic Atlas of Late Mediaeval English)
- Margery Kempe's text as exemplar
- East Midlands dialect studies

## Tools and Scripts

### To Be Created:
- `me_to_ipa.py` - Convert ME text to IPA
- `phoneme_frequency.py` - Count phonemes
- `compare_distributions.py` - Statistical comparison
- `visualize_phonemes.py` - Create charts

### Python Libraries:
- `epitran` - Phonetic transcription
- `pandas` - Data manipulation
- `scipy` - Statistical tests
- `matplotlib` - Visualization

## Research Protocol

### Phase 1: Build Phoneme Inventory
1. [ ] Read Lass article
2. [ ] Extract complete phoneme list
3. [ ] Add Norfolk-specific features
4. [ ] Create reference document
5. [ ] Validate against multiple sources

### Phase 2: Transcribe Corpus
1. [ ] Select ME texts 1400-1450
2. [ ] Develop transcription rules
3. [ ] Transcribe sample (10,000 words)
4. [ ] Verify transcription accuracy
5. [ ] Full corpus transcription

### Phase 3: Calculate Frequencies
1. [ ] Count each phoneme
2. [ ] Calculate percentages
3. [ ] Create frequency table
4. [ ] Visualize distribution
5. [ ] Document methodology

### Phase 4: Compare with Voynich
1. [ ] Get Voynich symbol frequencies
2. [ ] Align distributions
3. [ ] Run statistical tests
4. [ ] Interpret results
5. [ ] Document findings

## Expected Outcomes

### If Hypothesis is Correct:
- ME phoneme distribution matches Voynich symbol distribution
- Common phonemes = common symbols
- Rare phonemes = rare symbols
- Statistical correlation significant (p < 0.05)

### If Hypothesis is Wrong:
- No correlation
- Distributions fundamentally different
- Random patterns when mapped
- → Move to alternative hypothesis

## Additional Resources

### Linguistic Databases
- **IPA Chart**: https://www.ipachart.com/
- **Middle English Dictionary**: https://quod.lib.umich.edu/m/middle-english-dictionary/
- **Etymological databases**: For sound changes

### Academic Papers
Search Google Scholar:
- "Middle English phonology 1400"
- "East Midlands dialect phonology"
- "Late Middle English sound system"

---

**Status**: Resources identified, analysis pending
**Last Updated**: 2025-10-29
