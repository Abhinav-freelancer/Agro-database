import ee
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from shapely.geometry import shape

# Initialize Earth Engine
# In a real app, this would use service account credentials
ee_initialized = False
try:
    ee.Initialize()
    ee_initialized = True
except Exception as e:
    print(f"Error initializing Earth Engine: {str(e)}")
    print("Using mock data instead")

def get_ndvi_data(polygon: Dict[str, Any], start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Get NDVI data from Google Earth Engine.

    Parameters:
    - polygon: GeoJSON polygon
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format

    Returns:
    - Dictionary containing NDVI data and metadata
    """
    if not ee_initialized:
        # Return mock data if Earth Engine is not initialized
        return {
            "ndvi_min": -0.2,
            "ndvi_max": 0.9,
            "ndvi_mean": 0.45,
            "download_url": "https://example.com/mock-ndvi.tif",
            "file_path": "/tmp/mock-ndvi.tif",
            "start_date": start_date,
            "end_date": end_date,
            "is_mock": True
        }

    try:
        # Convert GeoJSON polygon to Earth Engine geometry
        geom = shape(polygon)
        coords = []
        
        # Handle different polygon types
        if geom.geom_type == 'Polygon':
            # Convert exterior ring to EE format
            for point in list(geom.exterior.coords):
                coords.append([point[0], point[1]])
        else:
            # For now, just use the first polygon if it's a MultiPolygon
            for point in list(geom.geoms[0].exterior.coords):
                coords.append([point[0], point[1]])
        
        ee_polygon = ee.Geometry.Polygon(coords)
        
        # Get Sentinel-2 imagery collection
        s2 = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterDate(start_date, end_date) \
            .filterBounds(ee_polygon) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        # Function to calculate NDVI
        def add_ndvi(image):
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            return image.addBands(ndvi)
        
        # Add NDVI band to all images
        s2_with_ndvi = s2.map(add_ndvi)
        
        # Get the median NDVI value
        ndvi_median = s2_with_ndvi.select('NDVI').median()
        
        # Clip to the polygon
        ndvi_clipped = ndvi_median.clip(ee_polygon)
        
        # Get NDVI statistics
        ndvi_stats = ndvi_clipped.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                reducer2=ee.Reducer.minMax(),
                sharedInputs=True
            ),
            geometry=ee_polygon,
            scale=10,
            maxPixels=1e9
        ).getInfo()
        
        # Create a temporary file for the GeoTIFF
        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
            # Get the download URL
            url = ndvi_clipped.getDownloadURL({
                'scale': 10,
                'crs': 'EPSG:4326',
                'region': ee_polygon,
                'format': 'GEO_TIFF'
            })
            
            # In a real app, we would download the file here
            # For now, just return the URL and stats
            return {
                "ndvi_min": ndvi_stats.get('NDVI_min', -1),
                "ndvi_max": ndvi_stats.get('NDVI_max', 1),
                "ndvi_mean": ndvi_stats.get('NDVI_mean', 0),
                "download_url": url,
                "file_path": tmp.name,
                "start_date": start_date,
                "end_date": end_date
            }
    
    except Exception as e:
        print(f"Error getting NDVI data from Earth Engine: {str(e)}")
        # Return mock data
        return {
            "ndvi_min": -0.2,
            "ndvi_max": 0.9,
            "ndvi_mean": 0.45,
            "download_url": "https://example.com/mock-ndvi.tif",
            "file_path": "/tmp/mock-ndvi.tif",
            "start_date": start_date,
            "end_date": end_date,
            "is_mock": True
        }