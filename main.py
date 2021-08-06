from pyproj.crs.crs import CRS
from shapely import geometry
from pydantic import BaseModel, validator
from fastapi import FastAPI
from typing import List, Optional, Union
from providers import soilgrids


class GeoJsonGeom(BaseModel):
    """Represents GeoJson geometry spec"""
    type: str
    coordinates: Union[List, List[List]]

class FieldProperties(BaseModel):
    field_name: Optional[str]
    farm_id: Optional[int]
    pk: Optional[int]

class GeoJsonFeature(BaseModel):
    type: str
    properties: FieldProperties
    geometry: GeoJsonGeom

    @validator('type')
    def type_must_be_feature(cls, v):
        if v != "Feature":
            raise ValueError(f'Expected Feature, got {type}')
        return v

class GeoJsonPolygonFeature(GeoJsonFeature):
    """Represents the GeoJson Polygon feature spec"""
    geometry: GeoJsonGeom

    @validator('geometry')
    def geometry_must_be_polygon(cls, v):
        if v.type != "Polygon":
            raise ValueError(f'Expected a polygon, got {v.type}')
        return v

    @validator('geometry')
    def coordinates_must_be_list_of_lists(cls, v):
        if not isinstance(v.coordinates[0], list):
            raise ValueError(f'Expected a list of coordinate pairs, got {v.coordinates}')
        return v

class CRSName(BaseModel):
    name: str

class CRS(BaseModel):
    type: str
    properties: CRSName

class GeoJsonFeatureCollection(BaseModel):
    type: str
    crs: CRS
    features: List[GeoJsonFeature]

    @validator('type')
    def type_must_be_feature(cls, v):
        if v != "FeatureCollection":
            raise ValueError(f'Expected FeatureCollection, got {v}')
        return v.title

class GeoJsonPolygonFeatureCollection(GeoJsonFeatureCollection):
    features: List[GeoJsonPolygonFeature]

class SoilStats(BaseModel):
    layer: str
    data: List


app = FastAPI()

@app.get("/")
async def index():
    return {"status": "alive"}

@app.get("/health")
async def healthcheck():
    return {"status": "alive"}

@app.post("/soilgrids/{lyr}", response_model=SoilStats)
async def address_parser(aoi: GeoJsonPolygonFeatureCollection, lyr: str) -> SoilStats:

    crs = aoi.crs.properties.name

    stats_coll = []
    for i, feature in enumerate(aoi.features):
        data = soilgrids.stats_for_polygon(feature.geometry.dict(), crs, lyr)
        data['feature_id'] = i
        stats_coll.append(data)
    return {
        'layer': lyr,
        'data': stats_coll
    }