#!/usr/bin/env python3
"""
Download Margery Kempe's Book (Middle English & Modern Translation)
Voynich-Kempe Hypothesis Research Project

This script downloads The Book of Margery Kempe from publicly available sources.
Middle English version from TEAMS (University of Rochester) is the primary source.
"""

import os
import sys
import requests
from pathlib import Path
from typing import Optional, List
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
import time


class KempeDownloader:
    """Downloads Margery Kempe texts from various sources."""

    # TEAMS Middle English Text Series structure
    # These are the section URLs from Rochester
    TEAMS_SECTIONS = {
        "book1_part1": "https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-i-part-i",
        "book1_part2": "https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-i-part-ii",
        "book1_part3": "https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-i-part-iii",
        "book1_part4": "https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-i-part-iv",
        "book1_part5": "https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-i-part-v",
        "book1_part6": "https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-i-part-vi",
        "book2": "https://d.lib.rochester.edu/teams/text/staley-book-of-margery-kempe-book-ii",
    }

    # Luminarium excerpts (backup source)
    LUMINARIUM_URL = "https://www.luminarium.org/medlit/kempebk.htm"

    def __init__(self, output_dir: str = "data/margery_kempe"):
        """
        Initialize downloader.

        Args:
            output_dir: Base directory for Margery Kempe texts
        """
        self.output_dir = Path(output_dir)
        self.middle_english_dir = self.output_dir / "middle_english"
        self.modern_translation_dir = self.output_dir / "modern_translation"

        self.middle_english_dir.mkdir(parents=True, exist_ok=True)
        self.modern_translation_dir.mkdir(parents=True, exist_ok=True)

        # Session for requests with headers
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Research Project"}
        )

    def download_teams_section(self, section_key: str, url: str) -> bool:
        """
        Download a section from TEAMS website.

        Args:
            section_key: Identifier for the section
            url: URL to download from

        Returns:
            True if successful
        """
        output_file = self.middle_english_dir / f"{section_key}.txt"

        try:
            print(f"\n  Downloading: {section_key}")
            print(f"  From: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the main text content
            # TEAMS uses specific div classes, adjust if needed
            main_content = soup.find("div", class_="text-content")

            if not main_content:
                # Try alternative selectors
                main_content = soup.find("div", id="main-content")

            if not main_content:
                # Fall back to body
                main_content = soup.find("body")

            if main_content:
                # Extract text, preserving line breaks
                text = main_content.get_text(separator="\n", strip=True)

                # Save to file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"# The Book of Margery Kempe - {section_key}\n")
                    f.write(f"# Source: {url}\n")
                    f.write(f"# Downloaded: {time.strftime('%Y-%m-%d')}\n\n")
                    f.write(text)

                print(f"  ✓ Saved to: {output_file}")
                return True
            else:
                print(f"  ✗ Could not find text content in HTML")
                return False

        except requests.RequestException as e:
            print(f"  ✗ Download failed: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Error processing: {e}")
            return False

    def download_middle_english(self) -> dict:
        """
        Download Middle English text from TEAMS.

        Returns:
            Dictionary with download results for each section
        """
        print("=" * 70)
        print("DOWNLOADING MIDDLE ENGLISH TEXT (TEAMS)")
        print("=" * 70)
        print("\nSource: University of Rochester TEAMS Middle English Text Series")
        print("Editor: Lynn Staley")
        print("License: Open access educational resource")

        results = {}

        for section_key, url in self.TEAMS_SECTIONS.items():
            # Check if file exists
            output_file = self.middle_english_dir / f"{section_key}.txt"
            if output_file.exists():
                print(f"\n✓ {section_key}: Already exists")
                overwrite = input("  Overwrite? (y/n): ").lower().strip()
                if overwrite != "y":
                    results[section_key] = "skipped"
                    continue

            success = self.download_teams_section(section_key, url)
            results[section_key] = success

            # Be polite to server
            time.sleep(1)

        # Create combined file
        self.combine_sections()

        return results

    def combine_sections(self) -> None:
        """Combine all downloaded sections into a single file."""
        combined_file = self.middle_english_dir / "complete_text.txt"

        print(f"\nCombining sections into: {combined_file}")

        try:
            with open(combined_file, "w", encoding="utf-8") as outfile:
                outfile.write("# The Book of Margery Kempe - Complete Text\n")
                outfile.write("# Middle English Edition (TEAMS)\n")
                outfile.write(f"# Combined: {time.strftime('%Y-%m-%d')}\n")
                outfile.write("=" * 70 + "\n\n")

                for section_key in self.TEAMS_SECTIONS.keys():
                    section_file = self.middle_english_dir / f"{section_key}.txt"

                    if section_file.exists():
                        with open(section_file, "r", encoding="utf-8") as infile:
                            content = infile.read()
                            outfile.write(f"\n\n{'=' * 70}\n")
                            outfile.write(f"# {section_key.upper()}\n")
                            outfile.write(f"{'=' * 70}\n\n")
                            outfile.write(content)
                            outfile.write("\n\n")

            print(f"✓ Combined file created: {combined_file}")

        except Exception as e:
            print(f"✗ Error combining files: {e}")

    def download_luminarium_excerpts(self) -> bool:
        """
        Download excerpts from Luminarium (backup source).

        Returns:
            True if successful
        """
        output_file = self.middle_english_dir / "luminarium_excerpts.txt"

        print("\n" + "=" * 70)
        print("DOWNLOADING LUMINARIUM EXCERPTS (Backup Source)")
        print("=" * 70)

        try:
            print(f"\nDownloading from: {self.LUMINARIUM_URL}")

            response = self.session.get(self.LUMINARIUM_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract text
            text = soup.get_text(separator="\n", strip=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# The Book of Margery Kempe - Excerpts\n")
                f.write(f"# Source: Luminarium Medieval Literature\n")
                f.write(f"# URL: {self.LUMINARIUM_URL}\n")
                f.write(f"# Downloaded: {time.strftime('%Y-%m-%d')}\n\n")
                f.write(text)

            print(f"✓ Saved to: {output_file}")
            return True

        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def create_modern_translation_readme(self) -> None:
        """Create README with instructions for obtaining modern translation."""
        readme_file = self.modern_translation_dir / "README.md"

        content = """# Modern English Translation of The Book of Margery Kempe

## Barry Windeatt Translation (Recommended)

**NOTE:** This is a copyrighted modern translation. Purchase or obtain through library.

### Purchase Options:
- **Penguin Classics** (ISBN: 9780140432510)
  - Paperback: ~$15-20
  - eBook/Kindle: Available
  - Purchase: Amazon, Penguin Random House, Barnes & Noble

### Library Options:
- Check your local university library
- Interlibrary loan
- Online library services (e.g., Internet Archive lending)

### Why This Translation?
- Barry Windeatt is a Cambridge scholar specializing in medieval literature
- Includes comprehensive introduction and notes
- Balances readability with accuracy
- Standard edition used in academic research

### Alternative Free Sources:
- Project Gutenberg may have older public domain translations
- Some universities provide excerpts online for educational use
- Check TEAMS website for any freely available modern language notes

## Fair Use for Research

For this research project, we can use:
- Brief quotations for analysis (with proper citation)
- Comparison of specific passages between Middle English and modern versions
- Summary and paraphrase of content

## Citation Format

When citing:
```
Kempe, Margery. The Book of Margery Kempe.
Translated by Barry Windeatt, Penguin Classics, 2004.
```

## Using Modern Translation in This Research

The modern translation helps with:
1. **Understanding context** - Grasp the meaning before analyzing ME vocabulary
2. **Theme identification** - Locate passages about childbirth, healing, plants, etc.
3. **Cross-referencing** - Match modern themes to ME words
4. **Pattern validation** - Confirm interpretations of Middle English passages

## Next Steps

1. Obtain translation through purchase or library
2. Place PDF or text file in this directory (gitignored for copyright)
3. Use alongside Middle English version for analysis
4. Maintain proper citations in all research outputs
"""

        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n✓ Created: {readme_file}")

    def verify_downloads(self) -> dict:
        """Verify downloaded files."""
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        results = {}

        # Check each section
        for section_key in self.TEAMS_SECTIONS.keys():
            filepath = self.middle_english_dir / f"{section_key}.txt"

            if filepath.exists() and filepath.stat().st_size > 100:
                print(f"✓ {section_key}: OK")
                results[section_key] = True
            else:
                print(f"✗ {section_key}: MISSING or EMPTY")
                results[section_key] = False

        # Check combined file
        combined = self.middle_english_dir / "complete_text.txt"
        if combined.exists():
            size = combined.stat().st_size
            print(f"✓ complete_text.txt: OK ({size:,} bytes)")
            results["combined"] = True
        else:
            print(f"✗ complete_text.txt: MISSING")
            results["combined"] = False

        return results

    def get_statistics(self) -> None:
        """Display statistics about downloaded text."""
        print("\n" + "=" * 70)
        print("STATISTICS")
        print("=" * 70)

        combined_file = self.middle_english_dir / "complete_text.txt"

        if not combined_file.exists():
            print("✗ Combined text file not found")
            return

        try:
            with open(combined_file, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            words = content.split()
            chars = len(content)

            print(f"Total lines: {len(lines):,}")
            print(f"Total words: {len(words):,}")
            print(f"Total characters: {chars:,}")
            print(f"\nFile location: {combined_file.absolute()}")

        except Exception as e:
            print(f"✗ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download The Book of Margery Kempe texts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download Middle English version from TEAMS
  python download_kempe.py --version middle_english

  # Download Luminarium excerpts (backup)
  python download_kempe.py --version luminarium

  # Download both
  python download_kempe.py --version all

  # Verify existing downloads
  python download_kempe.py --verify-only
        """,
    )

    parser.add_argument(
        "--output-dir", default="data/margery_kempe", help="Output directory for texts"
    )

    parser.add_argument(
        "--version",
        choices=["middle_english", "luminarium", "all"],
        default="middle_english",
        help="Which version to download",
    )

    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify existing downloads"
    )

    parser.add_argument(
        "--stats", action="store_true", help="Show statistics after download"
    )

    args = parser.parse_args()

    # Initialize downloader
    downloader = KempeDownloader(args.output_dir)

    # Create modern translation README
    downloader.create_modern_translation_readme()

    # Verify only mode
    if args.verify_only:
        downloader.verify_downloads()
        if args.stats:
            downloader.get_statistics()
        return

    # Download based on version selection
    results = {}

    if args.version in ["middle_english", "all"]:
        me_results = downloader.download_middle_english()
        results.update(me_results)

    if args.version in ["luminarium", "all"]:
        lum_result = downloader.download_luminarium_excerpts()
        results["luminarium"] = lum_result

    # Verify
    verification = downloader.verify_downloads()

    # Statistics
    if args.stats:
        downloader.get_statistics()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    successful = sum(1 for v in verification.values() if v is True)
    total = len(verification)
    print(f"Successfully downloaded and verified: {successful}/{total} files")

    if successful > 0:
        print("\n✓ Download completed!")
        print(
            f"\nMiddle English text location: {downloader.middle_english_dir.absolute()}"
        )
        print("\nNext steps:")
        print("  1. Review downloaded Middle English text")
        print("  2. Obtain modern translation (see README in modern_translation/)")
        print("  3. Run: python scripts/data_acquisition/download_corpus.py")
    else:
        print("\n⚠ Download failed. Check errors above.")
        print("\nTroubleshooting:")
        print("  - Check internet connection")
        print("  - Verify URLs are still accessible")
        print("  - Try Luminarium backup: --version luminarium")
        sys.exit(1)


if __name__ == "__main__":
    main()
