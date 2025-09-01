-- PostgreSQL + PostGIS database schema for Sustainable Agriculture in India

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create schema
CREATE SCHEMA IF NOT EXISTS agro;

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS agro.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create soil data table
CREATE TABLE IF NOT EXISTS agro.soil_data (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    soil_type VARCHAR(50) NOT NULL,
    ph_value NUMERIC(4,2),
    nitrogen_kgha NUMERIC(6,2),
    phosphorus_kgha NUMERIC(6,2),
    potassium_kgha NUMERIC(6,2),
    organic_carbon_pct NUMERIC(4,2),
    cec_meq NUMERIC(5,2),
    texture VARCHAR(50),
    drainage VARCHAR(50),
    depth_cm INTEGER,
    source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create rainfall zones table
CREATE TABLE IF NOT EXISTS agro.rainfall_zones (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    annual_rainfall_mm INTEGER,
    monsoon_rainfall_mm INTEGER,
    winter_rainfall_mm INTEGER,
    rainfall_zone VARCHAR(50),
    drought_prone BOOLEAN,
    source VARCHAR(100),
    year INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create crop suitability table
CREATE TABLE IF NOT EXISTS agro.crop_suitability (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    crop_name VARCHAR(50) NOT NULL,
    suitability_score INTEGER CHECK (suitability_score BETWEEN 1 AND 10),
    yield_potential_tonha NUMERIC(5,2),
    water_requirement_mm INTEGER,
    growing_season VARCHAR(50),
    soil_requirements TEXT,
    climate_requirements TEXT,
    source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create raster metadata table
CREATE TABLE IF NOT EXISTS agro.raster_metadata (
    id SERIAL PRIMARY KEY,
    raster_type VARCHAR(50) NOT NULL, -- NDVI, EVI, etc.
    acquisition_date DATE NOT NULL,
    cloud_cover_pct NUMERIC(5,2),
    resolution_m INTEGER,
    satellite VARCHAR(50), -- Sentinel-2, Landsat, etc.
    storage_url TEXT NOT NULL, -- URL to cloud storage
    bounds GEOMETRY(Polygon, 4326),
    min_value NUMERIC(8,4),
    max_value NUMERIC(8,4),
    mean_value NUMERIC(8,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create user saved areas table
CREATE TABLE IF NOT EXISTS agro.user_areas (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES agro.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS agro.reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES agro.users(id) ON DELETE SET NULL,
    area_id INTEGER REFERENCES agro.user_areas(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial indexes
CREATE INDEX IF NOT EXISTS soil_data_geom_idx ON agro.soil_data USING GIST(geom);
CREATE INDEX IF NOT EXISTS rainfall_zones_geom_idx ON agro.rainfall_zones USING GIST(geom);
CREATE INDEX IF NOT EXISTS crop_suitability_geom_idx ON agro.crop_suitability USING GIST(geom);
CREATE INDEX IF NOT EXISTS raster_metadata_bounds_idx ON agro.raster_metadata USING GIST(bounds);
CREATE INDEX IF NOT EXISTS user_areas_geom_idx ON agro.user_areas USING GIST(geom);

-- Create indexes on commonly queried fields
CREATE INDEX IF NOT EXISTS soil_data_soil_type_idx ON agro.soil_data(soil_type);
CREATE INDEX IF NOT EXISTS rainfall_zones_rainfall_zone_idx ON agro.rainfall_zones(rainfall_zone);
CREATE INDEX IF NOT EXISTS crop_suitability_crop_name_idx ON agro.crop_suitability(crop_name);
CREATE INDEX IF NOT EXISTS raster_metadata_type_date_idx ON agro.raster_metadata(raster_type, acquisition_date);

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to update timestamps
CREATE TRIGGER update_soil_data_timestamp
    BEFORE UPDATE ON agro.soil_data
    FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_rainfall_zones_timestamp
    BEFORE UPDATE ON agro.rainfall_zones
    FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_crop_suitability_timestamp
    BEFORE UPDATE ON agro.crop_suitability
    FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_user_areas_timestamp
    BEFORE UPDATE ON agro.user_areas
    FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_users_timestamp
    BEFORE UPDATE ON agro.users
    FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- Sample data insertion function (for development purposes)
CREATE OR REPLACE FUNCTION agro.insert_sample_data()
    RETURNS VOID AS $$
BEGIN
    -- Insert sample user
    INSERT INTO agro.users (username, email, password_hash, is_admin)
    VALUES ('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE)
    ON CONFLICT (username) DO NOTHING;
    
    -- Insert sample soil data for parts of India
    INSERT INTO agro.soil_data (geom, soil_type, ph_value, nitrogen_kgha, phosphorus_kgha, potassium_kgha, organic_carbon_pct)
    VALUES 
    (ST_Multi(ST_GeomFromText('POLYGON((73.0 19.0, 73.5 19.0, 73.5 19.5, 73.0 19.5, 73.0 19.0))', 4326)), 'Black Cotton Soil', 7.2, 280.5, 12.8, 190.3, 0.75),
    (ST_Multi(ST_GeomFromText('POLYGON((72.5 19.0, 73.0 19.0, 73.0 19.5, 72.5 19.5, 72.5 19.0))', 4326)), 'Red Soil', 6.5, 240.2, 10.5, 150.8, 0.62),
    (ST_Multi(ST_GeomFromText('POLYGON((73.5 19.0, 74.0 19.0, 74.0 19.5, 73.5 19.5, 73.5 19.0))', 4326)), 'Alluvial Soil', 7.8, 320.1, 15.2, 210.5, 0.88)
    ON CONFLICT DO NOTHING;
    
    -- Insert sample rainfall zones
    INSERT INTO agro.rainfall_zones (geom, annual_rainfall_mm, monsoon_rainfall_mm, winter_rainfall_mm, rainfall_zone)
    VALUES 
    (ST_Multi(ST_GeomFromText('POLYGON((73.0 19.0, 74.0 19.0, 74.0 20.0, 73.0 20.0, 73.0 19.0))', 4326)), 2500, 2200, 150, 'High Rainfall'),
    (ST_Multi(ST_GeomFromText('POLYGON((72.0 19.0, 73.0 19.0, 73.0 20.0, 72.0 20.0, 72.0 19.0))', 4326)), 1200, 1000, 100, 'Medium Rainfall'),
    (ST_Multi(ST_GeomFromText('POLYGON((71.0 19.0, 72.0 19.0, 72.0 20.0, 71.0 20.0, 71.0 19.0))', 4326)), 600, 500, 50, 'Low Rainfall')
    ON CONFLICT DO NOTHING;
    
    -- Insert sample crop suitability
    INSERT INTO agro.crop_suitability (geom, crop_name, suitability_score, yield_potential_tonha, water_requirement_mm)
    VALUES 
    (ST_Multi(ST_GeomFromText('POLYGON((73.0 19.0, 73.5 19.0, 73.5 19.5, 73.0 19.5, 73.0 19.0))', 4326)), 'Rice', 9, 5.2, 1200),
    (ST_Multi(ST_GeomFromText('POLYGON((72.5 19.0, 73.0 19.0, 73.0 19.5, 72.5 19.5, 72.5 19.0))', 4326)), 'Cotton', 8, 2.8, 700),
    (ST_Multi(ST_GeomFromText('POLYGON((73.5 19.0, 74.0 19.0, 74.0 19.5, 73.5 19.5, 73.5 19.0))', 4326)), 'Wheat', 7, 4.5, 450)
    ON CONFLICT DO NOTHING;
    
    -- Insert sample raster metadata
    INSERT INTO agro.raster_metadata (raster_type, acquisition_date, cloud_cover_pct, resolution_m, satellite, storage_url, bounds, min_value, max_value, mean_value)
    VALUES 
    ('NDVI', '2023-06-15', 2.5, 10, 'Sentinel-2', 'https://storage.example.com/ndvi_20230615.tif', 
     ST_GeomFromText('POLYGON((72.0 19.0, 74.0 19.0, 74.0 20.0, 72.0 20.0, 72.0 19.0))', 4326), -0.2, 0.9, 0.45),
    ('EVI', '2023-06-15', 2.5, 10, 'Sentinel-2', 'https://storage.example.com/evi_20230615.tif', 
     ST_GeomFromText('POLYGON((72.0 19.0, 74.0 19.0, 74.0 20.0, 72.0 20.0, 72.0 19.0))', 4326), 0.0, 1.0, 0.5)
    ON CONFLICT DO NOTHING;
    
END;
$$ LANGUAGE plpgsql;