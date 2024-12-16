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
            self.listing_2_4_ast,
        )

    def test_parse_exp(self):
        self.assertEqual(
            parser.parse_exp(["1", "+", "(", "2", "*", "3", ")", ";"]),
            self.figure_3_1_ast,
        )

        self.assertEqual(
            parser.parse_exp(["(", "1", "+", "2", ")", "*", "3", ";"]),
            self.figure_3_2_ast,
        )

        self.assertEqual(
            parser.parse_exp(["1", "+", "2", "*", "3", "+", "4", ";"]),
            self.dealing_with_precedence_ast,
        )

        self.assertEqual(
            parser.parse_exp(
                ["1", "*", "2", "-", "3", "*", "(", "4", "+", "5", ")", ";"]
            ),
            self.precedence_climbing_in_action_ast,
        )

        self.assertEqual(
            parser.parse_exp(["!", "2", ";"]),
            asdl.UnaryAST(
                asdl.UnaryOperatorAST.NOT,
                asdl.ConstantAST(2),
            ),
        )

        self.assertEqual(
            parser.parse_exp(["2", "&&", "2", ";"]),
            asdl.BinaryAST(
                asdl.BinaryOperatorAST.AND,
                asdl.ConstantAST(2),
                asdl.ConstantAST(2),
            ),
        )


if __name__ == "__main__":
    unittest.main()
