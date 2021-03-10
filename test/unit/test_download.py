# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
# ---------------------------
from QWeb.internal.download import get_modified_files
from unittest.mock import patch


def notfounderror(_):
    # This should be FileNotFoundError but is does not exist in Py2
    raise IOError()


@patch('os.listdir')
def test_no_dl_directory(patch_listdir):
    patch_listdir.return_value = ['asdf']
    patch_listdir.side_effect = notfounderror
    assert get_modified_files('foo', 1) == []
