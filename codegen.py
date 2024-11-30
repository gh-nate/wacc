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

import asdl


def convert(tree):
    return convert_ProgramAST_to_ProgramAC(tree)


def convert_ProgramAST_to_ProgramAC(node):
    return asdl.ProgramAC(convert_FunctionAST_to_FunctionAC(node.function_definition))


def convert_FunctionAST_to_FunctionAC(node):
    return asdl.FunctionAC(node.name, convert_ReturnAST_to_Instructions(node.body))


def convert_ReturnAST_to_Instructions(node):
    return [
        asdl.MovAC(convert_ConstantAST_to_ImmAC(node.exp), asdl.RegisterAC()),
        asdl.RetAC(),
    ]


def convert_ConstantAST_to_ImmAC(node):
    return asdl.ImmAC(node.i)
