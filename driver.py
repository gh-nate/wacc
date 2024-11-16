#!/usr/bin/env python3

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

import argparse
import shlex
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("input_file")
parser.add_argument(
    "-S", action="store_true", help="emit an assembly file, but not assemble or link it"
)
parser.add_argument(
    "--lex", action="store_true", help="run the lexer, but stop before parsing"
)
parser.add_argument(
    "--parse",
    action="store_true",
    help="run the lexer and parser, but stop before assembly generation",
)
parser.add_argument(
    "--codegen",
    action="store_true",
    help="perform lexing, parsing, and assembly generation, but stop before code emission",
)
args = parser.parse_args()

stem = Path(args.input_file).name

preprocessed_file = Path(stem + ".i")
subprocess.run(shlex.split(f"gcc -E -P {args.input_file} -o {preprocessed_file}"))
preprocessed_file.unlink()

if args.lex:
    sys.exit()

if args.parse:
    sys.exit()

if args.codegen:
    sys.exit()

if args.S:
    sys.exit()

assembly_file = Path(stem + ".s")
subprocess.run(shlex.split(f"gcc {assembly_file} -o {stem}"))
assembly_file.unlink()
