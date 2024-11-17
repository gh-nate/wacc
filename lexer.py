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

import re

patterns = [
    re.compile(r"[a-zA-Z_]\w*\b"),
    re.compile(r"[0-9]+\b"),
    re.compile(r"int\b"),
    re.compile(r"void\b"),
    re.compile(r"return\b"),
    re.compile(r"\("),
    re.compile(r"\)"),
    re.compile(r"{"),
    re.compile(r"}"),
    re.compile(r";"),
]


def lex(input_file: Path) -> list[str]:
    tokens = []
    with input_file.open() as f:
        input = f.read()
    while input := input.lstrip():
        longest_match_length = 0
        for pattern in patterns:
            if m := pattern.match(input):
                match = m.group()
                match_length = len(match)
                if match_length > longest_match_length:
                    longest_match_length = match_length
                    longest_match = match
        if longest_match_length == 0:
            raise RuntimeError(f"No match found for '{input}'")
        tokens.append(longest_match)
        input = input[longest_match_length:]
    return tokens
