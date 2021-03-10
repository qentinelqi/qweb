# -*- coding: utf-8 -*-
# --------------------------
# Copyright © 2014 - 2020 Qentinel Group. All rights reserved.
#
# The software code and any other material contained in this file are property
# of Qentinel Group and protected by international copyright laws.
# Any copying, re-licensing, re-distribution, development of
# derivative works, or reverse engineering are prohibited.
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
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Robot Framework',
        'Framework :: Robot Framework :: Library'
    ],

    keywords='test automation robot framework',
    author='Qentinel Group',
    author_email='libraries@qentinel.com',

    install_requires=["setuptools",
                      "pyautogui>=0.9.38",
                      "pynput>=1.6.7",
                      "pyperclip==1.7.0",
                      "pyparsing==2.2.2",
                      'requests>=2.22.0',
                      "robotframework==3.2.2",
                      "robotframework-debuglibrary==2.2.1",
                      "selenium>=3.141.0",
                      "msedge-selenium-tools==3.141.2",
                      "Pillow==7.1.0",
                      "scipy==1.4.1",
                      "scikit-image==0.16.2",
                      "ply",
                      "opencv-python==3.4.13.47",
                      "slate3k>=0.5.3"],

    extras_require={':"linux" in sys_platform': ['xlib'],
                    ':"darwin" in sys_platform': ['pyobjc-core', 'pyobjc']}
)
