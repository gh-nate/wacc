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

# -------------------------------------------------------------------------------


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


@dataclass
class ImmASM(Operand):
    int: int


class RegisterASM(Operand):
    def __eq__(self, o):
        return isinstance(o, RegisterASM)


@dataclass
class MovASM(Instruction):
    src: Operand
    dst: Operand


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
