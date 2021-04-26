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

from setuptools import find_packages, setup
import versioneer

setup(
    name="QWeb",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Keyword driven automation for the web",
    url='https://github.com/qentinelqi/qweb/',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),

    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Robot Framework',
        'Framework :: Robot Framework :: Library'
    ],

    keywords='test automation robot framework',
    author='Qentinel Group',
    author_email='libraries@qentinel.com',
    python_requires= ">=3.6,<4.0",
    install_requires=["setuptools",
                      "pyautogui>=0.9.38",
                      "pynput>=1.6.7",
                      "pyperclip==1.7.0",
                      "pyparsing==2.2.2",
                      'requests>=2.22.0',
                      "robotframework>=3.2.2",
                      "robotframework-debuglibrary==2.2.1",
                      "selenium>=3.141.0",
                      "msedge-selenium-tools==3.141.2",
                      "Pillow==8.1.1",
                      "scipy==1.5.*",
                      "scikit-image==0.17.2;python_version=='3.6'",
                      "scikit-image==0.18.0;python_version>'3.6'",
                      "ply",
                      "opencv-python==3.4.13.47",
                      "slate3k>=0.5.3"],

    extras_require={':"linux" in sys_platform': ['xlib'],
                    ':"darwin" in sys_platform': ['pyobjc-core', 'pyobjc']}
)
