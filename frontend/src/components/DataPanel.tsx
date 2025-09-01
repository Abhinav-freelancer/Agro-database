import React from 'react';
import { SelectedArea } from '../App';

interface DataPanelProps {
  selectedArea: SelectedArea | null;
  vectorData: any;
  rasterData: any;
}

const DataPanel: React.FC<DataPanelProps> = ({ selectedArea, vectorData, rasterData }) => {
  if (!selectedArea) return null;
  
  // In a real app, this data would come from the backend API
  // For now, we'll use mock data
  const mockSoilData = {
    type: 'Alluvial',
    ph: 6.8,
    organicMatter: '2.3%',
    nitrogen: 'Medium',
    phosphorus: 'Low',
    potassium: 'High'
  };
  
  const mockRainfallData = {
    annualAverage: '1200mm',
    monsoonAverage: '850mm',
    drySeasonAverage: '120mm',
    zone: 'High Rainfall Zone'
  };
  
  const mockCropData = {
    suitableCrops: ['Rice', 'Wheat', 'Sugarcane', 'Vegetables'],
    recommendedCrop: 'Rice',
    growingSeason: 'June - November'
  };
  
  return (
    <div className="data-panel">
      <h3>Area Information</h3>
      
      {/* Display area type and details */}
      <div className="area-info">
        <p>
          <strong>Selection Type:</strong> {selectedArea.type}
          {selectedArea.label && <span> - {selectedArea.label}</span>}
        </p>
        {selectedArea.type === 'polygon' && (
          <p><strong>Area Size:</strong> ~25 hectares</p>
        )}
      </div>
      
      {/* Soil Data */}
      <div className="data-section">
        <h4>Soil Data</h4>
        <table>
          <tbody>
            <tr>
              <td>Soil Type:</td>
              <td>{mockSoilData.type}</td>
            </tr>
            <tr>
              <td>pH Level:</td>
              <td>{mockSoilData.ph}</td>
            </tr>
            <tr>
              <td>Organic Matter:</td>
              <td>{mockSoilData.organicMatter}</td>
            </tr>
            <tr>
              <td>Nitrogen:</td>
              <td>{mockSoilData.nitrogen}</td>
            </tr>
            <tr>
              <td>Phosphorus:</td>
              <td>{mockSoilData.phosphorus}</td>
            </tr>
            <tr>
              <td>Potassium:</td>
              <td>{mockSoilData.potassium}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      {/* Rainfall Data */}
      <div className="data-section">
        <h4>Rainfall Data</h4>
        <table>
          <tbody>
            <tr>
              <td>Annual Average:</td>
              <td>{mockRainfallData.annualAverage}</td>
            </tr>
            <tr>
              <td>Monsoon Average:</td>
              <td>{mockRainfallData.monsoonAverage}</td>
            </tr>
            <tr>
              <td>Dry Season Average:</td>
              <td>{mockRainfallData.drySeasonAverage}</td>
            </tr>
            <tr>
              <td>Rainfall Zone:</td>
              <td>{mockRainfallData.zone}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      {/* Crop Suitability */}
      <div className="data-section">
        <h4>Crop Suitability</h4>
        <p><strong>Suitable Crops:</strong> {mockCropData.suitableCrops.join(', ')}</p>
        <p><strong>Recommended Crop:</strong> {mockCropData.recommendedCrop}</p>
        <p><strong>Growing Season:</strong> {mockCropData.growingSeason}</p>
      </div>
    </div>
  );
};

export default DataPanel;