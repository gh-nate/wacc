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

from test_common import TestCommon

import asdl
import tacky
import unittest


class TestTacky(TestCommon):
    def test_convert(self):
        self.assertEqual(
            tacky.convert(self.listing_1_1_ast),
            self.listing_1_1_tacky,
        )

        self.assertEqual(
            tacky.convert(
                asdl.ProgramAST(
                    asdl.FunctionAST(
                        "main",
                        asdl.ReturnAST(
                            asdl.UnaryAST(
                                asdl.UnaryOperatorAST.COMPLEMENT,
                                asdl.ConstantAST(2),
                            ),
                        ),
                    )
                ),
            ),
            self.table_2_1_row_2_tacky,
        )

        self.assertEqual(
            tacky.convert(self.listing_2_1_ast),
            self.listing_2_1_tacky,
        )

        self.assertEqual(
            tacky.convert(self.listing_2_4_ast),
            self.listing_2_4_tacky,
        )

        self.assertEqual(
            tacky.convert(
                asdl.ProgramAST(
                    asdl.FunctionAST(
                        "main",
                        asdl.ReturnAST(
                            asdl.UnaryAST(
                                asdl.UnaryOperatorAST.NEGATE,
                                asdl.UnaryAST(
                                    asdl.UnaryOperatorAST.COMPLEMENT,
                                    asdl.UnaryAST(
                                        asdl.UnaryOperatorAST.NEGATE,
                                        asdl.ConstantAST(8),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.table_2_1_row_3_tacky,
        )

    def test_convert_tacky(self):
        g, instructions = tacky.mk_tmp(), []
        tacky.convert_tacky(g, self.figure_3_1_ast, instructions)
        self.assertEqual(
            instructions,
            [
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.MULTIPLY,
                    asdl.ConstantTACKY(2),
                    asdl.ConstantTACKY(3),
                    asdl.VarTACKY("tmp.0"),
                ),
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.ADD,
                    asdl.ConstantTACKY(1),
                    asdl.VarTACKY("tmp.0"),
                    asdl.VarTACKY("tmp.1"),
                ),
            ],
        )

        g = tacky.mk_tmp()
        instructions.clear()
        tacky.convert_tacky(g, self.figure_3_2_ast, instructions)
        self.assertEqual(
            instructions,
            [
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.ADD,
                    asdl.ConstantTACKY(1),
                    asdl.ConstantTACKY(2),
                    asdl.VarTACKY("tmp.0"),
                ),
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.MULTIPLY,
                    asdl.VarTACKY("tmp.0"),
                    asdl.ConstantTACKY(3),
                    asdl.VarTACKY("tmp.1"),
                ),
            ],
        )

        g = tacky.mk_tmp()
        instructions.clear()
        tacky.convert_tacky(g, self.dealing_with_precedence_ast, instructions)
        self.assertEqual(
            instructions,
            [
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.MULTIPLY,
                    asdl.ConstantTACKY(2),
                    asdl.ConstantTACKY(3),
                    asdl.VarTACKY("tmp.0"),
                ),
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.ADD,
                    asdl.ConstantTACKY(1),
                    asdl.VarTACKY("tmp.0"),
                    asdl.VarTACKY("tmp.1"),
                ),
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.ADD,
                    asdl.VarTACKY("tmp.1"),
                    asdl.ConstantTACKY(4),
                    asdl.VarTACKY("tmp.2"),
                ),
            ],
        )

        g = tacky.mk_tmp()
        instructions.clear()
        tacky.convert_tacky(g, self.precedence_climbing_in_action_ast, instructions)
        self.assertEqual(
            instructions,
            [
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.MULTIPLY,
                    asdl.ConstantTACKY(1),
                    asdl.ConstantTACKY(2),
                    asdl.VarTACKY("tmp.0"),
                ),
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.ADD,
                    asdl.ConstantTACKY(4),
                    asdl.ConstantTACKY(5),
                    asdl.VarTACKY("tmp.1"),
                ),
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.MULTIPLY,
                    asdl.ConstantTACKY(3),
                    asdl.VarTACKY("tmp.1"),
                    asdl.VarTACKY("tmp.2"),
                ),
                asdl.BinaryTACKY(
                    asdl.BinaryOperatorTACKY.SUBTRACT,
                    asdl.VarTACKY("tmp.0"),
                    asdl.VarTACKY("tmp.2"),
                    asdl.VarTACKY("tmp.3"),
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
