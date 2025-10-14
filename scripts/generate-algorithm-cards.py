#!/usr/bin/env python3

import typing as t
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import requests
import typer

Algorithm = t.NewType("Algorithm", str)
type View = t.Literal["plan", "trans"]
type MaybeView = View | None
type FrontColour = t.Literal["RED", "BLUE", "ORANGE", "GREEN"]

app = typer.Typer(help="Generate algorithm cards for Rubik's cubes in SVG format.")
_FMT = "svg"
_BASE_URL = f"https://visualcube.api.cubing.net?fmt={_FMT}&ac=black&"


@dataclass(frozen=True)
class OLLAlgorithmConfig:
    name: str
    size: int
    _alg: Algorithm
    view: t.ClassVar[View] = "plan"
    anki_tags: list[str] = field(hash=False)

    @property
    def parameters(self) -> dict[str, str]:
        return {"sch": "ysssss"}

    @property
    def arrows(self) -> list[str]:
        return []

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return self._alg


@dataclass(frozen=True)
class PLLAlgorithmConfig:
    name: str
    size: int
    _alg: Algorithm
    view: t.ClassVar[View] = "plan"
    anki_tags: list[str] = field(hash=False)
    arrows: list[str] = field(default_factory=list, hash=False)
    parameters: dict[str, str] = field(default_factory=dict, hash=False)

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return self._alg


@dataclass(frozen=True)
class FrontAlgorithmConfig:
    """For algorithms that need to be done from a front face"""

    name: str
    size: int
    _alg: Algorithm
    _front_colour: FrontColour
    view: t.ClassVar[View] = "plan"
    anki_tags: list[str] = field(hash=False)
    parameters: dict[str, str] = field(default_factory=dict, hash=False)
    _y_rotations: t.ClassVar[dict[FrontColour, Algorithm]] = field(
        hash=False,
        default={
            "RED": Algorithm("y"),
            "BLUE": Algorithm(""),
            "ORANGE": Algorithm("y'"),
            "GREEN": Algorithm("y2"),
        },
    )

    @property
    def arrows(self) -> list[str]:
        return []

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        # The visualiser will generate the cube that will be solved with the algorithm.
        # Thus, to present a front face, the algorithm needs to start with "x'" to put
        # the front face from top (where it can be displayed "plan") to front. At the
        # end of the algorithm, front needs to be moved back to its default location, so
        # the reverse of the "y" rotation is needed.
        if self._front_colour == "BLUE":
            y_rot = ""  # No y rotation needed
        else:
            y_rot = self._y_rotations[self._front_colour] + "'"
        x_rot = Algorithm("x'")
        full_alg = f"{x_rot} {self._alg} {y_rot}"
        return Algorithm(full_alg)


@dataclass(frozen=True)
class GeneralAlgorithmConfig:
    name: str
    size: int
    _alg: Algorithm
    view: t.Literal["plan", "trans"] | None
    anki_tags: list[str] = field(hash=False)
    arrows: list[str] = field(default_factory=list, hash=False)
    parameters: dict[str, str] = field(default_factory=dict, hash=False)

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return self._alg


type AlgorithmConfig = (
    OLLAlgorithmConfig
    | PLLAlgorithmConfig
    | FrontAlgorithmConfig
    | GeneralAlgorithmConfig
)


