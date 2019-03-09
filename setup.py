#!/usr/bin/env python3
""" file:   setup.py (explore_australia)
    author: Jess Robertson, @jesserobertson
    date:   October 2016

    description: Setuptools installer script for explore_australia.
"""

from setuptools import setup, find_packages

REQUIREMENTS = [
    'shapely',
    'fiona',
    'rasterio',
    'numpy',
    'scipy',
    'owslib',
    'ipykernel',
    'matplotlib',
    'geopandas',
    'scikit-learn',
    'pint',
    'tqdm'
]
DEV_REQUIREMENTS = [
    'pylint',
    'pytest',
    'pytest-runner',
    'pytest-cov',
    'coverage'
]

## PACKAGE INFORMATION
setup(
    name='explore_australia',
    version="0.1.0",
    description='Data generator for machine learning on exploration data',
    long_description='making something good here',
    author='Jess Robertson',
    author_email='jess@unearthed.solutions',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # Dependencies
    install_requires=[
        REQUIREMENTS
    ],
    extras_require={
        'dev': DEV_REQUIREMENTS
    },
    tests_require=DEV_REQUIREMENTS,

    # Contents
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    test_suite="tests",

    # Some entry points for running CLIs
    entry_points={
        'console_scripts': [
            'get_coverages = explore_australia:cli.main',
        ],
    }
)
