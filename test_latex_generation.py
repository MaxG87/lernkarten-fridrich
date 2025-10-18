#!/usr/bin/env python3
"""Simple test script to generate LaTeX without needing typer installed."""

import sys
from pathlib import Path

# We'll just copy the necessary functions directly since we can't import the module without typer
import typing as t
from dataclasses import dataclass, field

# Copy the minimal necessary classes and data
Algorithm = t.NewType("Algorithm", str)

@dataclass(frozen=True)
class PLLAlgorithmConfig:
    name: str
    size: int
    _alg: Algorithm
    arrows: list[str] = field(hash=False)
    _setup_rotation_before: Algorithm = Algorithm("")
    _setup_rotation_after: Algorithm = Algorithm("")
    anki_tags: list[str] = field(hash=False, default_factory=lambda: ["3x3x3", "PLL"])

    @property
    def parameters(self) -> dict[str, str]:
        return {}

    @property
    def view(self):
        return "plan"

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return Algorithm(
            self._setup_rotation_before + self._alg + self._setup_rotation_after
        )


@dataclass(frozen=True)
class OLLAlgorithmConfig:
    name: str
    size: int
    _alg: Algorithm
    anki_tags: list[str] = field(hash=False, default_factory=lambda: ["3x3x3", "OLL"])
    _setup_rotation_before: Algorithm = Algorithm("")
    _setup_rotation_after: Algorithm = Algorithm("")

    @property
    def parameters(self) -> dict[str, str]:
        return {"sch": "ysssss"}

    @property
    def arrows(self) -> list[str]:
        return []

    @property
    def view(self):
        return "plan"

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return Algorithm(
            self._setup_rotation_before + self._alg + self._setup_rotation_after
        )


# Sample algorithms for testing
test_algorithms = [
    PLLAlgorithmConfig(
        "Aa",
        3,
        Algorithm("x (R' U R') D2 (R U' R')(D2 R2)"),
        ["U0U2-s8", "U2U8-s8", "U8U0-s8"],
        _setup_rotation_after=Algorithm("x'"),
    ),
    PLLAlgorithmConfig(
        "Ab",
        3,
        Algorithm("x (R2 D2)(R U R') D2 (R U' R)"),
        ["U8U2-s8", "U0U8-s8", "U2U0-s8"],
        _setup_rotation_after=Algorithm("x'"),
    ),
    OLLAlgorithmConfig("OCLL1 - 21", 3, Algorithm("(R U R' U)(R U' R' U)(R U2 R')")),
    OLLAlgorithmConfig("OCLL2 - 22", 3, Algorithm("R U2 R2 U' R2 U' R2 U2 R")),
    OLLAlgorithmConfig("T1 - 33", 3, Algorithm("(R U R' U')(R' F R F')")),
    OLLAlgorithmConfig("T2 - 45", 3, Algorithm("F (R U R' U') F'")),
]


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
    """Convert algorithm notation to LaTeX format with proper formatting.
    
    This converts cube notation like "R U R' U'" to LaTeX with primes as superscripts.
    """
    import re
    
    # First remove parentheses as they're just for grouping
    alg_str = str(alg).replace("(", "").replace(")", "")
    
    # Split the algorithm into individual moves
    # A move can be: single letter or letter+w, optionally followed by number(s) and/or prime(s)
    # Examples: R, U, R', R2, R2', Rw, Rw', Rw2, M, M', M2, etc.
    # Common multi-letter moves: Rw, Lw, Uw, Dw, Fw, Bw, 2R, 3L, etc.
    move_pattern = r"\d*[a-zA-Z]w?\d*'*"
    moves = re.findall(move_pattern, alg_str)
    
    latex_tokens = []
    
    for move in moves:
        if not move:
            continue
        
        # Parse the move: optional prefix number + base letter(s) + optional suffix number + optional primes
        # Examples: R, R', R2, R2', Rw, 2R, 2Rw2, etc.
        match = re.match(r'^(\d*)([a-zA-Z]w?)(\d*)(.*)$', move)
        if not match:
            latex_tokens.append(move)
            continue
        
        prefix_num, base, suffix_num, primes = match.groups()
        
        # Build the LaTeX representation
        if primes or suffix_num or prefix_num:
            # Combine prefix and base
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
            # Just a plain move letter
            latex_tokens.append(base)
    
    return " ".join(latex_tokens)



