import React from 'react';
import { SelectedArea } from '../App';

interface DownloadPanelProps {
  selectedArea: SelectedArea | null;
  vectorData: any;
  rasterData: any;
}

const DownloadPanel: React.FC<DownloadPanelProps> = ({ selectedArea, vectorData, rasterData }) => {
  if (!selectedArea) return null;
  
  const handleDownload = (format: string) => {
    // In a real app, this would call the backend API to generate and download the file
    console.log(`Downloading data in ${format} format`);
    alert(`In a real app, this would download the data in ${format} format`);
  };
  
  return (
    <div className="download-panel">
      <h3>Download Data</h3>
      <div className="download-buttons">
        <button 
          className="download-button"
          onClick={() => handleDownload('CSV')}
        >
          CSV
        </button>
        <button 
          className="download-button"
          onClick={() => handleDownload('GeoJSON')}
        >
          GeoJSON
        </button>
        <button 
          className="download-button"
          onClick={() => handleDownload('GeoTIFF')}
        >
          GeoTIFF
        </button>
        <button 
          className="download-button"
          onClick={() => handleDownload('PDF')}
        >
          PDF Report
        </button>
      </div>
    </div>
  );
};

export default DownloadPanel;