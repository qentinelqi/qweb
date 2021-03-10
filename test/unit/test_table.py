# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------

from QWeb.internal import table


def test_convert_coordinates():
    # pylint: disable=W0212
    table_obj = table.Table(None, 'locator', 'anchor')
    assert table_obj._convert_coordinates('r1c3') == (1, 3)
    assert table_obj._convert_coordinates('c1r3') == (3, 1)
    assert table_obj._convert_coordinates('r12c3') == (12, 3)
    assert table_obj._convert_coordinates('r7c42') == (7, 42)
    assert table_obj._convert_coordinates('r31337c652') == (31337, 652)
