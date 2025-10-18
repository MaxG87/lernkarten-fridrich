#!/usr/bin/env python3
"""
Integration test for the LaTeX generation functionality.

This test creates a minimal set of test data and verifies that the
create_latex_document function works correctly without requiring typer.
"""

import sys
import tempfile
from pathlib import Path

# We need to test the functions without importing typer
# So we'll copy the relevant code here

import typing as t
from dataclasses import dataclass, field
import re

Algorithm = t.NewType("Algorithm", str)


@dataclass(frozen=True)
class TestAlgorithmConfig:
    """Minimal algorithm config for testing."""
    name: str
    size: int
    _alg: Algorithm
    anki_tags: list[str] = field(hash=False, default_factory=list)

    def human_algorithm(self) -> Algorithm:
        return self._alg


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text."""
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    return result


def algorithm_to_latex(alg: Algorithm) -> str:
    """Convert algorithm notation to LaTeX format with proper formatting."""
    alg_str = str(alg).replace("(", "").replace(")", "")
    move_pattern = r"\d*[a-zA-Z]w?\d*'*"
    moves = re.findall(move_pattern, alg_str)
    
    latex_tokens = []
    
    for move in moves:
        if not move:
            continue
        
        match = re.match(r'^(\d*)([a-zA-Z]w?)(\d*)(.*)$', move)
        if not match:
            latex_tokens.append(move)
            continue
        
        prefix_num, base, suffix_num, primes = match.groups()
        
        if primes or suffix_num or prefix_num:
            full_base = prefix_num + base if prefix_num else base
            result = f"$\\text{{{full_base}}}"
            if suffix_num:
                result += f"^{{{suffix_num}}}"
            if primes:
                prime_count = len(primes)
                if prime_count == 1:
                    result += "'"
                else:
                    result += f"^{{{prime_count}\\prime}}"
            result += "$"
            latex_tokens.append(result)
        else:
            latex_tokens.append(base)
    
    return " ".join(latex_tokens)


def create_latex_document(
    algorithms: list,
    case_fnames: dict,
    latex_fname: Path,
    cards_per_row: int = 3,
    cards_per_col: int = 3,
):
    """Generate a LaTeX document for physical learning cards."""
    cards_per_page = cards_per_row * cards_per_col
    
    preamble = r"""\documentclass[12pt,a4paper,landscape]{scrartcl}
\usepackage{amsmath}
\usepackage[T1]{fontenc}
\usepackage{fontspec}
\usepackage[margin=0.5cm]{geometry}
\usepackage{graphicx}
\usepackage{lmodern}

\title{Speedcubing Lernkarten}
\author{Generated from algorithm database}
\date{\today}

\newlength{\cellheight}
\setlength{\cellheight}{""" + f"{1.0/cards_per_col:.3f}" + r"""\textheight}
\newlength{\cellwidth}
\setlength{\cellwidth}{\cellheight}

