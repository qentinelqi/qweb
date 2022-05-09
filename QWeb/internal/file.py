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
from typing import Any, Union
from pathlib import Path
import os
import slate3k as slate_pdf_reader
from pdfminer.pdfparser import PSEOF
from QWeb.internal import download, util
from QWeb.internal.exceptions import QWebFileNotFoundError, QWebValueMismatchError


class File:

    ACTIVE_FILE: Any = None

    def __init__(self, content: Any, file: Union[str, Path]):
        self.content = content
        self.file = file
        File.ACTIVE_FILE = self

    @staticmethod
    def create_pdf_instance(filename: str) -> File:
        all_text = ''
        filepath = download.get_path(filename)
        try:
            with open(filepath, 'rb') as pdf_obj:
                pdf = slate_pdf_reader.PDF(pdf_obj)
                for page in pdf:
                    all_text += page.strip()
                if all_text != '':
                    return File(all_text, filepath)
                raise QWebValueMismatchError('Text not found. Seems that the pdf is empty.')
        except TypeError as e:
            raise QWebFileNotFoundError(f'File not found. Got {e} instead.') from e
        except PSEOF as e:
            raise QWebFileNotFoundError(f'File found, but it\'s not valid pdf-file: {e}') from e

    @staticmethod
    def create_text_file_instance(filename: str) -> File:
        filepath = download.get_path(filename)
        try:
            with open(filepath, 'rb') as txt_file:
                filebytes = txt_file.read()
                data = filebytes.decode("utf-8")
                if data != '':
                    return File(data, filepath)
                raise QWebValueMismatchError('Text not found. Seems that the file is empty.')
        except TypeError as e:
            raise QWebFileNotFoundError('File not found. Got {} instead.'.format(e)) from e

    def get(self, **kwargs) -> Any:
        if kwargs:
            return util.get_substring(self.content, **kwargs)
        return self.content

    def verify(self, text: str, normalize: bool = False) -> bool:
        txt_content = self._normalize_text(self.content) if normalize else self.content
        if text in txt_content:
            return True
        raise QWebValueMismatchError('File did not contain the text "{}"'.format(text))

    def remove(self) -> None:
        os.remove(self.file)

    def get_index_of(self, text: str, condition: Union[int, str, bool]) -> int:
        index = self.content.find(text)
        if index > -1:
            if util.par2bool(condition) is False:
                index += len(text)
            return index
        raise QWebValueMismatchError('File did not contain the text "{}"'.format(text))

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(text.replace("\n", " ").split())
