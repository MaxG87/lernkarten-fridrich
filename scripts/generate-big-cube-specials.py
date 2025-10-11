#!/usr/bin/env python3

import argparse
import typing as t
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Algorithm:
    name: str
    size: int
    alg: str
    view: t.Literal["plan", "trans"] | None
    parameters: dict[str, str] = field(default_factory=dict)


base_url = "https://visualcube.api.cubing.net?fmt=svg&"

algorithms = [
    Algorithm(
        "4x4x4 Edge Pairing",
        4,
        "2R2 U2 2R2 u2 2R2 2U2",
        "plan",
    ),
]


def download_case(case: Algorithm, destfile: Path) -> None:
    params = "&".join(f"{param}={value}" for param, value in case.parameters.items())
    params += f"&pzl={case.size}"
    if case.view is not None:
        params += f"&view={case.view}"
    full_url = f"{base_url}{params}"
    print(full_url)
    urllib.request.urlretrieve(full_url, destfile)


def main():
    parser = argparse.ArgumentParser(
        description="Generate special cases for cubes of size >=4 in SVG format."
    )
    parser.add_argument("tagetdir", help="Target directory for output files")
    args = parser.parse_args()

    target_dir = Path(args.tagetdir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor() as executor:
        futures = executor.map(
            lambda case: download_case(case, target_dir / f"{case.name}.svg"),
            algorithms,
        )
        list(futures)


if __name__ == "__main__":
    main()
