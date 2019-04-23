""" file:    endpoints.py (explore_australia)
    author:  Jess Robertson, @jesserobertson
    date:    Tuesday, 05 March 2019

    description: Endpoint locations for geophysical coverages on NCI
"""

RADMAP = {
    'filtered_terrestrial_dose': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_dose/radmap_v3_2015_filtered_dose.nc',
    'filtered_potassium_pct': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_pctk/radmap_v3_2015_filtered_pctk.nc',
    'filtered_thorium_ppm': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_ppmth/radmap_v3_2015_filtered_ppmth.nc',
    'filtered_uranium_ppm': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/radmap_v3_2015_filtered_ppmu/radmap_v3_2015_filtered_ppmu.nc'
}

MAGNETICS = {
    'variable_reduction_to_pole': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/magmap_v6_2015_VRTP/magmap_v6_2015_VRTP.nc',
    'total_magnetic_intensity': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/magmap_v6_2015/magmap_v6_2015.nc'
}

# For some reason a couple of these are b0rked
ASTER = {
    'aloh_group_composition': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_AlOH_group_composition_reprojected.nc4',
    'ferrous_iron_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Ferrous_Iron_Index_reprojected.nc4',
    'opaque_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Opaque_Index_reprojected.nc4',
    'ferric_oxide_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Ferric_oxide_content_reprojected.nc4',
    # 'feoh_group_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_FeOH_group_content_reprojected.nc4',
    'kaolin_group_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Kaolin_group_index_reprojected.nc4',
    'tir_quartz_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Quartz_Index_reprojected.nc4',
    'mgoh_group_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_MgOH_group_content_reprojected.nc4',
    # 'mgoh_group_composition': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_MgOH_group_composition_reprojected.nc4',
    'ferrous_iron_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_Ferrous_iron_content_in_MgOH_reprojected.nc4',
    'aloh_groun_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Aus_Mainland/Aus_Mainland_AlOH_group_content_reprojected.nc4',
    'thermal_infrared_gypsum_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Gypsum_Index_reprojected.nc4',
    'thermal_infrared_silica_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Silica_Index_reprojected.nc4'
}
ASTER_TAS = {
    'aloh_group_composition': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_AlOH_Group_composition_reprojected.nc4',
    'ferrous_iron_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_Ferrous_Iron_index_reprojected.nc4',
    'opaque_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_Opaque_index_reprojected.nc4',
    'ferric_oxide_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_Ferric_Oxide_content_reprojected.nc4',
    # 'feoh_group_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_FeOH_Group_content_reprojected.nc4',
    'kaolin_group_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_Kaolin_group_index_reprojected.nc4',
    'tir_quartz_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Quartz_Index_reprojected.nc4',
    'mgoh_group_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_MgOH_group_content_reprojected.nc4',
    # 'mgoh_group_composition': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_MgOH_group_composition_reprojected.nc4',
    'ferrous_iron_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_Ferrous_iron_in_MgOH_content_reprojected.nc4',
    'aloh_groun_content': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/vnir/Tasmania/Tas_AlOH_group_content_reprojected.nc4',
    'thermal_infrared_gypsum_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Gypsum_Index_reprojected.nc4',
    'thermal_infrared_silica_index': 'http://dap-wms.nci.org.au/thredds/wcs/wx7/aster/thermal/Aus_ASTER_L2EM_Silica_Index_reprojected.nc4'
}

GRAVITY = {
    'isostatic_residual_gravity_anomaly': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/onshore_geodetic_Isostatic_Residual_v2_2016/onshore_geodetic_Isostatic_Residual_v2_2016.nc',
    'bouger_gravity_anomaly': 'http://dap-wms.nci.org.au/thredds/wcs/rr2/geophysics/onshore_geodetic_Complete_Bouguer_2016/onshore_geodetic_Complete_Bouguer_2016.nc',
}

TOTAL_COVERAGES = len(ASTER) + len(GRAVITY) + len(RADMAP) + len(MAGNETICS)
