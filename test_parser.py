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
import parser
import unittest


class TestParser(TestCommon):
    def test_parse(self):
        self.assertEqual(
            parser.parse(self.listing_1_1_tokens),
            self.listing_1_1_ast,
        )

        self.assertEqual(
            parser.parse(self.listing_2_1_tokens),
            self.listing_2_1_ast,
        )

        with self.assertRaises(parser.SyntaxError):
            parser.parse(self.listing_2_3_tokens)

        self.assertEqual(
            parser.parse(self.listing_2_4_tokens),
            asdl.ProgramAST(
                asdl.FunctionAST(
                    "main",
                    [
                        asdl.SAST(
                            asdl.ReturnAST(
                                asdl.UnaryAST(
                                    asdl.UnaryOperatorAST.NEGATE,
                                    asdl.UnaryAST(
                                        asdl.UnaryOperatorAST.NEGATE,
                                        asdl.ConstantAST(2),
                                    ),
                                )
                            )
                        )
                    ],
                )
            ),
        )

    def test_parse_exp(self):
        # Precedence Climbing in Action
        self.assertEqual(
            parser.parse_exp(
                ["1", "*", "2", "-", "3", "*", "(", "4", "+", "5", ")", ";"]
            ),
            asdl.BinaryAST(
                asdl.BinaryOperatorAST.SUBTRACT,
                asdl.BinaryAST(
                    asdl.BinaryOperatorAST.MULTIPLY,
                    asdl.ConstantAST(1),
                    asdl.ConstantAST(2),
                ),
                asdl.BinaryAST(
                    asdl.BinaryOperatorAST.MULTIPLY,
                    asdl.ConstantAST(3),
                    asdl.BinaryAST(
                        asdl.BinaryOperatorAST.ADD,
                        asdl.ConstantAST(4),
                        asdl.ConstantAST(5),
                    ),
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
