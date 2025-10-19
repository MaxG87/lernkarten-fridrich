#!/usr/bin/env python3
"""
Script to generate physical learning cards folder with LaTeX and Makefile.

This script scans a directory for SVG icon files and algorithm files,
then generates a LaTeX document and Makefile for creating physical learning cards.
"""

import argparse
import re
from pathlib import Path


def find_numbered_files(directory: Path, pattern: str) -> list[tuple[int, Path]]:
    """Find files matching a numbered pattern and return them sorted by number."""
    numbered_files = []
    regex = re.compile(pattern)
    
    for file in directory.iterdir():
        if match := regex.match(file.name):
            number = int(match.group(1))
            numbered_files.append((number, file))
    
    return sorted(numbered_files)


def generate_latex_pages(num_cards: int) -> str:
    """Generate the page commands for the LaTeX document."""
    pages = []
    
    # Generate full pages (9 cards per page)
    for start_idx in range(1, num_cards, 9):
        if start_idx + 8 <= num_cards:
            pages.append(f"\\cubepage{{{start_idx}}}")
    
    # Handle remaining cards if not a multiple of 9
    remaining = num_cards % 9
    if remaining > 0:
        start_idx = (num_cards // 9) * 9 + 1
        pages.append(generate_partial_page(start_idx, remaining))
    
    return "\n".join(pages)


def generate_partial_page(start_idx: int, count: int) -> str:
    """Generate LaTeX for a partial page with fewer than 9 cards."""
    # Calculate how many rows we need
    rows = (count + 2) // 3  # Round up division
    
    # Front page (icons)
    front_rows = []
    counter = start_idx
    for row in range(rows):
        cells = []
        for col in range(3):
            if counter <= start_idx + count - 1:
                cells.append("\\cubeimgstep")
                counter += 1
            else:
                cells.append("")
        front_rows.append(" & ".join(cells) + " \\\\\\hline")
    
    front_table = (
        "\\setcounter{cardcounter}{" + str(start_idx) + "}\n"
        "\\begin{center}\n"
        "    \\begin{tabular}{|p{\\cellwidth}|p{\\cellwidth}|p{\\cellwidth}|}\n"
        "        \\hline\n"
        "        " + "\n        ".join(front_rows) + "\n"
        "    \\end{tabular}\n"
        "\\end{center}\n"
    )
    
    # Back page (algorithms in reverse order)
    back_rows = []
    for row in range(rows):
        cells = []
        row_start = start_idx + row * 3
        for col in range(2, -1, -1):  # Reverse order: 2, 1, 0
            idx = row_start + col
            if idx <= start_idx + count - 1:
                cells.append(f"\\cubealgo{{{idx:02d}}}")
            else:
                cells.append("")
        back_rows.append(" & ".join(cells) + " \\\\\\hline")
    
    back_table = (
        "\\newpage\n\n"
        "\\begin{center}\n"
        "    \\begin{tabular}{|p{\\cellwidth}|p{\\cellwidth}|p{\\cellwidth}|}\n"
        "        \\hline\n"
        "        " + "\n        ".join(back_rows) + "\n"
        "    \\end{tabular}\n"
        "\\end{center}\n"
    )
    
    return front_table + "\n" + back_table


def create_makefile(target_dir: Path) -> None:
    """Copy the Makefile template to the target directory."""
    template_path = Path(__file__).parent / "templates" / "Makefile.template"
    makefile_content = template_path.read_text()
    (target_dir / "Makefile").write_text(makefile_content)


def create_latex_file(target_dir: Path, num_cards: int) -> None:
    """Generate the LaTeX file from the template."""
    template_path = Path(__file__).parent / "templates" / "Lernkarten.tex.template"
    template_content = template_path.read_text()
    
    pages_content = generate_latex_pages(num_cards)
    latex_content = template_content.replace("{{PAGES}}", pages_content)
    
    (target_dir / "Lernkarten.tex").write_text(latex_content)


def main():
    """Main function to generate physical learning cards setup."""
    parser = argparse.ArgumentParser(
        description="Generate physical learning cards folder with LaTeX and Makefile."
    )
    parser.add_argument(
        "targetdir",
        type=Path,
        help="Target directory for physical learning cards (will be created if it doesn't exist)",
    )
    
    args = parser.parse_args()
    target_dir = args.targetdir
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for existing icon files (SVG or PDF) to determine number of cards
    svg_files = find_numbered_files(target_dir, r"(\d+)\.svg")
    pdf_files = find_numbered_files(target_dir, r"(\d+)\.pdf")
    algo_files = find_numbered_files(target_dir, r"algo-(\d+)\.tex")
    
    # Determine the number of cards from existing files
    num_cards = 0
    if svg_files:
        num_cards = max(num_cards, max(num for num, _ in svg_files))
    if pdf_files:
        num_cards = max(num_cards, max(num for num, _ in pdf_files))
    if algo_files:
        num_cards = max(num_cards, max(num for num, _ in algo_files))
    
    if num_cards == 0:
        print(f"Warning: No numbered icon files (NN.svg or NN.pdf) or algorithm files (algo-NN.tex) found in {target_dir}")
        print("The script will generate templates, but you need to add:")
        print("  - Icon files: 01.svg, 02.svg, ... (or 01.pdf, 02.pdf, ...)")
        print("  - Algorithm files: algo-01.tex, algo-02.tex, ...")
        # Default to generating structure for at least one card
        num_cards = 1
    
    # Generate files
    create_makefile(target_dir)
    create_latex_file(target_dir, num_cards)
    
    print(f"Successfully created physical learning cards setup in {target_dir}")
    print(f"Configuration for {num_cards} card(s)")
    print("\nGenerated files:")
    print(f"  - {target_dir / 'Makefile'}")
    print(f"  - {target_dir / 'Lernkarten.tex'}")
    print("\nNext steps:")
    if num_cards == 1 and not (svg_files or pdf_files or algo_files):
        print(f"1. Add icon files (01.svg, 02.svg, ...) to {target_dir}")
        print(f"2. Add algorithm files (algo-01.tex, algo-02.tex, ...) to {target_dir}")
        print(f"3. Re-run this script to update Lernkarten.tex with the correct number of cards")
        print(f"4. Run 'make' in {target_dir} to build the PDF")
    else:
        print(f"1. Ensure all icon and algorithm files are present in {target_dir}")
        print(f"2. Run 'make' in {target_dir} to build the PDF")


if __name__ == "__main__":
    main()
