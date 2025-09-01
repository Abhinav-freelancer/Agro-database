import React, { useRef, useEffect } from 'react';
import { MapContainer, TileLayer, FeatureGroup, Polygon, GeoJSON } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import { LatLngTuple, LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import { SelectedArea, LayerVisibility } from '../App';

interface MapComponentProps {
  center: LatLngTuple;
  zoom: number;
  selectedArea: SelectedArea | null;
  layerVisibility: LayerVisibility;
  vectorData: any;
  rasterData: any;
  onAreaSelection: (area: SelectedArea) => void;
}

const MapComponent: React.FC<MapComponentProps> = ({
  center,
  zoom,
  selectedArea,
  layerVisibility,
  vectorData,
  rasterData,
  onAreaSelection
}) => {
  const featureGroupRef = useRef<any>(null);

  // Handle polygon creation
  const handleCreated = (e: any) => {
    const { layerType, layer } = e;
    
    if (layerType === 'polygon') {
      const polygonCoords = layer.getLatLngs()[0].map((coord: any) => [
        coord.lat,
        coord.lng
      ]);
      
      onAreaSelection({
        type: 'polygon',
        data: polygonCoords
      });
    }
  };

  // Render selected area if it exists
  const renderSelectedArea = () => {
    if (!selectedArea) return null;

    if (selectedArea.type === 'polygon') {
      return (
        <Polygon 
          positions={selectedArea.data as LatLngExpression[]}
          pathOptions={{ color: 'green', fillColor: 'green', fillOpacity: 0.2 }}
        />
      );
    }
    
    // Other area types (point, etc.) would be handled here
    return null;
  };

  // Render vector layers based on visibility settings
  const renderVectorLayers = () => {
    if (!vectorData) return null;

    return (
      <>
        {layerVisibility.soil && vectorData.soil && (
          <GeoJSON 
            data={vectorData.soil}
            style={() => ({ color: '#8B4513', weight: 2, opacity: 0.7 })}
          />
        )}
        {layerVisibility.rainfall && vectorData.rainfall && (
          <GeoJSON 
            data={vectorData.rainfall}
            style={() => ({ color: '#0000FF', weight: 2, opacity: 0.7 })}
          />
        )}
      </>
    );
  };

  // Render raster overlay if visible
  const renderRasterOverlay = () => {
    if (!layerVisibility.ndvi || !rasterData || !rasterData.ndviUrl) return null;

    return (
      <TileLayer
        url={rasterData.ndviUrl}
        opacity={0.7}
      />
    );
  };

  return (
    <div className="map-container">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
      >
        {/* Base map layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Drawing tools */}
        <FeatureGroup ref={featureGroupRef}>
          <EditControl
            position="topright"
            onCreated={handleCreated}
            draw={{
              rectangle: false,
              circle: false,
              circlemarker: false,
              marker: true,
              polyline: false
            }}
          />
        </FeatureGroup>

        {/* Selected area */}
        {renderSelectedArea()}

        {/* Vector layers */}
        {renderVectorLayers()}

        {/* Raster overlay */}
        {renderRasterOverlay()}
      </MapContainer>
    </div>
  );
};

export default MapComponent;