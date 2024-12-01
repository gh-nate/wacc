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
    return convert_program(tree)


def convert_program(node):
    return asdl.ProgramASM(convert_function(node.function_definition))


def convert_function(node):
    return asdl.FunctionASM(node.name, convert_return(node.body))


def convert_return(node):
    return [
        asdl.MovASM(convert_constant(node.exp), asdl.RegisterASM()),
        asdl.RetASM(),
    ]


def convert_constant(node):
    return asdl.ImmASM(node.i)
