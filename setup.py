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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Robot Framework',
        'Framework :: Robot Framework :: Library'
    ],

    keywords='test automation robot framework',
    author='Qentinel Group',
    author_email='libraries@qentinel.com',
    python_requires= ">3.6,<4.0",
    license= "Apache License 2.0",
    install_requires=["setuptools>=65.5.1",
                      "pyscreeze>=0.1.28",
                      "pyautogui>=0.9.53",
                      "pynput>=1.7.6",
                      'requests>=2.27.0',
                      "robotframework>=3.2.2,<7",
                      "robotframework-debuglibrary==2.3.0",
                      "selenium==4.6.0",
                      "Pillow==9.3.0",
                      "scipy>=1.7.3",
                      "scikit-image==0.19.1",
                      "ply",
                      "opencv-python==4.5.5.62",
                      "slate3k>=0.5.3"],

    extras_require={':"linux" in sys_platform': ['xlib'],
                    ':"darwin" in sys_platform': ['pyobjc-core==8.3', 'pyobjc==8.3']}
)
