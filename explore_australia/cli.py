import pathlib

import rasterio
from rasterio import crs, warp
from shapely import geometry
from tqdm import tqdm
import click
import numpy as np

from .geometry import make_box, make_stamp
from .rotation import rotate
from .utilities import omerc_projection
from .endpoints import ASTER, GRAVITY, MAGNETICS, RADMAP, TOTAL_COVERAGES
from . import CoverageService

def get_stamp(output, wcs, stamp, centre, angle, distance, npoints=500):
    """
    Get the raster in a given stamp area from a WCS

    Parameters:
        output - the mane of the output tif file
        wcs - the URL pointing to the WCS endpoint
        stamp - the stamp to use to crop the data
        centre - the centre of the box, given as a shapely Point object
        angle - the angle to rotate the box through, in degrees
        distance - the approximate length of the sides of the box (in km)
        npoints - the number of points per side in the new stamp
    """
    # Get data
    try:
        serv = CoverageService(wcs)
        _temp = pathlib.Path(serv(stamp.bounds))

        # Construct output metadata
        width = height = npoints
        output_meta = rasterio_reprojection_meta(
            distance=distance,
            centre=centre,
            angle=angle,
            width=width,
            height=height
        )

        # Warp input to output
        destination = np.empty((output_meta['width'], output_meta['height']),
                               dtype=np.float32)
        with rasterio.open(_temp, 'r') as src:
            warp.reproject(
                source=src.read(1),
                destination=destination,
                src_transform=src.meta['transform'],
                src_crs=src.meta['crs'],
                dst_transform=output_meta['transform'],
                dst_crs=output_meta['crs'],
                resampling=warp.Resampling.nearest
            )

        # Dump output to file without CRS info
        output_meta['crs'] = None
        with rasterio.open(output, 'w', **output_meta) as sink:
            sink.write(destination, 1)
    finally:
        if _temp.exists():
            _temp.unlink()

@click.command()
@click.option('--lat', type=float, help='latitude')
@click.option('--lon', type=float, help='longitude')
@click.option('--distance', type=int, default=25, help='scale in km')
@click.option('--angle', type=float, default=None, help='angle to rotate')
@click.argument('name')
def get_coverages(name, lat, lon, angle, distance=25):
    """
    Get coverages for a given centre and angle
    """
    # Construct stamp
    centre = geometry.Point(lon, lat)
    stamp = make_stamp(centre, angle=angle, distance=distance)
    kwargs = {
        'centre': centre,
        'angle': angle,
        'distance': distance,
        'stamp': stamp
    }

    # Construct folder structure
    root = pathlib.Path(name)
    folders = [
        root / 'geophysics' / 'gravity',
        root / 'geophysics' / 'magnetics',
        root / 'geophysics' / 'radiometrics',
        root / 'remote_sensing' / 'aster',
        root / 'geology',
        root / 'chemistry'
    ]
    for folder in folders:
        if not folder.exists():
            folder.mkdir(parents=True)
    with tqdm(total=TOTAL_COVERAGES, desc='Downloading coverages') as pbar:
        for layer in RADMAP:
            output = root / 'geophysics' / 'radiometrics' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, RADMAP[layer], **kwargs)
            pbar.update(1)
        for layer in MAGNETICS:
            output = root / 'geophysics' / 'magnetics' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, MAGNETICS[layer], **kwargs)
            pbar.update(1)
        for layer in ASTER:
            output = root / 'remote_sensing' / 'aster' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, ASTER[layer], **kwargs)
            pbar.update(1)
        for layer in GRAVITY:
            output = root / 'geophysics' / 'gravity' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, GRAVITY[layer], **kwargs)
            pbar.update(1)