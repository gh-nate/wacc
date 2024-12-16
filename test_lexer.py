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

import lexer
import parser
import unittest


class TestLexer(TestCommon):
    def test_tokenize(self):
        self.assertEqual(
            lexer.tokenize("int main(void) {\n\treturn 2;\n}\n"),
            self.listing_1_1_tokens,
        )

        self.assertEqual(
            lexer.tokenize("int main(void) {\n\treturn ~(-2);\n}\n"),
            self.listing_2_1_tokens,
        )

        self.assertEqual(
            lexer.tokenize("int main(void) {\n\treturn --2;\n}\n"),
            self.listing_2_3_tokens,
        )

        self.assertEqual(
            lexer.tokenize("int main(void) {\n\treturn -(-2);\n}\n"),
            self.listing_2_4_tokens,
        )

        for binop in parser.BINARY_OPERATOR_PRECEDENCE.keys():
            self.assertEqual(
                lexer.tokenize("int main(void) {\n\treturn 2 " + binop + " 2;\n}\n"),
                [
                    "int",
                    "main",
                    "(",
                    "void",
                    ")",
                    "{",
                    "return",
                    "2",
                    binop,
                    "2",
                    ";",
                    "}",
                ],
            )

        self.assertEqual(
            lexer.tokenize("int main(void) {\n\treturn !2;\n}\n"),
            ["int", "main", "(", "void", ")", "{", "return", "!", "2", ";", "}"],
        )


if __name__ == "__main__":
    unittest.main()
