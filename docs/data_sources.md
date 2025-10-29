# Data Sources for Voynich-Kempe Hypothesis Research

## Overview

This document provides detailed information on all data sources required for testing the hypothesis that the Voynich Manuscript contains obfuscated Middle English women's medical knowledge, with Margery Kempe's Book serving as a potential linguistic key.

**Status Legend:**
- ✅ Free and publicly accessible
- 🔓 Free with registration
- 🔒 Requires institutional access
- 📥 Manual download required

---

## 1. Voynich Manuscript Resources

### 1.1 EVA Transcription (Primary Source)
**Status:** ✅ Free and publicly accessible

**What it is:** The European Voynich Alphabet (EVA) is a standardized Latin character encoding of Voynich "glyphs" designed to facilitate computational analysis.

**Sources:**

1. **Voynich.nu (Recommended)**
   - URL: https://www.voynich.nu/transcr.html
   - Format: Plain text, interlinear transcription
   - Coverage: Complete manuscript
   - Notes: Includes multiple transcriber versions (Landini, Takahashi, etc.)
   
2. **Internet Archive - EVA Lexemes List**
   - URL: https://archive.org/details/Voynich_Manuscript_Lexemes_List
   - Format: Sorted word list with frequencies
   - Author: Joachim Dathe
   - Download: Direct PDF/text download

3. **Internet Archive - Similarity Sorted Analysis**
   - URL: https://archive.org/details/eva27sim
   - Format: N-gram analysis, similarity sorted
   - Useful for: Pattern recognition studies

**How to obtain:**
```bash
# Primary source - download directly
wget https://www.voynich.nu/data/vms_text.txt -O data/voynich/eva_transcription/vms_complete.txt

# Or use our provided script
python scripts/data_acquisition/download_voynich.py
```

### 1.2 High-Resolution Images
**Status:** ✅ Free and publicly accessible

**Yale Beinecke Digital Library**
- URL: https://collections.library.yale.edu/catalog/2002046
- Format: High-resolution JPEG
- License: Public domain
- Download: Individual pages or complete manuscript

**Voynich Portal**
- URL: https://voynichportal.com/
- Includes: Various analysis tools and downloadable images

### 1.3 Statistical Analysis Data
**Status:** ✅ Free and publicly accessible

**Academic Publications:**
- Bowern & Lindemann (2021) - Supplementary data on linguistic patterns
- Montemurro et al. (2013) - Keyword co-occurrence data
- Check journal websites for data repositories

---

## 2. Margery Kempe's Book

### 2.1 Middle English Text (CRITICAL - PRIMARY SOURCE)
**Status:** ✅ Free and publicly accessible

**TEAMS Middle English Text Series - University of Rochester**
- URL: https://d.lib.rochester.edu/teams/publication/staley-the-book-of-margery-kempe
- Editor: Lynn Staley
- Format: Online reader, downloadable PDF sections
- Features: 
  - Original Middle English text
  - Glossary included
  - Scholarly introduction
  - Critical notes

**Individual sections:**
- Book I, Part I: https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-i-part-i
- Navigate through site for complete text

**How to obtain:**
```bash
# Use our download script to fetch all sections
python scripts/data_acquisition/download_kempe.py --version middle_english
```

**Alternative Source:**
- Luminarium Medieval Literature: https://www.luminarium.org/medlit/kempebk.htm
- Format: HTML excerpts
- Coverage: Selected passages

### 2.2 Modern English Translation (PARALLEL CORPUS)
**Status:** 📥 Manual download/purchase recommended

**Barry Windeatt Translation (Penguin Classics)**
- ISBN: 9780140432510
- Format: Paperback, eBook
- Best for: Understanding context, identifying thematic patterns
- Purchase: Amazon, Penguin Random House, local bookstores

**Why both versions matter:**
- Middle English: Linguistic analysis, vocabulary mapping, phoneme frequencies
- Modern English: Semantic analysis, theme identification, contextual understanding
- Together: Cross-reference for pattern validation

**Public Domain Excerpts:**
- Project Gutenberg may have selected passages
- Check university library digital collections

---

## 3. Middle English Corpora (1400-1450)

### 3.1 Penn-Helsinki Parsed Corpus of Middle English, 2nd Edition (PPCME2)
**Status:** 🔓 Free with user agreement

**Official Source:**
- URL: https://www.ling.upenn.edu/hist-corpora/PPCME2-RELEASE-4/
- Size: 1.2 million words
- Date Range: 1150-1500 (focus on 1400-1450 texts)
- Format: Parsed text files with POS tagging
- Includes: CorpusSearch2 search tool

