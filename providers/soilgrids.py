from array import array
from typing import List
from owslib.wcs import WebCoverageService
import rasterio
import sys
from rasterio import MemoryFile
from pyproj import CRS, Transformer
import fiona
from fiona.transform import transform_geom
import numpy as np

from shapely.geometry import shape, Point, Polygon

SOILGRIDS_BASE_URL = "https://maps.isric.org/mapserv"

SOILGRIDS_CRS = CRS.from_string("""
    PROJCS["Homolosine", 
        GEOGCS["WGS 84", 
            DATUM["WGS_1984", 
                SPHEROID["WGS 84",6378137,298.257223563, 
                    AUTHORITY["EPSG","7030"]], 
    AUTHORITY["EPSG","6326"]], 
            PRIMEM["Greenwich",0, 
                AUTHORITY["EPSG","8901"]], 
            UNIT["degree",0.0174532925199433, 
                AUTHORITY["EPSG","9122"]], 
            AUTHORITY["EPSG","4326"]], 
        PROJECTION["Interrupted_Goode_Homolosine"], 
        UNIT["Meter",1]]
    """)

SOILGRIDS_CRS_EPSG = "http://www.opengis.net/def/crs/EPSG/0/152160"

SOILGRIDS_DEPTHS = [
    (0,5),
    (5-15),
    (15-30),
    (30-60),
    (60-100),
    (100-200)
]

SOILGRIDS_PRODUCTS = {
    'soc': {
        'description': 'Soil organic carbon content',
        'unit': 'dg/kg'
        },
    'bdod': {
        'description': 'Bulk density',
        'unit': 'cg/cm³'
        },
    'clay': {
        'description': 'Clay content',
        'unit': 'g/kg'
        },
    'wrb': {
        'description': 'WRB classes and probabilites',
        'unit': None
        },
    'cec': {
        'description': 'Cation exchange capacity at ph 7',
        'unit': 'mmol(c)/kg'
        },
    'cfvo': {
        'description': 'Coarse fragments volumetric',
        'unit': 'cm3/dm3 (vol‰)'
        },
    'nitrogen': {
        'description': 'Nitrogen',
        'unit': 'cg/kg'
        },
    'phh20': {
        'description': 'Soil pH in H2O',
        'unit': 'pHx10'
        },
    'sand': {
        'description': 'Sand content',
        'unit': 'g/kg'
        },
    'silt': {
        'description': 'Silt content',
        'unit': 'g/kg'
        },
    'ocs': {
        'description': 'Soil organic carbon stock',
        'unit': 't/ha'
        },
    'ocd': {
        'description': 'Organic carbon densities',
        'unit': 'hg/m³'
        },
}

SOILGRIDS_TYPES = [
    'Q0.05',
    'mean',
    'Q0.95',
    'uncertainty'
]


def read_shapefile(shp: str) -> dict:
    with fiona.open(shp) as f:
        field = next(iter(f))
    return field


def get_bbox(geometry: dict) -> tuple:
    return shape(geometry).bounds


def reproject_field_geom(geometry, s_crs):
    return transform_geom(
        s_crs, 
        SOILGRIDS_CRS.to_proj4(), 
        geometry)


def get_wcs_subsets(bbox: tuple) -> List[tuple]:
    min_x, min_y, max_x, max_y = bbox
    return [("X", min_x, max_x), ("Y", min_y, max_y)]


def get_wcs_available_layers(url):
    wcs = WebCoverageService(url, version="2.0.1")
    return wcs.contents.keys()


def get_wcs_layer(url, lyr, subsets, format="image/tiff"):
    wcs = WebCoverageService(url, version="2.0.1")
    return wcs.getCoverage(
        identifier=[lyr],
        subsets =subsets,
        format='image/tiff',
        crs = SOILGRIDS_CRS_EPSG
    )

def raster_to_points(dataset, band=1, offset='center'):
    if offset == 'center':
        coff, roff = (0.5, 0.5)
    elif offset == 'ul':
        coff, roff = (0, 0)
    elif offset == 'ur':
        coff, roff = (1, 0)
    elif offset == 'll':
        coff, roff = (0, 1)
    elif offset == 'lr':
        coff, roff = (1, 1)
    else:
        raise ValueError("Invalid offset")
    
    data = dataset.read(band)
    transform = dataset.transform
    T = transform * transform.translation(coff, roff)
    points = []
    values = []
    for i in range(dataset.width):
        for j in range(dataset.height):
            x, y = T * (i,j)
            points.append((x,y))
            val = data[j,i]
            values.append(val)
    return points, values


def points_in_boundary(response, boundary):
    points = []
    valid = []

    with MemoryFile(response.read()) as memfile:
        with memfile.open() as dataset:
            points, values = raster_to_points(dataset)
            for p, v in zip(points, values):        
                pos = Point(*p)
                if boundary.contains(pos):
                    points.append(p)
                    valid.append(v)
    
    return points, valid

def get_stats(values, stats=['mean', 'min', 'max', 'std']):
    values = np.array(values)
    return {s: float(getattr(np, s)(values)) for s in stats}

def stats_for_polygon(geometry, crs, lyr):
    product = lyr.split('_')[0]
    map_route = f"/map/{product}.map"
    url = "?map=".join((SOILGRIDS_BASE_URL, map_route))

    transformed = reproject_field_geom(geometry, crs)
    bbox = get_bbox(transformed)
    subsets = get_wcs_subsets(bbox)
    response = get_wcs_layer(url, lyr, subsets)
    points, values = points_in_boundary(response, shape(transformed))
    stats = get_stats(values)
    return {
        'statistics': stats,
        'unit': SOILGRIDS_PRODUCTS[product]['unit']
    }

if __name__ == "__main__":
    # For local run with shapefile path
    shp = sys.argv[1]
    soilgrids_soc = "/map/ocs.map" #"/map/soc.map"

    layer = "ocs_0-30cm" #"soc_0-5cm_mean"
    url = "?map=".join((SOILGRIDS_BASE_URL, soilgrids_soc))
    s_crs = "EPSG:4326"

    import pdb; pdb.set_trace()
    layers = get_wcs_available_layers(url)
    print(layers)

    field = read_shapefile(shp)
    transformed = reproject_field_geom(field['geometry'], s_crs)
    bbox = get_bbox(transformed)
    subsets = get_wcs_subsets(bbox)

    area_ha = shape(transformed).area / 10000

    print("###############################")
    print("Results:")
    print("###############################")
    print('Area: ', area_ha)

    print(url)

    for type in SOILGRIDS_TYPES:
        lyr = '_'.join((layer, type))
        response = get_wcs_layer(url, lyr, subsets)
        points, values = points_in_boundary(response, shape(transformed))
        stats = get_stats(values)
        print(lyr)
        print(stats)

    with open(f'./test_{lyr}.tif', 'wb') as file:
        file.write(response.read())
