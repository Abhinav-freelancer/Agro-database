
import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="logo">
        <Link to="/">
          <h1>Agro Geospatial Intelligence</h1>
        </Link>
      </div>
      <div className="nav-links">
        <Link to="/">Dashboard</Link>
        <Link to="/about">About</Link>
        <Link to="/help">Help</Link>
      </div>
    </header>
  );
};

export default Header;
