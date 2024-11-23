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


Identifier = NewType("Identifier", str)


class FunctionAstNode(FunctionDefinition):
    def __init__(self, name: Identifier, body: Statement) -> None:
        self.name = name
        self.body = body
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, FunctionAstNode):
            return NotImplemented
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
            return NotImplemented
        return self.name == o.name and self.instructions == o.instructions

    def __repr__(self) -> str:
        return f"Function({self.name}, {self.instructions!r})"


class ReturnAstNode(Statement):
    def __init__(self, exp: Exp) -> None:
        self.exp = exp
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ReturnAstNode):
            return NotImplemented
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
            return NotImplemented
        return self.src == o.src and self.dst == o.dst

    def __repr__(self) -> str:
        return f"Mov({self.src!r}, {self.dst!r})"


class RetAssemblyConstruct(Instruction):

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RetAssemblyConstruct):
            return NotImplemented
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Ret"


class ConstantAstNode(Exp):

    def __init__(self, int: int) -> None:
        self.int = int
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ConstantAstNode):
            return NotImplemented
        return self.int == o.int

    def __repr__(self) -> str:
        return f"Constant({self.int})"


class ImmAssemblyConstruct(Operand):

    def __init__(self, int: int) -> None:
        self.int = int
        super().__init__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ImmAssemblyConstruct):
            return NotImplemented
        return self.int == o.int

    def __repr__(self) -> str:
        return f"Imm({self.int})"


class RegisterAssemblyConstruct(Operand):

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, RegisterAssemblyConstruct):
            return NotImplemented
        return f"{self!r}" == f"{o!r}"

    def __repr__(self) -> str:
        return "Register"
