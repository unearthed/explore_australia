""" file:    stamp.py (explore_australia)
    author:  Jess Robertson, jess@unearthed.solutions
    date:    Saturday, 09 March 2019

    description: Utilities for generating stamps at scale
"""

import pathlib
import concurrent.futures
import logging

from tqdm import tqdm
from shapely import geometry
import rasterio
from rasterio import warp
import numpy as np

from . import CoverageService
from .raster import rasterio_reprojection_meta
from .geometry import make_stamp
from .endpoints import GRAVITY, MAGNETICS, RADMAP, ASTER, TOTAL_COVERAGES

def get_stamp(output, wcs, stamp, centre, angle, distance,
              npoints=500, remove_crs=False):
    """
    Get the raster in a given stamp area from a WCS

    Warps the raster into a locally uniform oblique Mercator projection

    Parameters:
        output - the mane of the output tif file
        wcs - the URL pointing to the WCS endpoint
        stamp - the stamp to use to crop the data
        centre - the centre of the box, given as a shapely Point object
        angle - the angle to rotate the box through, in degrees
        distance - the approximate length of the sides of the box (in km)
        npoints - the number of points per side in the new stamp
        remove_crs - if True, remove coordinate reference system before writing
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
        if remove_crs:
            output_meta['crs'] = None
        with rasterio.open(output, 'w', **output_meta) as sink:
            sink.write(destination, 1)
    finally:
        if _temp.exists():
            _temp.unlink()

def get_coverages(name, lat, lon, angle, distance, no_crs, show_progress=True):
    """
    Get coverages for a given centre and angle

    Note that because we're getting a square on the surface of the earth,
    it might not be an exact square! Distances are approximate, depending
    on latitude.

    Parameters:
        lat - Central latitude of the coverage, in degrees
        lon - Central longitude of the coverage, in degrees
        distance - The approximate length of the sides of the coverage (in km)
        angle - An angle to rotate the box, in degrees from north
        no_crs - if True, remove CRS from data
        show_progress - if True, show a progress bar
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
    if no_crs:
        kwargs['remove_crs'] = True

    # Construct folder structure
    root = pathlib.Path(name)
    folders = [
        (GRAVITY, root / 'geophysics' / 'gravity'),
        (MAGNETICS, root / 'geophysics' / 'magnetics'),
        (RADMAP, root / 'geophysics' / 'radiometrics'),
        (ASTER, root / 'remote_sensing' / 'aster'),
    ]
    for _, folder in folders:
        if not folder.exists():
            folder.mkdir(parents=True)

    # Download data
    if show_progress:
        with tqdm(total=TOTAL_COVERAGES, desc='Downloading coverages') as pbar:
            for endpoints, folder in folders:
                for layer, endpoint in endpoints.items():
                    output_tif = folder / f'{layer}.tif'
                    if not output_tif.exists():
                        get_stamp(output_tif, endpoint, **kwargs)
                    pbar.update(1)
    else:
        for endpoints, folder in folders:
            for layer, endpoint in endpoints.items():
                output_tif = folder / f'{layer}.tif'
                if not output_tif.exists():
                    get_stamp(output_tif, endpoint, **kwargs)

def get_coverages_parallel(stamps, logfile='get_stamps.log'):
    """
    Get stamp raster data in parallel using a threadpool

    Parameters:
        stamps - a dataframe with 'id', 'centre_latitude', 'centre_longitude'
            and 'rotation' columns to generate all the stamps
    """
    # Some info about how we're going to run
    total_stamps = len(stamps)
    nworkers = 10

    # Set up basic logging to file
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=logfile,
                        filemode='a')

    # Map row to arguments
    row_to_kwargs = lambda row: dict(
        name=row.id,
        lat=row.centre_latitude,
        lon=row.centre_longitude,
        angle=row.rotation,
        distance=25,
        no_crs=True,
        show_progress=False
    )

    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=nworkers) as executor:
        # Start the load operations and mark each future with the name
        future_to_args = {
            executor.submit(get_coverages, **row_to_kwargs(row)): row.id
            for _, row in tqdm(stamps.iterrows(), total=total_stamps, desc='Loading futures')
        }

        # Iterate over futures and collect them as they're sent, logging to file
        for future in tqdm(concurrent.futures.as_completed(future_to_args),
                           total=total_stamps, desc='Collecting futures'):
            key = future_to_args[future]
            try:
                _ = future.result()
                del future_to_args[future]
                del future
            except Exception as exc:
                logging.error('Stamp %s get generated an exception: %s\n', key, exc)
