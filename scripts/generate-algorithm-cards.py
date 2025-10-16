#!/usr/bin/env python3

import fnmatch
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
    anki_tags: list[str] = field(hash=False, default_factory=lambda: ["3x3x3", "OLL"])
    # The visualiser generates the cube that will be solved by the algorithm. "Solved"
    # means the top face is yellow and the front face is blue. However, for consistency,
    # all generated icons should start in a well defined state which usually means that
    # the blue face is in front and the yellow is face on top. If the algorithm involves
    # whole cube rotations, the generated starting orientation may not match the desired
    # one. Since there is no way to tell the visualiser to start with a specific
    # orientation, the workaround is to use setup rotations at the start and end of the
    # algorithm to achieve the desired orientation.
    #
    # For example, if the algorithm is `x (R2 D2)(R U R') D2 (R U' R)` (PLL Ab), the
    # visualiser will generate a cube with the green face on top. While the permutation
    # still applies correctly, this is inconsistent with other PLL icons. To fix this,
    # the `x` rotation needs to be undone at the end by applying `x'`. This can be
    # achieved by setting `setup_rotation_after` to `x'`. The human-readable algorithm
    # remains unaffected, as the cube is solved regardless of orientation.
    _setup_rotation_before: Algorithm = Algorithm("")
    _setup_rotation_after: Algorithm = Algorithm("")

    @property
    def parameters(self) -> dict[str, str]:
        return {"sch": "ysssss"}

    @property
    def arrows(self) -> list[str]:
        return []

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return Algorithm(
            self._setup_rotation_before + self._alg + self._setup_rotation_after
        )


