//Creat polygons for three fields:
var Field1 = ee.Geometry.Polygon([
    [[11.9517, 45.3465], [11.9517, 45.3460],  [11.9523, 45.3460], [11.9523, 45.3465]]]);
  
var Field2 = ee.Geometry.Polygon([
[[11.9517, 45.3460], [11.9517, 45.3455],  [11.9523, 45.3455], [11.9523, 45.3460]]]);

var Field3 = ee.Geometry.Polygon([
[[11.9517, 45.3455], [11.9517, 45.3450],  [11.9523, 45.3450], [11.9523, 45.3455]]]);

// FeatureCollection.
var regions = ee.FeatureCollection([
ee.Feature( (Field1), {label: 'Field1'}),
ee.Feature( (Field2), {label: 'Field2'}),
ee.Feature( (Field3), {label: 'Field3'}),]);

// Create image collection of S-2 imagery for the period 2016-2020
var S2 = ee.ImageCollection('COPERNICUS/S2')
.filter(ee.Filter.calendarRange(2016,2020,'year'))
.filter(ee.Filter.calendarRange(7,8,'month'))
.filterBounds(regions)
.filterMetadata('CLOUDY_PIXEL_PERCENTAGE', 'less_than', 20);

// Function to calculate and add NDVI, GNDVI & NDRE as bands
var addNDVI = function(image) {
var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
return image.addBands(ndvi);
};
var addGNDVI = function(image) {
var gndvi = image.normalizedDifference(['B8', 'B3']).rename('GNDVI');
return image.addBands(gndvi);
};
var addNDRE = function(image) {
var ndre = image.normalizedDifference(['B8', 'B5']).rename('NDRE');
return image.addBands(ndre);
};

// Add VI band to image collection
var S2 = S2.map(addNDVI).map(addGNDVI).map(addNDRE);

// Extract NDVI band and create NDVI median composite image
var NDVI = S2.select(['NDVI']);
var NDVI = NDVI.max();

// Create palettes for display of NDVI
var ndvi_pal = ['ECB176','E6E600', 'EFC2B3', '00A600','63C600','F2F2F2','E9BD3A'];
// Display NDVI results on map
Map.centerObject(regions);
Map.addLayer(NDVI.clip(regions), {min:0.8, max:0.9, palette: ndvi_pal}, 'NDVI');
Map.addLayer(regions);
// Create a time series chart NDVI mean.
var plotNDVImean = ui.Chart.image.seriesByRegion(S2, regions , ee.Reducer.mean(),('NDVI'), 100,'system:time_start', 'label')
        .setChartType('ScatterChart')
        .setOptions({
        title: 'NDVI Mean',
        vAxis: {title: 'NDVI mean'},
        lineWidth: 1,
        pointSize: 4,
        series: {
            0: {color: 'FF0000'}, 
            1: {color: '00FF00'}, 
            2: {color: '0000FF'}  
}});
/// Display.
print(plotNDVImean);

// Create a time series chart GNDVI mean.
var plotGNDVImean = ui.Chart.image.seriesByRegion(S2, regions , ee.Reducer.mean(),('GNDVI'), 100,'system:time_start', 'label')
        .setChartType('ScatterChart')
        .setOptions({
        title: 'GNDVI Mean',
        vAxis: {title: 'GNDVI mean'},
        lineWidth: 1,
        pointSize: 4,
        series: {
            0: {color: 'FF0000'}, 
            1: {color: '00FF00'}, 
            2: {color: '0000FF'}  
}});
/// Display.
print(plotGNDVImean);

// Create a time series chart NDRE mean.
var plotNDREmean = ui.Chart.image.seriesByRegion(S2, regions , ee.Reducer.mean(),('NDRE'), 100,'system:time_start', 'label')
        .setChartType('ScatterChart')
        .setOptions({
        title: 'NDRE Mean',
        vAxis: {title: 'NDRE mean'},
        lineWidth: 1,
        pointSize: 4,
        series: {
            0: {color: 'FF0000'}, 
            1: {color: '00FF00'}, 
            2: {color: '0000FF'}  
}});
/// Display.
print(plotNDREmean);