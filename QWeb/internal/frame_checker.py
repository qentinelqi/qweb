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

from robot.api import logger
from QWeb.internal import javascript


def check_frames(driver, **kwargs):
    visible_frames = []
    frames = javascript.execute_javascript(
        'return document.querySelectorAll("iframe, frame")')
    frames += driver.find_elements_by_xpath("//iframe|//frame")
    visible_only = kwargs.get('visibility', True)
    if not visible_only:
        return frames
    frames_obj = javascript.get_visibility(list(dict.fromkeys(frames)))
    for frame in frames_obj:
        offset = frame.get('offset')
        if offset:
            visible_frames.append(frame.get('elem'))
    if visible_frames:
        logger.debug('Found {} visible frames'.format(len(visible_frames)))
    return visible_frames
