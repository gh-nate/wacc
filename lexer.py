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

from enum import Enum, auto
import re


class TOKEN(Enum):
    IDENTIFIER = auto()
    CONSTANT = auto()
    INT_KEYWORD = auto()
    VOID_KEYWORD = auto()
    RETURN_KEYWORD = auto()
    OPEN_PARENTHESIS = auto()
    CLOSE_PARENTHESIS = auto()
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    SEMICOLON = auto()
    BITWISE_COMPLEMENT_OPERATOR = auto()
    NEGATION_OPERATOR = auto()
    DECREMENT_OPERATOR = auto()
    ADDITION_OPERATOR = auto()
    MULTIPLICATION_OPERATOR = auto()
    DIVISION_OPERATOR = auto()
    REMAINDER_OPERATOR = auto()


TOKEN_PATTERNS = {
    TOKEN.IDENTIFIER: re.compile(r"[a-zA-Z_]\w*\b"),
    TOKEN.CONSTANT: re.compile(r"[0-9]+\b"),
    TOKEN.INT_KEYWORD: re.compile(r"int\b"),
    TOKEN.VOID_KEYWORD: re.compile(r"void\b"),
    TOKEN.RETURN_KEYWORD: re.compile(r"return\b"),
    TOKEN.OPEN_PARENTHESIS: re.compile(r"\("),
    TOKEN.CLOSE_PARENTHESIS: re.compile(r"\)"),
    TOKEN.OPEN_BRACE: re.compile(r"{"),
    TOKEN.CLOSE_BRACE: re.compile(r"}"),
    TOKEN.SEMICOLON: re.compile(r";"),
    TOKEN.BITWISE_COMPLEMENT_OPERATOR: re.compile(r"~"),
    TOKEN.NEGATION_OPERATOR: re.compile(r"-"),
    TOKEN.DECREMENT_OPERATOR: re.compile(r"--"),
    TOKEN.ADDITION_OPERATOR: re.compile(r"\+"),
    TOKEN.MULTIPLICATION_OPERATOR: re.compile(r"\*"),
    TOKEN.DIVISION_OPERATOR: re.compile(r"/"),
    TOKEN.REMAINDER_OPERATOR: re.compile(r"%"),
}


def tokenize(s):
    tokens = []
    while s := s.lstrip():
        longest_length = 0
        for pattern in TOKEN_PATTERNS.values():
            if m := pattern.match(s):
                match = m.group()
                match_length = len(match)
                if match_length > longest_length:
                    longest = match
                    longest_length = match_length
        if not longest_length:
            raise RuntimeError(f"No match found for '{s}'")
        tokens.append(longest)
        s = s[longest_length:]
    return tokens
