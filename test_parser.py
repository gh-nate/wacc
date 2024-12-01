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
import parser
import random
import unittest


class TestParser(unittest.TestCase):
    def test_parse(self):
        name = "main"
        common_prefix = ["int", name, "(", "void", ")", "{", "return"]
        common_suffix = [";", "}"]
        n = random.randint(0, 255)
        constant = asdl.ConstantAST(n)
        n = str(n)

        tokens = common_prefix + [n] + common_suffix
        expected = asdl.ProgramAST(asdl.FunctionAST(name, asdl.ReturnAST(constant)))
        self.assertEqual(parser.parse(tokens), expected)

        tokens = common_prefix + ["~", "(", "-", n, ")"] + common_suffix
        negate = asdl.NegateAST()
        unary_negate_constant = asdl.UnaryAST(negate, constant)
        expected = asdl.ProgramAST(
            asdl.FunctionAST(
                name,
                asdl.ReturnAST(
                    asdl.UnaryAST(asdl.ComplementAST(), unary_negate_constant)
                ),
            )
        )
        self.assertEqual(parser.parse(tokens), expected)

        tokens = common_prefix + ["--", n] + common_suffix
        with self.assertRaises(ValueError):
            parser.parse(tokens)

        tokens = common_prefix + ["-", "(", "-", n, ")"] + common_suffix
        expected = asdl.ProgramAST(
            asdl.FunctionAST(
                name,
                asdl.ReturnAST(asdl.UnaryAST(negate, unary_negate_constant)),
            )
        )
        self.assertEqual(parser.parse(tokens), expected)


if __name__ == "__main__":
    unittest.main()
