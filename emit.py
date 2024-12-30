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
import io
import platform

_platform_system = platform.system()
IS_LINUX = _platform_system == "Linux"
IS_MACOS = _platform_system == "Darwin"


def output(tree):
    with io.StringIO() as s:
        output_program(tree, s)
        if IS_LINUX:
            print('.section .note.GNU-stack,"",@progbits', file=s)
        r = s.getvalue()
    return r


def output_program(tree, s):
    output_function(tree.function_definition, s)


def output_function(node, s):
    if IS_LINUX:
        name = node.name
    elif IS_MACOS:
        name = "_" + node.name
    print(f"\t.globl {name}\n{name}:", file=s)
    output_instructions(node.instructions, s)


def output_instructions(instructions, s):
    for instruction in instructions:
        output_instruction(instruction, s)


def output_instruction(instruction, s):
    match instruction:
        case asdl.MovASM(src, dst):
            s.write("\tmovl ")
            output_operand(src, s)
            s.write(", ")
            output_operand(dst, s)
            s.write("\n")
        case asdl.RetASM():
            print("\tret", file=s)


def output_operand(node, s):
    match node:
        case asdl.ImmASM(int):
            s.write(f"${int}")
        case asdl.RegisterASM():
            s.write("%eax")
