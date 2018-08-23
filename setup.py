#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import setup

# Package meta-data.
NAME = 'pykube'
DESCRIPTION = 'Automate Kubernetes workflow.'
URL = 'https://github.com/zyt312074545/pykube'
EMAIL = 'zyt312074545@gmail.com'
AUTHOR = 'zyt'
VERSION = '0.0.1'

# What packages are required for this module to be executed?
REQUIRED = [
    'click', 'pyyaml', 'prompt-toolkit'
]

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires='>=3.6.0',
    py_modules=['pykube'],
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    entry_points='''
        [console_scripts]
        pykube=pykube:cli
    ''',
)