pll_algorithms: list[AlgorithmConfig] = [
    PLLAlgorithmConfig(
        "Aa",
        3,
        Algorithm("x (R' U R') D2 (R U' R')(D2 R2) x'"),
        ["3x3x3", "PLL"],
        ["U0U2-s8", "U2U8-s8", "U8U0-s8"],
    ),
    PLLAlgorithmConfig(
        "Ab",
        3,
        Algorithm("x (R2 D2)(R U R') D2 (R U' R) x'"),
        ["3x3x3", "PLL"],
        ["U8U2-s8", "U0U8-s8", "U2U0-s8"],
    ),
    PLLAlgorithmConfig(
        "E",
        3,
        Algorithm("R2 U R' y (R U' R' U) (R U' R' U) (R U' R' U) y' R U' R2 "),
        ["3x3x3", "PLL"],
        ["U0U2", "U2U0", "U6U8", "U8U6"],
    ),
    PLLAlgorithmConfig(
        "F",
        3,
        Algorithm("(R' U' F')(R U R' U')(R' F)(R2 U')(R' U' R U) R' U R"),
        ["3x3x3", "PLL"],
        ["U1U7", "U7U1", "U2U8", "U8U2"],
    ),
    PLLAlgorithmConfig(
        "Ga",
        3,
        Algorithm("(R2' u)(R' U R' U')(R u') R2 y' (R' U R)"),
        ["3x3x3", "PLL"],
        ["U0U2-s8", "U2U6-s8", "U6U0-s8", "U1U3-s7", "U3U5-s7", "U5U1-s7"],
    ),
    PLLAlgorithmConfig(
        "Gb",
        3,
        Algorithm("(R' U' R) y (R2 u)(R' U R U')(R u') R2"),
        ["3x3x3", "PLL"],
        ["U0U6-s8", "U6U8-s8", "U8U0-s8", "U1U7-s7", "U7U3-s7", "U3U1-s7"],
    ),
    PLLAlgorithmConfig(
        "Gc",
        3,
        Algorithm("(R2 u')(R U' R U)(R' u) R2 y (R U' R')"),
        ["3x3x3", "PLL"],
        ["U0U6-s8", "U6U8-s8", "U8U0-s8", "U7U3-s7", "U3U5-s7", "U5U7-s7"],
    ),
    PLLAlgorithmConfig(
        "Gd",
        3,
        Algorithm("(R U R') y' (R2 u')(R U' R' U)(R' u) R2"),
        ["3x3x3", "PLL"],
        ["U0U2-s8", "U2U6-s8", "U6U0-s8", "U1U3-s7", "U3U7-s7", "U7U1-s7"],
    ),
    PLLAlgorithmConfig(
        "H",
        3,
        Algorithm("(M2' U' M2') U2 (M2' U' M2')"),
        ["3x3x3", "PLL"],
        ["U1U7", "U7U1", "U5U3", "U3U5"],
    ),
    PLLAlgorithmConfig(
        "Ja",
        3,
        Algorithm("(L' U2 L) U (L' U2) (R U') (L U R)'"),
        ["3x3x3", "PLL"],
        ["U0U6", "U6U0", "U3U7", "U7U3"],
    ),
    PLLAlgorithmConfig(
        "Jb",
        3,
        Algorithm("(R U R' F')(R U R' U')(R' F)(R2 U')(R' U')"),
        ["3x3x3", "PLL"],
        ["U2U8", "U8U2", "U5U7", "U7U5"],
    ),
    PLLAlgorithmConfig(
        "Na",
        3,
        Algorithm("(L U') R U2' (L' U) R' (L U') R U2' (L' U) R' U'"),
        ["3x3x3", "PLL"],
        ["U6U2", "U2U6", "U3U5", "U5U3"],
    ),
    PLLAlgorithmConfig(
        "Nb",
        3,
        Algorithm("(R' U) L' U2 (R U') L (R' U) L' U2 (R U') L U"),
        ["3x3x3", "PLL"],
        ["U0U8", "U8U0", "U3U5", "U5U3"],
    ),
    PLLAlgorithmConfig(
        "Ra",
        3,
        Algorithm("(R U2')(R' U2)(R B')(R' U' R U)(R B R2 U)"),
        ["3x3x3", "PLL"],
        ["U1U5", "U5U1", "U6U8", "U8U6"],
    ),
    PLLAlgorithmConfig(
        "Rb",
        3,
        Algorithm("(R' U2)(R U2')(R' F)(R U R' U')(R' F' R2 U')"),
        ["3x3x3", "PLL"],
        ["U0U2", "U2U0", "U5U7", "U7U5"],
    ),
    PLLAlgorithmConfig(
        "T",
        3,
        Algorithm("(R U R' U')(R' F)(R2 U')(R' U' R U) R' F'"),
        ["3x3x3", "PLL"],
        ["U3U5-s8", "U5U3-s8", "U2U8", "U8U2"],
    ),
    PLLAlgorithmConfig(
        "Ua",
        3,
        Algorithm("(R2 U')(R' U' R U)(R U)(R U' R)"),
        ["3x3x3", "PLL"],
        ["U5U1-s7", "U1U3-s7", "U3U5-s7"],
    ),
    PLLAlgorithmConfig(
        "Ub",
        3,
        Algorithm("(R2' U)(R U R' U')(R' U')(R' U R')"),
        ["3x3x3", "PLL"],
        ["U3U5-s7", "U5U7-s7", "U7U3-s7"],
    ),
    PLLAlgorithmConfig(
        "V",
        3,
        Algorithm("(R' U R' U') x2 y' (R' U R' U') l (R U' R' U) R U x'"),
        ["3x3x3", "PLL"],
        ["U1U5", "U5U1", "U0U8", "U8U0"],
    ),
    PLLAlgorithmConfig(
        "Y",
        3,
        Algorithm("F (R U')(R' U' R U)(R' F')(R U R' U')(R' F R F')"),
        ["3x3x3", "PLL"],
        ["U1U3", "U3U1", "U0U8", "U8U0"],
    ),
    PLLAlgorithmConfig(
        "Z",
        3,
        Algorithm("(R' U' R U') R U (R U' R' U) R U R2 U' R' (U2)"),
        ["3x3x3", "PLL"],
        ["U1U5", "U5U1", "U3U7", "U7U3"],
    ),
]


