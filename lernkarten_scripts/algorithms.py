import typing as t
from dataclasses import dataclass, field, replace

Algorithm = t.NewType("Algorithm", str)
type FrontColour = t.Literal["RED", "BLUE", "ORANGE", "GREEN"]
type View = t.Literal["plan", "trans"]
type AlgorithmConfig = (
    OLLAlgorithmConfig
    | PLLAlgorithmConfig
    | FrontAlgorithmConfig
    | GeneralAlgorithmConfig
)


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

    def extend_anki_tags(self, tags: list[str]) -> "OLLAlgorithmConfig":
        return OLLAlgorithmConfig(
            name=self.name,
            size=self.size,
            _alg=self._alg,
            _setup_rotation_before=self._setup_rotation_before,
            _setup_rotation_after=self._setup_rotation_after,
            anki_tags=self.anki_tags + tags,
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
    view: View | None
    anki_tags: list[str] = field(hash=False)
    arrows: list[str] = field(default_factory=list, hash=False)
    parameters: dict[str, str] = field(default_factory=dict, hash=False)

    def human_algorithm(self) -> Algorithm:
        return self._alg

    def visualiser_algorithm(self) -> Algorithm:
        return self._alg


PLL: list[AlgorithmConfig] = [
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
        Algorithm("(R' U L' U2) (R U' R' U2 R) L U'"),
        ["U0U2", "U2U0", "U1U3", "U3U1"],
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
        Algorithm("z (R' U R') D (R2 U' R) (U D') (R' D R2 U' R D')"),
        ["U0U8", "U8U0", "U1U7", "U7U1"],
        _setup_rotation_after=Algorithm("z'"),
    ),
    PLLAlgorithmConfig(
        "Nb",
        3,
        Algorithm("(R' U R U') (R' F' U') (F R U) (R' F R' F') (R U' R)"),
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

OLL: list[AlgorithmConfig] = [
    # All Edges Oriented Correctly
    OLLAlgorithmConfig(
        "OCLL1 - 21", 3, Algorithm("(R U R' U)(R U' R' U)(R U2 R')")
    ).extend_anki_tags(["2-Look-OLL"]),
    OLLAlgorithmConfig(
        "OCLL2 - 22", 3, Algorithm("R U2 R2 U' R2 U' R2 U2 R")
    ).extend_anki_tags(["2-Look-OLL"]),
    OLLAlgorithmConfig(
        "OCLL3 - 23", 3, Algorithm("R2 D (R' U2 R) D' (R' U2 R')")
    ).extend_anki_tags(["2-Look-OLL"]),
    OLLAlgorithmConfig(
        "OCLL4 - 24", 3, Algorithm("(r U R' U') (r' F R F')")
    ).extend_anki_tags(["2-Look-OLL"]),
    OLLAlgorithmConfig(
        "OCLL5 - 25", 3, Algorithm("x (R' U R) D' (R' U' R) D x'")
    ).extend_anki_tags(["2-Look-OLL"]),
    OLLAlgorithmConfig(
        "OCLL6 - 26", 3, Algorithm("R' U' R U' R' U2 R")
    ).extend_anki_tags(["2-Look-OLL"]),
    OLLAlgorithmConfig("OCLL7 - 27", 3, Algorithm("R U R' U R U2 R'")).extend_anki_tags(
        ["2-Look-OLL"]
    ),
    # T-Shapes
    OLLAlgorithmConfig("T1 - 33", 3, Algorithm("(R U R' U')(R' F R F')")),
    OLLAlgorithmConfig("T2 - 45", 3, Algorithm("F (R U R' U') F'")),
    # Squares
    OLLAlgorithmConfig("S1 - 5", 3, Algorithm("(r' U2 R U R' U r)")),
    OLLAlgorithmConfig("S2 - 6", 3, Algorithm("(r U2 R' U' R U' r')")),
    # C-Shapes
    OLLAlgorithmConfig("C1 - 34", 3, Algorithm("(R U R2' U') (R' F R U) R U' F'")),
    OLLAlgorithmConfig("C2 - 46", 3, Algorithm("R' U' (R' F R F') U R")),
    # W-Shapes
    OLLAlgorithmConfig("W1 - 36", 3, Algorithm("(R' U' R U')(R' U R U) (l U' R' U) x")),
    OLLAlgorithmConfig("W2 - 38", 3, Algorithm("(R U R' U)(R U' R' U')(R' F R F')")),
    # Corners Correct, Edges Flipped
    OLLAlgorithmConfig("E1 - 28", 3, Algorithm("(r U R' U') M (U R U' R')")),
    OLLAlgorithmConfig("E2 - 57", 3, Algorithm("(R U R' U') M' (U R U' r')")),
    # P-Shapes
    OLLAlgorithmConfig("P1 - 31", 3, Algorithm("(R' U' F)(U R U' R') F' R")),
    OLLAlgorithmConfig("P2 - 32", 3, Algorithm("R U B' (U' R' U) (R B R')")),
    OLLAlgorithmConfig("P3 - 43", 3, Algorithm("F' U' L' U L F")),
    OLLAlgorithmConfig("P4 - 44", 3, Algorithm("f (R U R' U') f'")),
    # I-Shapes
    OLLAlgorithmConfig("I1 - 51", 3, Algorithm("f (R U R' U')(R U R' U') f'")),
    OLLAlgorithmConfig("I2 - 52", 3, Algorithm("(R U R' U R U') y (R U' R') F'")),
    OLLAlgorithmConfig("I3 - 55", 3, Algorithm("R U2 R2 U' (R U' R' U2) (F R F')")),
    OLLAlgorithmConfig(
        "I4 - 56", 3, Algorithm("r' U' r (U' R' U R) (U' R' U R) r' U r")
    ),
    # Fish Shapes
    OLLAlgorithmConfig("F1 - 9", 3, Algorithm("(R U R' U') R' F (R2 U R' U') F'")),
    OLLAlgorithmConfig("F2 - 10", 3, Algorithm("(R U R' U) (R' F R F') (R U2' R')")),
    OLLAlgorithmConfig("F3 - 35", 3, Algorithm("(R U2) (R2 F R F') (R U2 R')")),
    OLLAlgorithmConfig("F4 - 37", 3, Algorithm("F (R U' R' U') (R U R' F')")),
    # Knight Move Shapes
    OLLAlgorithmConfig("K1 - 13", 3, Algorithm("(r U' r') (U' r U r') y' (R' U R)")),
    OLLAlgorithmConfig("K2 - 14", 3, Algorithm("(R' F R) (U R' F' R) y' (R U' R')")),
    OLLAlgorithmConfig("K3 - 15", 3, Algorithm("(r' U' r) (R' U' R U) (r' U r)")),
    OLLAlgorithmConfig("K4 - 16", 3, Algorithm("(r U r') (R U R' U') (r U' r')")),
    # Awkward Shapes
    OLLAlgorithmConfig(
        "A1 - 29", 3, Algorithm("(R U R' U') (R U' R') (F' U' F) (R U R')")
    ),
    OLLAlgorithmConfig("A2 - 30", 3, Algorithm("F U (R U2 R' U') (R U2 R' U') F'")),
    OLLAlgorithmConfig("A3 - 41", 3, Algorithm("(R U R' U R U2' R') F (R U R' U') F'")),
    OLLAlgorithmConfig(
        "A4 - 42", 3, Algorithm("(R' U' R U' R' U2 R) F (R U R' U') F'")
    ),
    # L-Shapes
    OLLAlgorithmConfig("L1 - 47", 3, Algorithm("F' (L' U' L U)(L' U' L U) F")),
    OLLAlgorithmConfig("L2 - 48", 3, Algorithm("F (R U R' U')(R U R' U') F'")),
    OLLAlgorithmConfig("L3 - 49", 3, Algorithm("r U' r2' U r2 U r2' U' r")),
    OLLAlgorithmConfig("L4 - 50", 3, Algorithm("r' U r2 U' r2' U' r2 U r'")),
    OLLAlgorithmConfig("L5 - 53", 3, Algorithm("(r' U' R U') (R' U R U') R' U2 r")),
    OLLAlgorithmConfig("L6 - 54", 3, Algorithm("(r U R' U) (R U' R' U) R U2' r'")),
    # Lightning Bolts
    OLLAlgorithmConfig("B1 - 7", 3, Algorithm("r U R' U R U2 r'")),
    OLLAlgorithmConfig("B2 - 8", 3, Algorithm("r' U' R U' R' U2 r")),
    OLLAlgorithmConfig("B3 - 11", 3, Algorithm("r' (R2 U R' U R U2 R') U M'")),
    OLLAlgorithmConfig("B4 - 12", 3, Algorithm("M' (R' U' R U' R' U2 R) U' M")),
    OLLAlgorithmConfig("B5 - 39", 3, Algorithm("(L F')(L' U' L U) F U' L'")),
    OLLAlgorithmConfig("B6 - 40", 3, Algorithm("(R' F)(R U R' U') F' U R")),
    # No Edges Flipped Correctly
    OLLAlgorithmConfig("O1 - 1", 3, Algorithm("(R U2)(R2 F R F') U2 (R' F R F')")),
    OLLAlgorithmConfig("O2 - 2", 3, Algorithm("F (R U R' U') F' f (R U R' U') f'")),
    OLLAlgorithmConfig("O3 - 3", 3, Algorithm("f (R U R' U') f' U' F (R U R' U') F'")),
    OLLAlgorithmConfig("O4 - 4", 3, Algorithm("f (R U R' U') f' U F (R U R' U') F'")),
    OLLAlgorithmConfig(
        "O5 - 17", 3, Algorithm("(R U R' U) (R' F R F') U2 (R' F R F')")
    ),
    OLLAlgorithmConfig("O6 - 18", 3, Algorithm("r U R' U R U2 r2 U' R U' R' U2 r")),
    OLLAlgorithmConfig("O7 - 19", 3, Algorithm("r' U2 R U R' U r2 U2 R' U' R U' r'")),
    OLLAlgorithmConfig("O8 - 20", 3, Algorithm("M U (R U R' U') M2 (U R U' r')")),
]

TWO_LOOK_OLL: list[AlgorithmConfig] = [
    replace(cur, name=f"2LOLL {n}")
    for n, cur in enumerate(
        filter(lambda alg: "2-Look-OLL" in alg.anki_tags, OLL), start=1
    )
]


BIG_CUBE: list[AlgorithmConfig] = [
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
