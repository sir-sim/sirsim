#!/usr/bin/env python
import imp
import io
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import find_packages, setup

root = os.path.dirname(os.path.realpath(__file__))
version_module = imp.load_source(
    'version', os.path.join(root, 'sirsim', 'version.py'))
description = "Tools for building and simulating social decision models"
with open(os.path.join(root, 'README.md')) as readme:
    long_description = readme.read()

setup(
    name="sirsim",
    version=version_module.version,
    author="Terry Stewart, Kirsten Wright, and David Robinson",
    author_email="k4robins@uwaterloo.ca",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sirsim = sirsim:main',
        ]
    },
    scripts=[],
    license="Free for non-commercial use",
    description=description,
    long_description=long_description,
    requires=[
    ],
)






















