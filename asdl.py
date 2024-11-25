# Copyright (c) 2024 gh-nate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from abc import ABC
from typing import NewType


class Program(ABC):
    pass


class FunctionDefinition(ABC):
    pass


class Instruction(ABC):
    pass


class Statement(ABC):
    pass


class Exp(ABC):
    pass


class Val(ABC):
    pass


class UnaryOperator(ABC):
    pass


class Operand(ABC):
    pass


class ProgramAstNode(Program):
    def __init__(self, function_definition: FunctionDefinition) -> None:
        self.function_definition = function_definition
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ProgramAstNode):
            raise NotImplementedError
        return self.function_definition == o.function_definition

    def __repr__(self) -> str:
        return f"Program({self.function_definition!r})"


class ProgramAssemblyConstruct(Program):
    def __init__(self, function_definition: FunctionDefinition) -> None:
        self.function_definition = function_definition
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ProgramAssemblyConstruct):
            raise NotImplementedError
        return self.function_definition == o.function_definition

    def __repr__(self) -> str:
        return f"Program({self.function_definition!r})"


class ProgramTacky(Program):
    def __init__(self, function_definition: FunctionDefinition) -> None:
        self.function_definition = function_definition
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ProgramTacky):
            raise NotImplementedError
        return self.function_definition == o.function_definition

    def __repr__(self) -> str:
        return f"Program({self.function_definition!r})"


Identifier = NewType("Identifier", str)


class FunctionAstNode(FunctionDefinition):
    def __init__(self, name: Identifier, body: Statement) -> None:
        self.name = name
        self.body = body
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, FunctionAstNode):
            raise NotImplementedError
        return self.name == o.name and self.body == o.body

    def __repr__(self) -> str:
        return f"Function({self.name}, {self.body!r})"


class FunctionAssemblyConstruct(FunctionDefinition):
    def __init__(self, name: Identifier, instructions: list[Instruction]) -> None:
        self.name = name
        self.instructions = instructions
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, FunctionAssemblyConstruct):
            raise NotImplementedError
        return self.name == o.name and self.instructions == o.instructions

    def __repr__(self) -> str:
        return f"Function({self.name}, {self.instructions!r})"


class FunctionTacky(FunctionDefinition):
    def __init__(self, identifier: Identifier, instructions: list[Instruction]) -> None:
        self.identifier = identifier
        self.instructions = instructions
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, FunctionTacky):
            raise NotImplementedError
        return self.identifier == o.identifier and self.instructions == o.instructions

    def __repr__(self) -> str:
        return f"Function({self.identifier}, {self.instructions!r})"


class ReturnAstNode(Statement):
    def __init__(self, exp: Exp) -> None:
        self.exp = exp
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ReturnAstNode):
            raise NotImplementedError
        return self.exp == o.exp

    def __repr__(self) -> str:
        return f"Return({self.exp!r})"


class MovAssemblyConstruct(Instruction):
    def __init__(self, src: Operand, dst: Operand) -> None:
        self.src = src
        self.dst = dst
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, MovAssemblyConstruct):
            raise NotImplementedError
        return self.src == o.src and self.dst == o.dst

    def __repr__(self) -> str:
        return f"Mov({self.src!r}, {self.dst!r})"


class RetAssemblyConstruct(Instruction):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RetAssemblyConstruct):
            raise NotImplementedError
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Ret"


class ReturnTacky(Instruction):
    def __init__(self, val: Val) -> None:
        self.val = val

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ReturnTacky):
            raise NotImplementedError
        return self.val == o.val

    def __repr__(self) -> str:
        return f"Return({self.val!r})"


class UnaryTacky(Instruction):
    def __init__(self, unary_operator: UnaryOperator, src: Val, dst, Val) -> None:
        self.unary_operator = unary_operator
        self.src = src
        self.dst = dst

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, UnaryTacky):
            raise NotImplementedError
        return (
            self.unary_operator == o.unary_operator
            and self.src == o.src
            and self.dst == o.dst
        )

    def __repr__(self) -> str:
        return f"Unary({self.unary_operator!r}, {self.src!r}, {self.dst!r})"


class ConstantAstNode(Exp):
    def __init__(self, int: int) -> None:
        self.int = int
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ConstantAstNode):
            raise NotImplementedError
        return self.int == o.int

    def __repr__(self) -> str:
        return f"Constant({self.int})"


class UnaryAstNode(Exp):
    def __init__(self, unary_operator: UnaryOperator, exp: Exp) -> None:
        self.unary_operator = unary_operator
        self.exp = exp
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, UnaryAstNode):
            raise NotImplementedError
        return self.unary_operator == o.unary_operator and self.exp == o.exp

    def __repr__(self) -> str:
        return f"Unary({self.unary_operator!r}, {self.exp!r})"


class ComplementAstNode(UnaryOperator):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ComplementAstNode):
            raise NotImplementedError
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Complement"


class NegateAstNode(UnaryOperator):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, NegateAstNode):
            raise NotImplementedError
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Negate"


class ImmAssemblyConstruct(Operand):
    def __init__(self, int: int) -> None:
        self.int = int
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ImmAssemblyConstruct):
            raise NotImplementedError
        return self.int == o.int

    def __repr__(self) -> str:
        return f"Imm({self.int})"


class RegisterAssemblyConstruct(Operand):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RegisterAssemblyConstruct):
            raise NotImplementedError
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Register"


class ConstantTacky(Val):
    def __init__(self, int: int) -> None:
        self.int = int
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ConstantTacky):
            raise NotImplementedError
        return self.int == o.int

    def __repr__(self) -> str:
        return f"Constant({self.int})"


class VarTacky(Val):
    def __init__(self, identifier: Identifier) -> None:
        self.identifier = identifier
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, VarTacky):
            raise NotImplementedError
        return self.identifier == o.identifier

    def __repr__(self) -> str:
        return f"Constant({self.identifier})"


class ComplementTacky(UnaryOperator):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ComplementTacky):
            raise NotImplementedError
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Complement"


class NegateTacky(UnaryOperator):
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, NegateTacky):
            raise NotImplementedError
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Negate"