**How to obtain:**
1. Visit: https://www.ling.upenn.edu/histcorpora/
2. Download and complete User Agreement
3. Submit order form
4. Receive download link via email
5. Install with CorpusSearch2 tool

**Alternative Access:**
- University of Helsinki: https://varieng.helsinki.fi/CoRD/corpora/PPCME2/
- Documentation and sample files

**Key texts for our research (1400-1450):**
- Religious prose from East Anglia
- Medical treatises
- Sermons and devotional texts
- Look for Norfolk/East Midlands dialect markers

### 3.2 Corpus of Middle English Prose and Verse (CMEPV)
**Status:** ✅ Free and publicly accessible

**Primary Source - University of Michigan**
- URL: https://quod.lib.umich.edu/c/cme/
- Size: ~300 texts, 289 items
- Format: TEI-encoded XML, SGML
- Features: Cross-searchable, diverse genres
- License: Public domain

**How to obtain:**
```bash
# Option 1: Download individual texts from web interface
# Browse: https://quod.lib.umich.edu/c/cme/browse.html

# Option 2: Clone GitHub repository (complete corpus)
cd data/middle_english_corpus/cmepv
git clone https://github.com/cltk/middle_english_text_cmepv.git
```

**GitHub Repository (Backup/Bulk Download):**
- URL: https://github.com/cltk/middle_english_text_cmepv
- Maintainer: Classical Language Toolkit (CLTK)
- Format: SGML files
- Complete corpus available for download

**Notable included works:**
- Chaucer Society transcripts
- Higden's Polychronicon
- Complete Wycliffite Bible
- Various religious and secular prose

### 3.3 Middle English Dictionary & Compendium
**Status:** ✅ Free and publicly accessible

**University of Michigan Middle English Compendium**
- URL: https://quod.lib.umich.edu/m/middle-english-dictionary/
- Features:
  - Searchable dictionary
  - HyperBibliography
  - Links to corpus texts
  - Etymology and dates

**Use cases:**
- Verify word meanings in Margery Kempe
- Check attestation dates (1400-1450)
- Find cognates and variants
- Identify medical/botanical terminology

### 3.4 Norfolk Dialect Specific Resources
**Status:** 🔓 Mixed accessibility

**Linguistic Atlas of Late Mediaeval English (eLALME)**
- URL: http://www.amc.lel.ed.ac.uk/amc-projects-hub/project/elalme/
- Date Range: 1325-1450 (PERFECT for our needs)
- Focus: Geographic distribution of dialect features
- Access: Free online atlas, some features require registration

**Key features for our research:**
- Norfolk-specific linguistic markers
- East Midlands dialect boundaries
- Phonological feature maps
- Lexical variation patterns

**How to use:**
1. Access online atlas
2. Search for Norfolk/East Anglia region
3. Identify phonological and lexical features 1400-1450
4. Extract characteristic patterns for comparison

---

## 4. Reference Materials: Medieval Herbals

### 4.1 British Library Digitized Herbals
**Status:** ✅ Free and publicly accessible

**British Library Digitised Manuscripts**
- URL: https://www.bl.uk/manuscripts/
- Search: "herbal" filtered by date 1400-1500

**Specific Manuscripts:**

1. **Cotton MS Vitellius C III**
   - Earliest illustrated Old English herbal
   - Search: British Library catalog
   
2. **Harley MS 585**
   - Old English herbal texts
   - Medical recipes

3. **Egerton MS 747**
   - Tractatus de Herbis (early version)
   - Plant illustrations

4. **Sloane MS 4016**
   - North Italian herbal tradition
   - 15th century

**How to access:**
```
1. Visit: https://www.bl.uk/manuscripts/
2. Use advanced search
3. Filter: Date range 1400-1500, keyword "herbal"
4. Download high-resolution images (free)
```

### 4.2 Tractatus de Herbis
**Status:** ✅ Scholarly editions available

**Digital Sources:**
- Bibliothèque nationale de France: Latin MS 6823
- British Library: Egerton MS 747
- Both digitized through Polonsky Foundation project

**Why relevant:**
- Contemporary botanical knowledge (15th century)
- Visual comparison with Voynich plant drawings
- Identification of English medicinal plants

### 4.3 English Herbal Databases
**Status:** ✅ Free and publicly accessible

**Medieval Herbal Manuscripts Database**
- URL: https://www.herbalhistory.org/home/medieval-herbal-manuscripts/
- Herbal History Research Network
- Catalog of digitized manuscripts
- Links to various library collections

