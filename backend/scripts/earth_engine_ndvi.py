#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Google Earth Engine NDVI Data Processing Script

This script demonstrates how to use Google Earth Engine to process NDVI data
for agricultural monitoring in India. It includes functions to:
1. Authenticate with Earth Engine
2. Fetch Sentinel-2 imagery for a given area and time period
3. Calculate NDVI (Normalized Difference Vegetation Index)
4. Export NDVI data as GeoTIFF
5. Calculate statistics for agricultural analysis

Usage:
    python earth_engine_ndvi.py --geojson area.geojson --start 2023-01-01 --end 2023-12-31 --output ndvi.tif
"""

import argparse
import datetime
import ee
import geojson
import os
import sys
import time
from shapely.geometry import shape
from typing import Dict, Any, List, Optional, Union

# Initialize Earth Engine
def initialize_earth_engine(service_account_key: Optional[str] = None):
    """
    Initialize Google Earth Engine with service account or user account.
    
    Args:
        service_account_key: Path to service account key JSON file (optional)
    """
    try:
        if service_account_key and os.path.exists(service_account_key):
            # Initialize with service account
            credentials = ee.ServiceAccountCredentials(
                os.environ.get('EE_SERVICE_ACCOUNT', ''),
                service_account_key
            )
            ee.Initialize(credentials)
            print("Initialized Earth Engine with service account.")
        else:
            # Initialize with user account (requires authentication)
            ee.Initialize()
            print("Initialized Earth Engine with user account.")
    except Exception as e:
        print(f"Error initializing Earth Engine: {str(e)}")
        print("Please make sure you have authenticated with Earth Engine.")
        print("Run 'earthengine authenticate' if using the earthengine-api package.")
        sys.exit(1)

def load_geojson(geojson_path: str) -> Dict[str, Any]:
    """
    Load GeoJSON file and return as dictionary.
    
    Args:
        geojson_path: Path to GeoJSON file
        
    Returns:
        GeoJSON as dictionary
    """
    try:
        with open(geojson_path, 'r') as f:
            return geojson.load(f)
    except Exception as e:
        print(f"Error loading GeoJSON file: {str(e)}")
        sys.exit(1)

def geojson_to_ee_geometry(geojson_dict: Dict[str, Any]) -> ee.Geometry:
    """
    Convert GeoJSON to Earth Engine geometry.
    
    Args:
        geojson_dict: GeoJSON as dictionary
        
    Returns:
        Earth Engine geometry
    """
    try:
        # Handle different GeoJSON types
        if geojson_dict['type'] == 'FeatureCollection':
            # Use the first feature
            feature = geojson_dict['features'][0]
            geom = feature['geometry']
        elif geojson_dict['type'] == 'Feature':
            geom = geojson_dict['geometry']
        else:
            # Assume it's a geometry
            geom = geojson_dict
        
        # Convert to shapely geometry
        shapely_geom = shape(geom)
        
        # Convert to EE geometry based on type
        if shapely_geom.geom_type == 'Polygon':
            coords = [list(shapely_geom.exterior.coords)]
            return ee.Geometry.Polygon(coords)
        elif shapely_geom.geom_type == 'MultiPolygon':
            # Convert each polygon
            ee_polygons = []
            for poly in shapely_geom.geoms:
                coords = list(poly.exterior.coords)
                ee_polygons.append(coords)
            return ee.Geometry.MultiPolygon(ee_polygons)
        else:
            print(f"Unsupported geometry type: {shapely_geom.geom_type}")
            sys.exit(1)
    except Exception as e:
        print(f"Error converting GeoJSON to Earth Engine geometry: {str(e)}")
        sys.exit(1)

def get_sentinel2_collection(start_date: str, end_date: str, geometry: ee.Geometry, 
                            max_cloud_cover: int = 20) -> ee.ImageCollection:
    """
    Get Sentinel-2 image collection for a given time period and area.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        geometry: Earth Engine geometry
        max_cloud_cover: Maximum cloud cover percentage
        
    Returns:
        Earth Engine image collection
    """
    try:
        # Get Sentinel-2 Surface Reflectance collection
        collection = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterDate(start_date, end_date) \
            .filterBounds(geometry) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloud_cover))
        
        # Check if collection is empty
        count = collection.size().getInfo()
        if count == 0:
            print(f"No Sentinel-2 images found for the given parameters.")
            print(f"Try expanding the date range or increasing max_cloud_cover.")
            sys.exit(1)
            
        print(f"Found {count} Sentinel-2 images.")
        return collection
    except Exception as e:
        print(f"Error getting Sentinel-2 collection: {str(e)}")
        sys.exit(1)

def calculate_ndvi(image: ee.Image) -> ee.Image:
    """
    Calculate NDVI for a Sentinel-2 image.
    
    Args:
        image: Earth Engine image
        
    Returns:
        Image with NDVI band added
    """
    # Calculate NDVI: (NIR - RED) / (NIR + RED)
    # For Sentinel-2, NIR is B8 and RED is B4
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

def create_ndvi_composite(collection: ee.ImageCollection, method: str = 'median') -> ee.Image:
    """
    Create an NDVI composite from an image collection.
    
    Args:
        collection: Earth Engine image collection
        method: Compositing method ('median', 'mean', 'max', 'min')
        
    Returns:
        NDVI composite image
    """
    # Add NDVI band to all images
    ndvi_collection = collection.map(calculate_ndvi)
    
    # Create composite based on method
    if method == 'mean':
        composite = ndvi_collection.select('NDVI').mean()
    elif method == 'max':
        composite = ndvi_collection.select('NDVI').max()
    elif method == 'min':
        composite = ndvi_collection.select('NDVI').min()
    else:  # Default to median
        composite = ndvi_collection.select('NDVI').median()
    
    return composite

def calculate_ndvi_statistics(ndvi_image: ee.Image, geometry: ee.Geometry) -> Dict[str, float]:
    """
    Calculate NDVI statistics for a region.
    
    Args:
        ndvi_image: NDVI image
        geometry: Region of interest
        
    Returns:
        Dictionary of statistics
    """
    try:
        # Calculate statistics
        stats = ndvi_image.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                reducer2=ee.Reducer.minMax(),
                sharedInputs=True
            ).combine(
                reducer2=ee.Reducer.stdDev(),
                sharedInputs=True
            ),
            geometry=geometry,
            scale=10,  # Sentinel-2 resolution
            maxPixels=1e9
        ).getInfo()
        
        return {
            'ndvi_min': stats.get('NDVI_min', None),
            'ndvi_max': stats.get('NDVI_max', None),
            'ndvi_mean': stats.get('NDVI_mean', None),
            'ndvi_stdDev': stats.get('NDVI_stdDev', None)
        }
    except Exception as e:
        print(f"Error calculating NDVI statistics: {str(e)}")
        return {}

def export_ndvi_image(ndvi_image: ee.Image, geometry: ee.Geometry, output_path: str):
    """
    Export NDVI image as GeoTIFF.
    
    Args:
        ndvi_image: NDVI image
        geometry: Region of interest
        output_path: Output file path
    """
    try:
        # Get the download URL
        url = ndvi_image.getDownloadURL({
            'scale': 10,  # Sentinel-2 resolution
            'crs': 'EPSG:4326',
            'region': geometry,
            'format': 'GEO_TIFF'
        })
        
        print(f"Download URL: {url}")
        print(f"To download the GeoTIFF, use the URL above or implement a download function.")
        
        # In a real application, you would download the file here
        # For example:
        # import requests
        # response = requests.get(url)
        # with open(output_path, 'wb') as f:
        #     f.write(response.content)
        # print(f"Saved NDVI image to {output_path}")
    except Exception as e:
        print(f"Error exporting NDVI image: {str(e)}")

def analyze_agricultural_health(ndvi_stats: Dict[str, float]) -> Dict[str, Any]:
    """
    Analyze agricultural health based on NDVI statistics.
    
    Args:
        ndvi_stats: NDVI statistics
        
    Returns:
        Dictionary with analysis results
    """
    # Simple analysis based on NDVI ranges
    ndvi_mean = ndvi_stats.get('ndvi_mean', 0)
    
    if ndvi_mean < 0.2:
        health = 'Poor'
        description = 'Vegetation is sparse or unhealthy. This may indicate bare soil, drought stress, or crop failure.'
    elif ndvi_mean < 0.4:
        health = 'Fair'
        description = 'Moderate vegetation health. This may indicate early growth stages or moderate stress conditions.'
    elif ndvi_mean < 0.6:
        health = 'Good'
        description = 'Good vegetation health. Crops are likely in active growth phase with adequate water and nutrients.'
    else:
        health = 'Excellent'
        description = 'Excellent vegetation health. Crops are likely at peak growth with optimal conditions.'
    
    return {
        'health_status': health,
        'description': description,
        'ndvi_stats': ndvi_stats
    }

def main():
    """
    Main function to process NDVI data.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process NDVI data from Google Earth Engine')
    parser.add_argument('--geojson', required=True, help='Path to GeoJSON file')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', required=True, help='Output GeoTIFF path')
    parser.add_argument('--cloud', type=int, default=20, help='Maximum cloud cover percentage')
    parser.add_argument('--method', choices=['median', 'mean', 'max', 'min'], default='median',
                        help='NDVI compositing method')
    parser.add_argument('--key', help='Path to service account key JSON file')
    
    args = parser.parse_args()
    
    # Initialize Earth Engine
    initialize_earth_engine(args.key)
    
    # Load GeoJSON
    geojson_dict = load_geojson(args.geojson)
    
    # Convert to Earth Engine geometry
    geometry = geojson_to_ee_geometry(geojson_dict)
    
    # Get Sentinel-2 collection
    collection = get_sentinel2_collection(args.start, args.end, geometry, args.cloud)
    
    # Create NDVI composite
    ndvi_composite = create_ndvi_composite(collection, args.method)
    
    # Calculate statistics
    stats = calculate_ndvi_statistics(ndvi_composite, geometry)
    print("NDVI Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Analyze agricultural health
    analysis = analyze_agricultural_health(stats)
    print(f"\nAgricultural Health: {analysis['health_status']}")
    print(f"Description: {analysis['description']}")
    
    # Export NDVI image
    export_ndvi_image(ndvi_composite, geometry, args.output)

if __name__ == '__main__':
    main()