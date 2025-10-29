#!/usr/bin/env python3
"""
Download Voynich Manuscript EVA Transcription
Voynich-Kempe Hypothesis Research Project

This script downloads the Voynich manuscript EVA (European Voynich Alphabet)
transcription from publicly available GitHub sources.
"""

import os
import sys
import requests
from pathlib import Path
from typing import Optional
import argparse
from tqdm import tqdm


class VoynichDownloader:
    """Downloads and processes Voynich manuscript transcription data."""

    # Primary sources for EVA transcription (updated URLs)
    SOURCES = {
        "github_takahashi": {
            "url": "https://raw.githubusercontent.com/pbloem/voynich-experiments/master/src/main/resources/data/eva.takahashi.txt",
            "description": "Takahashi EVA transcription from GitHub",
            "filename": "voynich_eva_takahashi.txt",
        },
        "github_interlinear": {
            "url": "https://raw.githubusercontent.com/pbloem/voynich-experiments/master/src/main/resources/data/eva.interlinear.txt",
            "description": "Landini-Stolfi Interlinear EVA from GitHub",
            "filename": "voynich_eva_interlinear.txt",
        },
    }

    def __init__(self, output_dir: str = "data/voynich/eva_transcription"):
        """
        Initialize downloader.

        Args:
            output_dir: Directory to save downloaded files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_file(self, url: str, output_path: Path, description: str = "") -> bool:
        """
        Download a file with progress bar.

        Args:
            url: URL to download from
            output_path: Path to save file
            description: Description for progress bar

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\nDownloading: {description}")
            print(f"From: {url}")
            print(f"To: {output_path}")

            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Get file size if available
            total_size = int(response.headers.get("content-length", 0))

            # Download with progress bar
            with open(output_path, "wb") as f:
                if total_size == 0:
                    f.write(response.content)
                    print("✓ Downloaded (size unknown)")
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
            print(f"✗ Unexpected error: {e}")
            return False

    def download_all(self, sources: Optional[list] = None) -> dict:
        """
        Download all or specified sources.

        Args:
            sources: List of source keys to download, or None for all

        Returns:
            Dictionary with download results
        """
        if sources is None:
            sources = list(self.SOURCES.keys())

        results = {}

        print("=" * 70)
        print("VOYNICH MANUSCRIPT EVA TRANSCRIPTION DOWNLOAD")
        print("=" * 70)

        for source_key in sources:
            if source_key not in self.SOURCES:
                print(f"\n✗ Unknown source: {source_key}")
                results[source_key] = False
                continue

            source = self.SOURCES[source_key]
            output_path = self.output_dir / source["filename"]

            # Skip if file already exists
            if output_path.exists():
                print(f"\n✓ File already exists: {output_path}")
                overwrite = input("  Overwrite? (y/n): ").lower().strip()
                if overwrite != "y":
                    results[source_key] = "skipped"
                    continue

            success = self.download_file(
                source["url"], output_path, source["description"]
            )
            results[source_key] = success

        return results

    def verify_downloads(self) -> dict:
        """
        Verify downloaded files exist and contain data.

        Returns:
            Dictionary with verification results
        """
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        results = {}

        for source_key, source in self.SOURCES.items():
            filepath = self.output_dir / source["filename"]

            if not filepath.exists():
                print(f"✗ {source['filename']}: NOT FOUND")
                results[source_key] = False
                continue

            file_size = filepath.stat().st_size

            if file_size == 0:
                print(f"✗ {source['filename']}: EMPTY FILE")
                results[source_key] = False
                continue

            # Try to read first few lines
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = [f.readline() for _ in range(3)]

                print(f"✓ {source['filename']}: OK ({file_size:,} bytes)")
                print(f"  First line: {lines[0][:60]}...")
                results[source_key] = True

            except Exception as e:
                print(f"✗ {source['filename']}: READ ERROR - {e}")
                results[source_key] = False

        return results

    def get_basic_stats(self) -> None:
        """Display basic statistics about downloaded files."""
        print("\n" + "=" * 70)
        print("BASIC STATISTICS")
        print("=" * 70)

        # Try to find any downloaded file
        files = list(self.output_dir.glob("voynich_eva_*.txt"))
        if not files:
            print("✗ No transcription files found")
            return

        # Use the first available file for stats
        main_file = files[0]

        try:
            with open(main_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.split("\n")
            words = content.split()
            chars = len(content)

            # Count EVA characters (rough estimate)
            eva_chars = set("abcdefghijklmnopqrstuvwxy")
            eva_count = sum(1 for c in content.lower() if c in eva_chars)

            print(f"File analyzed: {main_file.name}")
            print(f"Total lines: {len(lines):,}")
            print(f"Total words: {len(words):,}")
            print(f"Total characters: {chars:,}")
            print(f"EVA characters: {eva_count:,}")
            print(f"\nFile location: {main_file}")

        except Exception as e:
            print(f"✗ Error reading file: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Download Voynich Manuscript EVA Transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all sources
  python download_voynich.py

  # Download specific source
  python download_voynich.py --source github_takahashi

  # Specify custom output directory
  python download_voynich.py --output-dir /path/to/data

  # Just verify existing downloads
  python download_voynich.py --verify-only
        """,
    )

    parser.add_argument(
        "--output-dir",
        default="data/voynich/eva_transcription",
        help="Output directory for downloaded files",
    )

    parser.add_argument(
        "--source",
        choices=["github_takahashi", "github_interlinear", "all"],
        default="all",
        help="Which source(s) to download",
    )

    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing downloads, do not download",
    )

    parser.add_argument(
        "--stats", action="store_true", help="Show statistics after download"
    )

    args = parser.parse_args()

    # Initialize downloader
    downloader = VoynichDownloader(args.output_dir)

    # Verify only mode
    if args.verify_only:
        downloader.verify_downloads()
        if args.stats:
            downloader.get_basic_stats()
        return

    # Download files
    sources = None if args.source == "all" else [args.source]
    results = downloader.download_all(sources)

    # Verify downloads
    verification = downloader.verify_downloads()

    # Show statistics if requested
    if args.stats:
        downloader.get_basic_stats()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    successful = sum(1 for v in verification.values() if v is True)
    total = len(verification)
    print(f"Successfully downloaded and verified: {successful}/{total} files")

    if successful == total:
        print("\n✓ All downloads completed successfully!")
        print(f"\nData location: {Path(args.output_dir).absolute()}")
        print("\nNext steps:")
        print("  1. Run: python scripts/data_acquisition/download_kempe.py")
        print("  2. Review downloaded data")
        print("  3. Begin frequency analysis")
    else:
        print("\n⚠ Some downloads failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
