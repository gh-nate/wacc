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

NO_EXEC_STACK = '.section .note.GNU-stack,"",@progbits'
SYSTEM = platform.system()


def output(tree):
    with io.StringIO() as s:
        output_program(tree, s)
        if SYSTEM == "Linux":
            print(NO_EXEC_STACK, file=s)
        r = s.getvalue()
    return r


def output_program(tree, s):
    output_function(tree.function_definition, s)


def output_function(node, s):
    if SYSTEM == "Darwin":
        name = "_" + node.name
    else:
        name = node.name
    print(f"\t.globl {name}\n{name}:\n\tpushq %rbp\n\tmovq %rsp, %rbp", file=s)
    output_instructions(node.instructions, s)


def output_instructions(instructions, s):
    for instruction in instructions:
        match instruction:
            case asdl.MovASM(src, dst):
                s.write("\tmovl ")
                output_operand(src, s)
                s.write(", ")
                output_operand(dst, s)
                s.write("\n")
            case asdl.RetASM():
                print("\tmovq %rbp, %rsp", file=s)
                print("\tpopq %rbp", file=s)
                print("\tret", file=s)
            case asdl.UnaryASM(unary_operator, operand):
                match unary_operator:
                    case asdl.NegASM():
                        s.write("\tnegl ")
                    case asdl.NotASM():
                        s.write("\tnotl ")
                output_operand(operand, s)
                s.write("\n")
            case asdl.AllocateStackASM(i):
                print(f"\tsubq ${i}, %rsp", file=s)


def output_operand(node, s):
    match node:
        case asdl.RegASM(asdl.AxASM()):
            s.write("%eax")
        case asdl.RegASM(asdl.R10ASM()):
            s.write("%r10d")
        case asdl.StackASM(i):
            s.write(f"{i}(%rbp)")
        case asdl.ImmASM(i):
            s.write(f"${i}")