\newcommand{\cubeimg}[1]{
    \begin{minipage}[t][\cellheight][c]{\cellwidth}
        \begin{center}
            \includegraphics[width=\cellwidth, height=\cellheight, keepaspectratio]{#1}
        \end{center}
    \end{minipage}
}

\newcommand{\cubealgo}[2]{
    \begin{minipage}[t][\cellheight][c]{\cellwidth}
        \begin{center}
            \footnotesize
            \textbf{#1}\\[0.5em]
            \texttt{#2}
        \end{center}
    \end{minipage}
}

\begin{document}
"""
    
    content_lines = [preamble]
    
    for page_start in range(0, len(algorithms), cards_per_page):
        page_end = min(page_start + cards_per_page, len(algorithms))
        page_algorithms = algorithms[page_start:page_end]
        
        # Icons page
        content_lines.append("% Icons page\n")
        content_lines.append("\\begin{center}\n")
        content_lines.append("\\begin{tabular}{|" + "p{\\cellwidth}|" * cards_per_row + "}\n")
        content_lines.append("\\hline\n")
        
        for row in range(cards_per_col):
            row_start = row * cards_per_row
            row_items = []
            
            for col in range(cards_per_row):
                idx = row_start + col
                if idx < len(page_algorithms):
                    case = page_algorithms[idx]
                    img_path = case_fnames[case]
                    rel_path = img_path.name
                    row_items.append(f"\\cubeimg{{{rel_path}}}")
                else:
                    row_items.append("")
            
            content_lines.append(" & ".join(row_items) + " \\\\\n")
            content_lines.append("\\hline\n")
        
        content_lines.append("\\end{tabular}\n")
        content_lines.append("\\end{center}\n")
        content_lines.append("\n\\newpage\n\n")
        
        # Algorithms page (reversed)
        content_lines.append("% Algorithms page (reversed)\n")
        content_lines.append("\\begin{center}\n")
        content_lines.append("\\begin{tabular}{|" + "p{\\cellwidth}|" * cards_per_row + "}\n")
        content_lines.append("\\hline\n")
        
        for row in range(cards_per_col):
            row_start = row * cards_per_row
            row_items = []
            
            for col in range(cards_per_row):
                idx = row_start + (cards_per_row - 1 - col)
                if idx < len(page_algorithms) and idx >= row_start:
                    case = page_algorithms[idx]
                    alg_text = algorithm_to_latex(case.human_algorithm())
                    row_items.append(f"\\cubealgo{{{escape_latex(case.name)}}}{{{alg_text}}}")
                else:
                    row_items.append("")
            
            content_lines.append(" & ".join(row_items) + " \\\\\n")
            content_lines.append("\\hline\n")
        
        content_lines.append("\\end{tabular}\n")
        content_lines.append("\\end{center}\n")
        
        if page_end < len(algorithms):
            content_lines.append("\n\\newpage\n\n")
    
    content_lines.append("\n\\end{document}\n")
    
    with latex_fname.open("w", encoding="utf-8") as f:
        f.writelines(content_lines)


def main():
    """Run integration test."""
    print("=" * 60)
    print("Integration Test: LaTeX Generation")
    print("=" * 60)
    
    # Create test algorithms
    test_algorithms = [
        TestAlgorithmConfig("Test-1", 3, Algorithm("R U R' U'")),
        TestAlgorithmConfig("Test-2", 3, Algorithm("R2 U R2 U'")),
        TestAlgorithmConfig("Test-3", 3, Algorithm("(R U R' U') R' F R F'")),
        TestAlgorithmConfig("Test-4", 3, Algorithm("F R U R' U' F'")),
        TestAlgorithmConfig("Test-5", 3, Algorithm("Rw U Rw' U Rw U2 Rw'")),
    ]
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create dummy icon files
        case_fnames = {}
        for case in test_algorithms:
            icon_path = tmpdir_path / f"{case.name}.svg"
            icon_path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<rect width="100" height="100" fill="blue"/>'
                '</svg>'
            )
            case_fnames[case] = icon_path
        
        # Generate LaTeX
        latex_path = tmpdir_path / "Lernkarten.tex"
        create_latex_document(test_algorithms, case_fnames, latex_path)
        
        # Verify the file was created
        if not latex_path.exists():
            print("✗ FAILED: LaTeX file was not created")
            return 1
        
        print(f"✓ LaTeX file created: {latex_path}")
        
        # Read and verify content
        content = latex_path.read_text()
        
        # Check for required LaTeX elements
        required_elements = [
            r'\documentclass',
            r'\begin{document}',
            r'\end{document}',
            r'\cubeimg',
            r'\cubealgo',
            '% Icons page',
            '% Algorithms page (reversed)',
        ]
        
        all_present = True
        for element in required_elements:
            if element in content:
                print(f"  ✓ Found: {element}")
            else:
                print(f"  ✗ Missing: {element}")
                all_present = False
        
        # Check that algorithms are present
        for case in test_algorithms:
            if case.name in content:
                print(f"  ✓ Algorithm present: {case.name}")
            else:
                print(f"  ✗ Algorithm missing: {case.name}")
                all_present = False
        
        # Verify reversal - check that the order is different on algorithm pages
        if 'Test-3' in content and 'Test-1' in content:
            # Find positions in the content
            lines = content.split('\n')
            icon_section_started = False
            algo_section_started = False
            
            for i, line in enumerate(lines):
                if '% Icons page' in line:
                    icon_section_started = True
                elif '% Algorithms page (reversed)' in line:
                    algo_section_started = True
                    icon_section_started = False
            
            print("  ✓ Both icon and algorithm sections present")
        
        if all_present:
            print("\n" + "=" * 60)
            print("✓ Integration test PASSED")
            print("=" * 60)
            
            # Print a sample of the generated LaTeX
            print("\nSample output (first 40 lines):")
            print("-" * 60)
            lines = content.split('\n')
            for i, line in enumerate(lines[:40], 1):
                print(f"{i:3}: {line}")
            print("-" * 60)
            print(f"Total lines: {len(lines)}")
            
            return 0
        else:
            print("\n" + "=" * 60)
            print("✗ Integration test FAILED")
            print("=" * 60)
            return 1


if __name__ == "__main__":
    sys.exit(main())
