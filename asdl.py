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
Block = type("Block", _bases, _dict)
BlockItem = type("BlockItem", _bases, _dict)
Declaration = type("Declaration", _bases, _dict)
Exp = type("Exp", _bases, _dict)
ForInit = type("ForInit", _bases, _dict)
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
    AND = auto()
    OR = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_OR_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_OR_EQUAL = auto()
    VAR_ASSIGN = auto()


class UnaryOperatorAST(Enum):
    COMPLEMENT = auto()
    NEGATE = auto()
    NOT = auto()


@dataclass
class ConstantAST(Exp):
    int: int


@dataclass
class VarAST(Exp):
    identifier: str


@dataclass
class UnaryAST(Exp):
    unop: UnaryOperatorAST
    exp: Exp


@dataclass
class BinaryAST(Exp):
    binop: BinaryOperatorAST
    lhs: Exp
    rhs: Exp


@dataclass
class AssignmentAST(Exp):
    lhs: Exp
    rhs: Exp


@dataclass
class ConditionalAST(Exp):
    condition: Exp
    e1: Exp
    e2: Exp


@dataclass
class ReturnAST(Statement):
    exp: Exp


@dataclass
class ExpressionAST(Statement):
    exp: Exp


@dataclass
class IfAST(Statement):
    condition: Exp
    then: Statement
    else_: Statement | None


@dataclass
class BreakAST(Statement):
    label: str


@dataclass
class ContinueAST(Statement):
    label: str


@dataclass
class WhileAST(Statement):
    condition: Exp
    body: Statement
    label: str


@dataclass
class DoWhileAST(Statement):
    body: Statement
    condition: Exp
    label: str


@dataclass
class ForAST(Statement):
    init: ForInit
    condition: Exp | None
    post: Exp | None
    body: Statement
    label: str


@dataclass
class CompoundAST(Statement):
    block: Block


class NullAST(Statement):
    def __eq__(self, o):
        return isinstance(o, NullAST)


@dataclass
class InitDeclAST(ForInit):
    decl: Declaration


@dataclass
class InitExpAST(ForInit):
    exp: Exp | None


@dataclass
class DeclarationAST(Declaration):
    name: str
    init: Exp | None


@dataclass
class BlockAST(Block):
    items: list[BlockItem]


@dataclass
class SAST(BlockItem):
    statement: Statement


@dataclass
class DAST(BlockItem):
    declaration: Declaration


@dataclass
class FunctionAST(FunctionDefinition):
    name: str
    body: Block


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
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_OR_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_OR_EQUAL = auto()


class UnaryOperatorTACKY(Enum):
    COMPLEMENT = auto()
    NEGATE = auto()
    NOT = auto()


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
    unop: UnaryOperatorTACKY
    src: Val
    dst: Val


@dataclass
class BinaryTACKY(Instruction):
    binop: BinaryOperatorTACKY
    src1: Val
    src2: Val
    dst: Val


@dataclass
class CopyTACKY(Instruction):
    src: Val
    dst: Val


@dataclass
class JumpTACKY(Instruction):
    target: str


@dataclass
class JumpIfZeroTACKY(Instruction):
    condition: Val
    target: str


@dataclass
class JumpIfNotZeroTACKY(Instruction):
    condition: Val
    target: str


@dataclass
class LabelTACKY(Instruction):
    identifier: str


@dataclass
class FunctionTACKY(FunctionDefinition):
    identifier: str
    body: list[Instruction]


@dataclass
class ProgramTACKY(FunctionDefinition):
    function_definition: FunctionDefinition


# -------------------------------------------------------------------------------


class RegASM(Enum):
    AX = auto()
    DX = auto()
    R10 = auto()
    R11 = auto()


class CondCodeASM(Enum):
    E = "e"
    NE = "ne"
    G = "g"
    GE = "ge"
    L = "l"
    LE = "le"


@dataclass
class ImmASM(Operand):
    int: int


@dataclass
class RegisterASM(Operand):
    reg: RegASM


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
class MovASM(Instruction):
    src: Operand
    dst: Operand


@dataclass
class UnaryASM(Instruction):
    unop: UnaryOperatorASM
    operand: Operand


@dataclass
class BinaryASM(Instruction):
    binop: BinaryOperatorASM
    o1: Operand
    o2: Operand


@dataclass
class CmpASM(Instruction):
    o1: Operand
    o2: Operand


@dataclass
class IdivASM(Instruction):
    operand: Operand


class CdqASM(Instruction):
    def __eq__(self, o):
        return isinstance(o, CdqASM)


@dataclass
class JmpASM(Instruction):
    identifier: str


@dataclass
class JmpCcASM(Instruction):
    cond_code: CondCodeASM
    identifier: str


@dataclass
class SetCcASM(Instruction):
    cond_code: CondCodeASM
    operand: Operand


@dataclass
class LabelASM(Instruction):
    identifier: str


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
