#!/usr/bin/env python3

import typing as t
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import requests
import typer

_FMT = "svg"
Algorithm = t.NewType("Algorithm", str)


@dataclass(frozen=True)
class AlgorithmConfig:
    name: str
    size: int
    alg: Algorithm
    view: t.Literal["plan", "trans"] | None
    arrows: list[str] = field(default_factory=list)
    parameters: dict[str, str] = field(default_factory=dict)


base_url = f"https://visualcube.api.cubing.net?fmt={_FMT}&ac=black&"

algorithms = [
    AlgorithmConfig(
        "4x4x4 Edge Pairing",
        4,
        Algorithm("y2 x' u' R F' U R' F u y2"),
        "plan",
        [],
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
    AlgorithmConfig(
        "4x4x4 PLL Parity",
        4,
        Algorithm("2R2 U2 2R2 u2 2R2 2U2"),
        "plan",
        ["U13U2", "U2U13", "U14U1", "U1U14"],
    ),
    AlgorithmConfig(
        "4x4x4 OLL Parity",
        4,
        Algorithm("r U2 x r U2 r U2 r' U2 l U2 r' U2 r U2 r' U2 r'"),
        "plan",
        [],
        {"sch": "ysssss"},
    ),
    AlgorithmConfig(
        "5x5x5 Parity",
        5,
        Algorithm("r2 B2 U2 l U2 r' U2 r U2 F2 r F2 l' B2 r2"),
        "plan",
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
]


def download_case(case: AlgorithmConfig) -> bytes:
    alg = human_to_visualiser(case.alg)

    param_assignments = [f"{param}={value}" for param, value in case.parameters.items()]
    param_assignments.extend([f"pzl={case.size}", f"case={alg}"])
    if case.view is not None:
        param_assignments.append(f"view={case.view}")
    if len(case.arrows) > 0:
        arrows = ",".join(case.arrows)
        param_assignments.append(f"arw={arrows}")
    params = "&".join(param_assignments)
    full_url = f"{base_url}{params}"
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


app = typer.Typer(help="Generate special cases for cubes of size >=4 in SVG format.")


@app.command()
def main(
    targetDir: t.Annotated[
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
    targetDir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = executor.map(
            lambda case: (targetDir / f"{case.name}.{_FMT}", download_case(case)),
            algorithms,
        )
        for dest, content in futures:
            dest.write_bytes(content)


if __name__ == "__main__":
    app()
