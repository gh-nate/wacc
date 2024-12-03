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


class UnaryOperator(ABC):
    pass


class ComplementAST(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, ComplementAST)


class NegateAST(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NegateAST)


class ComplementTACKY(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, ComplementTACKY)


class NegateTACKY(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NegateTACKY)


class NegASM(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NegASM)


class NotASM(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NotASM)


class Exp(ABC):
    pass


@dataclass
class ConstantAST(Exp):
    i: int


@dataclass
class UnaryAST(Exp):
    unary_operator: UnaryOperator
    exp: Exp


class Val(ABC):
    pass


@dataclass
class ConstantTACKY(Val):
    i: int


@dataclass
class VarTACKY(Val):
    identifier: str


class Operand(ABC):
    pass


@dataclass
class ImmASM(Operand):
    i: int


class Reg(ABC):
    pass


class AxASM(Reg):
    def __eq__(self, o):
        return isinstance(o, AxASM)


class R10ASM(Reg):
    def __eq__(self, o):
        return isinstance(o, R10ASM)


@dataclass
class RegASM(Operand):
    reg: Reg


@dataclass
class PseudoASM(Operand):
    identifier: str


@dataclass
class StackASM(Operand):
    i: int


class Statement(ABC):
    pass


@dataclass
class ReturnAST(Statement):
    exp: Exp


class Instruction(ABC):
    pass


@dataclass
class MovASM(Instruction):
    src: Operand
    dst: Operand


@dataclass
class UnaryASM(Instruction):
    unary_operator: UnaryOperator
    operand: Operand


@dataclass
class AllocateStackASM(Instruction):
    i: int


class RetASM(Instruction):
    def __eq__(self, o):
        return isinstance(o, RetASM)


@dataclass
class ReturnTACKY(Instruction):
    val: Val


@dataclass
class UnaryTACKY(Instruction):
    unary_operator: UnaryOperator
    src: Val
    dst: Val


class FunctionDefinition(ABC):
    pass


@dataclass
class FunctionAST(FunctionDefinition):
    name: str
    body: Statement


@dataclass
class FunctionASM(FunctionDefinition):
    name: str
    instructions: list[Instruction]


@dataclass
class FunctionTACKY(FunctionDefinition):
    identifier: str
    body: list[Instruction]


class Program(ABC):
    pass


@dataclass
class ProgramAST(Program):
    function_definition: FunctionDefinition


@dataclass
class ProgramASM(Program):
    function_definition: FunctionDefinition


@dataclass
class ProgramTACKY(Program):
    function_definition: FunctionDefinition
