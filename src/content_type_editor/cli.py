# Copyright (C) 2025 Jaromir Hradilek

# MIT License
#
# Permission  is hereby granted,  free of charge,  to any person  obtaining
# a copy of  this software  and associated documentation files  (the 'Soft-
# ware'),  to deal in the Software  without restriction,  including without
# limitation the rights to use,  copy, modify, merge,  publish, distribute,
# sublicense, and/or sell copies of the Software,  and to permit persons to
# whom the Software is furnished to do so,  subject to the following condi-
# tions:
#
# The above copyright notice  and this permission notice  shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS',  WITHOUT WARRANTY OF ANY KIND,  EXPRESS
# OR IMPLIED,  INCLUDING BUT NOT LIMITED TO  THE WARRANTIES OF MERCHANTABI-
# LITY,  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT
# SHALL THE AUTHORS OR COPYRIGHT HOLDERS  BE LIABLE FOR ANY CLAIM,  DAMAGES
# OR OTHER LIABILITY,  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM,  OUT OF OR IN CONNECTION WITH  THE SOFTWARE  OR  THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import argparse
import errno
import sys
from pathlib import Path
from streamlit.web import cli
from . import NAME, VERSION, DESCRIPTION

# Print a message to standard error output and terminate the script:
def exit_with_error(error_message: str, exit_status: int = errno.EPERM) -> None:
    # Print the supplied message to standard error output:
    print(f'{NAME}: {error_message}', file=sys.stderr)

    # Terminate the script with the supplied exit status:
    sys.exit(exit_status)

# Parse supplied command-line options:
def parse_args(argv: list[str] | None = None) -> None:
    # Configure the option parser:
    parser = argparse.ArgumentParser(prog=NAME,
        description=DESCRIPTION,
        add_help=False)

    # Redefine section titles:
    parser._optionals.title = 'Options'
    parser._positionals.title = 'Arguments'

    # Define supported options:
    info = parser.add_mutually_exclusive_group()
    info.add_argument('-h', '--help',
        action='help',
        help="display this help and exit")
    info.add_argument('-v', '--version',
        action='version',
        version=f'{NAME} {VERSION}',
        help="display version information and exit")

    # Define supported arguments:
    parser.add_argument('directory', metavar='DIRECTORY',
        default='.',
        nargs='?',
        help="the directory with AsciiDoc files (default: current directory)")

    # Parse command-line options:
    args = parser.parse_args(argv)

    if not Path(args.directory).is_dir():
        exit_with_error(f"error: Not a directory: {args.directory}", errno.ENOTDIR)

    # Open the web UI editor:
    cli.main_run([str(Path(__file__).parent / 'webui.py'), args.directory])
