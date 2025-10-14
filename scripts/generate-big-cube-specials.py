#!/usr/bin/env python3

import typing as t
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import requests
import typer

_FMT = "svg"
_BASE_URL = f"https://visualcube.api.cubing.net?fmt={_FMT}&ac=black&"

Algorithm = t.NewType("Algorithm", str)
type View = t.Literal["plan", "trans"]
type MaybeView = View | None


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
    view: t.Literal["plan", "trans"] | None
    anki_tags: list[str] = field(hash=False)
    parameters: dict[str, str] = field(default_factory=dict, hash=False)

    @property
    def arrows(self) -> list[str]:
        return []

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return self._alg


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


type AlgorithmConfig = OLLAlgorithmConfig | PLLAlgorithmConfig | FrontAlgorithmConfig


algorithms: list[AlgorithmConfig] = [
    FrontAlgorithmConfig(
        "4x4x4 Edge Pairing",
        4,
        Algorithm("y2 x' u' R F' U R' F u y2"),
        "plan",
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
    FrontAlgorithmConfig(
        "5x5x5 Parity",
        5,
        Algorithm("r2 B2 U2 l U2 r' U2 r U2 F2 r F2 l' B2 r2"),
        "plan",
        ["5x5x5", "parity"],
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
        Algorithm("x' u' R F' U R' F u y2"),
        "plan",
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
        Algorithm("x' u' R F' U R' F u y2"),
        "plan",
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
        Algorithm("x' d R F' U R' F d' y2"),
        "plan",
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
        Algorithm("x' d R F' U R' F d' y2"),
        "plan",
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
        Algorithm("x' (R U R') (F R' F' R) y'"),
        "plan",
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
        # Write Headers
        f.write("#separator:tab\n")
        f.write("#notetype:cubingalg+\n")
        f.write(f"#deck:{deckname}\n")
        f.write("Image\tName\tAlgorithm\tTags\n")

        # Write cards
        for case in algorithms:
            img_path = case_fnames[case]
            img_html = f'<img src="{img_path.name}">'
            tags = " ".join(case.anki_tags)
            alg = case.human_algorithm()
            f.write(f"{img_html}\t{case.name}\t{alg}\t{tags}\n")


app = typer.Typer(help="Generate special cases for cubes of size >=4 in SVG format.")


@app.command()
def main(
    targetdir: t.Annotated[
        Path,
        typer.Argument(..., help="Target directory for output files"),
    ],
    max_workers: t.Annotated[
        int | None,
        typer.Option(
            ...,
            help="Maximum number of concurrent workers (will be determined automatically if unset)",
        ),
    ] = None,
):
    case_fnames = {case: targetdir / f"{case.name}.{_FMT}" for case in algorithms}
    targetdir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = executor.map(
            lambda case: (targetdir / f"{case.name}.{_FMT}", download_case(case)),
            algorithms,
        )
        for dest, content in futures:
            dest.write_bytes(content)

    create_anki_csv(
        algorithms, case_fnames, targetdir, "Cubing::NxNxN::Parities and Edge Pairing"
    )


if __name__ == "__main__":
    app()
