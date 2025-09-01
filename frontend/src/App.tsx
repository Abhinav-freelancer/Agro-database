
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import MapComponent from './components/MapComponent';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import AdminDashboard from './components/AdminDashboard';
import UserProfile from './components/UserProfile';
import { LatLngTuple } from 'leaflet';

// Define types for our application state
export interface SelectedArea {
  type: 'coordinates' | 'polygon' | 'search';
  data: any; // This will be coordinates, polygon points, or search result
  label?: string;
}

export interface LayerVisibility {
  soil: boolean;
  rainfall: boolean;
  ndvi: boolean;
}

// Main application component with map and sidebar
const MainApp: React.FC = () => {
  // State for selected area (coordinates, polygon, or search result)
  const [selectedArea, setSelectedArea] = useState<SelectedArea | null>(null);
  
  // State for layer visibility
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
    soil: true,
    rainfall: true,
    ndvi: false
  });
  
  // State for map center and zoom
  const [mapCenter, setMapCenter] = useState<LatLngTuple>([20.5937, 78.9629]); // Center of India
  const [mapZoom, setMapZoom] = useState<number>(5);
  
  // State for loading data
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // State for data from backend
  const [vectorData, setVectorData] = useState<any>(null);
  const [rasterData, setRasterData] = useState<any>(null);
  
  // Function to toggle layer visibility
  const toggleLayer = (layer: keyof LayerVisibility) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };
  
  // Function to handle area selection
  const handleAreaSelection = (area: SelectedArea) => {
    setSelectedArea(area);
    // Here we would typically make API calls to fetch data based on the selected area
    setIsLoading(true);
    
    // Simulate API call delay for now
    setTimeout(() => {
      setVectorData({ /* mock data */ });
      setRasterData({ /* mock data */ });
      setIsLoading(false);
    }, 1000);
  };
  
  return (
    <div className="app-container">
      <Header />
      <div className="main-content">
        <MapComponent 
          center={mapCenter}
          zoom={mapZoom}
          selectedArea={selectedArea}
          layerVisibility={layerVisibility}
          vectorData={vectorData}
          rasterData={rasterData}
          onAreaSelection={handleAreaSelection}
        />
        <Sidebar 
          selectedArea={selectedArea}
          layerVisibility={layerVisibility}
          toggleLayer={toggleLayer}
          vectorData={vectorData}
          rasterData={rasterData}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

// Main App component with routing
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/profile" element={<UserProfile />} />
        <Route path="/admin" element={<AdminDashboard />} />
        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
