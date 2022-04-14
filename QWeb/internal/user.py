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

import os


def is_root() -> bool:
    try:
        # Windows doesn't have getuid. We just assume that user is not root. We
        # most likely won't need proper Windows support here anyway.
        uid = os.getuid()  # type: ignore[attr-defined] # pylint: disable=no-member
    except AttributeError:
        return False
    # User id 0 is reserved for superuser aka root
    if uid == 0:
        return True
    return False


def is_docker() -> bool:
    path = '/proc/self/cgroup'
    return (os.path.exists('/.dockerenv')
            or os.path.isfile(path) and any('docker' in line
                                            for line in open(path))  # noqa: W503,W1514
            )
