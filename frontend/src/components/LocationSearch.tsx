import React, { useState } from 'react';

const LocationSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [coordinates, setCoordinates] = useState<{lat: string, lng: string}>({ lat: '', lng: '' });
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would call the Google Maps API for geocoding
    console.log('Searching for:', searchQuery);
    // Mock API call
    alert(`Search functionality would call Google Maps API to find: ${searchQuery}`);
  };
  
  const handleCoordinateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Validate coordinates
    const lat = parseFloat(coordinates.lat);
    const lng = parseFloat(coordinates.lng);
    
    if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
      alert('Please enter valid coordinates');
      return;
    }
    
    // In a real app, this would center the map and possibly fetch data
    console.log('Coordinates entered:', lat, lng);
    alert(`Map would center on coordinates: ${lat}, ${lng}`);
  };
  
  return (
    <div className="location-search">
      {/* Search by place name */}
      <form onSubmit={handleSearch}>
        <div className="form-group">
          <label htmlFor="search">Search Location:</label>
          <div className="search-input">
            <input
              type="text"
              id="search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter city, district, or state"
            />
            <button type="submit">Search</button>
          </div>
        </div>
      </form>
      
      {/* Enter coordinates */}
      <form onSubmit={handleCoordinateSubmit}>
        <div className="form-group">
          <label>Enter Coordinates:</label>
          <div className="coordinates-input">
            <input
              type="text"
              value={coordinates.lat}
              onChange={(e) => setCoordinates({ ...coordinates, lat: e.target.value })}
              placeholder="Latitude"
            />
            <input
              type="text"
              value={coordinates.lng}
              onChange={(e) => setCoordinates({ ...coordinates, lng: e.target.value })}
              placeholder="Longitude"
            />
            <button type="submit">Go</button>
          </div>
        </div>
      </form>
      
      <div className="draw-instructions">
        <p><small>Or use the polygon tool on the map to draw an area</small></p>
      </div>
    </div>
  );
};

export default LocationSearch;