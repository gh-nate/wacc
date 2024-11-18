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


class Statement(ABC):
    pass


class Exp(ABC):
    pass


class ProgramAST(Program):
    def __init__(self, function_definition: FunctionDefinition) -> None:
        self.function_definition = function_definition
        super().__init__()


Identifier = NewType("Identifier", str)


class FunctionAST(FunctionDefinition):
    def __init__(self, name: Identifier, body: Statement) -> None:
        self.name = name
        self.body = body
        super().__init__()


class ReturnAST(Statement):
    def __init__(self, exp: Exp) -> None:
        self.exp = exp
        super().__init__()


class ConstantAST(Exp):
    def __init__(self, int: int) -> None:
        self.int = int
        super().__init__()
