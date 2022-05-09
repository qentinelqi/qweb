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
# ---------------------------
from __future__ import annotations
from typing import Any, Optional
from pathlib import Path
import re
from robot.libraries.BuiltIn import BuiltIn


def set_robot_args(*args: Any, **kwargs: Any) -> list[Any]:
    new_args = []
    for a in list(args):
        if _contains_var(a):
            new_args.append(BuiltIn().get_variable_value(a))
        else:
            new_args.append(a)
    for key, val in kwargs.items():
        if _contains_var(key):
            key = BuiltIn().get_variable_value(key)
        if _contains_var(val):
            val = BuiltIn().get_variable_value(val)
        new_args.append('{}={}'.format(key, val))
    return new_args


def get_steps(name: str, caller_fn: str, **kwargs: Any) -> Optional[list[dict[str, Any]]]:
    file = Path(BuiltIn().get_variable_value('${SUITE SOURCE}'))
    test_case = BuiltIn().get_variable_value('${TEST_NAME}')
    with open(file, "r+") as fo:
        data = fo.readlines()
    idx = 0
    while data:
        if data[idx].strip() == test_case:
            data = data[idx:len(data)]
            for i, line in enumerate(data):
                if caller_fn in line.replace(' ', '').strip().lower() and name in line.strip():
                    steps = _parse_steps(data, i + 1, **kwargs)
                    return steps
        idx += 1
    return None


def _parse_steps(data: list[str], iterator: int, **kwargs: Any) -> list[dict[str, Any]]:
    steps = []
    while not data[iterator].replace(' ', '').lower().strip().startswith('endblock'):
        varname = None
        line = re.split(r'\s{2,}', data[iterator].strip())
        if line[0].startswith('#'):
            iterator += 1
            continue
        if _contains_var(line[0]):
            pw = line[1].strip()
            varname = line[0].strip()
            args, kwargs = _parse_arguments(line, starting_point=2, **kwargs)
        else:
            pw = line[0].strip()
            args, kwargs = _parse_arguments(line, starting_point=1, **kwargs)
        step = {"variable": varname, "paceword": pw, "args": args, "kwargs": kwargs}
        steps.append(step)
        iterator += 1
    return steps


def _parse_arguments(line: list[str], starting_point: int,
                     **kwargs: Any) -> tuple[list[str], dict[Any, Any]]:
    args = []
    for a in range(starting_point, len(line)):
        if line[a].strip() != '':
            if '=' not in line[a]:
                args.append(line[a].strip())
            elif '\\=' in line[a]:
                args.append(line[a].strip())
            else:
                key, value = line[a].strip().split('=', 1)
                kwargs.update({key: value})
    return args, kwargs


def _contains_var(arg: str, from_start: bool = True) -> bool:
    var_types = ['${', '@{', '&{']
    if from_start:
        return any(arg.strip().startswith(v) for v in var_types)
    return any(v in arg and '}' in arg for v in var_types)
