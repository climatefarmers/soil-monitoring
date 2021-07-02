# soil-monitoring
A set of tools and services to collect and process soil monitoring data

# Roadmap
## 1. Data acquisition functions
As a first step, we need to identify currently available data sources and develop a series of function with a common interface to query data from these sources. 
Data sources should cover soil, weather, and possibly administrative data. The common interface of the query functions should allow passing a georeferenced region of interest polygon as a parameter and retrieving data either raw or aggregated (descriptive statistics) for this region of interest. 

### 1.1 Soil property data

#### 1.1.1 Soilgrids
A set of 250m resolution global raster layers with soil properties such as pH, soc, clay content, bulk density, etc. See this (list)[https://maps.isric.org/] of available layers.  
(Documentation for querying the data using WCS from python)[https://www.isric.org/web-coverage-services-wcs] - see OWSLib

Task: Write a function that receives a georeferenced Polygon (using for example Shapely) and a the name of a soilgrids source layer. It should be possible to pass options to receive either: 1.) the original raster clipped to the polygon extent or 2.) descriptive statistics (mean, median, std, etc.) for all raster cells covered by the polygon.

#### 1.1.2 Restor
TBD, see platform (here)[https://restor.eco/]

#### 1.1.3 Vandersat
Partnership TBD

### 1.2 Weather data
Use publicly available sources for temperature, humidity, precipation, wind etc. and implement the same functionality as described above. 

## 2. Workflow executor
TBD

## 3. Integration with modelling service
TBD
