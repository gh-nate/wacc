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

from pathlib import Path

import lexer
import unittest


class TestLexer(unittest.TestCase):
    def setUp(self) -> None:
        self.source_files = [
            Path("return_2.c"),
            Path("return_negation_bitwise_complement_2.c"),
            Path("return_decrement_2.c"),
            Path("return_double_negation_2.c"),
        ]
        # Listing 1-1
        with self.source_files[0].open("w") as f:
            f.write(
                """\
int main(void) {
    return 2;
}"""
            )
        # Listing 2-1
        with self.source_files[1].open("w") as f:
            f.write(
                """\
int main(void) {
    return ~(-2);
}"""
            )
        # Listing 2-3
        with self.source_files[2].open("w") as f:
            f.write(
                """\
int main(void) {
    return --2;
}"""
            )
        # Listing 2-4
        with self.source_files[3].open("w") as f:
            f.write(
                """\
int main(void) {
    return -(-2);
}"""
            )

    def tearDown(self) -> None:
        for f in self.source_files:
            f.unlink()

    def test_listing_1_1(self) -> None:
        self.assertEqual(
            lexer.lex(self.source_files[0]),
            ["int", "main", "(", "void", ")", "{", "return", "2", ";", "}"],
        )

    def test_listing_2_1(self) -> None:
        self.assertEqual(
            lexer.lex(self.source_files[1]),
            [
                "int",
                "main",
                "(",
                "void",
                ")",
                "{",
                "return",
                "~",
                "(",
                "-",
                "2",
                ")",
                ";",
                "}",
            ],
        )

    def test_listing_2_3(self) -> None:
        self.assertEqual(
            lexer.lex(self.source_files[2]),
            ["int", "main", "(", "void", ")", "{", "return", "--", "2", ";", "}"],
        )

    def test_listing_2_4(self) -> None:
        self.assertEqual(
            lexer.lex(self.source_files[3]),
            [
                "int",
                "main",
                "(",
                "void",
                ")",
                "{",
                "return",
                "-",
                "(",
                "-",
                "2",
                ")",
                ";",
                "}",
            ],
        )


if __name__ == "__main__":
    unittest.main()
