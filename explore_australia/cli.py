""" file:    cli.py (explore_australia)
    author: Jess Robertson, jess@unearthed.solutions
    date:    Saturday, 09 March 2019

    description: CLI implementation
"""
import logging

import click

from .stamp import get_coverages, Stamp

LOGGER = logging.getLogger('explore_australia')

@click.command()
@click.option('--lat', type=float, help='Central latitude of the coverage, in degrees')
@click.option('--lon', type=float, help='Central longitude of the coverage, in degrees')
@click.option('--distance', type=int, default=25, help='The approximate length of the sides of the coverage (in km)')
@click.option('--angle', type=float, default=None, help='An angle to rotate the box, in degrees')
@click.option('--no-crs', is_flag=True, help='If set, remove CRS from data')
@click.argument('name')
def main(name, lat, lon, angle, distance, no_crs):
    """
    Get coverages for a given centre and angle

    Note that because we're getting a square on the surface of the earth,
    it might not be an exact square! Distances are approximate, depending
    on latitude.
    """
    stamp = Stamp(lat=lat, lon=lon, angle=angle or 0, distance=distance)
    get_coverages(name=name, stamp=stamp, no_crs=no_crs, show_progress=True)

if __name__ == '__main__':
    main()