big_cube_algorithms: list[AlgorithmConfig] = [
    FrontAlgorithmConfig(
        "4x4x4 Edge Pairing",
        4,
        Algorithm("u' R F' U R' F u"),
        "GREEN",
        ["4x4x4", "EdgePairing"],
        {
            "fc": (
                "ssssssssssssssss"
                "sssssssrsssrssss"
                "ssssssssssssssss"
                "ssssssssssssssss"
                "ssssssssssssssss"
                "ssssgddsgddsssss"
            ),
        },
    ),
    PLLAlgorithmConfig(
        "4x4x4 PLL Parity",
        4,
        Algorithm("2R2 U2 2R2 u2 2R2 2U2"),
        ["4x4x4", "PLL", "parity"],
        ["U13U2", "U2U13", "U14U1", "U1U14"],
    ),
    OLLAlgorithmConfig(
        "4x4x4 OLL Parity",
        4,
        Algorithm("r U2 x r U2 r U2 r' U2 l U2 r' U2 r U2 r' U2 r'"),
        ["4x4x4", "OLL", "parity"],
    ),
    GeneralAlgorithmConfig(
        "5x5x5 Parity",
        5,
        Algorithm("r2 B2 U2 l U2 r' U2 r U2 F2 r F2 l' B2 r2"),
        "plan",
        ["5x5x5", "parity"],
        [],
        {
            "fc": (
                "ssssssdddssdddssdddssrrrs"
                "ssssssdddssdddssdddssssss"
                "sbbbssdddssdddssdddssssss"
                "ssssssdddssdddssdddssssss"
                "ssssssdddssdddssdddssssss"
                "ssssssdddssdddssdddssssss"
            ),
        },
    ),
    FrontAlgorithmConfig(
        "5x5x5 Edge Pairing 1",
        5,
        Algorithm("u' R F' U R' F u"),
        "GREEN",
        ["5x5x5", "EdgePairing"],
        {
            "fc": (
                "sssssssssssssssssssssssss"
                "sssssssssrssssrssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssgdddsgdddssdddsssgs"
            ),
        },
    ),
    FrontAlgorithmConfig(
        "5x5x5 Edge Pairing 2",
        5,
        Algorithm("u' R F' U R' F u"),
        "GREEN",
        ["5x5x5", "EdgePairing"],
        {
            "fc": (
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "ssssssssssossssosssssssss"
                "ssssssdddssdddgsdddgsssss"
            ),
        },
    ),
    FrontAlgorithmConfig(
        "5x5x5 Edge Pairing 3",
        5,
        Algorithm("d R F' U R' F d'"),
        "GREEN",
        ["5x5x5", "EdgePairing"],
        {
            "fc": (
                "sssssssssssssssssssssssss"
                "ssssssssssssssrssssrsssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "ssssssdddsgdddsgdddsssss"
            ),
        },
    ),
    FrontAlgorithmConfig(
        "5x5x5 Edge Pairing 4",
        5,
        Algorithm("d R F' U R' F d'"),
        "GREEN",
        ["5x5x5", "EdgePairing"],
        {
            "fc": (
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssossssossssssssssssss"
                "ssssssdddgsdddgsdddssssss"
            ),
        },
    ),
    FrontAlgorithmConfig(
        "5x5x5 Edge Flipping",
        5,
        Algorithm("(R U R') (F R' F' R)"),
        "RED",
        ["5x5x5", "EdgePairing"],
        {
            "fc": (
                "sssssssssssssssssssssssss"
                "ssssssrrrrsrrrrsrrrrsssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssssssssssssssssssssss"
                "sssssgssssgssssgsssssssss"
            ),
        },
    ),
]


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


def download_case(case: GeneralAlgorithmConfig) -> bytes:
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
    substitutions = [("(", ""), (")", ""), ("2R2", "r2R2"), ("2U2", "u2U2"), (" ", "")]
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
        t.Literal["all", "pll", "big-cube"],
        typer.Option(
            ...,
            help="Which algorithm set to generate: 'all' (default), 'pll' (3x3x3 PLL only), or 'big-cube' (4x4x4+ algorithms only)",
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
):
    # Select which algorithms to generate based on user choice
    if algorithm_set == "pll":
        algorithms = pll_algorithms
        deckname = "Cubing::3x3x3::PLL"
    elif algorithm_set == "big-cube":
        algorithms = big_cube_algorithms
        deckname = "Cubing::NxNxN::Parities and Edge Pairing"
    else:  # "all"
        algorithms = pll_algorithms + big_cube_algorithms
        deckname = "Cubing::Algorithms"

    case_fnames = {case: targetdir / f"{case.name}.{_FMT}" for case in algorithms}
    targetdir.mkdir(parents=True, exist_ok=True)
    if not skip_image_generation:
        download_images(algorithms, case_fnames, max_workers)
    create_anki_csv(algorithms, case_fnames, targetdir, deckname)


if __name__ == "__main__":
    app()
