
var collection = ee.ImageCollection('COPERNICUS/S2_SR')
.filterDate('2020-01-01', '2020-12-31')
.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',20))

var addNDVI = function(image) {
var ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI');
return image.addBands(ndvi);
};

var clipper = function(image) {
return image.clip(geometry);
};

var withNDVI = collection.map(addNDVI).map(clipper);
var greenest = withNDVI.qualityMosaic('NDVI');


var visParams = {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000};

var ndviParams = {min: 0, max: 1, palette: ['red', 'white', 'green']};
Map.centerObject(geometry, 14);
Map.addLayer(greenest, visParams, 'RGB');
Map.addLayer(greenest.select('NDVI'), ndviParams, 'NDVI band');


// change field views by selecting the layer on the 'layers' toolbar on the right
// red = very low NDVI, white = middle area, green = higher NDVI
