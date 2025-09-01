import React from 'react';
import { SelectedArea, LayerVisibility } from '../App';
import LocationSearch from './LocationSearch';
import LayerControl from './LayerControl';
import DataPanel from './DataPanel';
import ChartPanel from './ChartPanel';
import DownloadPanel from './DownloadPanel';

interface SidebarProps {
  selectedArea: SelectedArea | null;
  layerVisibility: LayerVisibility;
  toggleLayer: (layer: keyof LayerVisibility) => void;
  vectorData: any;
  rasterData: any;
  isLoading: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({
  selectedArea,
  layerVisibility,
  toggleLayer,
  vectorData,
  rasterData,
  isLoading
}) => {
  return (
    <div className="sidebar">
      <h2>Agricultural Intelligence</h2>
      
      {/* Location search component */}
      <div className="control-panel">
        <h3>Location Selection</h3>
        <LocationSearch />
        <p className="help-text">
          Search for a location, enter coordinates, or draw a polygon on the map
        </p>
      </div>
      
      {/* Layer control component */}
      <div className="control-panel">
        <h3>Map Layers</h3>
        <LayerControl 
          layerVisibility={layerVisibility}
          toggleLayer={toggleLayer}
        />
      </div>
      
      {/* Data display panel */}
      {isLoading ? (
        <div className="loading">Loading data...</div>
      ) : selectedArea ? (
        <>
          <DataPanel 
            selectedArea={selectedArea}
            vectorData={vectorData}
            rasterData={rasterData}
          />
          
          <ChartPanel 
            vectorData={vectorData}
            rasterData={rasterData}
          />
          
          <DownloadPanel 
            selectedArea={selectedArea}
            vectorData={vectorData}
            rasterData={rasterData}
          />
        </>
      ) : (
        <div className="no-selection">
          <p>Select an area on the map to view data</p>
        </div>
      )}
    </div>
  );
};

export default Sidebar;