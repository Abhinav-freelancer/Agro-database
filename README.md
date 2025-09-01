# Geospatial Agricultural Intelligence System for Sustainable Agriculture in India

## Project Overview

This project aims to develop a web-based geospatial agricultural intelligence system for sustainable agriculture in India. The system allows users to select a location (via Google Maps search, coordinates input, or polygon selection on a map) and automatically retrieves, processes, and visualizes both vector data (database attributes) and raster data (satellite imagery and derived indices) about that location.

## System Architecture

The system architecture consists of the following components:

- **Frontend Client**: React.js UI, Leaflet/Mapbox for maps, D3.js/Chart.js for data visualization, and Google Maps API for location search.
- **API Gateway**: Handles user requests and forwards them to the backend services.
- **Backend Services**: Includes location parser, vector data service, raster data service, and analytics engine.
- **Database Layer**: PostgreSQL with PostGIS for spatial queries and a raster datastore for large datasets.
- **External APIs**: Integration with Google Earth Engine, Sentinel Hub, and Bhuvan APIs.
- **Output Layer**: Provides data in various formats (GeoJSON, GeoTIFF, PDF, CSV) for download.

## Data Pipeline

The data pipeline follows these steps:

1. **User Input Stage**: Users can select a location using Google Maps search, direct coordinate input, polygon drawing, or shapefile upload.
2. **Backend Processing**:
   - **Step 1**: Spatial Query - Query PostGIS database for attributes intersecting with the user-selected location.
   - **Step 2**: Raster Extraction - Clip satellite datasets to the user polygon and generate vegetation indices.
   - **Step 3**: Data Fusion - Combine vector attributes with raster layers and normalize datasets.
3. **Data Visualization Layer**: Interactive web map with toggleable layers, chart panels, and tabular views.
4. **User Output Stage**: On-screen interactive map, download options, and decision-support outputs.

## Project Roadmap

The project will be implemented in the following phases:

1. **Phase 1**: Setup PostGIS database, integrate Google Maps input, and display soil/rainfall vector data.
2. **Phase 2**: Integrate satellite APIs (Sentinel Hub, GEE), implement raster extraction, and NDVI visualization.
3. **Phase 3**: Develop analytics engine for charts, trends, and recommendations.
4. **Phase 4**: Enable report generation (PDF, GeoTIFF, CSV downloads).
5. **Phase 5**: Deploy on cloud (AWS/GCP) with scalable architecture.
6. **Phase 6**: Add AI-driven decision support, mobile app, and alerting system.

## Use Cases

The system supports three main user types:

1. **Farmer**: Selects village → gets soil pH, organic carbon, NDVI-based crop health → receives recommendation for best crop + fertilizer dose.
2. **Policymaker**: Selects district → gets aggregated rainfall, cropping pattern, drought zones → uses data for subsidy planning.
3. **Researcher**: Uploads shapefile of study area → system extracts Sentinel-2 NDVI time-series → exports data for modeling.

## Diagrams

The following diagrams are available in the `docs/diagrams` directory:

- `system_architecture.svg`: Shows the components of the system architecture.
- `data_pipeline.svg`: Illustrates the flow from user input to vector query, raster extraction, and visualization.
- `project_roadmap.svg`: Outlines the phased development plan.
- `use_case_flowchart.svg`: Depicts the user interactions for different user types.

## Project Structure

```
agro/
├── docs/
│   └── diagrams/
│       ├── system_architecture.svg
│       ├── data_pipeline.svg
│       ├── project_roadmap.svg
│       └── use_case_flowchart.svg
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       └── assets/
├── backend/
│   ├── api/
│   ├── services/
│   └── database/
└── README.md
```

## Getting Started

This project is currently in the planning phase. The diagrams in the `docs/diagrams` directory provide a visual representation of the system architecture, data pipeline, project roadmap, and use cases.

## Next Steps

1. Set up the development environment for frontend and backend.
2. Initialize the PostgreSQL database with PostGIS extension.
3. Develop the basic frontend UI with React.js.
4. Implement the location selection functionality using Google Maps API.
5. Create the API endpoints for vector data retrieval.

## Technologies

- **Frontend**: React.js, Leaflet.js/Mapbox GL JS, D3.js/Chart.js, Google Maps API
- **Backend**: Python (FastAPI), GDAL, Rasterio, Shapely, GeoPandas, Google Earth Engine Python API
- **Database**: PostgreSQL + PostGIS
- **Cloud**: AWS/GCP (planned for deployment)