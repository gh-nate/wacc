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
import unittest


class TestCommon(unittest.TestCase):
    def setUp(self):
        def fill_tokens(*tokens):
            return (
                ["int", "main", "(", "void", ")", "{", "return"]
                + [*tokens]
                + [";", "}"]
            )

        def fill_ast(exp):
            return asdl.ProgramAST(
                asdl.FunctionAST("main", [asdl.SAST(asdl.ReturnAST(exp))])
            )

        def fill_tacky(*instructions):
            return asdl.ProgramTACKY(asdl.FunctionTACKY("main", [*instructions]))

        self.listing_1_1_tokens = fill_tokens("2")
        self.listing_1_1_ast = fill_ast(asdl.ConstantAST(2))
        imm_asm_2 = asdl.ImmASM(2)
        rax = asdl.RegisterASM(asdl.RegASM.AX)
        ret_asm = asdl.RetASM()
        self.listing_1_1_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [
                    asdl.AllocateStackASM(0),
                    asdl.MovASM(imm_asm_2, rax),
                    ret_asm,
                ],
            )
        )
        constant_tacky_2 = asdl.ConstantTACKY(2)
        self.listing_1_1_tacky = fill_tacky(asdl.ReturnTACKY(constant_tacky_2))

        self.listing_2_1_tokens = fill_tokens("~", "(", "-", "2", ")")
        self.listing_2_1_ast = fill_ast(
            asdl.UnaryAST(
                asdl.UnaryOperatorAST.COMPLEMENT,
                asdl.UnaryAST(asdl.UnaryOperatorAST.NEGATE, asdl.ConstantAST(2)),
            )
        )
        var_tacky_tmp_0 = asdl.VarTACKY("tmp.0")
        var_tacky_tmp_1 = asdl.VarTACKY("tmp.1")
        self.listing_2_1_tacky = fill_tacky(
            asdl.UnaryTACKY(
                asdl.UnaryOperatorTACKY.NEGATE,
                constant_tacky_2,
                var_tacky_tmp_0,
            ),
            asdl.UnaryTACKY(
                asdl.UnaryOperatorTACKY.COMPLEMENT,
                var_tacky_tmp_0,
                var_tacky_tmp_1,
            ),
            asdl.ReturnTACKY(var_tacky_tmp_1),
        )

        r10 = asdl.RegisterASM(asdl.RegASM.R10)
        stack_4, stack_8 = asdl.StackASM(-4), asdl.StackASM(-8)
        self.listing_2_1_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [
                    asdl.AllocateStackASM(8),
                    asdl.MovASM(imm_asm_2, stack_4),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, stack_4),
                    asdl.MovASM(stack_4, r10),
                    asdl.MovASM(r10, stack_8),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NOT, stack_8),
                    asdl.MovASM(stack_8, rax),
                    ret_asm,
                ],
            ),
        )

        self.listing_2_3_tokens = fill_tokens("--", "2")

        self.listing_2_4_tokens = fill_tokens("-", "(", "-", "2", ")")
