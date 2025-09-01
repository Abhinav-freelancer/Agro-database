from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List, Dict, Any
import json
import os
import uuid
from datetime import datetime, timedelta

# Import security middleware
from .middleware.security import setup_security

# Import API routers
from .api.vector_data import router as vector_router
from .api.raster_data import router as raster_router
from .api.report import router as report_router

# Create FastAPI app
app = FastAPI(
    title="Agro Geospatial API",
    description="API for the Geospatial Agricultural Intelligence System",
    version="0.1.0"
)

# Configure security middleware
setup_security(app, allowed_origins=["*"])  # In production, replace with specific origins

# Include routers
app.include_router(vector_router, prefix="/vector", tags=["Vector Data"])
app.include_router(raster_router, prefix="/raster", tags=["Raster Data"])
app.include_router(report_router, prefix="/report", tags=["Reports"])

# Configure startup and shutdown events
@app.on_event("startup")
async def startup_event():
    print("Starting up the Agro Geospatial API...")
    # Initialize any services here

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down the Agro Geospatial API...")
    # Clean up any resources here

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Agro Geospatial API"}

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Search location endpoint (placeholder for Google Maps API integration)
@app.get("/search_location", tags=["Location"])
async def search_location(q: str):
    # In a real app, this would call the Google Maps API
    # For now, return mock data
    return {
        "query": q,
        "results": [
            {
                "name": f"Sample location for {q}",
                "lat": 20.5937,
                "lng": 78.9629,
                "address": f"Sample address for {q}, India"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)