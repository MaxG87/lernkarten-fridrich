"""
Functions for generating physical learning cards with LaTeX and Makefile.

This module provides functionality to create LaTeX documents and Makefiles
for printing physical learning cards with algorithms and icons.
"""

import shutil
from pathlib import Path

import typer

from .algorithms import AlgorithmConfig

RESOURCES = Path(__file__).parent / "resources"


def generate_latex_pages(
    algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
) -> str:
    """Generate the page commands for the LaTeX document."""
    pages = []

    # Generate full pages (9 cards per page)
    for start_idx in range(0, len(algorithms), 9):
        end_idx = min(start_idx + 9, len(algorithms))
        page_algorithms = algorithms[start_idx:end_idx]

        if len(page_algorithms) == 9:
            pages.append(_generate_full_page(page_algorithms, case_fnames, start_idx))
        else:
            pages.append(
                _generate_partial_page(page_algorithms, case_fnames, start_idx)
            )

    return "\n".join(pages)


def _generate_full_page(
    page_algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
    start_idx: int,
) -> str:
    """Generate LaTeX for a full page with 9 cards."""
    # Convert SVG paths to PDF paths
    icon_paths = [case_fnames[alg].with_suffix(".pdf").name for alg in page_algorithms]
    # Get algorithm texts directly
    algo_texts = [str(alg.human_algorithm()) + "\\\\\\\\" for alg in page_algorithms]

    # Front page (icons) - 3x3 grid
    front_table = "\\begin{center}\n"
    front_table += (
        "    \\begin{tabular}{|p{\\cellwidth}|p{\\cellwidth}|p{\\cellwidth}|}\n"
    )
    front_table += "        \\hline\n"

    for row in range(3):
        cells = []
        for col in range(3):
            idx = row * 3 + col
            cells.append(f"\\cubeimg{{{icon_paths[idx]}}}")
        front_table += "        " + " & ".join(cells) + " \\\\\\hline\n"

    front_table += "    \\end{tabular}\n"
    front_table += "\\end{center}\n"

    # Back page (algorithms) - reversed order for proper alignment
    back_table = "\\newpage\n\n"
    back_table += "\\begin{center}\n"
    back_table += (
        "    \\begin{tabular}{|p{\\cellwidth}|p{\\cellwidth}|p{\\cellwidth}|}\n"
    )
    back_table += "        \\hline\n"

    for row in range(3):
        cells = []
        for col in range(2, -1, -1):  # Reverse order: 2, 1, 0
            idx = row * 3 + col
            cells.append(f"\\cubealgo{{{algo_texts[idx]}}}")
        back_table += "        " + " & ".join(cells) + " \\\\\\hline\n"

    back_table += "    \\end{tabular}\n"
    back_table += "\\end{center}\n"

    return front_table + "\n" + back_table


def _generate_partial_page(
    page_algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
    start_idx: int,
) -> str:
    """Generate LaTeX for a partial page with fewer than 9 cards."""
    count = len(page_algorithms)
    rows = (count + 2) // 3  # Round up division

    # Convert SVG paths to PDF paths
    icon_paths = [case_fnames[alg].with_suffix(".pdf").name for alg in page_algorithms]
    # Get algorithm texts directly
    algo_texts = [str(alg.human_algorithm()) for alg in page_algorithms]

    # Front page (icons)
    front_rows = []
    counter = 0
    for row in range(rows):
        cells = []
        for col in range(3):
            if counter < count:
                cells.append(f"\\cubeimg{{{icon_paths[counter]}}}")
                counter += 1
            else:
                cells.append("")
        front_rows.append(" & ".join(cells) + " \\\\\\hline")

    front_table = (
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
        row_start = row * 3
        for col in range(2, -1, -1):  # Reverse order: 2, 1, 0
            idx = row_start + col
            if idx < count:
                cells.append(f"\\cubealgo{{{algo_texts[idx]}}}")
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
    source = RESOURCES / "Makefile.template"
    dest = target_dir / "Makefile"
    shutil.copy(source, dest)


def create_latex_file(
    target_dir: Path,
    algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
) -> None:
    """Generate the LaTeX file from the template."""
    template_path = RESOURCES / "Lernkarten.tex.template"
    template_content = template_path.read_text()

    pages_content = generate_latex_pages(algorithms, case_fnames)
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
    - A Lernkarten.tex file with the card layout and algorithms embedded
    - A Makefile to build the PDF

    Args:
        algorithms: List of AlgorithmConfig objects to generate cards for
        case_fnames: Mapping of algorithms to their icon filenames
        target_dir: Directory where files will be created
    """
    # Create Makefile
    create_makefile(target_dir)

    # Create LaTeX file with embedded algorithms
    create_latex_file(target_dir, algorithms, case_fnames)

    typer.echo(f"\nGenerated physical learning cards setup in {target_dir}")
    typer.echo(
        f"  - Created Lernkarten.tex (with {len(algorithms)} algorithms embedded)"
    )
    typer.echo("  - Created Makefile")
    typer.echo("\nTo build the PDF:")
    typer.echo("  1. Ensure SVG icon files are present (icon-01.svg, icon-02.svg, ...)")
    typer.echo(f"  2. Run 'make' in {target_dir}")
