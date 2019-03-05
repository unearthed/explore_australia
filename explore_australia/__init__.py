""" file:    __init__.py (explore_australia)
    author:  Jess Robertson, jess@unearthed.solutions
    date:    Tuesday, 05 March 2019

    description: imports
"""

from ._version import __version__
from .coverage import CoverageService
from .geometry import make_box
from . import coverage, geometry, vector, utilities, cli
