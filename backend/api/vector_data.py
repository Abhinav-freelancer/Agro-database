from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
import geopandas as gpd
from shapely.geometry import Polygon, Point
import os
import datetime
from typing import List, Dict, Any, Optional

# Import services
from ..services.database import get_db_connection

# Create router
router = APIRouter()

# API endpoints
@router.post("/upload")
async def upload_vector_data(
    geojson: Dict[str, Any]
):
    """
    Upload vector data in GeoJSON format.
    """
    try:
        # Convert GeoJSON to GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(geojson["features"])

        # Add metadata
        gdf["upload_date"] = datetime.datetime.now()
        
        # Save to database or file
        # For demo, we'll just return success
        return {"status": "success", "message": "Vector data uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user-data")
async def get_user_vector_data():
    """
    Get vector data uploaded by the current user.
    """
    # In a real app, this would query the database
    # For demo, return sample data
    sample_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Sample Field",
                    "area": "10 hectares",
                    "crop": "Wheat"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [73.856, 18.516],
                            [73.858, 18.516],
                            [73.858, 18.518],
                            [73.856, 18.518],
                            [73.856, 18.516]
                        ]
                    ]
                }
            }
        ]
    }
    return sample_data

@router.post("/get_vector_data")
async def get_vector_data(
    data: Dict[str, Any]
):
    """
    Get vector data based on a polygon or coordinates.
    
    Parameters:
    - data: Dictionary containing either a GeoJSON polygon or coordinates
    
    Returns:
    - GeoJSON features for soil, rainfall, and crop suitability data
    """
    try:
        # Extract geometry from request
        if "polygon" in data:
            # Convert GeoJSON polygon to shapely geometry
            geom = shape(data["polygon"])
        elif "coordinates" in data:
            # Create point from coordinates
            coords = data["coordinates"]
            geom = Point(coords["lng"], coords["lat"])
            # Create a small buffer around the point (e.g., 1km)
            geom = geom.buffer(0.01)  # Approximately 1km buffer
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either polygon or coordinates must be provided"
            )
        
        # Connect to PostGIS database
        conn = get_db_connection()
        
        # Query soil data
        soil_query = f"""
            SELECT 
                soil_type, ph_level, organic_matter, nitrogen, phosphorus, potassium, 
                ST_AsGeoJSON(geom) as geometry
            FROM soil_data
            WHERE ST_Intersects(geom, ST_GeomFromText('{geom.wkt}', 4326))
        """
        
        # Query rainfall data
        rainfall_query = f"""
            SELECT 
                zone_name, annual_avg, monsoon_avg, dry_season_avg, 
                ST_AsGeoJSON(geom) as geometry
            FROM rainfall_zones
            WHERE ST_Intersects(geom, ST_GeomFromText('{geom.wkt}', 4326))
        """
        
        # Query crop suitability data
        crop_query = f"""
            SELECT 
                crop_name, suitability_score, growing_season, 
                ST_AsGeoJSON(geom) as geometry
            FROM crop_suitability
            WHERE ST_Intersects(geom, ST_GeomFromText('{geom.wkt}', 4326))
            ORDER BY suitability_score DESC
        """
        
        # Execute queries and fetch results
        # In a real app, these would be actual database queries
        # For now, return mock data
        
        # Mock soil data
        soil_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "soil_type": "Alluvial",
                        "ph_level": 6.8,
                        "organic_matter": "2.3%",
                        "nitrogen": "Medium",
                        "phosphorus": "Low",
                        "potassium": "High"
                    },
                    "geometry": json.loads(geom.buffer(-0.001).simplify(0.001).__geo_interface__)
                }
            ]
        }
        
        # Mock rainfall data
        rainfall_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "zone_name": "High Rainfall Zone",
                        "annual_avg": "1200mm",
                        "monsoon_avg": "850mm",
                        "dry_season_avg": "120mm"
                    },
                    "geometry": json.loads(geom.buffer(-0.002).simplify(0.001).__geo_interface__)
                }
            ]
        }
        
        # Mock crop suitability data
        crop_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "crop_name": "Rice",
                        "suitability_score": 0.85,
                        "growing_season": "June - November"
                    },
                    "geometry": json.loads(geom.buffer(-0.003).simplify(0.001).__geo_interface__)
                },
                {
                    "type": "Feature",
                    "properties": {
                        "crop_name": "Wheat",
                        "suitability_score": 0.75,
                        "growing_season": "November - March"
                    },
                    "geometry": json.loads(geom.buffer(-0.003).simplify(0.001).__geo_interface__)
                }
            ]
        }
        
        # Return combined data
        return {
            "soil": soil_data,
            "rainfall": rainfall_data,
            "crop_suitability": crop_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching vector data: {str(e)}"
        )