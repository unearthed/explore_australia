import pathlib

import rasterio
from rasterio import crs, warp
from rasterio.transform import from_origin
from shapely import geometry
from tqdm import tqdm
import click
import numpy as np

from .geometry import make_box
from .rotation import rotate
from . import CoverageService

def make_stamp(centre, angle=None, distance=25):
    "make a random stamp"
    angle = angle or np.random.uniform(0, 360)
    return rotate(make_box(centre, distance=distance), centre, angle)

def omerc_projection(centre, angle):
    "Get a projection string for a oblique Mercator at some centre point rotated by angle"
    centre_lat = centre.y
    centre_lon = centre.x
    return (
        f"+proj=omerc +lat_0={centre_lat} +lonc={centre_lon} +alpha=-{angle} "\
        "+k=1 +x_0=0 +y_0=0 +gamma=0 "
        "+ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
    )

def rasterio_reprojection_meta(centre, angle, distance=10, width=250, height=250):
    """
    Return a custom projection and grid transform rotated through some angle
    """
    km = 1000
    half = distance / 2
    return dict(
        driver='GTiff',
        dtype='float32',
        nodata=None,
        count=1,
        width=width,
        height=height,
        transform=from_origin(
            -half * km,
            half * km,
            distance * km / (width - 1),
            distance * km / (height - 1)
        ),
        crs=crs.CRS.from_string(omerc_projection(centre, angle))
    )

def get_stamp(output, wcs, stamp, centre, angle, distance, npoints=500):
    """
    Reproject raster
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

# endpoint data
radmap = {
    'filtered_terrestrial_dose': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_dose/radmap_v3_2015_filtered_dose.nc',
    'filtered_potassium_pct': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_pctk/radmap_v3_2015_filtered_pctk.nc',
    'filtered_thorium_ppm': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_ppmth/radmap_v3_2015_filtered_ppmth.nc',
    'filtered_uranium_ppm': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_ppmu/radmap_v3_2015_filtered_ppmu.nc'
}

magnetics = {
    'variable_reduction_to_pole': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/magmap_v6_2015_VRTP/magmap_v6_2015_VRTP.nc',
    'total_magnetic_intensity': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/magmap_v6_2015/magmap_v6_2015.nc'
}

aster = {
    'aloh_group_composition': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_AlOH_group_composition_reprojected.nc4',
    'ferrous_iron_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Ferrous_Iron_Index_reprojected.nc4',
    'opaque_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Opaque_Index_reprojected.nc4',
    'ferric_oxide_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Ferric_oxide_content_reprojected.nc4',
#         'feoh_group_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_FeOH_group_content_reprojected.nc4',
    'kaolin_group_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Kaolin_group_index_reprojected.nc4',
    'tir_quartz_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Quartz_Index_reprojected.nc4',
    'mgoh_group_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_MgOH_group_content_reprojected.nc4',
#         'mgoh_group_composition': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_MgOH_group_composition_reprojected.nc4',
    'ferrous_iron_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Ferrous_iron_content_in_MgOH_reprojected.nc4',
    'aloh_groun_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_AlOH_group_content_reprojected.nc4',
    'thermal_infrared_gypsum_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Gypsum_Index_reprojected.nc4',
    'thermal_infrared_silica_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Silica_Index_reprojected.nc4'
}

gravity = {
    'isostatic_residual_gravity_anomaly': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/onshore_geodetic_Isostatic_Residual_v2_2016/onshore_geodetic_Isostatic_Residual_v2_2016.nc',
    'bouger_gravity_anomaly': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/onshore_geodetic_Complete_Bouguer_2016/onshore_geodetic_Complete_Bouguer_2016.nc',
}

total_coverages = len(aster) + len(gravity) + len(radmap) + len(magnetics)

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
    with tqdm(total=total_coverages, desc='Downloading coverages') as pbar:
        for layer in radmap:
            output = root / 'geophysics' / 'radiometrics' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, radmap[layer], **kwargs)
            pbar.update(1)
        for layer in magnetics:
            output = root / 'geophysics' / 'magnetics' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, magnetics[layer], **kwargs)
            pbar.update(1)
        for layer in aster:
            output = root / 'remote_sensing' / 'aster' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, aster[layer], **kwargs)
            pbar.update(1)
        for layer in gravity:
            output = root / 'geophysics' / 'gravity' / f'{layer}.tif'
            if not output.exists():
                get_stamp(output, gravity[layer], **kwargs)
            pbar.update(1)