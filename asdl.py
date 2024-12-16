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


class BinaryOperator(Enum):
    pass


class BinaryOperatorAST(BinaryOperator):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()
    AND = auto()
    OR = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_OR_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_OR_EQUAL = auto()


class BinaryOperatorTACKY(BinaryOperator):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()


class BinaryOperatorASM(BinaryOperator):
    ADD = auto()
    SUB = auto()
    MULT = auto()


class UnaryOperator(Enum):
    pass


class UnaryOperatorAST(UnaryOperator):
    COMPLEMENT = auto()
    NEGATE = auto()
    NOT = auto()


class UnaryOperatorTACKY(UnaryOperator):
    COMPLEMENT = auto()
    NEGATE = auto()


class UnaryOperatorASM(UnaryOperator):
    NEG = auto()
    NOT = auto()


class Reg(Enum):
    AX = auto()
    DX = auto()
    R10 = auto()
    R11 = auto()


class Operand(ABC):
    pass


@dataclass
class ImmASM(Operand):
    int: int


@dataclass
class RegASM(Operand):
    reg: Reg


@dataclass
class PseudoASM(Operand):
    identifier: str


@dataclass
class StackASM(Operand):
    int: int


class Val(ABC):
    pass


@dataclass
class ConstantTACKY(Val):
    int: int


@dataclass
class VarTACKY(Val):
    identifier: str


class Exp(ABC):
    pass


@dataclass
class ConstantAST(Exp):
    int: int


@dataclass
class UnaryAST(Exp):
    unary_operator: UnaryOperatorAST
    exp: Exp


@dataclass
class BinaryAST(Exp):
    binary_operator: BinaryOperatorAST
    lhs: Exp
    rhs: Exp


class Statement(ABC):
    pass


@dataclass
class ReturnAST(Statement):
    exp: Exp


class Instruction(ABC):
    pass


@dataclass
class ReturnTACKY(Instruction):
    val: Val


@dataclass
class UnaryTACKY(Instruction):
    unary_operator: UnaryOperatorTACKY
    src: Val
    dst: Val


@dataclass
class BinaryTACKY(Instruction):
    binary_operator: BinaryOperatorTACKY
    src1: Val
    src2: Val
    dst: Val


@dataclass
class MovASM(Instruction):
    src: Operand
    dst: Operand


@dataclass
class UnaryASM(Instruction):
    unop: UnaryOperatorASM
    op: Operand


@dataclass
class BinaryASM(Instruction):
    binop: BinaryOperatorASM
    lhs: Operand
    rhs: Operand


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


class FunctionDefinition(ABC):
    pass


@dataclass
class FunctionAST(FunctionDefinition):
    name: str
    body: Statement


@dataclass
class FunctionTACKY(FunctionDefinition):
    identifier: str
    body: list[Instruction]


@dataclass
class FunctionASM(FunctionDefinition):
    name: str
    instructions: list[Instruction]


class Program(ABC):
    pass


@dataclass
class ProgramAST(Program):
    function_definition: FunctionDefinition


@dataclass
class ProgramTACKY(Program):
    function_definition: FunctionDefinition


@dataclass
class ProgramASM(Program):
    function_definition: FunctionDefinition
