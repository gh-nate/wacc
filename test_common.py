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
import copy
import unittest


class TestCommon(unittest.TestCase):
    def setUp(self):
        def fill_tokens(*tokens):
            return ["int", "main", "(", "void", ")", "{"] + [*tokens] + [";", "}"]

        def fill_ast(*block_items):
            return asdl.ProgramAST(
                asdl.FunctionAST("main", asdl.BlockAST([*block_items]))
            )

        def fill_tacky(*instructions):
            return asdl.ProgramTACKY(
                asdl.FunctionTACKY(
                    "main", [*instructions, asdl.ReturnTACKY(asdl.ConstantTACKY(0))]
                )
            )

        def fill_asm(*instructions):
            return asdl.ProgramASM(asdl.FunctionASM("main", [*instructions, *ret0_asm]))

        constant_ast_2 = asdl.ConstantAST(2)
        return_keyword = "return"
        self.listing_1_1_tokens = fill_tokens(return_keyword, "2")
        self.listing_1_1_ast = fill_ast(asdl.SAST(asdl.ReturnAST(constant_ast_2)))
        imm_asm_2 = asdl.ImmASM(2)
        rax = asdl.RegisterASM(asdl.RegASM.AX)
        ret_asm = asdl.RetASM()
        ret0_asm = [asdl.MovASM(asdl.ImmASM(0), rax), ret_asm]
        self.listing_1_1_asm = fill_asm(
            asdl.AllocateStackASM(0),
            asdl.MovASM(imm_asm_2, rax),
            ret_asm,
        )
        constant_tacky_2 = asdl.ConstantTACKY(2)
        self.listing_1_1_tacky = fill_tacky(asdl.ReturnTACKY(constant_tacky_2))

        self.listing_2_1_tokens = fill_tokens(return_keyword, "~", "(", "-", "2", ")")
        self.listing_2_1_ast = fill_ast(
            asdl.SAST(
                asdl.ReturnAST(
                    asdl.UnaryAST(
                        asdl.UnaryOperatorAST.COMPLEMENT,
                        asdl.UnaryAST(asdl.UnaryOperatorAST.NEGATE, constant_ast_2),
                    )
                )
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
        self.listing_2_1_asm = fill_asm(
            asdl.AllocateStackASM(8),
            asdl.MovASM(imm_asm_2, stack_4),
            asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, stack_4),
            asdl.MovASM(stack_4, r10),
            asdl.MovASM(r10, stack_8),
            asdl.UnaryASM(asdl.UnaryOperatorASM.NOT, stack_8),
            asdl.MovASM(stack_8, rax),
            ret_asm,
        )

        self.listing_2_3_tokens = fill_tokens(return_keyword, "--", "2")

        self.listing_2_4_tokens = fill_tokens(return_keyword, "-", "(", "-", "2", ")")

        a, b = "a", "b"
        self.listing_5_13_tokens = fill_tokens(
            "int",
            b,
            ";",
            "int",
            a,
            "=",
            "10",
            "+",
            "1",
            ";",
            b,
            "=",
            a,
            "*",
            "2",
            ";",
            return_keyword,
            b,
        )
        self.listing_5_13_ast = fill_ast(
            asdl.DAST(asdl.DeclarationAST(b, None)),
            asdl.DAST(
                asdl.DeclarationAST(
                    a,
                    asdl.BinaryAST(
                        asdl.BinaryOperatorAST.ADD,
                        asdl.ConstantAST(10),
                        asdl.ConstantAST(1),
                    ),
                )
            ),
            asdl.SAST(
                asdl.ExpressionAST(
                    asdl.AssignmentAST(
                        asdl.VarAST(b),
                        asdl.BinaryAST(
                            asdl.BinaryOperatorAST.MULTIPLY,
                            asdl.VarAST(a),
                            constant_ast_2,
                        ),
                    )
                )
            ),
            asdl.SAST(asdl.ReturnAST(asdl.VarAST(b))),
        )
        self.listing_5_13_sema = copy.deepcopy(self.listing_5_13_ast)
        sema_items = self.listing_5_13_sema.function_definition.body.items
        a_0, b_0 = a + ".0", b + ".0"
        sema_items[0].declaration.name = b_0
        sema_items[1].declaration.name = a_0
        sema_items_2_assignment = sema_items[2].statement.exp
        sema_items_2_assignment.lhs.identifier = b_0
        sema_items_2_assignment.rhs.lhs.identifier = a_0
        sema_items[3].statement.exp.identifier = b_0
        var_tacky_a_0 = asdl.VarTACKY(a_0)
        var_tacky_b_0 = asdl.VarTACKY(b_0)
        self.listing_5_13_tacky = fill_tacky(
            asdl.BinaryTACKY(
                asdl.BinaryOperatorTACKY.ADD,
                asdl.ConstantTACKY(10),
                asdl.ConstantTACKY(1),
                var_tacky_tmp_0,
            ),
            asdl.CopyTACKY(
                var_tacky_tmp_0,
                var_tacky_a_0,
            ),
            asdl.BinaryTACKY(
                asdl.BinaryOperatorTACKY.MULTIPLY,
                var_tacky_a_0,
                constant_tacky_2,
                var_tacky_tmp_1,
            ),
            asdl.CopyTACKY(
                var_tacky_tmp_1,
                var_tacky_b_0,
            ),
            asdl.ReturnTACKY(var_tacky_b_0),
        )
        r11 = asdl.RegisterASM(asdl.RegASM.R11)
        stack_12, stack_16 = asdl.StackASM(-12), asdl.StackASM(-16)
        self.listing_5_13_asm = fill_asm(
            asdl.AllocateStackASM(16),
            asdl.MovASM(asdl.ImmASM(10), stack_4),
            asdl.BinaryASM(asdl.BinaryOperatorASM.ADD, asdl.ImmASM(1), stack_4),
            asdl.MovASM(stack_4, r10),
            asdl.MovASM(r10, stack_8),
            asdl.MovASM(stack_8, r10),
            asdl.MovASM(r10, stack_12),
            asdl.MovASM(stack_12, r11),
            asdl.BinaryASM(asdl.BinaryOperatorASM.MULT, imm_asm_2, r11),
            asdl.MovASM(r11, stack_12),
            asdl.MovASM(stack_12, r10),
            asdl.MovASM(r10, stack_16),
            asdl.MovASM(stack_16, rax),
            ret_asm,
        )
