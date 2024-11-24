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

import asdl
import parser
import unittest


class TestParser(unittest.TestCase):
    def test_listing_1_1(self) -> None:
        fn_name, int_value = "main", 2
        self.assertEqual(
            parser.parse_program(
                [
                    "int",
                    fn_name,
                    "(",
                    "void",
                    ")",
                    "{",
                    "return",
                    str(int_value),
                    ";",
                    "}",
                ]
            ),
            asdl.ProgramAstNode(
                asdl.FunctionAstNode(
                    asdl.Identifier(fn_name),
                    asdl.ReturnAstNode(asdl.ConstantAstNode(int_value)),
                )
            ),
        )

    def test_listing_2_1(self) -> None:
        fn_name, int_value = "main", 2
        self.assertEqual(
            parser.parse_program(
                [
                    "int",
                    fn_name,
                    "(",
                    "void",
                    ")",
                    "{",
                    "return",
                    "~",
                    "(",
                    "-",
                    str(int_value),
                    ")",
                    ";",
                    "}",
                ]
            ),
            asdl.ProgramAstNode(
                asdl.FunctionAstNode(
                    asdl.Identifier(fn_name),
                    asdl.ReturnAstNode(
                        asdl.UnaryAstNode(
                            asdl.ComplementAstNode(),
                            asdl.UnaryAstNode(
                                asdl.NegateAstNode(), asdl.ConstantAstNode(int_value)
                            ),
                        )
                    ),
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