---

## 5. Reference Materials: Women's Secrets Tradition

### 5.1 Secreta Mulierum (Primary Text)
**Status:** ✅ Free and publicly accessible

**Internet Archive - Complete English Translation**
- URL: https://archive.org/details/womenssecretstra0000unse
- Title: "Women's Secrets: A Translation of Pseudo-Albertus Magnus's De Secretis Mulierum"
- Format: PDF, EPUB, online reader
- Includes: Medieval commentaries
- Download: Free, no registration

**Early Printed Editions:**
- Early English Books Online (EEBO): University of Michigan
- URL: https://quod.lib.umich.edu/e/eebo/
- Search: "Secreta mulierum"

**Why critical:**
- Defines "women's secrets" genre
- Shows typical content/structure
- Documents censorship patterns
- Provides vocabulary comparison base

### 5.2 Trotula Texts
**Status:** ✅ Free translation available

**Internet Archive - Monica Green Edition**
- URL: https://archive.org/details/trotulaenglishtr0000unse
- Title: "The Trotula: An English Translation of the Medieval Compendium of Women's Medicine"
- Editor: Monica H. Green (authoritative edition)
- Format: PDF, online reader
- Download: Free

**Alternative Access:**
- JSTOR: https://www.jstor.org/stable/j.ctt3fhj5p (institutional access)
- Project MUSE: https://muse.jhu.edu/book/24644 (institutional access)

**Why critical:**
- Most influential medieval women's medicine text
- 200+ extant manuscripts (shows widespread use)
- Contains gynecological knowledge that Voynich might encode
- Vocabulary for contraception, childbirth, women's health

### 5.3 Johannes Hartlieb Study (2024)
**Status:** 🔒 Requires institutional access (abstract free)

**Academic Publication:**
- Journal: Social History of Medicine, Volume 37, Issue 3, August 2024
- Title: "Voynich Manuscript, Dr Johannes Hartlieb and the Encipherment of Women's Secrets"
- Authors: Keagan Brewer & Michelle L. Lewis
- DOI: https://academic.oup.com/shm/article-abstract/37/3/559/7633883

**Free Access Options:**
- Abstract: Freely available at journal site
- Public summary: https://theconversation.com/for-600-years-the-voynich-manuscript-has-remained-a-mystery-now-we-think-its-partly-about-sex-227157
- University library access: Check if your institution subscribes

**Key findings (from abstract/public articles):**
- Hartlieb advocated "secret letters" for gynecological recipes
- Decoded 21-line cipher from northern Italy (abortion recipe)
- Documents widespread self-censorship of women's health knowledge
- Direct relevance to Voynich obfuscation hypothesis

---

## 6. Reference Materials: Middle English Phonology

### 6.1 Academic Resources
**Status:** ✅ Mostly open access

**Roger Lass - "Middle English Phonology"**
- Available on: Academia.edu
- URL: https://www.academia.edu/25303539/Middle_English_phonology
- Format: PDF chapter
- Coverage: Complete phonological system 1100-1450

**Wikipedia - Comprehensive Overview**
- URL: https://en.wikipedia.org/wiki/Middle_English_phonology
- Good starting point for system understanding
- References lead to academic sources

### 6.2 Dialect-Specific Studies
**Status:** 🔓 Mixed accessibility

**Oxford Research Encyclopedia - Middle English**
- URL: https://oxfordre.com/linguistics/linguistics/view/10.1093/acrefore/9780199384655.001.0001/acrefore-9780199384655-e-263
- Comprehensive scholarly article
- May require institutional access

**East Anglian English Studies**
- Wikipedia overview: https://en.wikipedia.org/wiki/East_Anglian_English
- Academic articles: Search Google Scholar for "Norfolk dialect Middle English"

### 6.3 Phoneme Inventories
**Status:** ✅ Reconstructable from sources

**What we need:**
- Consonant inventory 1400-1450
- Vowel inventory (pre-Great Vowel Shift)
- Norfolk-specific features:
  - Retention of /h/ (no h-dropping)
  - Possible /tr/ for ⟨thr⟩
  - Other regional markers

**Sources to compile:**
- LALME data (eLALME)
- Academic phonology papers
- PPCME2 documentation
- Dialectology studies

---

## 7. Supporting Tools & Software

### 7.1 Text Analysis Tools
**Status:** ✅ Free and open source

**Python Libraries (see requirements.txt):**
- NLTK: Natural Language Toolkit
- SpaCy: Advanced NLP
- Pandas: Data manipulation
- Matplotlib/Seaborn: Visualization
- SciPy: Statistical analysis

