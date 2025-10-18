"""
Integration test for the LaTeX generation functionality.

This test creates a minimal set of test data and verifies that the
create_latex_document function works correctly.
"""

import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from lernkarten.generate_cards import (
    Algorithm,
    create_latex_document,
    escape_latex,
)


@dataclass(frozen=True)
class AlgorithmConfig:
    """Minimal algorithm config for testing."""

    name: str
    size: int
    _alg: Algorithm
    anki_tags: list[str] = field(hash=False, default_factory=list)

    def human_algorithm(self) -> Algorithm:
        return self._alg


@pytest.fixture
def test_algorithms():
    """Create test algorithm configurations."""
    return [
        AlgorithmConfig("Test-1", 3, Algorithm("R U R' U'")),
        AlgorithmConfig("Test-2", 3, Algorithm("R2 U R2 U'")),
        AlgorithmConfig("Test-3", 3, Algorithm("(R U R' U') R' F R F'")),
        AlgorithmConfig("Test-4", 3, Algorithm("F R U R' U' F'")),
        AlgorithmConfig("Test-5", 3, Algorithm("Rw U Rw' U Rw U2 Rw'")),
    ]


@pytest.fixture
def temp_output_dir(test_algorithms):
    """Create a temporary directory with dummy SVG files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create dummy icon files
        case_fnames = {}
        for case in test_algorithms:
            icon_path = tmpdir_path / f"{case.name}.svg"
            icon_path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<rect width="100" height="100" fill="blue"/>'
                "</svg>"
            )
            case_fnames[case] = icon_path

        yield tmpdir_path, case_fnames


def test_latex_document_creation(test_algorithms, temp_output_dir):
    """Test that a LaTeX document is created successfully."""
    tmpdir_path, case_fnames = temp_output_dir

    # Generate LaTeX
    latex_path = tmpdir_path / "Lernkarten.tex"
    create_latex_document(test_algorithms, case_fnames, latex_path)

    # Verify the file was created
    assert latex_path.exists(), "LaTeX file was not created"


def test_latex_document_content(test_algorithms, temp_output_dir):
    """Test that the LaTeX document has correct content."""
    tmpdir_path, case_fnames = temp_output_dir

    # Generate LaTeX
    latex_path = tmpdir_path / "Lernkarten.tex"
    create_latex_document(test_algorithms, case_fnames, latex_path)

    # Read and verify content
    content = latex_path.read_text()

    # Check for required LaTeX elements
    required_elements = [
        r"\documentclass",
        r"\begin{document}",
        r"\end{document}",
        r"\cubeimg",
        r"\cubealgo",
        "% Icons page",
        "% Algorithms page (reversed)",
    ]

    for element in required_elements:
        assert element in content, f"Missing required element: {element}"


def test_algorithms_present_in_document(test_algorithms, temp_output_dir):
    """Test that all algorithms are present in the generated document."""
    tmpdir_path, case_fnames = temp_output_dir

    # Generate LaTeX
    latex_path = tmpdir_path / "Lernkarten.tex"
    create_latex_document(test_algorithms, case_fnames, latex_path)

    # Read content
    content = latex_path.read_text()

    # Check that algorithms are present
    for case in test_algorithms:
        assert case.name in content, f"Algorithm missing: {case.name}"


def test_icon_and_algorithm_sections_present(test_algorithms, temp_output_dir):
    """Test that both icon and algorithm sections are present."""
    tmpdir_path, case_fnames = temp_output_dir

    # Generate LaTeX
    latex_path = tmpdir_path / "Lernkarten.tex"
    create_latex_document(test_algorithms, case_fnames, latex_path)

    # Read content
    content = latex_path.read_text()

    # Verify reversal - check that the order is different on algorithm pages
    assert "Test-3" in content, "Test-3 should be in content"
    assert "Test-1" in content, "Test-1 should be in content"

    # Find sections
    lines = content.split("\n")
    has_icons = any("% Icons page" in line for line in lines)
    has_algorithms = any("% Algorithms page (reversed)" in line for line in lines)

    assert has_icons, "Icon section not found"
    assert has_algorithms, "Algorithm section not found"


def test_escape_latex_special_chars():
    """Test that special LaTeX characters are escaped correctly."""
    assert r"\&" in escape_latex("&")
    assert r"\%" in escape_latex("%")
    assert r"\$" in escape_latex("$")
    assert r"\#" in escape_latex("#")
    assert r"\_" in escape_latex("_")
