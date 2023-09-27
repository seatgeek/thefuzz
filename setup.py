#!/usr/bin/env python

# Copyright (c) 2014 SeatGeek

# This file is part of thefuzz.

from thefuzz import __version__
from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='thefuzz',
    version=__version__,
    author='Adam Cohen',
    author_email='adam@seatgeek.com',
    packages=['thefuzz'],
    # keep for backwards compatibility of projects depending on `thefuzz[speedup]`
    extras_require={'speedup': []},
    install_requires=['rapidfuzz>=3.0.0, < 4.0.0'],
    url='https://github.com/seatgeek/thefuzz',
    license="GPLv2",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
    ],
    description='Fuzzy string matching in python',
    long_description=long_description,
    zip_safe=True,
    python_requires='>=3.8'
)
