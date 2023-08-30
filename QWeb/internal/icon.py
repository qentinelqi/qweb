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
from numpy import ndarray

import cv2
import numpy as np
import math
import os
from pathlib import Path
from QWeb.internal import frame, download, util
from QWeb.internal.meas import MEAS
from QWeb.internal.screenshot import save_screenshot, log_screenshot_file, SCREEN_SHOT_DIR_NAME
from QWeb.internal.config_defaults import CONFIG
from uuid import uuid4


class QIcon:
    """ Functions related to image matching. """

    def __init__(self):
        pass

    @staticmethod
    def _get_image_size(image: ndarray) -> tuple[int, int]:
        """Returns image width and height
        """
        # pylint: disable=no-self-use
        screen_h, screen_w = image.shape[:2]
        return screen_w, screen_h

    @staticmethod
    def _get_scale_ratios(template_res_w: int, device_res_w: int) -> list[float]:
        """Get a list of different scale ratios to scale template image
        for different device resolutions. They should be ordered so
        that more common resolution scalings are at the top of the list.
        Ratios are for scaling 1440p img to 1080p, 720p,
        scaling 1080p img to 1440p, 720p and other, rarer scalings.
        If we know what the resolution of the template should be,
        then scaling that to device resolution will be the first item.

        Parameters
        ----------
        template_res_w : int
            Native resolution (width) of the screenshot
            the template image was a part of before being cropped.
        device_res_w : int
            Resolution of the device we are testing
        """

        scale_ratios = [
            1.00, 0.75, 0.50, 0.86, 0.78, 0.58, 1.33, 0.67, 1.15, 2.00, 1.50, 1.25, 1.75
        ]

        if device_res_w <= 0 or template_res_w <= 0:
            raise ValueError("Device resolution {} or template resolution {}"
                             " can't be zero or less".format(device_res_w, template_res_w))

        if not round(device_res_w / template_res_w, 2) in scale_ratios:
            scale_ratios.insert(0, round(device_res_w / template_res_w, 2))

        return scale_ratios

    @staticmethod
    def _get_image_pyramid(image_obj: ndarray, level: int) -> list[tuple[ndarray, float]]:
        """
        Returns a list of up- and downsampled images of image_obj.
        Each sampling goes 10% up and down in size
        image_obj = Image as uint8 NumPy array in RGB color space.
        level = Image pyramid size - how many times the image is up- and downsampled.
        """
        print("*INFO* Start _get_image_pyramid")
        image_levels = []
        if level == 0:
            image_levels.append((image_obj, 1.0))
        else:
            # width, height = self._get_image_size(image_obj)
            scales = []
            scales.append(1.0)
            for i in range(1, level + 1):
                # scales.append(1.0 + 0.1 * i)
                # scales.append(1.0 - 0.1 * i)
                scales.append(1.0 + 0.05 * i)
                scales.append(1.0 - 0.05 * i)
                # scales.append(1.0 - 0.03 * i)
                # scales.append(1.0 + 0.03 * i)
            # scales.append(1.0)
            # scales.sort()
            print("*DEBUG* Scales: {}".format(scales))
            for scale in scales:
                if scale <= 0:
                    continue
                    # raise ValueError("Scaling Error: Scale coefficient is zero or less."
                    #                 "Scale coefficient: {}."
                    #                 .format(scale))
                if scale < 1.0:
                    image_levels.append((cv2.resize(image_obj,
                                                    None,
                                                    fx=scale,
                                                    fy=scale,
                                                    interpolation=cv2.INTER_LINEAR), scale))
                elif scale == 1.0:
                    image_levels.append((image_obj, scale))
                else:  # scale > 1.0
                    image_levels.append((cv2.resize(image_obj,
                                                    None,
                                                    fx=scale,
                                                    fy=scale,
                                                    interpolation=cv2.INTER_LINEAR), scale))
        return image_levels

    def get_template_locations(
            self,
            image_obj: ndarray,
            template: ndarray,
            threshold: float,
            level: int = 0  # pylint: disable=unused-argument
    ) -> list[tuple[int, int]]:
        """Returns a list of template locations. Uses image pyramid.
        _image_obj_ = Image as uint8 NumPy array in RGB color space.
        _threshold_ = Threshold value for template matching, float.
        _level_ = starting depth of image pyramid.
        """
        # pylint: disable=no-member, too-many-locals, unused-variable, no-self-use
        color_image_obj = image_obj
        if isinstance(image_obj, np.ndarray) and len(image_obj.shape) > 2:
            image_obj = cv2.cvtColor(image_obj, cv2.COLOR_BGR2GRAY)
            # pylint: disable=no-self-use, no-member
        color_template = template
        if isinstance(template, np.ndarray) and len(template.shape) > 2:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        width, height = self._get_image_size(template)
        img_width, img_height = self._get_image_size(image_obj)

        print("*DEBUG* source haystack (image_obj) image size: {}x{}".format(img_width, img_height))
        print("*DEBUG* original needle (template) image size: {}x{}".format(width, height))

        if height > img_height or width > img_width:
            raise ValueError("Image Size Error: Template image is larger than source image. "
                             "Template size: {}x{}, source image size: {}x{}.".format(
                                 width, height, img_width, img_height))
        print("*DEBUG* Resampling by 16 levels for needle, 0 levels for haystack")

        # temp = image_obj
        # image_obj = template
        # template = temp

        MEAS.start("RESAMPLING TIME (_get_image_pyramid)")
        template_levels = self._get_image_pyramid(template, 16)
        MEAS.stop()
        print("*DEBUG* Test print")
        # template_levels = self._get_image_pyramid(template, 0)
        # image_levels = self._get_image_pyramid(image_obj, level)
        image_levels = self._get_image_pyramid(image_obj, 0)

        best_highest_max_val = 0.0
        best_highest_max_val_loc = (-1, -1)
        points = []
        best_scale = 0.0
        best_matched_image: ndarray  # = None

        print("*DEBUG* Different resamplings used: " + str(len(template_levels)))
        # for template_level in template_levels:
        #     w, h = self._get_image_size(template_level)
        #     print("template_level image size: {}x{}".format(w, h))

        MEAS.start("WHOLE TEMPLATE MATCHING AND POINT EXTRACTION TIME")
        for template_level in template_levels:
            w, h = self._get_image_size(template_level[0])
            print("*DEBUG* Resampled needle (template_level) with scale {}, "
                  "image size: {}x{}".format(template_level[1], w, h))
            MEAS.start("CV2.MATCHTEMPLATE TIME")
            res = cv2.matchTemplate(image_levels[0][0], template_level[0], cv2.TM_CCOEFF_NORMED)
            MEAS.stop()
            # print("did matchTemplate, res:\n")
            # print(res)
            MEAS.start("EXTRACT POINTS TIME")
            current_points, highest_max_val, highest_max_val_loc = self._extract_points(
                h, res, threshold, w)
            MEAS.stop()
            # print("did extract_points, points:\n")
            # print(current_points)
            if highest_max_val > best_highest_max_val:
                best_highest_max_val = highest_max_val
                best_highest_max_val_loc = highest_max_val_loc
                points = current_points
                best_scale = template_level[1]
                best_matched_image = template_level[0]
                if best_highest_max_val >= threshold:
                    break
        MEAS.stop()

        if points:
            points.sort(key=lambda coord: (coord[1], coord[0]))
        else:
            print("*INFO* Template image not found. "
                  "Closest match threshold value {} found at {}, {}. "
                  "Threshold used: {}".format(best_highest_max_val, best_highest_max_val_loc[0],
                                              best_highest_max_val_loc[1], threshold))
        print("*INFO* Closest match threshold value {} found at {}, {}.\n"
              "Threshold used: {}\n"
              "Scale with best result: {}".format(best_highest_max_val, best_highest_max_val_loc[0],
                                                  best_highest_max_val_loc[1], threshold,
                                                  best_scale))
        self._log_matched_image(color_image_obj, color_template, best_matched_image,
                                best_highest_max_val_loc, best_scale)
        print("*DEBUG {}".format(points))
        return points

    def image_location(self,
                       needle: str,
                       haystack: str,
                       tolerance: float = 0.95,
                       draw: int = 1,
                       template_res_w: int = 1440,
                       device_res_w: int = 1080) -> tuple[int, int]:
        """Locate an image (needle) within an bigger image (haystack). Tolarance
        is pixel tolerance, i.e. 1.0 = all pixels are correct, 0.5 = 50% of the pixels
        are correct. If we know the original resolution, from which the template
        image is coming, we can supply it as template_res_w.
        Return value is the central (x,y) of the first image found.
        Draw function will plot red lines where needle image is found.
        """

        print("*INFO* _image_location Starts")

        image = cv2.imread(haystack)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _hay_h, hay_w = image_gray.shape[:2]

        needle_path = Path(needle)
        if not needle_path.exists():
            raise Exception("Needle file does not exist. Tried: {}".format(needle_path))
        template = cv2.imread(str(needle_path.resolve()), 0)

        if template is None:
            raise Exception("Cannot read template image. Tried: {}".format(needle))
        height, width = template.shape[:2]

        scale_ratios = self._get_scale_ratios(template_res_w, device_res_w)
        print("*DEBUG* Scale ratios to be used in order: {}".format(scale_ratios))

        best_highest_max_val = 0.0
        best_highest_max_val_loc = (-1, -1)
        best_scale_ratio: float  # = None
        best_matched_image: ndarray  # = None

        print("*DEBUG* Resampling loop Starts")
        for scale_ratio in scale_ratios:
            interpolation_method = cv2.INTER_LINEAR if scale_ratio > 1.0 else cv2.INTER_AREA

            print(("*DEBUG* resize starts: for scale {}".format(scale_ratio)))

            if math.isclose(scale_ratio, 1.0, rel_tol=0.03):
                scaled_img_template = template
            else:
                scaled_img_template = cv2.resize(template,
                                                 None,
                                                 fx=scale_ratio,
                                                 fy=scale_ratio,
                                                 interpolation=interpolation_method)
            print("*DEBUG* matchTemplate Starts:")

            res = cv2.matchTemplate(image_gray, scaled_img_template, cv2.TM_CCOEFF_NORMED)

            ratio = device_res_w / hay_w

            if CONFIG.get_value("RetinaDisplay"):
                ratio = ratio * 2
            elif ratio < 1.1:
                ratio = 1.0

            print("*DEBUG* _extract_points Starts:")
            _current_points, highest_max_val, highest_max_val_loc = \
                self._extract_points(height * scale_ratio,
                                     res,
                                     tolerance,
                                     width * scale_ratio,
                                     ratio)

            if highest_max_val > best_highest_max_val:
                best_highest_max_val = highest_max_val
                best_highest_max_val_loc = highest_max_val_loc

                best_scale_ratio = scale_ratio
                best_matched_image = scaled_img_template
                print("*DEBUG* Current best match location: {},\n"
                      "max_value: {},\n"
                      "scale_ratio: {}".format(best_highest_max_val_loc, best_highest_max_val,
                                               best_scale_ratio))

                if best_highest_max_val > tolerance:
                    if draw == 1:
                        loc = np.where(res >= tolerance)

                        for pt in zip(*loc[::-1]):
                            cv2.rectangle(image, pt, (pt[0] + width, pt[1] + height), (0, 0, 255),
                                          2)
                        cv2.imwrite('temp_matched_area.png', image)
                    break

        print("*DEBUG* Ready to return points:")
        print("*DEBUG* Best match location: {}, best correlation value: {}, "
              "best scale ratio: {}".format(best_highest_max_val_loc, best_highest_max_val,
                                            best_scale_ratio))
        self._log_matched_image(image, template, best_matched_image, best_highest_max_val_loc,
                                best_scale_ratio)

        if best_highest_max_val >= tolerance:
            return best_highest_max_val_loc

        return -1, -1

    @staticmethod
    def _extract_points(height: int,
                        res: ndarray,
                        threshold: float,
                        width: int,
                        coordinate_ratio: float = 1.0
                        ) -> tuple[list[tuple[int, int]], float, tuple[int, int]]:
        """Extracts match locations from a result matrix. This goes through the best
        match locations in the result and while the correlation value of a location
        is over the threshold, it adds the location to the list of best locations.
        It then masks a template-sized area of the result matrix and continues while
        the correlation value of the best remaining location is over threshold.
        Returns the best locations that reach the threshold and separately the best
        location and the corresponding correlation value.
        """
        i = 0
        points = []
        highest_max_val = 0.0
        highest_max_val_loc = (-1, -1)
        while True:
            if i == 100:
                break
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            top_left = max_loc
            if max_val >= highest_max_val:
                highest_max_val = max_val
                highest_max_val_loc = (int(round((top_left[0] + width / 2) * coordinate_ratio)),
                                       int(round((top_left[1] + height / 2) * coordinate_ratio)))
            if max_val > threshold:
                # flood fill the already found area
                for loc_x in range(int(round(top_left[0] - width / 2)),
                                   int(round(top_left[0] + width / 2))):
                    for loc_y in range(int(round(top_left[1] - height / 2)),
                                       int(round(top_left[1] + height / 2))):
                        try:
                            res[loc_y][loc_x] = np.float32(-10000)  # -MAX
                        except IndexError:  # ignore out of bounds
                            pass
                points.append(highest_max_val_loc)
                i += 1
            else:
                break

        print("*DEBUG* Extracted points.\n"
              "Coordinate ratio was {}\n"
              "Highest max value was {}\n"
              "Highest max value location was {}\n"
              "All points: {}".format(coordinate_ratio, highest_max_val, highest_max_val_loc,
                                      points))
        return points, highest_max_val, highest_max_val_loc

    @staticmethod
    def _log_matched_image(haystack: ndarray, needle: ndarray, scaled_needle: ndarray,
                           loc: tuple[int, int], best_scale: float) -> None:
        """Draw a composite image with the needle image, the haystack image,
        the scaled needle that matches the best and show where in haystack
        the best match is. This is best used in debugging, but it could be
        modified to add the image to the Robot log as well.
        """
        needle = cv2.cvtColor(needle, cv2.COLOR_GRAY2BGR)
        scaled_needle = cv2.cvtColor(scaled_needle, cv2.COLOR_GRAY2BGR)
        h1, w1 = needle.shape[:2]
        hs, ws = scaled_needle.shape[:2]
        h2, w2 = haystack.shape[:2]
        max_left_w = max(w1, ws)
        cv2.rectangle(haystack,
                      (loc[0] - int(w1 / 2 * best_scale), loc[1] - int(h1 / 2 * best_scale)),
                      (loc[0] + int(w1 / 2 * best_scale), loc[1] + int(h1 / 2 * best_scale)),
                      (0, 0, 255), 2)
        result = np.zeros((max(h2, h1), w2 + max_left_w, 3), np.uint8)
        result[:h1, :w1, :3] = needle
        result[h1:h1 + hs, :ws, :3] = scaled_needle
        result[:h2, max_left_w:max_left_w + w2, :3] = haystack

        cv2.line(result, (ws, h1), (loc[0] + max_left_w + int(ws / 2), loc[1] - int(hs / 2)),
                 (0, 0, 255), 2)
        cv2.line(result, (0, h1 + hs), (loc[0] + max_left_w - int(ws / 2), loc[1] + int(hs / 2)),
                 (0, 0, 255), 2)

        if CONFIG.get_value("LogMatchedIcons"):
            output = util.get_rfw_variable_value('${OUTPUT DIR}') or os.getcwd()
            filename = "temp_matched_image-{}".format(uuid4()) + ".png"
            filepath = os.path.join(output, SCREEN_SHOT_DIR_NAME, filename)
            cv2.imwrite(filepath, result)
            log_screenshot_file(filepath)


def image_recognition(image_path: str, template_res_w: int, browser_res_w: int,
                      pyautog: bool) -> tuple[int, int]:
    """Return icon's coordinates."""
    image_rec = QIcon()
    frame.wait_page_loaded()
    screenshot_path = save_screenshot("screenshot.png", pyautog=pyautog)
    x, y = image_rec.image_location(needle=image_path,
                                    haystack=screenshot_path,
                                    template_res_w=template_res_w,
                                    device_res_w=browser_res_w)
    return x, y


def get_full_image_path(icon: str) -> Path:
    """Return image's full path."""
    if icon.endswith('.png') or icon.endswith('.jpg'):
        full_path = download.get_path(icon)
    else:
        full_path = download.get_path('{}.png'.format(icon))
    return full_path
