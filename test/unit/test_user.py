# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------

from QWeb.internal.user import is_root
from unittest.mock import patch
import os


@patch.object(os, 'getuid', create=True, return_value=0)
def test_user_is_root(_patch):
    result = is_root()
    assert result


@patch.object(os, 'getuid', create=True, return_value=1)
def test_user_is_not_root(_patch):
    result = is_root()
    assert not result
