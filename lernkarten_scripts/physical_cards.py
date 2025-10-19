"""
Functions for generating physical learning cards with LaTeX and Makefile.

This module provides functionality to create LaTeX documents and Makefiles
for printing physical learning cards with algorithms and icons.
"""

from pathlib import Path

from .algorithms import AlgorithmConfig


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
        pages.append(_generate_partial_page(start_idx, remaining))

    return "\n".join(pages)


def _generate_partial_page(start_idx: int, count: int) -> str:
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


def create_algorithm_tex_files(
    algorithms: list[AlgorithmConfig],
    target_dir: Path,
) -> None:
    """Create algorithm .tex files from AlgorithmConfig objects."""
    for idx, alg_config in enumerate(algorithms, start=1):
        algo_file = target_dir / f"algo-{idx:02d}.tex"
        # Get the human-readable algorithm and format it for LaTeX
        algorithm_text = str(alg_config.human_algorithm())
        algo_file.write_text(f"{algorithm_text}\\\\\n")


def generate_physical_cards(
    algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
    target_dir: Path,
) -> None:
    """
    Generate physical learning cards setup in the target directory.

    This function creates:
    - Algorithm .tex files for each algorithm
    - A Lernkarten.tex file with the card layout
    - A Makefile to build the PDF

    Args:
        algorithms: List of AlgorithmConfig objects to generate cards for
        target_dir: Directory where files will be created
    """
    # Create algorithm files
    create_algorithm_tex_files(algorithms, target_dir)

    # Create Makefile
    create_makefile(target_dir)

    # Create LaTeX file
    create_latex_file(target_dir, len(algorithms))

    print(f"\nGenerated physical learning cards setup in {target_dir}")
    print(f"  - Created {len(algorithms)} algorithm files")
    print("  - Created Lernkarten.tex")
    print("  - Created Makefile")
    print("\nTo build the PDF:")
    print("  1. Ensure SVG icon files are present (icon-01.svg, icon-02.svg, ...)")
    print(f"  2. Run 'make' in {target_dir}")
