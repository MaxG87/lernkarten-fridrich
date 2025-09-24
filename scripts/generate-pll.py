#!/usr/bin/env python3

import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PLLCase:
    name: str
    alg: str
    arrows: list[str]


pll_arrows_url = (
    "https://visualcube.api.cubing.net?fmt=svg&pzl=3&view=plan&ac=black&case="
)

plls = [
    PLLCase(
        "Aa", "x (R' U R') D2 (R U' R')(D2 R2) x'", ["U0U2-s8", "U2U8-s8", "U8U0-s8"]
    ),
    PLLCase(
        "Ab", "x (R2 D2)(R U R') D2 (R U' R) x'", ["U8U2-s8", "U0U8-s8", "U2U0-s8"]
    ),
    PLLCase(
        "E",
        "R2 U R' y (R U' R' U) (R U' R' U) (R U' R' U) y' R U' R2 ",
        ["U0U2", "U2U0", "U6U8", "U8U6"],
    ),
    PLLCase(
        "F",
        "y (R' U' F')(R U R' U')(R' F)(R2 U')(R' U' R U) R' U R",
        ["U0U2", "U2U0", "U3U5", "U5U3"],
    ),
    PLLCase(
        "Ga",
        "(R2' u)(R' U R' U')(R u') R2 y' (R' U R)",
        ["U0U2-s8", "U2U6-s8", "U6U0-s8", "U1U3-s7", "U3U5-s7", "U5U1-s7"],
    ),
    PLLCase(
        "Gb",
        "R'U'RyR2uR'URU'Ru'R2",
        ["U0U6-s8", "U6U8-s8", "U8U0-s8", "U1U7-s7", "U7U3-s7", "U3U1-s7"],
    ),
    PLLCase(
        "Gc",
        "R2u'RU'RUR'uR2yRU'R'",
        ["U0U6-s8", "U6U8-s8", "U8U0-s8", "U7U3-s7", "U3U5-s7", "U5U7-s7"],
    ),
    PLLCase(
        "Gd",
        "RUR'y'R2u'RU'R'UR'uR2",
        ["U0U2-s8", "U2U6-s8", "U6U0-s8", "U1U3-s7", "U3U7-s7", "U7U1-s7"],
    ),
    PLLCase("H", "M2UM2U2M2UM2", ["U1U7", "U7U1", "U5U3", "U3U5"]),
    PLLCase("Ja", "y'L'U2LUL'U2RU'LUR'", ["U0U2", "U2U0", "U3U1", "U1U3"]),
    PLLCase("Jb", "RUR'F'RUR'U'R'FR2U'R'U'", ["U2U8", "U8U2", "U5U7", "U7U5"]),
    PLLCase("Na", "LU'RU2L'UR'LU'RU2L'UR'", ["U1U7", "U7U1", "U0U8", "U8U0"]),
    PLLCase("Nb", "R'UL'U2RU'LR'UL'U2RU'L", ["U1U7", "U7U1", "U6U2", "U2U6"]),
    PLLCase("Ra", "y'LU2L'U2LF'L'U'LULFL2", ["U1U3", "U3U1", "U2U8", "U8U2"]),
    PLLCase("Rb", "R'U2RU2R'FRUR'U'R'F'R2", ["U0U2", "U2U0", "U5U7", "U7U5"]),
    PLLCase("T", "RUR'U'R'FR2U'R'U'RUR'F'", ["U3U5-s8", "U5U3-s8", "U2U8", "U8U2"]),
    PLLCase("Ua", "y2R2U'R'U'RURURU'R", ["U5U3-s7", "U3U7-s7", "U7U5-s7"]),
    PLLCase("Ub", "y2R'UR'U'R'U'R'URUR2", ["U3U5-s7", "U5U7-s7", "U7U3-s7"]),
    PLLCase("V", "R'UR'd'R'F'R2U'R'UR'FRF", ["U1U5", "U5U1", "U0U8", "U8U0"]),
    PLLCase("Y", "FRU'R'U'RUR'F'RUR'U'R'FRF'", ["U1U3", "U3U1", "U0U8", "U8U0"]),
    PLLCase("Z", "M2UM2UM'U2M2U2M'", ["U1U3", "U3U1", "U5U7", "U7U5"]),
]


def download_case(case: PLLCase, destfile: Path) -> None:
    raw_alg = case.alg
    for char in "() ":
        raw_alg = raw_alg.replace(char, "")
    params = raw_alg + "&arw=" + ",".join(case.arrows)
    urllib.request.urlretrieve(f"{pll_arrows_url}{params}", destfile)


def main():
    parser = argparse.ArgumentParser(
        description="Generate PLL cases with arrows in SVG format."
    )
    parser.add_argument("tagetdir", help="Target directory for output files")
    args = parser.parse_args()

    target_dir = Path(args.tagetdir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor() as executor:
        futures = executor.map(
            lambda case: download_case(case, target_dir / f"{case.name}.svg"), plls
        )
        list(futures)


if __name__ == "__main__":
    main()
