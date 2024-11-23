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

from typing import cast

import asdl
import io
import platform

system = platform.system()


def output_program(program: asdl.ProgramAssemblyConstruct, f: io.TextIOBase) -> None:
    output_function_definition(
        cast(asdl.FunctionAssemblyConstruct, program.function_definition), f
    )
    if system == "Linux":
        f.write('.section .note.GNU-stack,"",@progbits\n')


def output_function_definition(
    program: asdl.FunctionAssemblyConstruct, f: io.TextIOBase
) -> None:
    name = f"_{program.name}" if system == "Darwin" else program.name
    f.write(f"\t.globl {name}\n")
    f.write(f"{name}:\n")
    output_instructions(program.instructions, f)


def output_instructions(instructions: list[asdl.Instruction], f: io.TextIOBase) -> None:
    for instruction in instructions:
        if isinstance(instruction, asdl.MovAssemblyConstruct):
            output_mov(instruction, f)
        elif isinstance(instruction, asdl.RetAssemblyConstruct):
            output_ret(instruction, f)


def output_mov(instruction: asdl.MovAssemblyConstruct, f: io.TextIOBase) -> None:
    f.write("\tmovl\t")
    output_immediate(cast(asdl.ImmAssemblyConstruct, instruction.src), f)
    f.write(", ")
    output_register(cast(asdl.RegisterAssemblyConstruct, instruction.dst), f)
    f.write("\n")


def output_ret(instruction: asdl.RetAssemblyConstruct, f: io.TextIOBase) -> None:
    f.write("\tret\n")


def output_register(register: asdl.RegisterAssemblyConstruct, f: io.TextIOBase) -> None:
    f.write("%eax")


def output_immediate(immediate: asdl.ImmAssemblyConstruct, f: io.TextIOBase) -> None:
    f.write(f"${immediate.int}")
