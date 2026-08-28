from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    BRIVLA = auto()
    GANAI = auto()
    GI = auto()
    GI_E = auto()
    NERBEI = auto()

    LI = auto()
    LA = auto()
    LU = auto()
    LU_O = auto()
    ZO_E = auto()

    XU = auto()
    MA = auto()

    BE = auto()
    BE_O = auto()

    DU = auto()
    NA = auto()
    SU_I = auto()
    VU_U = auto()
    PI_I = auto()
    PI = auto()
    FE_I = auto()
    ZMADU = auto()
    MLECA = auto()

    X1 = auto()
    X2 = auto()
    X3 = auto()
    X4 = auto()
    X5 = auto()

    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    DOT = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: object
    line: int
    column: int

    def __repr__(self) -> str:
        return (
            f"Token({self.type.name}, {self.value!r}, "
            f"line={self.line}, column={self.column})"
        )
