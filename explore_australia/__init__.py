""" file:    __init__.py (explore_australia)
    author:  Jess Robertson, @jesserobertson
    date:    Wednesday, 02 January 2019

    description: Init script for explore_australia
"""

from ._version import __version__
from .coverage import CoverageService
from .geometry import make_box
from . import coverage, geometry, vector, utilities, cli, stamp