**CorpusSearch2**
- Distributed with PPCME2
- Specifically designed for parsed historical corpora
- Powerful query language for syntactic searches

### 7.2 Voynich-Specific Tools
**Status:** ✅ Free and open source

**Voynich Portal Tools**
- URL: https://voynichportal.com/
- Online analysis tools
- Glyph frequency calculators
- Section navigation

**dCode Voynich Cipher Tool**
- URL: https://www.dcode.fr/voynich-manuscript
- Online decoder/encoder for testing
- EVA conversion utilities

---

## 8. Data Acquisition Priority Order

### Phase 1: Essential (Start Immediately)
1. ✅ **Voynich EVA Transcription** - Download from voynich.nu
2. ✅ **Margery Kempe Middle English** - TEAMS edition
3. ✅ **CMEPV Corpus** - Clone GitHub repo OR download from UMich

### Phase 2: Important (Week 1)
4. 🔓 **PPCME2** - Submit user agreement, await access
5. ✅ **Secreta Mulierum** - Download from Archive.org
6. ✅ **Trotula** - Download from Archive.org
7. ✅ **Middle English Dictionary** - Bookmark/access online

### Phase 3: Reference (Week 2)
8. ✅ **British Library Herbals** - Identify and download key manuscripts
9. 🔓 **eLALME** - Register and extract Norfolk data
10. 📥 **Margery Kempe Modern Translation** - Purchase or library loan
11. 🔒 **Hartlieb 2024 Study** - Access through institution or use public summary

### Phase 4: Supplementary (Ongoing)
12. Additional Middle English medical texts
13. Contemporary English herbals
14. Related linguistic studies
15. Historical context materials

---

## 9. Ethical & Legal Considerations

### Copyright Status
- **Voynich Manuscript**: Public domain (pre-1928 creation)
- **Medieval Texts**: Public domain (pre-1700)
- **TEAMS Edition**: Open access educational resource
- **Modern Translations**: Copyright protected (fair use for research)
- **Academic Articles**: Respect journal copyright, institutional access

### Usage Guidelines
- Cite all sources appropriately
- Respect institutional access terms
- Use modern translations under fair use for research purposes
- Do not redistribute copyrighted materials
- Acknowledge all corpus creators and maintainers

### Data Management
- Store downloaded materials locally
- Keep detailed provenance records
- Back up all data sources
- Document preprocessing steps
- Maintain original file formats alongside processed versions

---

## 10. Quick Start Commands

```bash
# Create data directory structure (already done)
# mkdir -p data/{voynich,margery_kempe,middle_english_corpus,reference_materials}

# Download Voynich EVA transcription
python scripts/data_acquisition/download_voynich.py

# Download Margery Kempe Middle English text
python scripts/data_acquisition/download_kempe.py --version middle_english

# Clone CMEPV corpus
cd data/middle_english_corpus/cmepv
git clone https://github.com/cltk/middle_english_text_cmepv.git

# Download women's secrets texts
python scripts/data_acquisition/download_references.py --category womens_secrets

# Install required Python packages
pip install -r requirements.txt
```

---

## 11. Troubleshooting & Alternatives

### If primary source unavailable:

**Voynich transcription:**
- Backup: Archive.org collections
- Alternative: Voynich Portal downloads

**Margery Kempe Middle English:**
- Backup: Corpus of Middle English Prose and Verse (may include)
- Alternative: University library digital collections
- Last resort: Medieval manuscript repositories

**PPCME2 access delayed:**
- Use CMEPV while waiting
- Focus on 1400-1450 texts
- Parallel processing of other data

**Institutional access required:**
- Check university library subscriptions
- Request through interlibrary loan
- Use author-provided preprints (Academia.edu, ResearchGate)
- Contact authors directly for copies (often permitted)

---

## 12. Contact & Support

### Corpus Maintainers
- **PPCME2**: Check official website for contact
- **CMEPV**: University of Michigan Humanities Text Initiative
- **TEAMS**: University of Rochester medieval studies

### Technical Issues
- Document issues in project GitHub repository
- Check corpus-specific mailing lists
- Consult DH (Digital Humanities) forums

---

## Document Version
- **Created**: 2025-10-29
- **Last Updated**: 2025-10-29
- **Status**: Initial comprehensive compilation

---

## Next Steps
1. Execute Phase 1 downloads (Essential sources)
2. Verify data integrity
3. Document actual file structures obtained
4. Begin Phase 2 acquisitions
5. Update this document with any access issues or new sources discovered