@dataclass(frozen=True)
class PLLAlgorithmConfig:
    name: str
    size: int
    _alg: Algorithm
    view: t.ClassVar[View] = "plan"
    arrows: list[str] = field(hash=False)
    # see comment in OLLAlgorithmConfig for explanation
    _setup_rotation_before: Algorithm = Algorithm("")
    _setup_rotation_after: Algorithm = Algorithm("")
    anki_tags: list[str] = field(hash=False, default_factory=lambda: ["3x3x3", "PLL"])

    @property
    def parameters(self) -> dict[str, str]:
        return {}

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return Algorithm(
            self._setup_rotation_before + self._alg + self._setup_rotation_after
        )


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
        Algorithm("x (R' U R') D2 (R U' R')(D2 R2)"),
        ["U0U2-s8", "U2U8-s8", "U8U0-s8"],
        _setup_rotation_after=Algorithm("x'"),
    ),
    PLLAlgorithmConfig(
        "Ab",
        3,
        Algorithm("x (R2 D2)(R U R') D2 (R U' R)"),
        ["U8U2-s8", "U0U8-s8", "U2U0-s8"],
        _setup_rotation_after=Algorithm("x'"),
    ),
    PLLAlgorithmConfig(
        "E",
        3,
        Algorithm("R2 U R' y (R U' R' U) (R U' R' U) (R U' R' U) y' R U' R2 "),
        ["U0U2", "U2U0", "U6U8", "U8U6"],
    ),
    PLLAlgorithmConfig(
        "F",
        3,
        Algorithm("(R' U' F')(R U R' U')(R' F)(R2 U')(R' U' R U) R' U R"),
        ["U1U7", "U7U1", "U2U8", "U8U2"],
    ),
    PLLAlgorithmConfig(
        "Ga",
        3,
        Algorithm("(R2' u)(R' U R' U')(R u') R2 y' (R' U R)"),
        ["U0U2-s8", "U2U6-s8", "U6U0-s8", "U1U3-s7", "U3U5-s7", "U5U1-s7"],
        _setup_rotation_after=Algorithm("y"),
    ),
    PLLAlgorithmConfig(
        "Gb",
        3,
        Algorithm("(R' U' R) y (R2 u)(R' U R U')(R u') R2"),
        ["U0U6-s8", "U6U8-s8", "U8U0-s8", "U1U7-s7", "U7U3-s7", "U3U1-s7"],
        _setup_rotation_after=Algorithm("y'"),
    ),
    PLLAlgorithmConfig(
        "Gc",
        3,
        Algorithm("(R2 u')(R U' R U)(R' u) R2 y (R U' R')"),
        ["U0U6-s8", "U6U8-s8", "U8U0-s8", "U7U3-s7", "U3U5-s7", "U5U7-s7"],
        _setup_rotation_after=Algorithm("y'"),
    ),
    PLLAlgorithmConfig(
        "Gd",
        3,
        Algorithm("(R U R') y' (R2 u')(R U' R' U)(R' u) R2"),
        ["U0U2-s8", "U2U6-s8", "U6U0-s8", "U1U3-s7", "U3U7-s7", "U7U1-s7"],
        _setup_rotation_after=Algorithm("y"),
    ),
    PLLAlgorithmConfig(
        "H",
        3,
        Algorithm("(M2' U' M2') U2 (M2' U' M2')"),
        ["U1U7", "U7U1", "U5U3", "U3U5"],
    ),
    PLLAlgorithmConfig(
        "Ja",
        3,
        Algorithm("(L' U2 L) U (L' U2) (R U') (L U R)'"),
        ["U0U6", "U6U0", "U3U7", "U7U3"],
    ),
    PLLAlgorithmConfig(
        "Jb",
        3,
        Algorithm("(R U R' F')(R U R' U')(R' F)(R2 U')(R' U')"),
        ["U2U8", "U8U2", "U5U7", "U7U5"],
    ),
    PLLAlgorithmConfig(
        "Na",
        3,
        Algorithm("(L U') R U2' (L' U) R' (L U') R U2' (L' U) R' U'"),
        ["U6U2", "U2U6", "U3U5", "U5U3"],
    ),
    PLLAlgorithmConfig(
        "Nb",
        3,
        Algorithm("(R' U) L' U2 (R U') L (R' U) L' U2 (R U') L U"),
        ["U0U8", "U8U0", "U3U5", "U5U3"],
    ),
    PLLAlgorithmConfig(
        "Ra",
        3,
        Algorithm("(R U2')(R' U2)(R B')(R' U' R U)(R B R2 U)"),
        ["U1U5", "U5U1", "U6U8", "U8U6"],
    ),
    PLLAlgorithmConfig(
        "Rb",
        3,
        Algorithm("(R' U2)(R U2')(R' F)(R U R' U')(R' F' R2 U')"),
        ["U0U2", "U2U0", "U5U7", "U7U5"],
    ),
    PLLAlgorithmConfig(
        "T",
        3,
        Algorithm("(R U R' U')(R' F)(R2 U')(R' U' R U) R' F'"),
        ["U3U5-s8", "U5U3-s8", "U2U8", "U8U2"],
    ),
    PLLAlgorithmConfig(
        "Ua",
        3,
        Algorithm("(R2 U')(R' U' R U)(R U)(R U' R)"),
        ["U5U1-s7", "U1U3-s7", "U3U5-s7"],
    ),
    PLLAlgorithmConfig(
        "Ub",
        3,
        Algorithm("(R2' U)(R U R' U')(R' U')(R' U R')"),
        ["U3U5-s7", "U5U7-s7", "U7U3-s7"],
    ),
    PLLAlgorithmConfig(
        "V",
        3,
        Algorithm("(R' U R' U') x2 y' (R' U R' U') l (R U' R' U) R U"),
        ["U1U5", "U5U1", "U0U8", "U8U0"],
        _setup_rotation_after=Algorithm("x' y'"),
    ),
    PLLAlgorithmConfig(
        "Y",
        3,
        Algorithm("F (R U')(R' U' R U)(R' F')(R U R' U')(R' F R F')"),
        ["U1U3", "U3U1", "U0U8", "U8U0"],
    ),
    PLLAlgorithmConfig(
        "Z",
        3,
        Algorithm("(R' U' R U') R U (R U' R' U) R U R2 U' R' (U2)"),
        ["U1U5", "U5U1", "U3U7", "U7U3"],
    ),
]


