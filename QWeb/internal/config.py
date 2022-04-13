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

import copy


class Config:

    DROPPED_DELIMITER_CHARS: str = " _-"

    def __init__(self, config_defaults: dict[str, Any]) -> None:
        self._config_defaults = {}
        # Clean config_defaults key values before storage
        _config_defaults = {}
        for k, v in config_defaults.items():
            _k = self._clean_string(k)
            _config_defaults[_k] = copy.deepcopy(v)
        self._config_defaults.update(_config_defaults)
        self.config = copy.deepcopy(self._config_defaults)

    def is_value(self, par: str) -> bool:
        """ Return True if parameter exists. """
        _par = self._clean_string(par)
        return _par in self.config

    def get_value(self, par: str) -> Optional[Any]:
        """ Return value(s) for given parameter,
            or None if parameter doesn't exist. """
        _par = self._clean_string(par)
        config_value, _ = self.config.get(_par, (None, None))
        return config_value

    def get_all_values(self) -> dict[str, Any]:
        """
        Return all configuration values in a dictionary.
        :return: configuration dict
        """
        _all_configs = {}
        for k, v in self.config.items():
            _all_configs[k] = copy.deepcopy(v[0])
        return _all_configs

    def set_value(self, par: str, value: Any) -> Any:
        """ Set value for given parameter. Setter uses pre-defined adapter function to process value
        before storage. Adapter functions are set in config_defaults. Returns old value. """
        _par = self._clean_string(par)
        if not self.is_value(_par):
            raise ValueError("Parameter {} doesn't exist".format(par))
        old_val, adapter_func = self.config[_par]
        stored_value = adapter_func(value) if adapter_func else value
        self.config[_par] = (stored_value, adapter_func)
        return old_val

    def reset_value(self, par: Optional[str] = None) -> None:
        """ Reset value(s) to original. """
        if par:
            _par = self._clean_string(par)
            self.config[_par] = copy.deepcopy(self._config_defaults[_par])
            # trigger adapter func for clearkey
            if "clearkey" in _par:
                val, adapter_func = self.config[_par]
                if adapter_func:
                    adapter_func(str(val))
        else:
            self.config = copy.deepcopy(self._config_defaults)
            # handle clearkey separately
            _par = self._clean_string("ClearKey")
            val, adapter_func = self.config[_par]
            self.set_value(_par, str(val))

    def __getitem__(self, par: str) -> Any:
        """ Allow accessing parameters in dictionary like syntax."""
        _par = self._clean_string(par)
        config_value, _ = self.config[_par]
        return config_value

    def __repr__(self) -> dict[str, Any]:  # type: ignore[override]
        return self.config

    def __str__(self) -> str:
        return "{}".format(self.config)

    @staticmethod
    def _clean_string(string_value: str) -> str:
        dropped_chars_dict = dict.fromkeys(Config.DROPPED_DELIMITER_CHARS)
        trans_table = str.maketrans(dropped_chars_dict)
        _string_value = string_value.lower().translate(trans_table)
        return _string_value
