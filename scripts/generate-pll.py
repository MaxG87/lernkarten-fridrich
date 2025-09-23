#!/usr/bin/env python3

import argparse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

pll_arrows_url = (
    "https://visualcube.api.cubing.net?fmt=svg&pzl=3&view=plan&ac=black&case="
)
plls = {
    "Aa": "R'FR'B2RF'R'B2R2&arw=U0U2-s8,U2U8-s8,U8U0-s8",
    "Ab": "l'R'D2RUR'D2RU'Rx'&arw=U8U2-s8,U0U8-s8,U2U0-s8",
    "E": "yLR'U'RUL'U'R'URrUR'U'r'FRF'&arw=U0U6,U6U0,U2U8,U8U2",
    "F": "y'R'URU'R2F'U'FURFR'F'R2&arw=U2U8,U8U2,U1U7,U7U1",
    "Ga": "R2uR'UR'U'Ru'R2y'R'UR&arw=U0U2-s8,U2U6-s8,U6U0-s8,U1U3-s7,U3U5-s7,U5U1-s7",
    "Gb": "R'U'RyR2uR'URU'Ru'R2&arw=U0U6-s8,U6U8-s8,U8U0-s8,U1U7-s7,U7U3-s7,U3U1-s7",
    "Gc": "R2u'RU'RUR'uR2yRU'R'&arw=U0U6-s8,U6U8-s8,U8U0-s8,U7U3-s7,U3U5-s7,U5U7-s7",
    "Gd": "RUR'y'R2u'RU'R'UR'uR2&arw=U0U2-s8,U2U6-s8,U6U0-s8,U1U3-s7,U3U7-s7,U7U1-s7",
    "H": "M2UM2U2M2UM2&arw=U1U7,U7U1,U5U3,U3U5",
    "Ja": "y'L'U2LUL'U2RU'LUR'&arw=U0U2,U2U0,U3U1,U1U3",
    "Jb": "RUR'F'RUR'U'R'FR2U'R'U'&arw=U2U8,U8U2,U5U7,U7U5",
    "Na": "LU'RU2L'UR'LU'RU2L'UR'&arw=U1U7,U7U1,U0U8,U8U0",
    "Nb": "R'UL'U2RU'LR'UL'U2RU'L&arw=U1U7,U7U1,U6U2,U2U6",
    "Ra": "y'LU2L'U2LF'L'U'LULFL2&arw=U1U3,U3U1,U2U8,U8U2",
    "Rb": "R'U2RU2R'FRUR'U'R'F'R2&arw=U0U2,U2U0,U5U7,U7U5",
    "T": "RUR'U'R'FR2U'R'U'RUR'F'&arw=U3U5-s8,U5U3-s8,U2U8,U8U2",
    "Ua": "y2R2U'R'U'RURURU'R&arw=U5U3-s7,U3U7-s7,U7U5-s7",
    "Ub": "y2R'UR'U'R'U'R'URUR2&arw=U3U5-s7,U5U7-s7,U7U3-s7",
    "V": "R'UR'd'R'F'R2U'R'UR'FRF&arw=U1U5,U5U1,U0U8,U8U0",
    "Y": "FRU'R'U'RUR'F'RUR'U'R'FRF'&arw=U1U3,U3U1,U0U8,U8U0",
    "Z": "M2UM2UM'U2M2U2M'&arw=U1U3,U3U1,U5U7,U7U5",
}


def download_alg(alg: str, destfile: Path) -> None:
    urllib.request.urlretrieve(f"{pll_arrows_url}{alg}", destfile)


def main():
    parser = argparse.ArgumentParser(
        description="Generate PLL cases with arrows in SVG format."
    )
    parser.add_argument("tagetdir", help="Target directory for output files")
    args = parser.parse_args()

    target_dir = Path(args.tagetdir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor() as executor:
        executor.map(
            lambda case_alg: download_alg(
                case_alg[1], target_dir / f"{case_alg[0]}.svg"
            ),
            plls.items(),
        )


if __name__ == "__main__":
    main()
