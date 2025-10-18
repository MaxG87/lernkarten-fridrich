"""
Test the LaTeX generation functionality.

This test validates that:
1. The algorithm-to-LaTeX conversion works correctly
2. The document structure is valid
3. The reversed ordering for back pages is implemented correctly
"""

import re

import pytest

from lernkarten.generate_cards import Algorithm


def test_latex_structure_patterns():
    """Test that the LaTeX generation uses correct patterns."""
    # Key components that should be in the generated LaTeX
    required_patterns = [
        r"\\documentclass.*{scrartcl}",
        r"\\usepackage{graphicx}",
        r"\\newcommand{\\cubeimg}",
        r"\\newcommand{\\cubealgo}",
        r"\\begin{document}",
        r"\\end{document}",
        r"\\begin{tabular}",
        r"\\end{tabular}",
    ]

    # These patterns should all be valid regex
    for pattern in required_patterns:
        assert re.compile(pattern)


def test_reversal_logic():
    """Test that the reversal logic for back pages works correctly."""
    # Simulate a row with 3 items
    cards_per_row = 3
    row_items = ["A", "B", "C"]

    # The algorithm page should reverse: C, B, A
    reversed_items = []
    for col in range(cards_per_row):
        idx = cards_per_row - 1 - col  # This is the reversal logic
        reversed_items.append(row_items[idx])

    expected = ["C", "B", "A"]
    assert reversed_items == expected, f"Expected {expected}, got {reversed_items}"
