#!/usr/bin/env python3
"""
Download Reference Materials
Voynich-Kempe Hypothesis Research Project

Downloads publicly available reference materials:
- Women's Secrets texts (Secreta Mulierum, Trotula)
- Medieval herbals information
- Phonology resources
"""

import os
import sys
import requests
from pathlib import Path
import argparse
from tqdm import tqdm
import time


class ReferenceDownloader:
    """Downloads reference materials for research."""

    SOURCES = {
        "secreta_mulierum": {
            "url": "https://archive.org/download/womenssecretstra0000unse/womenssecretstra0000unse.pdf",
            "filename": "secreta_mulierum.pdf",
            "category": "womens_secrets",
            "description": "Women's Secrets: Translation of Pseudo-Albertus Magnus",
        },
        "trotula": {
            "url": "https://archive.org/download/trotulaenglishtr0000unse/trotulaenglishtr0000unse.pdf",
            "filename": "trotula.pdf",
            "category": "womens_secrets",
            "description": "The Trotula: Medieval Compendium of Women's Medicine",
        },
    }

    def __init__(self, output_dir: str = "data/reference_materials"):
        """Initialize downloader."""
        self.output_dir = Path(output_dir)
        self.womens_secrets_dir = self.output_dir / "womens_secrets"
        self.herbals_dir = self.output_dir / "herbals"
        self.phonology_dir = self.output_dir / "phonology"

        for directory in [
            self.womens_secrets_dir,
            self.herbals_dir,
            self.phonology_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def download_file(self, url: str, output_path: Path, description: str = "") -> bool:
        """Download file with progress bar."""
        try:
            print(f"\nDownloading: {description}")
            print(f"From: {url}")
            print(f"To: {output_path}")

            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(output_path, "wb") as f:
                if total_size == 0:
                    f.write(response.content)
                    print("✓ Downloaded")
                else:
                    with tqdm(total=total_size, unit="B", unit_scale=True) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            pbar.update(len(chunk))
                    print("✓ Download complete")

            return True

        except requests.RequestException as e:
            print(f"✗ Download failed: {e}")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def download_womens_secrets(self) -> dict:
        """Download women's secrets texts."""
        print("=" * 70)
        print("DOWNLOADING WOMEN'S SECRETS TEXTS")
        print("=" * 70)

        results = {}

        for key, source in self.SOURCES.items():
            if source["category"] != "womens_secrets":
                continue

            output_path = self.womens_secrets_dir / source["filename"]

            if output_path.exists():
                print(f"\n✓ {source['filename']}: Already exists")
                overwrite = input("  Overwrite? (y/n): ").lower().strip()
                if overwrite != "y":
                    results[key] = "skipped"
                    continue

            success = self.download_file(
                source["url"], output_path, source["description"]
            )
            results[key] = success

            time.sleep(2)  # Be polite to server

        return results

    def create_herbals_guide(self) -> None:
        """Create guide for accessing medieval herbals."""
        readme = self.herbals_dir / "HERBALS_GUIDE.md"

        content = """# Medieval English Herbals Guide

## Primary Source: British Library Digitised Manuscripts

**URL**: https://www.bl.uk/manuscripts/

### How to Access

1. Visit British Library Manuscripts site
2. Use Advanced Search
3. Filter by:
   - Date: 1400-1500
   - Keyword: "herbal"
   - Language: English, Latin, or mixed

### Key Manuscripts to Download

#### 1. Cotton MS Vitellius C III
- **Description**: Earliest illustrated Old English herbal
- **Date**: 11th century (but relevant for tradition)
- **Search**: British Library catalog number
- **Why important**: Foundational English herbal tradition

#### 2. Harley MS 585
- **Description**: Old English herbal texts and medical recipes
- **Date**: 11th century
- **Content**: Plant-based medicine
- **Why important**: Shows continuity to ME period

#### 3. Egerton MS 747
- **Description**: Tractatus de Herbis (early version)
- **Date**: Late medieval
- **Content**: Plant illustrations, properties
- **Why important**: Contemporary with Voynich

#### 4. Sloane MS 4016
- **Description**: North Italian herbal tradition
- **Date**: 15th century
- **Content**: Botanical illustrations
- **Why important**: Compare with Voynich plants

### Additional Resources

#### Herbals Database
- **URL**: https://www.herbalhistory.org/home/medieval-herbal-manuscripts/
- **Description**: Herbal History Research Network
- **Content**: Catalog of digitized herbals
- **Access**: Free

#### Bibliothèque nationale de France
- **Latin MS 6823**: Tractatus de Herbis
- **Access**: Through Gallica digital library
- **URL**: https://gallica.bnf.fr/

### Research Tasks

#### Task 1: Identify English Medicinal Plants
- [ ] Download/view key manuscripts
- [ ] List plants mentioned in English herbals 1400-1500
- [ ] Note medicinal uses (especially women's health)
- [ ] Compare with Voynich botanical section

#### Task 2: Visual Comparison
- [ ] Examine illustration styles
- [ ] Compare plant representation methods
- [ ] Look for similar artistic conventions
- [ ] Note composite/symbolic representations

#### Task 3: Vocabulary Extraction
- [ ] Extract English plant names from manuscripts
- [ ] Latin names where given
- [ ] Common names vs. formal names
- [ ] Create plant name database

### Plant Names Priority List

Focus on plants relevant to women's health:
- Pennyroyal (Mentha pulegium)
- Rue (Ruta graveolens)
- Tansy (Tanacetum vulgare)
- Wormwood/Artemisia (Artemisia absinthium)
- Queen Anne's Lace (Daucus carota)
- Sage (Salvia officinalis)
- Rosemary (Rosmarinus officinalis)
- Parsley (Petroselinum crispum)
- Thyme (Thymus vulgaris)

### Integration with Research

#### If Voynich contains plant knowledge:
1. Plant names should appear in text
2. Names may be in phonetic ME spelling
3. Cross-reference with Kempe vocabulary
4. Look for emmenagogue references

#### Analysis Steps:
1. Extract plant vocabulary from ME herbals
2. Convert to phonemes
3. Search Voynich text for patterns
4. Validate against Voynich botanical illustrations

---

**Status**: Manual research required
**Last Updated**: 2025-10-29
"""

        with open(readme, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Created herbals guide: {readme}")

    def create_phonology_guide(self) -> None:
        """Create guide for phonology resources."""
        readme = self.phonology_dir / "PHONOLOGY_RESOURCES.md"

        content = """# Middle English Phonology Resources

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
"""

        with open(readme, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Created phonology guide: {readme}")

    def create_hartlieb_notes(self) -> None:
        """Create notes about accessing the 2024 Hartlieb study."""
        readme = self.womens_secrets_dir / "HARTLIEB_STUDY.md"

        content = """# Johannes Hartlieb 2024 Study

## Citation

Brewer, Keagan, and Michelle L. Lewis. "Voynich Manuscript, Dr Johannes Hartlieb and the Encipherment of Women's Secrets." *Social History of Medicine*, Volume 37, Issue 3, August 2024, Pages 559-578.

**DOI**: https://doi.org/10.1093/shm/hkae011

## Access Options

### 1. Institutional Access (Recommended)
- **Journal**: Social History of Medicine (Oxford Academic)
- **URL**: https://academic.oup.com/shm/article-abstract/37/3/559/7633883
- Check if your university subscribes
- Access through library portal

### 2. Free Abstract
- Abstract freely available at DOI link
- Provides key findings summary
- Enough for initial research phase

### 3. Public Summary Article
- **The Conversation**: https://theconversation.com/for-600-years-the-voynich-manuscript-has-remained-a-mystery-now-we-think-its-partly-about-sex-227157
- Free, accessible summary by authors
- Covers main findings
- Good for understanding context

### 4. Interlibrary Loan
- Request through your library
- Usually free for students/researchers
- Takes a few days

### 5. Contact Authors
- Often academics will share preprints
- ResearchGate or Academia.edu
- Direct email request

## Key Findings (from public sources)

### Johannes Hartlieb (c. 1410-1468)
- Bavarian physician
- Lived around same time/place as Voynich creation
- Wrote about plants, women, magic, astronomy, baths
- **Advocated "secret letters" for gynecological recipes**

### Encryption Culture
- Widespread self-censorship of women's health knowledge
- Authors deliberately obscured dangerous information
- **Cipher specifically for contraception/abortion recipes**
- Not paranoia—systematic cultural pattern

### Specific Examples Decoded
- **21-line cipher from northern Italy**
- Recipe with gynecological uses
- **Including abortion**
- Proves cipher use for exactly this content

### Self-Censorship Patterns
- Erased genital terms in manuscripts
- Removed pages from gynecological texts
- Authors omitting "dangerous" knowledge
- Readers destroying information

### Relevance to Voynich
- Voynich fits exactly this pattern
- Same period (1404-1438)
- Same content domains
- Same geographic area
- **Encoding women's secrets was NORMAL practice**

## Why This Study Matters for Our Research

### Validates Core Hypothesis
1. **Cultural Context**: Encoding medical knowledge was expected
2. **Method**: "Secret letters" = invented alphabets used
3. **Content**: Gynecology, contraception, abortion targeted
4. **Motivation**: Fear of persecution justified

### Strengthens Obfuscation Theory
- Not just theoretical—proven practice
- Multiple examples decoded
- Hartlieb explicitly recommended it
- **Our hypothesis fits historical pattern**

### Provides Methodology Clues
- Study shows how to decode period ciphers
- Techniques might apply to Voynich
- Understanding cultural context is key
- Recognition over brute force

## Integration with Our Research

### Questions to Answer
1. Did Hartlieb's advice influence Voynich creation?
2. Are Voynich "secret letters" similar to decoded examples?
3. Does Voynich follow same content pattern?
4. Can we apply Brewer & Lewis methods to Voynich?

### Research Tasks
- [ ] Obtain full paper (via library)
- [ ] Study decoding methods used
- [ ] Extract technical details of ciphers
- [ ] Compare with Voynich structure
- [ ] Apply insights to hypothesis testing

## Notes Section

Add your notes after reading:

---

**Personal Notes**:

(Add observations, insights, connections to hypothesis here)

---

**Status**: Paper identified, full text access pending
**Last Updated**: 2025-10-29
"""

        with open(readme, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Created Hartlieb study notes: {readme}")

    def verify_downloads(self) -> dict:
        """Verify downloaded materials."""
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        results = {}

        # Check downloaded PDFs
        for key, source in self.SOURCES.items():
            if source["category"] == "womens_secrets":
                filepath = self.womens_secrets_dir / source["filename"]
                if filepath.exists() and filepath.stat().st_size > 1000:
                    size_mb = filepath.stat().st_size / (1024 * 1024)
                    print(f"✓ {source['filename']}: OK ({size_mb:.1f} MB)")
                    results[key] = True
                else:
                    print(f"✗ {source['filename']}: Missing or incomplete")
                    results[key] = False

        # Check guides
        guides = {
            "herbals_guide": self.herbals_dir / "HERBALS_GUIDE.md",
            "phonology_guide": self.phonology_dir / "PHONOLOGY_RESOURCES.md",
            "hartlieb_notes": self.womens_secrets_dir / "HARTLIEB_STUDY.md",
        }

        for key, filepath in guides.items():
            if filepath.exists():
                print(f"✓ {filepath.name}: Created")
                results[key] = True
            else:
                print(f"✗ {filepath.name}: Missing")
                results[key] = False

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download reference materials for Voynich-Kempe research",
        epilog="""
Examples:
  # Download all women's secrets texts
  python download_references.py --category womens_secrets

  # Create all guides without downloading
  python download_references.py --guides-only

  # Verify what's been downloaded
  python download_references.py --verify-only
        """,
    )

    parser.add_argument(
        "--output-dir",
        default="data/reference_materials",
        help="Output directory for reference materials",
    )

    parser.add_argument(
        "--category",
        choices=["womens_secrets", "all"],
        default="all",
        help="Which category to download",
    )

    parser.add_argument(
        "--guides-only",
        action="store_true",
        help="Only create guides, do not download files",
    )

    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify existing downloads"
    )

    args = parser.parse_args()

    # Initialize downloader
    downloader = ReferenceDownloader(args.output_dir)

    # Always create guides
    downloader.create_herbals_guide()
    downloader.create_phonology_guide()
    downloader.create_hartlieb_notes()

    # Verify only mode
    if args.verify_only:
        downloader.verify_downloads()
        return

    # Guides only mode
    if args.guides_only:
        print("\n✓ All guides created successfully")
        return

    # Download files
    results = {}

    if args.category in ["womens_secrets", "all"]:
        ws_results = downloader.download_womens_secrets()
        results.update(ws_results)

    # Verify
    verification = downloader.verify_downloads()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    successful = sum(1 for v in verification.values() if v is True)
    total = len(verification)
    print(f"Successfully created/downloaded: {successful}/{total} items")

    print("\n✓ Reference materials setup complete!")
    print(f"\nMaterials location: {Path(args.output_dir).absolute()}")

    print("\nNext steps:")
    print("  1. Review downloaded texts")
    print("  2. Follow guides for manual acquisition:")
    print("     - Medieval herbals from British Library")
    print("     - Hartlieb 2024 study via institution")
    print("     - Phonology resources from academia")
    print("  3. Begin corpus analysis phase")


if __name__ == "__main__":
    main()
