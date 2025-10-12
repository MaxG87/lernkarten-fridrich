#!/usr/bin/env python3

import argparse
import typing as t
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import requests

Algorithm = t.NewType("Algorithm", str)


@dataclass(frozen=True)
class AlgorithmConfig:
    name: str
    size: int
    alg: Algorithm
    view: t.Literal["plan", "trans"] | None
    parameters: dict[str, str] = field(default_factory=dict)


base_url = "https://visualcube.api.cubing.net?fmt=png&"

algorithms = [
    AlgorithmConfig(
        "4x4x4 Edge Swap",
        4,
        Algorithm("2R2 U2 2R2 u2 2R2 2U2"),
        "plan",
    ),
    AlgorithmConfig(
        "4x4x4 Whole Edge Flip",
        4,
        Algorithm("r U2 x r U2 r U2 r' U2 l U2 r' U2 r U2 r' U2 r'"),
        "plan",
        {"sch": "ysssss"},
    ),
    AlgorithmConfig(
        "5x5x5 Parity",
        5,
        Algorithm("2R2 U2 2R2 u2 2R2 2U2"),
        "plan",
    ),
]


def download_case(case: AlgorithmConfig) -> bytes:
    alg = human_to_visualiser(case.alg)

    param_assignments = [f"{param}={value}" for param, value in case.parameters.items()]
    param_assignments.extend([f"pzl={case.size}", f"case={alg}"])
    if case.view is not None:
        param_assignments.append(f"view={case.view}")

    params = "&".join(param_assignments)
    full_url = f"{base_url}{params}"
    print(full_url)
    response = requests.get(full_url, timeout=30)
    response.raise_for_status()
    ret = response.content
    return ret


def human_to_visualiser(alg: Algorithm) -> Algorithm:
    raw_alg = str(alg)
    for char in "() ":
        raw_alg = raw_alg.replace(char, "")
    return Algorithm(raw_alg)


def main():
    parser = argparse.ArgumentParser(
        description="Generate special cases for cubes of size >=4 in SVG format."
    )
    parser.add_argument("tagetdir", help="Target directory for output files")
    args = parser.parse_args()

    target_dir = Path(args.tagetdir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = executor.map(
            lambda case: (target_dir / f"{case.name}.png", download_case(case)),
            algorithms,
        )
        for dest, content in futures:
            dest.write_bytes(content)


if __name__ == "__main__":
    main()
