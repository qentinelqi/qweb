# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 -            Qentinel Group.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys
from ._version import get_versions  # pylint: disable-msg=E0611
from robot import libdoc


def cli() -> None:
    parser = argparse.ArgumentParser(
        prog='QWeb',
        usage='python %(prog)s [options] INPUT'
        '\n\nEXAMPLES:\n'
        '%(prog)s --all (lists all keywords)\n'
        '%(prog)s --list Get (lists all keywords startin with "Get")\n'
        '%(prog)s --show TypeText (displays documentation for keyword "TypeText")',
        description='Note: This module is meant to be used as a robot famework library.'
        'Command line interface only provides access to keyword documentation.')
    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('-A', '--all', action='store_true', help='lists ALL keywords')
    parser.add_argument('-L', '--list', action='store', help='lists keywords based on input string')
    parser.add_argument('-S', '--show', action='store', help='show docs for keyword(s)')
    if len(sys.argv) == 1:
        parser.print_help()
    args = parser.parse_args()

    # handle known options
    if args.all:
        print(libdoc.libdoc_cli(["QWeb", "list"]))
    elif args.list:
        print(libdoc.libdoc_cli(["QWeb", "list", args.list]))
    elif args.show:
        print(libdoc.libdoc_cli(["QWeb", "show", args.show]))


if __name__ == "__main__":
    __version__ = get_versions()['version']
    del get_versions
    cli()
