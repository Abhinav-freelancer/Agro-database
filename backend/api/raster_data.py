from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse, Response
from typing import Dict, Any, List, Optional
import json
import os
import tempfile
from datetime import datetime, timedelta
import numpy as np

# Try to import rasterio, but handle the case where it's not installed
try:
    import rasterio
    from rasterio.transform import from_origin
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False

try:
    from shapely.geometry import shape, Polygon, Point
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

# Import services
# from ..services.earth_engine import get_ndvi_data
# from ..services.sentinel_hub import get_sentinel_data

# Import auth service
from services.auth_service import get_current_active_user, User

# Create router
router = APIRouter()

@router.post("/get_raster_data")
async def get_raster_data(
    data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """
    Get raster data (NDVI, etc.) based on a polygon and parameters.
    
    Parameters:
    - data: Dictionary containing GeoJSON polygon, date range, and raster type
    
    Returns:
    - GeoTIFF or PNG raster data
    """
    try:
        # Check if required libraries are available
        if not RASTERIO_AVAILABLE:
            return {"error": "Rasterio library is not installed. Please install it to use this feature."}
        
        if not SHAPELY_AVAILABLE:
            return {"error": "Shapely library is not installed. Please install it to use this feature."}
            
        # Extract parameters from request
        if "polygon" not in data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Polygon must be provided"
            )
        
        polygon = data["polygon"]
        raster_type = data.get("raster_type", "ndvi")
        start_date = data.get("start_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = data.get("end_date", datetime.now().strftime("%Y-%m-%d"))
        
        # Convert GeoJSON polygon to shapely geometry
        geom = shape(polygon)
        
        # Get raster data based on type
        if raster_type.lower() == "ndvi":
            # In a real app, this would call Google Earth Engine or Sentinel Hub API
            # For now, generate a mock NDVI raster
            
            # Create a temporary GeoTIFF file
            with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
                # Create a simple mock NDVI raster (values between -1 and 1)
                # In a real app, this would be actual satellite data
                
                # Get bounds of the geometry
                minx, miny, maxx, maxy = geom.bounds
                width = int((maxx - minx) * 1000)  # 1000 pixels per degree
                height = int((maxy - miny) * 1000)
                
                # Ensure minimum size
                width = max(width, 100)
                height = max(height, 100)
                
                # Create a transform for the raster
                transform = from_origin(minx, maxy, (maxx - minx) / width, (maxy - miny) / height)
                
                # Create mock NDVI data (random values between -0.2 and 0.9)
                ndvi_data = np.random.random((height, width)) * 1.1 - 0.2
                
                # Create a simple pattern (higher values in the center)
                y, x = np.ogrid[-1:1:height*1j, -1:1:width*1j]
                mask = x**2 + y**2 <= 1
                ndvi_data[mask] += 0.3
                
                # Clip values to valid NDVI range (-1 to 1)
                ndvi_data = np.clip(ndvi_data, -1, 1)
                
                # Write to GeoTIFF
                with rasterio.open(
                    tmp.name,
                    'w',
                    driver='GTiff',
                    height=height,
                    width=width,
                    count=1,
                    dtype=ndvi_data.dtype,
                    crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
                    transform=transform,
                ) as dst:
                    dst.write(ndvi_data, 1)
                
                # Return metadata and file path
                return {
                    "raster_type": raster_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "ndvi_min": float(ndvi_data.min()),
                    "ndvi_max": float(ndvi_data.max()),
                    "ndvi_mean": float(ndvi_data.mean()),
                    "width": width,
                    "height": height,
                    "crs": "EPSG:4326",
                    "ndviUrl": f"/raster/get_raster_file?filename={os.path.basename(tmp.name)}",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported raster type: {raster_type}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching raster data: {str(e)}"
        )

@router.get("/get_raster_file")
async def get_raster_file(filename: str):
    """
    Get a raster file by filename.
    
    Parameters:
    - filename: Name of the raster file
    
    Returns:
    - GeoTIFF file
    """
    try:
        # In a real app, this would check if the file exists and return it
        # For now, return a mock response
        return {"message": f"This endpoint would return the raster file: {filename}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching raster file: {str(e)}"
        )