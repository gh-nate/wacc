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


def translate_program(n: asdl.ProgramAstNode) -> asdl.ProgramAssemblyConstruct:
    return asdl.ProgramAssemblyConstruct(
        translate_function_definition(cast(asdl.FunctionAstNode, n.function_definition))
    )


def translate_function_definition(
    n: asdl.FunctionAstNode,
) -> asdl.FunctionAssemblyConstruct:
    return asdl.FunctionAssemblyConstruct(
        n.name, translate_return(cast(asdl.ReturnAstNode, n.body))
    )


def translate_return(n: asdl.ReturnAstNode) -> list[asdl.Instruction]:
    return [
        asdl.MovAssemblyConstruct(
            translate_constant(cast(asdl.ConstantAstNode, n.exp)),
            asdl.RegisterAssemblyConstruct(),
        ),
        asdl.RetAssemblyConstruct(),
    ]


def translate_constant(n: asdl.ConstantAstNode) -> asdl.ImmAssemblyConstruct:
    return asdl.ImmAssemblyConstruct(n.int)
