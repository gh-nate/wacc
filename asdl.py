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


class NotAST(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NotAST)


class ComplementTACKY(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, ComplementTACKY)


class NegateTACKY(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NegateTACKY)


class NotTACKY(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NotTACKY)


class NegASM(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NegASM)


class NotASM(UnaryOperator):
    def __eq__(self, o):
        return isinstance(o, NotASM)


class BinaryOperator(ABC):
    pass


class AddAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, AddAST)


class SubtractAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, SubtractAST)


class MultiplyAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, MultiplyAST)


class DivideAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, DivideAST)


class RemainderAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, RemainderAST)


class AndAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, AndAST)


class OrAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, OrAST)


class EqualAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, EqualAST)


class NotEqualAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, NotEqualAST)


class LessThanAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, LessThanAST)


class LessOrEqualAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, LessOrEqualAST)


class GreaterThanAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, GreaterThanAST)


class GreaterOrEqualAST(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, GreaterOrEqualAST)


class AddTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, AddTACKY)


class SubtractTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, SubtractTACKY)


class MultiplyTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, MultiplyTACKY)


class DivideTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, DivideTACKY)


class RemainderTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, RemainderTACKY)


class EqualTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, EqualTACKY)


class NotEqualTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, NotEqualTACKY)


class LessThanTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, LessThanTACKY)


class LessOrEqualTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, LessOrEqualTACKY)


class GreaterThanTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, GreaterThanTACKY)


class GreaterOrEqualTACKY(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, GreaterOrEqualTACKY)


class AddASM(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, AddASM)


class SubASM(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, SubASM)


class MultASM(BinaryOperator):
    def __eq__(self, o):
        return isinstance(o, MultASM)


class Exp(ABC):
    pass


@dataclass
class ConstantAST(Exp):
    i: int


@dataclass
class UnaryAST(Exp):
    unary_operator: UnaryOperator
    exp: Exp


@dataclass
class BinaryAST(Exp):
    binary_operator: BinaryOperator
    lhs: Exp
    rhs: Exp


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


class DxASM(Reg):
    def __eq__(self, o):
        return isinstance(o, DxASM)


class R10ASM(Reg):
    def __eq__(self, o):
        return isinstance(o, R10ASM)


class R11ASM(Reg):
    def __eq__(self, o):
        return isinstance(o, R11ASM)


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
class BinaryASM(Instruction):
    binary_operator: BinaryOperator
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


@dataclass
class BinaryTACKY(Instruction):
    binary_operator: BinaryOperator
    src1: Val
    src2: Val
    dst: Val


@dataclass
class CopyTACKY(Instruction):
    src: Val
    dst: Val


@dataclass
class Jump(Instruction):
    target: str


@dataclass
class JumpIfZero(Instruction):
    condition: Val
    target: str


@dataclass
class JumpIfNotZero(Instruction):
    condition: Val
    target: str


@dataclass
class Label(Instruction):
    identifier: str


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
