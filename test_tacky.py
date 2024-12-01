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
import random
import tacky
import unittest


class TestTacky(unittest.TestCase):
    def test_convert(self):
        n = random.randint(0, 255)
        name = "main"

        constant_ast = asdl.ConstantAST(n)
        ast_tree = asdl.ProgramAST(asdl.FunctionAST(name, asdl.ReturnAST(constant_ast)))
        constant_tacky = asdl.ConstantTACKY(n)
        tacky_tree = asdl.ProgramTACKY(
            asdl.FunctionTACKY(name, [asdl.ReturnTACKY(constant_tacky)])
        )
        self.assertEqual(tacky.convert(ast_tree), tacky_tree)

        complement_ast = asdl.ComplementAST()
        ast_tree = asdl.ProgramAST(
            asdl.FunctionAST(
                name, asdl.ReturnAST(asdl.UnaryAST(complement_ast, constant_ast))
            )
        )
        tmp_0 = asdl.VarTACKY("tmp.0")
        complement_tacky = asdl.ComplementTACKY()
        tacky_tree.function_definition.body = [
            asdl.UnaryTACKY(complement_tacky, constant_tacky, tmp_0),
            asdl.ReturnTACKY(tmp_0),
        ]
        self.assertEqual(tacky.convert(ast_tree), tacky_tree)

        negate_ast = asdl.NegateAST()
        ast_tree = asdl.ProgramAST(
            asdl.FunctionAST(
                name,
                asdl.ReturnAST(
                    asdl.UnaryAST(
                        negate_ast,
                        asdl.UnaryAST(
                            complement_ast, asdl.UnaryAST(negate_ast, constant_ast)
                        ),
                    )
                ),
            )
        )
        negate_tacky = asdl.NegateTACKY()
        tmp_1 = asdl.VarTACKY("tmp.1")
        tmp_2 = asdl.VarTACKY("tmp.2")
        tacky_tree.function_definition.body = [
            asdl.UnaryTACKY(negate_tacky, constant_tacky, tmp_0),
            asdl.UnaryTACKY(complement_tacky, tmp_0, tmp_1),
            asdl.UnaryTACKY(negate_tacky, tmp_1, tmp_2),
            asdl.ReturnTACKY(tmp_2),
        ]
        self.assertEqual(tacky.convert(ast_tree), tacky_tree)


if __name__ == "__main__":
    unittest.main()
