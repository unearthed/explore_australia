# explore_australia

Access to Australia-wide public data for OZ Minerals/Unearthed Explorer challenge - the jumpstarter repo!

## Installation

This is a basic Python package but it makes use of a number of system libraries to read/write geospatial data. We recommed using Anaconda to manage these libraries otherwise you're likely to get burnt with strange C++ exceptions & dependency conflicts. Download Anaconda for your system [here](https://www.anaconda.com/distribution/). Either the full distribution or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) is fine.

We've provided a conda environment file to install all the required dependencies - `environment.yml`. You can create the environment and install the dependencies with:

```bash
$ cd /path/to/explore_australia

$ conda env create --file environment.yml
Collecting package metadata/|\-
# ...snip output

$ conda activate explore_australia

(explore_australia) $ # you should see the prompt change
```

Then you can install the package with:

```bash
(explore_australia) $ python setup.py install
running install
# ...snip output
Successfully installed explore_australia
```

This should install the python package and also the `get_coverages` CLI tool.

```bash
$ which get_coverages
# should show where this is installed, probably in .../conda/bin
```

## Cleaned deposit locations

As targets, we've provided 3034 deposit locations gleaned from Geoscience Australia's [Identified Mineral Resources database](http://www.ga.gov.au/scientific-topics/minerals/mineral-resources-and-advice/aimr).

To clean this up and remove deposits that are unlikely to be useful targets we've done the following:
- Remove 'uninteresting' or difficult to predict commodity types like opal, coal, diamond etc
- Concatenated the commodity types into some larger groups for prediction purposes (e.g. illmenite -> Ti, hematite -> Fe)
- Streamlined the commodity type labels into a semicolon-delimited list (;)

and provided the latitude and longitude of these deposits in WGS84 longitude/latitude (epsg:4326).

## Getting geophysical coverage data

Most of the geophysical data for all of Australia is pretty big so we've created a couple of Python functions to pull the data from their [web coverage service endpoints](http://nci.org.au/services/nci-national-research-data-collection/geosciences/) - basically a little wrapper around [owslib](https://github.com/geopython/OWSLib).

All of the endpoints are stored in `explorer_australia/endpoints.py` (note you can also load these in any decent GIS package as well as see them in [nationalmap.gov.au](https://nationalmap.gov.au)). We've provided endpoints for continent-wide magnetics (TMI and VRTP), gravity (isostatic residual and bouger anomaly), a number of ASTER products (which map surface mineralogy at a 30 m scale), and radiometric data (K, Th, U and total dose).

### `get_coverages` CLI

You can use the CLI to pull out aligned coverages for any piece of Australia that you'd like (for example over deposit locations). This should be useful for generating test and train datasets for building your models.

If you've got a particular area that you'd like to look at (e.g. over a known deposit), then you can pull out a box of (roughly) size `distance` using:

```bash
$ get_coverages --help
Usage: get_coverages [OPTIONS] NAME

  Get coverages for a given centre and angle

Options:
  --lat FLOAT         latitude
  --lon FLOAT         longitude
  --distance INTEGER  scale in km
  --angle FLOAT       angle to rotate
  --help              Show this message and exit.

$ get_coverages --lon=122.169999 --lat=-32.42 --angle=239 test_output
# will loop through and grab tifs from WCS

# Show all the downloaded geotiffs
$ ls test_output/**/*
test_output/geophysics/gravity:
bouger_gravity_anomaly.tif  isostatic_residual_gravity_anomaly.tif

test_output/geophysics/magnetics:
total_magnetic_intensity.tif  variable_reduction_to_pole.tif

test_output/geophysics/radiometrics:
filtered_potassium_pct.tif  filtered_terrestrial_dose.tif  filtered_thorium_ppm.tif  filtered_uranium_ppm.tif

test_output/remote_sensing/aster:
aloh_groun_content.tif      ferric_oxide_content.tif  ferrous_iron_index.tif  mgoh_group_content.tif  thermal_infrared_gypsum_index.tif  tir_quartz_index.tif
aloh_group_composition.tif  ferrous_iron_content.tif  kaolin_group_index.tif  opaque_index.tif        thermal_infrared_silica_index.tif
```

The CLI code is in `explore_australia/cli.py` if you want to see the regridding and alignment process (using [rasterio](https://github.com/mapbox/rasterio)).

We've also provided a Jupyter notebook showing you how to use rasterio to read the data once you've downloaded it.

# Geological mapping data

Geoscience Australia provides

The data is available on data.gov.auYou can download the data directly from [here](https://d28rz98at9flks.cloudfront.net/74619/74619_1M_shapefiles.zip). You can see a rendered version [here](https://ecat.ga.gov.au/geonetwork/srv/eng/catalog.search#/metadata/73360).

We've provided a jupyter notebook which you can use to pull out the geology for a particular bounding box.