oll_algorithms: list[AlgorithmConfig] = [
    OLLAlgorithmConfig("OLL 01", 3, Algorithm("(R' U' R U' R' U2 R)")),
    OLLAlgorithmConfig("OLL 02", 3, Algorithm("(R' U2 R U R' U R)")),
    OLLAlgorithmConfig("OLL 03", 3, Algorithm("(R U R' U)(R U' R' U)(R U2 R')")),
    OLLAlgorithmConfig("OLL 04", 3, Algorithm("R U2 R2 U' R2 U' R2 U2 R")),
    OLLAlgorithmConfig("OLL 05", 3, Algorithm("x (R' U')(L U)(R U' L' U) x'")),
    OLLAlgorithmConfig("OLL 06", 3, Algorithm("(R' F)(R B')(R' F')(R B)")),
    OLLAlgorithmConfig("OLL 07", 3, Algorithm("R2 D (R' U2 R) D' (R' U2 R')")),
    OLLAlgorithmConfig("OLL 09", 3, Algorithm("(r U R' U') (M U R U' R')")),
    OLLAlgorithmConfig("OLL 10", 3, Algorithm("(R U R' U') (M' U R U' r')")),
    OLLAlgorithmConfig("OLL 11", 3, Algorithm("(R' U' F)(U R U' R') F' R")),
    OLLAlgorithmConfig("OLL 12", 3, Algorithm("(L U F')(U' L' U L) F L'")),
    OLLAlgorithmConfig("OLL 13", 3, Algorithm("F' (U' L' U L) F")),
    OLLAlgorithmConfig("OLL 14", 3, Algorithm("F (U R U' R') F'")),
    OLLAlgorithmConfig(
        "OLL 15", 3, Algorithm("(R' U' R U')(R' U R U) x' (R U' R' U) x")
    ),
    OLLAlgorithmConfig("OLL 16", 3, Algorithm("(R U R' U)(R U' R' U')(R' F R F')")),
    OLLAlgorithmConfig("OLL 17", 3, Algorithm("(r' U2 R U R' U r)")),
    OLLAlgorithmConfig("OLL 18", 3, Algorithm("(r U2 R' U' R U' r')")),
    OLLAlgorithmConfig("OLL 19", 3, Algorithm("F (R U R' U')(R U R' U') F'")),
    OLLAlgorithmConfig("OLL 20", 3, Algorithm("F' (L' U' L U)(L' U' L U) F")),
    OLLAlgorithmConfig("OLL 21", 3, Algorithm("(R B')(R2 F) R2 (B R2)(F' R)")),
    OLLAlgorithmConfig("OLL 22", 3, Algorithm("(R' F)(R2 B') R2 (F' R2)(B R')")),
    OLLAlgorithmConfig("OLL 23", 3, Algorithm("r' U2 (R U R' U') R U R' U r")),
    OLLAlgorithmConfig("OLL 24", 3, Algorithm("y r U R' U (R U' R' U) R U2 r'")),
    OLLAlgorithmConfig(
        "OLL 25", 3, Algorithm("(R' U' R) y' x' (R U' R' F)(R U R') x y")
    ),
    OLLAlgorithmConfig("OLL 26", 3, Algorithm("(R U R') y (R' F R U')(R' F' R)")),
    OLLAlgorithmConfig("OLL 27", 3, Algorithm("(R U2)(R2 F R F')(R U R')")),
    OLLAlgorithmConfig("OLL 28", 3, Algorithm("F (R U')(R' U' R U) R' F'")),
    OLLAlgorithmConfig("OLL 29", 3, Algorithm("M U (R U R' U')(R' F R F') M'")),
    OLLAlgorithmConfig("OLL 30", 3, Algorithm("F R' F R2 U' (R' U' R U) R' F2")),
    OLLAlgorithmConfig("OLL 31", 3, Algorithm("F (U R U' R') F' (R' U2 R U R' U R)")),
    OLLAlgorithmConfig("OLL 32", 3, Algorithm("(R' U' R U' R' U2 R) F (R U R' U') F'")),
    OLLAlgorithmConfig("OLL 33", 3, Algorithm("(r U R' U R U2 r')")),
    OLLAlgorithmConfig("OLL 34", 3, Algorithm("(r' U' R U' R' U2 r)")),
    OLLAlgorithmConfig("OLL 35", 3, Algorithm("r U R' U (R' F R F') R U2 r'")),
    OLLAlgorithmConfig("OLL 36", 3, Algorithm("F (R U R' U') F' U F (R U R' U') F'")),
    OLLAlgorithmConfig("OLL 37", 3, Algorithm("(L F')(L' U' L U) F U' L'")),
    OLLAlgorithmConfig("OLL 38", 3, Algorithm("(R' F)(R U R' U') F' U R")),
    OLLAlgorithmConfig("OLL 39", 3, Algorithm("(R U R' U')(R' F R F')")),
    OLLAlgorithmConfig("OLL 40", 3, Algorithm("F (R U R' U') F'")),
    OLLAlgorithmConfig("OLL 41", 3, Algorithm("(R U R' U') B' (R' F R F') B")),
    OLLAlgorithmConfig("OLL 42", 3, Algorithm("R' U' (R' F R F') U R")),
    OLLAlgorithmConfig("OLL 43", 3, Algorithm("f (R U R' U')(R U R' U') f'")),
    OLLAlgorithmConfig("OLL 44", 3, Algorithm("r' U' (r U' R' U)(R U' R' U) M U r")),
    OLLAlgorithmConfig("OLL 45", 3, Algorithm("(R U R' U)(R U') y (R U' R' F') y'")),
    OLLAlgorithmConfig("OLL 46", 3, Algorithm("R U2 R2 U' (R U' R' U2)(F R F')")),
    OLLAlgorithmConfig(
        "OLL 47", 3, Algorithm("x' (R U' R')(F' R U R') x y (R' U R) y'")
    ),
    OLLAlgorithmConfig("OLL 48", 3, Algorithm("(R' F R)(U R' F' R) y' (R U' R')")),
    OLLAlgorithmConfig("OLL 49", 3, Algorithm("(r U r')(R U R' U')(r U' r')")),
    OLLAlgorithmConfig("OLL 50", 3, Algorithm("(r' U' r)(R' U' R U)(r' U r)")),
    OLLAlgorithmConfig("OLL 51", 3, Algorithm("(R U2)(R2 F R F') U2 (R' F R F')")),
    OLLAlgorithmConfig("OLL 52", 3, Algorithm("F (R U R' U') F' f (R U R' U') f'")),
    OLLAlgorithmConfig("OLL 53", 3, Algorithm("f (R U R' U') f' U' F (R U R' U') F")),
    OLLAlgorithmConfig("OLL 54", 3, Algorithm("f (R U R' U') f' U F (R U R' U') F'")),
    OLLAlgorithmConfig("OLL 55", 3, Algorithm("(r U R' U R U2 (r2) U' R U' R' U2 r)")),
    OLLAlgorithmConfig("OLL 56", 3, Algorithm("M U (R U R' U') r (R2 F R F')")),
    OLLAlgorithmConfig("OLL 57", 3, Algorithm("(R U R' U)(R' F R F') U2 (R' F R F')")),
    OLLAlgorithmConfig("OLL 58", 3, Algorithm("M U (R U R' U') M2 (U R U' r')")),
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
        ["U13U2", "U2U13", "U14U1", "U1U14"],
        anki_tags=["4x4x4", "PLL", "parity"],
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
        t.Literal["all", "pll", "oll", "big-cube"],
        typer.Option(
            ...,
            help="Which algorithm set to generate: 'all' (default), 'pll' (3x3x3 PLL only), 'oll' (3x3x3 OLL only), or 'big-cube' (4x4x4+ algorithms only)",
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
        str | None,
        typer.Option(
            ...,
            help="Specific algorithms to generate. Only algorithms in the specified set will be considered. The value may be a glob to match several algorithms. Defaults to all algorithms in the set.",
        ),
    ] = "*",
):
    # Select which algorithms to generate based on user choice
    if algorithm_set == "pll":
        algorithms = pll_algorithms
        deckname = "Cubing::3x3x3::PLL"
    elif algorithm_set == "oll":
        algorithms = oll_algorithms
        deckname = "Cubing::3x3x3::OLL"
    elif algorithm_set == "big-cube":
        algorithms = big_cube_algorithms
        deckname = "Cubing::NxNxN::Parities and Edge Pairing"
    else:  # "all"
        algorithms = pll_algorithms + oll_algorithms + big_cube_algorithms
        deckname = "Cubing::Algorithms"

    if algorithm is not None:
        algorithms = [
            case for case in algorithms if fnmatch.fnmatch(case.name, algorithm)
        ]
        if len(algorithms) == 0:
            raise ValueError(f"Algorithm '{algorithm}' not found in selected set")

    case_fnames = {case: targetdir / f"{case.name}.{_FMT}" for case in algorithms}
    targetdir.mkdir(parents=True, exist_ok=True)
    if not skip_image_generation:
        download_images(algorithms, case_fnames, max_workers)
    create_anki_csv(algorithms, case_fnames, targetdir, deckname)


if __name__ == "__main__":
    app()
