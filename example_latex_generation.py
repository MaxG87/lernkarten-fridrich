#!/usr/bin/env python3
"""
Example script demonstrating how to generate a LaTeX file for physical learning cards.

This script shows how to use the create_latex_document function to generate a LaTeX
file that can be compiled into a PDF for printing physical learning cards.

The generated document is two-sided:
- Odd pages have the cube state icons (front of cards)
- Even pages have the algorithms (back of cards), with horizontally reversed order
  to align properly when printed back-to-back and cut

Usage:
    This example creates a LaTeX file from a subset of PLL algorithms.
    To generate the actual LaTeX file, you would need to:
    1. Have the icons generated (e.g., from running the main script)
    2. Call create_latex_document with the appropriate parameters
"""

# This is just a demonstration of the API.
# The actual usage would be in the main script with the --generate-latex flag.

# Example of how it would be used:
# python scripts/generate-algorithm-cards.py pll-with-arrows/ --algorithm-set pll --generate-latex

# The function signature is:
# create_latex_document(
#     algorithms: list[AlgorithmConfig],
#     case_fnames: dict[AlgorithmConfig, Path],
#     latex_fname: Path,
#     cards_per_row: int = 3,
#     cards_per_col: int = 3,
# )

# Where:
# - algorithms: List of algorithm configurations (PLL, OLL, etc.)
# - case_fnames: Dictionary mapping each algorithm to its icon file path
# - latex_fname: Path where the LaTeX file should be written
# - cards_per_row: Number of cards horizontally on each page (default: 3)
# - cards_per_col: Number of cards vertically on each page (default: 3)

print("Example usage:")
print("python scripts/generate-algorithm-cards.py pll-with-arrows/ --algorithm-set pll --generate-latex")
print("\nThis will:")
print("1. Generate SVG icons for all PLL algorithms in the pll-with-arrows/ directory")
print("2. Create an Anki CSV file for importing into Anki")
print("3. Create a Lernkarten.tex file that can be compiled to PDF")
print("\nTo compile the LaTeX file:")
print("cd pll-with-arrows/")
print("lualatex Lernkarten.tex")
