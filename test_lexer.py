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
import unittest


class TestLexer(TestCommon):
    def test_tokenize(self):
        self.assertEqual(
            lexer.tokenize("""\
int main(void) {
    return 2;
}
"""),
            self.listing_1_1_tokens,
        )

        self.assertEqual(
            lexer.tokenize("""\
int main(void) {
    return ~(-2);
}
"""),
            self.listing_2_1_tokens,
        )

        self.assertEqual(
            lexer.tokenize("""\
int main(void) {
    return --2;
}
"""),
            self.listing_2_3_tokens,
        )

        self.assertEqual(
            lexer.tokenize("""\
int main(void) {
    return -(-2);
}
"""),
            self.listing_2_4_tokens,
        )

        self.assertEqual(
            lexer.tokenize("""\
int main(void) {
    int b;
    int a = 10 + 1;
    b = a * 2;
    return b;
}
"""),
            self.listing_5_13_tokens,
        )


if __name__ == "__main__":
    unittest.main()
