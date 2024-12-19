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

import lexer
import unittest


class TestLexer(unittest.TestCase):
    def test_tokenize(self):
        self.assertEqual(
            lexer.tokenize("""\
int main(void) {
    return 2;
}
"""),
            ["int", "main", "(", "void", ")", "{", "return", "2", ";", "}"],
        )  # Listing 1-1


if __name__ == "__main__":
    unittest.main()
