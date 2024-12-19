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


class Exp(ABC):
    pass


@dataclass
class ConstantAST(Exp):
    int: int


class Statement(ABC):
    pass


@dataclass
class ReturnAST(Statement):
    exp: Exp


class FunctionDefinition(ABC):
    pass


@dataclass
class FunctionAST(FunctionDefinition):
    name: str
    body: Statement


class Program(ABC):
    pass


@dataclass
class ProgramAST(Program):
    function_definition: FunctionDefinition
