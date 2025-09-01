import React from 'react';
import { LayerVisibility } from '../App';

interface LayerControlProps {
  layerVisibility: LayerVisibility;
  toggleLayer: (layer: keyof LayerVisibility) => void;
}

const LayerControl: React.FC<LayerControlProps> = ({ layerVisibility, toggleLayer }) => {
  return (
    <div className="layer-controls">
      <div className="layer-control">
        <input
          type="checkbox"
          id="soil-layer"
          checked={layerVisibility.soil}
          onChange={() => toggleLayer('soil')}
        />
        <label htmlFor="soil-layer">Soil Data</label>
      </div>
      
      <div className="layer-control">
        <input
          type="checkbox"
          id="rainfall-layer"
          checked={layerVisibility.rainfall}
          onChange={() => toggleLayer('rainfall')}
        />
        <label htmlFor="rainfall-layer">Rainfall Zones</label>
      </div>
      
      <div className="layer-control">
        <input
          type="checkbox"
          id="ndvi-layer"
          checked={layerVisibility.ndvi}
          onChange={() => toggleLayer('ndvi')}
        />
        <label htmlFor="ndvi-layer">NDVI Vegetation Index</label>
      </div>
    </div>
  );
};

export default LayerControl;