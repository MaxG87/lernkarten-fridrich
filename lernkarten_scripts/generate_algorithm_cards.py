#!/usr/bin/env python3

import fnmatch
import typing as t
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
import typer

from .algorithms import BIG_CUBE, OLL, PLL, TWO_LOOK_OLL, Algorithm, AlgorithmConfig
from .physical_cards import generate_physical_cards

AlgorithmSets = t.Literal["all", "pll", "oll", "2-look-oll", "big-cube"]

app = typer.Typer(help="Generate algorithm cards for Rubik's cubes in SVG format.")
_FMT = "svg"
_BASE_URL = f"https://visualcube.api.cubing.net?fmt={_FMT}&ac=black&"


def download_images(
    algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
    max_workers: int | None,
) -> None:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = executor.map(
            lambda case: (case, download_case(case)),
            algorithms,
        )
        for case, content in futures:
            dest = case_fnames[case]
            dest.write_bytes(content)


def download_case(case: AlgorithmConfig) -> bytes:
    alg = human_to_visualiser(case.visualiser_algorithm())

    param_assignments = [f"{param}={value}" for param, value in case.parameters.items()]
    param_assignments.extend([f"pzl={case.size}", f"case={alg}"])
    if case.view is not None:
        param_assignments.append(f"view={case.view}")
    if len(case.arrows) > 0:
        arrows = ",".join(case.arrows)
        param_assignments.append(f"arw={arrows}")
    params = "&".join(param_assignments)
    full_url = f"{_BASE_URL}{params}"
    print(full_url)
    response = requests.get(full_url, timeout=30)
    response.raise_for_status()
    ret = response.content
    return ret


def human_to_visualiser(alg: Algorithm) -> Algorithm:
    raw_alg = str(alg)
    substitutions = [("2R2", "r2R2"), ("2U2", "u2U2"), (" ", ""), ("(", ""), (")", "")]
    for origin, substitution in substitutions:
        raw_alg = raw_alg.replace(origin, substitution)
    return Algorithm(raw_alg)


def create_anki_csv(
    algorithms: list[AlgorithmConfig],
    case_fnames: dict[AlgorithmConfig, Path],
    csv_fname: Path,
    deckname: str,
):
    if csv_fname.is_dir():
        csv_fname = csv_fname / "ankiCardSet.csv"
    with csv_fname.open("w", encoding="utf-8") as f:
        # Note: No CSV header row needed. If present, Anki will interpret it as a card

        # Write Headers
        f.write("#separator:tab\n")
        f.write("#notetype:cubingalg+\n")
        f.write(f"#deck:{deckname}\n")

        # Write cards
        for case in algorithms:
            img_path = case_fnames[case]
            img_html = f'<img src="{img_path.name}">'
            tags = " ".join(case.anki_tags)
            alg = case.human_algorithm()
            f.write(f"{img_html}\t{case.name}\t{alg}\t{tags}\n")


@app.command()
def main(
    targetdir: t.Annotated[
        Path,
        typer.Argument(..., help="Target directory for output files"),
    ],
    algorithm_set: t.Annotated[
        AlgorithmSets,
        typer.Option(
            ...,
            help="Which algorithm set to generate: 'all' (default), 'pll' (3x3x3 PLL only), 'oll' (3x3x3 OLL only), '2-look-oll' (second step of Two Look OLL), or 'big-cube' (4x4x4+ algorithms only)",
        ),
    ] = "all",
    max_workers: t.Annotated[
        int | None,
        typer.Option(
            ...,
            help="Maximum number of concurrent workers (will be determined automatically if unset)",
        ),
    ] = None,
    skip_image_generation: t.Annotated[
        bool,
        typer.Option(
            ...,
            help="Skip the image generation step (useful if only the CSV file is needed)",
        ),
    ] = False,
    algorithm: t.Annotated[
        str,
        typer.Option(
            ...,
            help="Specific algorithms to generate. Only algorithms in the specified set will be considered. The value may be a glob to match several algorithms. Defaults to all algorithms in the set.",
        ),
    ] = "*",
    generate_learning_cards: t.Annotated[
        bool,
        typer.Option(
            ...,
            help="Generate physical learning cards (Lernkarten.tex and Makefile) for printing",
        ),
    ] = False,
):
    algorithms_by_set_name: dict[AlgorithmSets, list[AlgorithmConfig]] = {
        "pll": PLL,
        "oll": OLL,
        "2-look-oll": TWO_LOOK_OLL,
        "big-cube": BIG_CUBE,
    }
    decknames: dict[AlgorithmSets, str] = {
        "pll": "Cubing::3x3x3::PLL with Arrows",
        "oll": "Cubing::3x3x3::OLL",
        "2-look-oll": "Cubing::3x3x3::2-Look OLL",
        "big-cube": "Cubing::NxNxN::Parities and Edge Pairing",
    }
    # Select which algorithms to generate based on user choice
    algorithms: list[AlgorithmConfig]
    if algorithm_set == "all":
        algorithms = [
            cur for cur_set in algorithms_by_set_name.values() for cur in cur_set
        ]
        deckname = "Cubing::Algorithms"
    else:
        algorithms = algorithms_by_set_name[algorithm_set]
        deckname = decknames[algorithm_set]

    algorithm_to_generate = [
        case for case in algorithms if fnmatch.fnmatch(case.name, algorithm)
    ]
    if len(algorithm_to_generate) == 0:
        raise ValueError(
            f"Algorithm '{algorithm}' does not match any case of the set {algorithm_set}!"
        )

    case_fnames = {case: targetdir / f"{case.name}.{_FMT}" for case in algorithms}
    targetdir.mkdir(parents=True, exist_ok=True)
    if not skip_image_generation:
        download_images(algorithm_to_generate, case_fnames, max_workers)
    create_anki_csv(algorithms, case_fnames, targetdir, deckname)

    # Generate physical learning cards if requested
    if generate_learning_cards:
        generate_physical_cards(algorithms, targetdir)


if __name__ == "__main__":
    app()
