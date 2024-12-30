# Copyright (C) 2024 gh-nate
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto


_bases, _dict = (ABC,), {}
Exp = type("Exp", _bases, _dict)
FunctionDefinition = type("FunctionDefinition", _bases, _dict)
Instruction = type("Instruction", _bases, _dict)
Operand = type("Operand", _bases, _dict)
Program = type("Program", _bases, _dict)
Statement = type("Statement", _bases, _dict)
Val = type("Val", _bases, _dict)

# -------------------------------------------------------------------------------


class BinaryOperatorAST(Enum):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()


class UnaryOperatorAST(Enum):
    COMPLEMENT = auto()
    NEGATE = auto()


@dataclass
class ConstantAST(Exp):
    int: int


@dataclass
class UnaryAST(Exp):
    op: UnaryOperatorAST
    exp: Exp


@dataclass
class BinaryAST(Exp):
    op: BinaryOperatorAST
    lhs: Exp
    rhs: Exp


@dataclass
class ReturnAST(Statement):
    exp: Exp


@dataclass
class FunctionAST(FunctionDefinition):
    name: str
    body: Statement


@dataclass
class ProgramAST(Program):
    function_definition: FunctionDefinition


# -------------------------------------------------------------------------------


class BinaryOperatorTACKY(Enum):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()


class UnaryOperatorTACKY(Enum):
    COMPLEMENT = auto()
    NEGATE = auto()


@dataclass
class ConstantTACKY(Val):
    int: int


@dataclass
class VarTACKY(Val):
    identifier: str


@dataclass
class ReturnTACKY(Instruction):
    val: Val


@dataclass
class UnaryTACKY(Instruction):
    op: UnaryOperatorTACKY
    src: Val
    dst: Val


@dataclass
class BinaryTACKY(Instruction):
    op: BinaryOperatorTACKY
    src1: Val
    src2: Val
    dst: Val


@dataclass
class FunctionTACKY(FunctionDefinition):
    identifier: str
    body: list[Instruction]


@dataclass
class ProgramTACKY(Program):
    function_definition: FunctionDefinition


# -------------------------------------------------------------------------------


class RegASM(Enum):
    AX = auto()
    DX = auto()
    R10 = auto()
    R11 = auto()


@dataclass
class ImmASM(Operand):
    int: int


@dataclass
class RegisterASM(Operand):
    reg: RegASM


@dataclass
class MovASM(Instruction):
    src: Operand
    dst: Operand


@dataclass
class PseudoASM(Operand):
    identifier: str


@dataclass
class StackASM(Operand):
    int: int


class BinaryOperatorASM(Enum):
    ADD = "addl"
    SUB = "subl"
    MULT = "imull"


class UnaryOperatorASM(Enum):
    NEG = "negl"
    NOT = "notl"


@dataclass
class UnaryASM(Instruction):
    op: UnaryOperatorASM
    operand: Operand


@dataclass
class BinaryASM(Instruction):
    op: BinaryOperatorASM
    o1: Operand
    o2: Operand


@dataclass
class IdivASM(Instruction):
    operand: Operand


class CdqASM(Instruction):
    def __eq__(self, o):
        return isinstance(o, CdqASM)


@dataclass
class AllocateStackASM(Instruction):
    int: int


class RetASM(Instruction):
    def __eq__(self, o):
        return isinstance(o, RetASM)


@dataclass
class FunctionASM(FunctionDefinition):
    name: str
    instructions: list[Instruction]


@dataclass
class ProgramASM(Program):
    function_definition: FunctionDefinition