def create_latex_document(
    algorithms: list,
    case_fnames: dict,
    latex_fname: Path,
    cards_per_row: int = 3,
    cards_per_col: int = 3,
):
    """Generate a LaTeX document for physical learning cards.
    
    The document is two-sided with icons on odd pages and algorithms on even pages.
    Algorithms are reversed horizontally (C, B, A for icons A, B, C) to align properly
    when the pages are printed back-to-back and cut.
    
    Args:
        algorithms: List of algorithm configurations
        case_fnames: Mapping of algorithm configs to their icon file paths
        latex_fname: Output path for the LaTeX file
        cards_per_row: Number of cards per row (default: 3)
        cards_per_col: Number of cards per column (default: 3)
    """
    cards_per_page = cards_per_row * cards_per_col
    
    # Prepare the LaTeX preamble
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
    
    # Build the document content
    content_lines = [preamble]
    
    # Process algorithms in batches
    for page_start in range(0, len(algorithms), cards_per_page):
        page_end = min(page_start + cards_per_page, len(algorithms))
        page_algorithms = algorithms[page_start:page_end]
        
        # Icons page (odd page)
        content_lines.append("% Icons page\n")
        content_lines.append("\\begin{center}\n")
        content_lines.append("\\begin{tabular}{|" + "p{\\cellwidth}|" * cards_per_row + "}\n")
        content_lines.append("\\hline\n")
        
        for row in range(cards_per_col):
            row_start = row * cards_per_row
            row_end = min(row_start + cards_per_row, len(page_algorithms))
            row_items = []
            
            for col in range(cards_per_row):
                idx = row_start + col
                if idx < len(page_algorithms):
                    case = page_algorithms[idx]
                    img_path = case_fnames[case]
                    # Use relative path from the LaTeX file location
                    rel_path = img_path.name
                    row_items.append(f"\\cubeimg{{{rel_path}}}")
                else:
                    row_items.append("")  # Empty cell
            
            content_lines.append(" & ".join(row_items) + " \\\\\n")
            content_lines.append("\\hline\n")
        
        content_lines.append("\\end{tabular}\n")
        content_lines.append("\\end{center}\n")
        content_lines.append("\n\\newpage\n\n")
        
        # Algorithms page (even page) - reversed order
        content_lines.append("% Algorithms page (reversed)\n")
        content_lines.append("\\begin{center}\n")
        content_lines.append("\\begin{tabular}{|" + "p{\\cellwidth}|" * cards_per_row + "}\n")
        content_lines.append("\\hline\n")
        
        for row in range(cards_per_col):
            row_start = row * cards_per_row
            row_end = min(row_start + cards_per_row, len(page_algorithms))
            row_items = []
            
            for col in range(cards_per_row):
                # Reverse the column order
                idx = row_start + (cards_per_row - 1 - col)
                if idx < len(page_algorithms) and idx >= row_start:
                    case = page_algorithms[idx]
                    alg_text = algorithm_to_latex(case.human_algorithm())
                    row_items.append(f"\\cubealgo{{{escape_latex(case.name)}}}{{{alg_text}}}")
                else:
                    row_items.append("")  # Empty cell
            
            content_lines.append(" & ".join(row_items) + " \\\\\n")
            content_lines.append("\\hline\n")
        
        content_lines.append("\\end{tabular}\n")
        content_lines.append("\\end{center}\n")
        
        # Add page break unless it's the last page
        if page_end < len(algorithms):
            content_lines.append("\n\\newpage\n\n")
    
    # Close the document
    content_lines.append("\n\\end{document}\n")
    
    # Write to file
    with latex_fname.open("w", encoding="utf-8") as f:
        f.writelines(content_lines)


# Test
if __name__ == "__main__":
    output_dir = Path("/tmp/test_latex_output")
    output_dir.mkdir(exist_ok=True)
    
    # Create dummy icon files
    case_fnames = {}
    for case in test_algorithms:
        icon_path = output_dir / f"{case.name}.svg"
        # Create a dummy SVG file
        icon_path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="blue"/></svg>')
        case_fnames[case] = icon_path
    
    # Generate LaTeX
    latex_path = output_dir / "Lernkarten.tex"
    create_latex_document(test_algorithms, case_fnames, latex_path)
    
    print(f"LaTeX file generated at: {latex_path}")
    print("\nFirst 50 lines of the generated file:")
    print("=" * 60)
    with latex_path.open() as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:50], 1):
            print(f"{i:3}: {line}", end="")
    print("=" * 60)
    print(f"\nTotal lines: {len(lines)}")
