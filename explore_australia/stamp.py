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

from . import CoverageService, endpoints
from .geometry import make_stamp

class Stamp:

    """
    Class to manage stamp geometry

    Parameters:
        lon, lat - the longitude and latitude of the centre of the stamp.
        angle - an angle through which the stamp is rotated.
        distance - the length of the side of the stamp.
        n_pixels - the number of points in a raster in the stamp. Optional,
            defaults to 500 pixels. If one-dimensional (e.g. `n_pixels=500`),
            sets the number to be the same in both dimensions, if two-dimensional
            (e.g. `n_pixels=(350, 400)`), sets the pixels seperately. Optional,
            defaults to 500.
    """

    def __init__(self, lon, lat, angle=0, distance=25, n_pixels=500):
        self.lon, self.lat = lon, lat
        self.angle = angle
        self.distance = distance
        try:
            self.width, self.height = n_pixels
        except TypeError:
            self.width, self.height = n_pixels, n_pixels

        # Set up geometry
        self.centre = geometry.Point(self.lon, self.lat)
        self.geometry = make_stamp(centre=self.centre, angle=self.angle, distance=self.distance)

        # Set up other stuff - gets calculated on the fly
        self._crs, self._transform = None, None

    @property
    def crs(self):
        "Return a local oblique Mercator CRS"
        if self._crs is None:
            self._crs = (
                f"+proj=omerc +lat_0={self.centre.y} +lonc={self.centre.x} +alpha={self.angle} "\
                "+k=1 +x_0=0 +y_0=0 +gamma=0 "
                "+ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
            )
        return self._crs

    @property
    def transform(self):
        "Return a raster transform"
        if self._transform is None:
            kilometres = 1000  # from crs, everything needs to be in m
            half = self.distance / 2
            self._transform = rasterio.transform.from_origin(
                -half * kilometres,
                half * kilometres,
                self.distance * kilometres / (self.width - 1),
                self.distance * kilometres / (self.height - 1)
            )
        return self._transform

    @property
    def rasterio_crs(self):
        "Return the CRS as a rasterio object"
        return rasterio.crs.CRS.from_string(self.crs)

    def get_tiff_metadata(self, dtype=None, nodata=None, count=1):
        "Return the metadata required to generate a reprojected geotiff"
        return dict(
            driver='GTiff',
            dtype=dtype or 'float32',
            nodata=nodata,
            count=count,
            width=self.width,
            height=self.height,
            transform=self.transform,
            crs=self.rasterio_crs
        )

def get_stamp(wcs, stamp, output='output.tif', remove_crs=False):
    """
    Get the raster in a given stamp area from a WCS

    Warps the raster into a local CRS

    Parameters:
        output - the name of the output tif file
        wcs - the URL pointing to the WCS endpoint
        stamp - the stamp to use to crop the data
        crs - the output local crs for the raster
        distance - the approximate length of the sides of the box (in km)
        npoints - the number of points per side in the new stamp
        remove_crs - if True, remove coordinate reference system before writing
    """
    # Get data
    try:
        serv = CoverageService(wcs)
        _temp = pathlib.Path(serv(stamp.geometry.bounds))

        # Warp input to output
        with rasterio.open(_temp, 'r') as src, \
             rasterio.open(output, 'w', **stamp.get_tiff_metadata()) as sink:
            src_band = rasterio.band(src, 1)
            dst_band = rasterio.band(sink, 1)
            rasterio.warp.reproject(
                source=src_band,
                destination=dst_band,
                resampling=rasterio.warp.Resampling.nearest
            )

        # Dump output to file without CRS info
        if remove_crs:
            kwargs = stamp.get_tiff_metadata()
            kwargs['crs'] = None
            with rasterio.open(output, 'r') as src:
                data = src.read(1)
            with rasterio.open(output, 'w', **kwargs) as sink:
                sink.write(data, 1)
        return output
    finally:
        try:
            if _temp.exists():
                _temp.unlink()
        except NameError:
            pass

def get_coverages(name, stamp, no_crs=True, show_progress=True):
    """
    Get coverages for a given centre and angle

    Note that because we're getting a square on the surface of the earth,
    it might not be an exact square! Distances are approximate, depending
    on latitude.

    Parameters:
        crs - the local crs for the stamp
        stamp - the geometry for the stamp
        distance - The approximate length of the sides of the coverage (in km)
        angle - An angle to rotate the box, in degrees from north
        no_crs - if True, remove CRS from data
        show_progress - if True, show a progress bar
    """
    # Contruct endpoints and folders
    root = pathlib.Path(name)
    folders = [
        (endpoints.GRAVITY, root / 'geophysics' / 'gravity'),
        (endpoints.MAGNETICS, root / 'geophysics' / 'magnetics'),
        (endpoints.RADMAP, root / 'geophysics' / 'radiometrics'),
        (endpoints.ASTER, root / 'remote_sensing' / 'aster'),
        #(endpoints.ASTER_TAS, root / 'remote_sensing' / 'aster'),
    ]
    for _, folder in folders:
        if not folder.exists():
            folder.mkdir(parents=True)

    # Download data
    if show_progress:
        failed = []
        with tqdm(total=endpoints.TOTAL_COVERAGES, desc='Downloading coverages') as pbar:
            for wcses, folder in folders:
                for layer, wcs in wcses.items():
                    output_tif = folder / f'{layer}.tif'
                    if not output_tif.exists():
                        try:
                            get_stamp(wcs=wcs, stamp=stamp, output=output_tif, remove_crs=no_crs)
                        except:
                            failed.append([wcs, stamp.centre])
                    pbar.update(1)
        if failed:
            for wcs, centre in failed:
                print(f'Failed to get {wcs} for ({centre})')
    else:
        for wcses, folder in folders:
            for layer, wcs in wcses.items():
                output_tif = folder / f'{layer}.tif'
                if not output_tif.exists():
                    try:
                        get_stamp(wcs=wcs, stamp=stamp, output=output_tif, remove_crs=no_crs)
                    except:
                        continue

def proj_to_stamp(proj):
    "Convert an orthogonal Mercator projection to a stamp"
    # Convert proj string to a dict
    kwargs = {}
    for defn in (s.strip().split('=') for s in proj.split('+')):
        try:
            kwargs[defn[0]] = defn[1]
        except IndexError:
            if defn[0]:
                kwargs[defn[0]] = True

    # Get the values we care about
    return Stamp(
        lat=float(kwargs['lat_0']),
        lon=float(kwargs['lonc']),
        angle=float(kwargs['alpha']),
        distance=25,
        n_pixels=500
    )

def get_coverages_parallel(stamps, logfile='get_stamps.log'):
    """
    Get stamp raster data in parallel using a threadpool

    Parameters:
        stamps - a geodataframe with 'id' and 'local_projection'
            columns containing stamp info
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
        stamp=proj_to_stamp(row.local_projection),
        no_crs=False,
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
