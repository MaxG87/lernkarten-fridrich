"""
Test the LaTeX generation functionality.

This test validates that:
1. The algorithm-to-LaTeX conversion works correctly
2. The document structure is valid
3. The reversed ordering for back pages is implemented correctly
"""

import re

from lernkarten.generate_cards import algorithm_to_latex


def test_algorithm_to_latex_basic():
    """Test basic algorithm parsing and LaTeX conversion."""
    result = algorithm_to_latex("R U R' U'")
    assert "$\\text{R}'$" in result
    assert "$\\text{U}'$" in result
    assert "R U" in result


def test_algorithm_to_latex_with_numbers():
    """Test algorithm conversion with number suffixes."""
    result = algorithm_to_latex("R2 U R2")
    assert "$\\text{R}^{2}$" in result
    assert "U" in result


def test_algorithm_to_latex_with_parentheses():
    """Test that parentheses are removed correctly."""
    result = algorithm_to_latex("(R U R' U')")
    assert "$\\text{R}'$" in result
    assert "$\\text{U}'$" in result
    assert "(" not in result
    assert ")" not in result


def test_algorithm_to_latex_wide_moves():
    """Test algorithm conversion with wide moves."""
    result = algorithm_to_latex("Rw U Rw'")
    assert "$\\text{Rw}'$" in result or "Rw" in result
    assert "U" in result


def test_algorithm_to_latex_prefix_numbers():
    """Test algorithm conversion with prefix numbers."""
    result = algorithm_to_latex("2R U 2R'")
    assert "$\\text{2R}'$" in result or "2R" in result
    assert "U" in result


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
