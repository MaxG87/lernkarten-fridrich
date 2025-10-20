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
    icons_per_row: int,
    icons_per_column: int,
) -> str:
    """Generate the page commands for the LaTeX document."""
    pages = []

    total_icons_per_page = icons_per_row * icons_per_column

    for start_idx in range(0, len(algorithms), total_icons_per_page):
        end_idx = min(start_idx + total_icons_per_page, len(algorithms))
        page_algorithms = algorithms[start_idx:end_idx]
        for cur_page in _generate_front_and_back_page(
            page_algorithms, case_fnames, icons_per_row, icons_per_column
        ):
            pages.append(cur_page)
            pages.append("")  # empty line as visual separator
            # Without this \newpage, LaTeX may try to fit both sides on one page. This
            # will happen especially when the last page has only cards for one row.
            pages.append(r"\newpage")
            pages.append("")  # empty line as visual separator
    pages.pop()  # Remove the last empty line
    pages.pop()  # Remove the last unnecessary \newpage

    return "\n".join(pages)


def _generate_front_and_back_page(
    page_algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
    icons_per_row: int,
    icons_per_column: int,
) -> tuple[str, str]:
    """Generate LaTeX for a partial page with fewer than 9 cards."""
    count = len(page_algorithms)
    table_header = "|" + "|".join(r"p{\cellwidth}" for _ in range(icons_per_row)) + "|"

    # Convert SVG paths to PDF paths
    icon_paths = [case_fnames[alg].with_suffix(".pdf").name for alg in page_algorithms]
    # Get algorithm texts directly
    algo_texts = [str(alg.human_algorithm()) for alg in page_algorithms]

    # Front page (icons)
    front_rows = []
    counter = 0
    for _ in range(icons_per_column):
        cells = []
        for _ in range(icons_per_row):
            if counter < count:
                cells.append(rf"\cubeimg{{{icon_paths[counter]}}}")
                counter += 1
            else:
                # Each table row requires the full amount of "&" cell separations. Empty
                # cells contain no content, so "" is a good fit to ensure this.
                cells.append("")
        front_rows.append(" & ".join(cells) + r" \\\hline")

    front_table_lines = [
        r"\begin{center}",
        rf"    \begin{{tabular}}{{{table_header}}}",
        r"        \hline",
        *[f"        {cur}" for cur in front_rows],
        r"    \end{tabular}",
        r"\end{center}",
    ]
    front_table = "\n".join(front_table_lines)

    # Back page (algorithms in reverse order)
    back_rows = []
    for row in range(icons_per_column):
        cells = []
        row_start = row * icons_per_row
        for col in range(icons_per_row - 1, -1, -1):  # Reverse order: 2, 1, 0
            idx = row_start + col
            if idx < count:
                cells.append(rf"\cubealgo{{{algo_texts[idx]}}}")
            else:
                cells.append("")
        back_rows.append(" & ".join(cells) + r" \\\hline")

    back_table_lines = [
        r"\begin{center}",
        rf"    \begin{{tabular}}{{{table_header}}}",
        r"        \hline",
        *[f"        {cur}" for cur in back_rows],
        r"    \end{tabular}",
        r"\end{center}",
    ]
    back_table = "\n".join(back_table_lines)
    return front_table, back_table


def create_makefile(target_dir: Path) -> None:
    """Copy the Makefile template to the target directory."""
    source = RESOURCES / "Makefile.template"
    dest = target_dir / "Makefile"
    shutil.copy(source, dest)


def create_latex_file(
    target_dir: Path,
    algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
    icons_per_row: int,
    icons_per_column: int,
    use_square_icons: bool,
) -> None:
    """Generate the LaTeX file from the template."""
    template_path = RESOURCES / "Lernkarten.tex.template"
    template_content = template_path.read_text()

    pages_content = generate_latex_pages(
        algorithms, case_fnames, icons_per_row, icons_per_column
    )
    latex_content = (
        template_content.replace("{{PAGES}}", pages_content)
        .replace("{{ICONS_PER_ROW}}", str(icons_per_row))
        .replace("{{ICONS_PER_COLUMN}}", str(icons_per_column))
        .replace("{{USE_SQUARE_ICONS}}", "true" if use_square_icons else "false")
    )

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
    icons_per_row: int,
    icons_per_column: int,
    use_square_icons: bool,
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
    create_latex_file(
        target_dir,
        algorithms,
        case_fnames,
        icons_per_row,
        icons_per_column,
        use_square_icons,
    )

    typer.echo(f"\nGenerated physical learning cards setup in {target_dir}")
    typer.echo(
        f"  - Created Lernkarten.tex (with {len(algorithms)} algorithms embedded)"
    )
    typer.echo("  - Created Makefile")
    typer.echo("\nTo build the PDF:")
    typer.echo("  1. Ensure SVG icon files are present (icon-01.svg, icon-02.svg, ...)")
    typer.echo(f"  2. Run 'make' in {target_dir}")
